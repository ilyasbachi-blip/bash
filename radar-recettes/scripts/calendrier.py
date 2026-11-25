#!/usr/bin/env python3
"""Construit dist/a-tourner.ics à partir des statuts cochés sur la page Radar.

Entrée : un export de la collection « statuts » de la page publiée (outil
ArtifactData, action list, out_dir) — un fichier JSON (liste de documents, ou
objet avec une clé "docs"/"documents"), ou un dossier de fichiers JSON (un
document par fichier). Chaque document : id, st, prio, date (AAAA-MM-JJ), t,
o, url, moi, ts.

Sortie : un calendrier iCalendar avec un événement « journée entière » par
ligne « À faire » qui a un jour de tournage. Les lignes sans jour sont listées
sur la sortie standard pour mémoire, mais pas dans le calendrier (Apple
Calendrier n'affiche pas les tâches d'un abonnement).

    python3 scripts/calendrier.py <export.json | dossier/> [--out dist/a-tourner.ics]

Apple Calendrier (iPhone : Réglages → Apps → Calendrier → Comptes → Autre →
« Ajouter un cal. avec abonnement » ; Mac : Fichier → Nouvel abonnement) lit
le fichier à son adresse publique dans le dépôt :
https://raw.githubusercontent.com/ilyasbachi-blip/bash/main/radar-recettes/dist/a-tourner.ics
"""
import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "a-tourner.ics"
PRIO_LABEL = {"1": "P1 · cette semaine", "2": "P2 · bientôt", "3": "P3 · plus tard"}
PRIO_ICAL = {"1": "1", "2": "5", "3": "9"}  # PRIORITY iCalendar : 1 haute, 5 moyenne, 9 basse


def load_docs(src: Path) -> list[dict]:
    paths = sorted(src.glob("*.json")) if src.is_dir() else [src]
    docs: list[dict] = []
    for p in paths:
        raw = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            for key in ("docs", "documents", "items", "data"):
                if isinstance(raw.get(key), list):
                    raw = raw[key]
                    break
        if isinstance(raw, dict):
            raw = [raw]
        for d in raw:
            if isinstance(d, dict) and "data" in d and isinstance(d["data"], dict):
                d = dict(d["data"], **{k: v for k, v in d.items() if k in ("id",) and "id" not in d["data"]})
            if isinstance(d, dict) and d.get("id"):
                docs.append(d)
    # un seul document par id, le plus récent gagne
    byid: dict[str, dict] = {}
    for d in docs:
        if d["id"] not in byid or str(d.get("ts", "")) >= str(byid[d["id"]].get("ts", "")):
            byid[d["id"]] = d
    return list(byid.values())


def ics_text(s) -> str:
    s = str(s or "")
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\r\n", "\\n").replace("\n", "\\n")


def fold(line: str) -> str:
    """Repli des lignes à 75 octets (RFC 5545)."""
    out, cur = [], ""
    for ch in line:
        if len((cur + ch).encode("utf-8")) > 74:
            out.append(cur)
            cur = " " + ch
        else:
            cur += ch
    out.append(cur)
    return "\r\n".join(out)


def uid(doc_id: str) -> str:
    """Stable pour une même ligne (Apple remplace l'événement au lieu de le dupliquer)."""
    import hashlib
    return hashlib.sha1(doc_id.encode("utf-8")).hexdigest()[:20] + "@radar.cookwithbash"


def build(docs: list[dict]) -> tuple[str, list[dict], list[dict]]:
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    todo = [d for d in docs if d.get("st") == "todo"]
    dated = [d for d in todo if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(d.get("date", "")))]
    undated = [d for d in todo if d not in dated]
    dated.sort(key=lambda d: (d["date"], str(d.get("prio") or "9"), str(d.get("t", ""))))
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//CookWithBash//Radar recettes//FR",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Radar · à tourner",
        "X-WR-CALDESC:Tournages cochés « À faire » sur la page Radar recettes",
        "X-WR-TIMEZONE:Europe/Paris",
        "REFRESH-INTERVAL;VALUE=DURATION:PT6H",
        "X-PUBLISHED-TTL:PT6H",
    ]
    for d in dated:
        day = date.fromisoformat(d["date"])
        prio = str(d.get("prio") or "")
        title = str(d.get("t") or d["id"])
        summary = f"🎬 {title}" + (f" ({PRIO_LABEL[prio].split(' · ')[0]})" if prio in PRIO_LABEL else "")
        desc_parts = [p for p in (d.get("o"), d.get("moi"), PRIO_LABEL.get(prio)) if p]
        lines += [
            "BEGIN:VEVENT",
            f"UID:{uid(d['id'])}",
            f"DTSTAMP:{now}",
            f"DTSTART;VALUE=DATE:{day.strftime('%Y%m%d')}",
            f"DTEND;VALUE=DATE:{(day + timedelta(days=1)).strftime('%Y%m%d')}",
            f"SUMMARY:{ics_text(summary)}",
        ]
        if desc_parts:
            lines.append(f"DESCRIPTION:{ics_text(' — '.join(desc_parts))}")
        if str(d.get("url", "")).startswith("https://"):
            lines.append(f"URL:{d['url']}")
        if prio in PRIO_ICAL:
            lines.append(f"PRIORITY:{PRIO_ICAL[prio]}")
        lines += ["CATEGORIES:Tournage", "TRANSP:TRANSPARENT", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    return "\r\n".join(fold(l) for l in lines) + "\r\n", dated, undated


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="export JSON de la collection statuts, ou dossier de documents")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    src = Path(args.source)
    if not src.exists():
        print(f"introuvable : {src}", file=sys.stderr)
        return 1
    docs = load_docs(src)
    text, dated, undated = build(docs)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"{out} : {len(dated)} événement(s) sur {len(docs)} statut(s) lus")
    for d in dated:
        print(f"  {d['date']}  P{d.get('prio') or '-'}  {d.get('t') or d['id']}")
    if undated:
        print(f"À faire sans jour (pas dans le calendrier) : {len(undated)}")
        for d in undated:
            print(f"  P{d.get('prio') or '-'}  {d.get('t') or d['id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
