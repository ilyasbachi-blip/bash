#!/usr/bin/env python3
"""Inventaire en LECTURE SEULE d'un dossier de rushs (Sony FX30 + iPhone).

- parcourt récursivement le dossier ;
- lit les métadonnées (ffprobe + sidecar XML Sony C####M01.XML) ;
- déduit l'heure réelle de tournage (avec fuseau quand il est connu) ;
- classe chronologiquement, regroupe par tournage (écart > --gap minutes) ;
- signale les doublons (empreinte partielle) et les fichiers inutilisables.

N'écrit QUE dans le dossier de sortie. Ne modifie, ne déplace, ne renomme rien.

Usage : python3 inventaire.py /chemin/rushs --out suivi/inventaire
"""
import argparse, csv, hashlib, json, os, re, subprocess, sys
from datetime import datetime, timedelta, timezone

VIDEO_EXT = {".mp4", ".mov", ".mxf", ".m4v", ".mts", ".avi", ".mkv"}
AUDIO_EXT = {".wav", ".m4a", ".mp3", ".aac"}


def ffprobe(path):
    cmd = ["ffprobe", "-v", "error", "-print_format", "json",
           "-show_format", "-show_streams", path]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return None, "ffprobe timeout"
    if r.returncode != 0:
        return None, (r.stderr.strip() or "ffprobe a échoué")[:300]
    return json.loads(r.stdout), None


def parse_dt(s):
    if not s:
        return None
    s = s.strip().replace("Z", "+00:00")
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S",
                "%Y:%m:%d %H:%M:%S%z", "%Y:%m:%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None


def sony_sidecar(path):
    """C0001.MP4 -> C0001M01.XML : CreationDate avec fuseau, modèle, timecode."""
    base, _ = os.path.splitext(path)
    for cand in (base + "M01.XML", base + "M01.xml"):
        if os.path.exists(cand):
            try:
                txt = open(cand, encoding="utf-8", errors="ignore").read()
            except OSError:
                return {}
            out = {"sidecar": os.path.basename(cand)}
            m = re.search(r'CreationDate value="([^"]+)"', txt)
            if m:
                out["date"] = m.group(1)
            m = re.search(r'modelName="([^"]+)"', txt)
            if m:
                out["model"] = m.group(1)
            m = re.search(r'LtcChange[^>]*?value="([0-9a-fA-F]{8})"', txt)
            if m:
                out["ltc_raw"] = m.group(1)
            return out
    return {}


def partial_hash(path, chunk=4 * 1024 * 1024):
    h = hashlib.sha1()
    size = os.path.getsize(path)
    h.update(str(size).encode())
    with open(path, "rb") as f:
        h.update(f.read(chunk))
        if size > 2 * chunk:
            f.seek(size // 2)
            h.update(f.read(chunk))
            f.seek(-chunk, os.SEEK_END)
            h.update(f.read(chunk))
    return h.hexdigest()


def decode_check(path, seconds=None):
    """Décode le fichier (entier par défaut) pour repérer les fichiers corrompus."""
    cmd = ["ffmpeg", "-v", "error", "-xerror", "-i", path]
    if seconds:
        cmd += ["-t", str(seconds)]
    cmd += ["-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0, r.stderr.strip()[:300]


def analyse(path, full_decode):
    info = {"fichier": path, "nom": os.path.basename(path),
            "taille_mo": round(os.path.getsize(path) / 1e6, 1)}
    data, err = ffprobe(path)
    if data is None:
        info.update(statut="INUTILISABLE", probleme=err)
        return info
    fmt = data.get("format", {})
    tags = {k.lower(): v for k, v in (fmt.get("tags") or {}).items()}
    v = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
    tmcd = next((s for s in data["streams"]
                 if (s.get("tags") or {}).get("timecode")), None)

    make = tags.get("com.apple.quicktime.make", "")
    model = tags.get("com.apple.quicktime.model", "")
    sc = sony_sidecar(path)
    if sc.get("model"):
        make, model = "Sony", sc["model"]
    if not make:
        enc = (tags.get("encoder", "") + tags.get("major_brand", "")).lower()
        if "xavc" in enc or re.match(r"^C\d{4}", info["nom"]):
            make = "Sony (probable)"
    info["appareil"] = f"{make} {model}".strip() or "inconnu"

    # Heure réelle : priorité aux sources avec fuseau horaire.
    src, dt = None, None
    for key, label in ((sc.get("date"), "sony_xml"),
                       (tags.get("com.apple.quicktime.creationdate"), "apple"),
                       (tags.get("creation_time"), "mp4_creation_time")):
        d = parse_dt(key)
        if d:
            src, dt = label, d
            break
    if dt is None:
        dt = datetime.fromtimestamp(os.path.getmtime(path))
        src = "mtime_fichier(peu fiable)"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)  # creation_time MP4 = UTC par norme
    info["heure_tournage"] = dt.isoformat()
    info["source_heure"] = src
    info["timecode"] = (tmcd or {}).get("tags", {}).get("timecode") or \
        (v or {}).get("tags", {}).get("timecode", "")

    dur = float(fmt.get("duration") or 0)
    info["duree_s"] = round(dur, 2)
    if v:
        rot = 0
        for sd in v.get("side_data_list", []) or []:
            if "rotation" in sd:
                rot = int(sd["rotation"])
        rot = rot or int((v.get("tags") or {}).get("rotate", 0) or 0)
        w, h = v.get("width"), v.get("height")
        if abs(rot) in (90, 270):
            w, h = h, w
        num, den = (v.get("r_frame_rate") or "0/1").split("/")
        info.update(
            resolution=f"{w}x{h}", orientation="vertical" if h > w else "horizontal",
            fps=round(int(num) / int(den), 3) if int(den) else 0,
            codec=v.get("codec_name"), profil=v.get("profile", ""),
            pix_fmt=v.get("pix_fmt"),
            transfert=v.get("color_transfer", ""), primaires=v.get("color_primaries", ""),
            hdr_ou_log=("OUI" if v.get("color_transfer") in ("arib-std-b67", "smpte2084")
                        else ""),
            bitrate_mbps=round(int(fmt.get("bit_rate", 0)) / 1e6, 1))
    else:
        info["resolution"] = "audio seul"
    info["audio"] = f'{a["codec_name"]} {a.get("channels")}ch {a.get("sample_rate")}Hz' if a else "AUCUN"

    probleme = []
    if dur < 1:
        probleme.append("durée < 1 s")
    if v is None and os.path.splitext(path)[1].lower() in VIDEO_EXT:
        probleme.append("pas de piste vidéo")
    ok, derr = decode_check(path, None if full_decode else 5)
    if not ok:
        probleme.append("erreur de décodage: " + derr)
    info["probleme"] = " ; ".join(probleme)
    info["statut"] = "INUTILISABLE" if probleme else "OK"
    info["empreinte"] = partial_hash(path)
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dossier")
    ap.add_argument("--out", default="suivi/inventaire")
    ap.add_argument("--gap", type=float, default=45, help="minutes entre deux tournages")
    ap.add_argument("--full-decode", action="store_true",
                    help="décoder chaque fichier en entier (lent mais exhaustif)")
    args = ap.parse_args()

    root = os.path.abspath(args.dossier)
    out = os.path.abspath(args.out)
    if out.startswith(root + os.sep) or out == root:
        sys.exit("Refus : le dossier de sortie ne doit pas être dans le dossier des rushs.")
    os.makedirs(out, exist_ok=True)

    files = []
    for d, _, names in os.walk(root):
        for n in names:
            if n.startswith("._"):
                continue  # métadonnées macOS
            if os.path.splitext(n)[1].lower() in VIDEO_EXT | AUDIO_EXT:
                files.append(os.path.join(d, n))
    print(f"{len(files)} fichiers média trouvés", file=sys.stderr)

    rows = []
    for i, f in enumerate(sorted(files), 1):
        print(f"[{i}/{len(files)}] {f}", file=sys.stderr)
        rows.append(analyse(f, args.full_decode))

    def instant(r):
        t = r.get("heure_tournage")
        return datetime.fromisoformat(t).astimezone(timezone.utc) if t else \
            datetime.max.replace(tzinfo=timezone.utc)
    rows.sort(key=instant)
    seen, shoot, last = {}, 0, None
    for r in rows:
        h = r.get("empreinte")
        r["doublon_de"] = seen.get(h, "") if h else ""
        if h and h not in seen:
            seen[h] = r["fichier"]
        t = instant(r) if r.get("heure_tournage") else None
        if t and (last is None or t - last > timedelta(minutes=args.gap)):
            shoot += 1
        if t:
            end = t + timedelta(seconds=r.get("duree_s", 0))
            last = max(last, end) if last else end
        r["tournage"] = f"T{shoot:02d}" if t else "ILLISIBLE"

    cols = ["tournage", "heure_tournage", "source_heure", "appareil", "nom", "duree_s",
            "resolution", "orientation", "fps", "codec", "profil", "pix_fmt", "transfert",
            "primaires", "hdr_ou_log", "bitrate_mbps", "audio", "timecode", "taille_mo",
            "statut", "probleme", "doublon_de", "empreinte", "fichier"]
    with open(os.path.join(out, "inventaire.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(out, "inventaire.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    n_bad = sum(r["statut"] != "OK" for r in rows)
    n_dup = sum(bool(r["doublon_de"]) for r in rows)
    print(f"OK : {len(rows)} fichiers, {shoot} tournage(s), {n_bad} inutilisable(s), "
          f"{n_dup} doublon(s) -> {out}/inventaire.csv", file=sys.stderr)


if __name__ == "__main__":
    main()
