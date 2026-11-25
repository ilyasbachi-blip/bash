#!/usr/bin/env python3
"""Outils pour les fichiers de semaine (data/semaines/AAAA-Wnn.json).

    python3 scripts/semaine.py id [AAAA-MM-JJ]     -> identifiant ISO de la semaine (ex. 2026-W49)
    python3 scripts/semaine.py new [AAAA-MM-JJ]    -> crée le squelette de la semaine (sans écraser)
    python3 scripts/semaine.py check <fichier.json> -> vérifie la structure attendue par la page
"""
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEMAINES = ROOT / "data" / "semaines"
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"]

VIRAL_KEYS = {"id", "t", "src", "vues", "date", "meca", "moi", "url"}
FORMAT_KEYS = {"t", "src", "d"}
FOCUS_KEYS = {"t", "q", "d"}


def parse(d: str | None) -> date:
    return datetime.strptime(d, "%Y-%m-%d").date() if d else date.today()


def week_id(d: date) -> str:
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def monday(d: date) -> date:
    return d - timedelta(days=d.weekday())


def fr(d: date) -> str:
    day = "1er" if d.day == 1 else str(d.day)
    return f"{day} {MOIS[d.month - 1]} {d.year}"


def skeleton(d: date) -> dict:
    m = monday(d)
    return {
        "start": m.isoformat(),
        "label": f"Semaine du {fr(m)}",
        "releve": fr(d),
        "note": "",
        "viral": [{"id": "", "t": "", "src": "", "vues": "", "date": "", "tags": [], "meca": "", "moi": "", "url": ""}],
        "formats": [{"t": "", "src": "", "d": ""}],
        "focus": [{"t": "", "q": "", "d": ""}],
    }


def check(path: Path) -> list[str]:
    errs = []
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return [f"JSON illisible : {e}"]
    for k in ("start", "label", "releve", "viral", "formats", "focus"):
        if k not in doc:
            errs.append(f"champ manquant : {k}")
    try:
        start = parse(doc.get("start"))
        if start.weekday() != 0:
            errs.append("start n'est pas un lundi")
        if path.stem != week_id(start):
            errs.append(f"nom de fichier {path.stem} ≠ semaine ISO de start ({week_id(start)})")
    except Exception:  # noqa: BLE001
        errs.append("start doit être AAAA-MM-JJ")
    for i, v in enumerate(doc.get("viral", [])):
        missing = VIRAL_KEYS - set(v)
        if missing:
            errs.append(f"viral[{i}] : champs manquants {sorted(missing)}")
        if v.get("url") and not str(v["url"]).startswith("https://"):
            errs.append(f"viral[{i}] : url non https")
        if not v.get("vues"):
            errs.append(f"viral[{i}] : vues vides (jamais d'estimation, mais toujours un chiffre relevé)")
    ids = [v.get("id") for v in doc.get("viral", [])]
    if len(ids) != len(set(ids)):
        errs.append("viral : identifiants en double")
    for i, f in enumerate(doc.get("formats", [])):
        if FORMAT_KEYS - set(f):
            errs.append(f"formats[{i}] : champs manquants")
    for i, f in enumerate(doc.get("focus", [])):
        if FOCUS_KEYS - set(f):
            errs.append(f"focus[{i}] : champs manquants")
    if len(doc.get("viral", [])) > 12:
        errs.append("plus de 12 viraux : garder les plus instructifs")
    return errs


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] not in {"id", "new", "check"}:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == "id":
        print(week_id(parse(argv[2] if len(argv) > 2 else None)))
        return 0
    if cmd == "new":
        d = parse(argv[2] if len(argv) > 2 else None)
        path = SEMAINES / f"{week_id(d)}.json"
        if path.exists():
            print(f"{path.relative_to(ROOT)} existe déjà, rien écrasé")
            return 1
        path.write_text(json.dumps(skeleton(d), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{path.relative_to(ROOT)} créé")
        return 0
    path = Path(argv[2])
    errs = check(path)
    if errs:
        print("\n".join(f"- {e}" for e in errs))
        return 1
    print(f"{path.name} : structure correcte")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
