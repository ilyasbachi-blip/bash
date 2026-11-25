#!/usr/bin/env python3
"""Assemble la page Radar recettes.

Lit page/template.html, y injecte les catalogues (data/catalogues/*.json) et
les semaines (data/semaines/*.json, de la plus récente à la plus ancienne),
puis écrit dist/radar-recettes.html.

La page publiée sur claude.ai lit aussi la collection « radar » de sa base :
les semaines embarquées ici servent de secours (page lisible hors base) et de
sauvegarde versionnée.

Usage :
    python3 scripts/build_page.py            # toutes les semaines
    python3 scripts/build_page.py --weeks 8  # les 8 dernières seulement
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "page" / "template.html"
CATALOGUES = ROOT / "data" / "catalogues"
SEMAINES = ROOT / "data" / "semaines"
DIST = ROOT / "dist" / "radar-recettes.html"


def js_json(value) -> str:
    """JSON sûr à l'intérieur d'une balise <script> (le < devient \\u003c)."""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def load_weeks(limit: int | None):
    weeks = []
    for path in sorted(SEMAINES.glob("*.json"), reverse=True):
        doc = json.loads(path.read_text(encoding="utf-8"))
        doc.setdefault("id", path.stem)
        weeks.append(doc)
    weeks.sort(key=lambda w: w.get("start", ""), reverse=True)
    return weeks[:limit] if limit else weeks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weeks", type=int, default=None, help="nombre de semaines à embarquer")
    args = ap.parse_args()

    html = TEMPLATE.read_text(encoding="utf-8")
    for name in ("saison", "dates", "classiques", "astuces"):
        data = json.loads((CATALOGUES / f"{name}.json").read_text(encoding="utf-8"))
        placeholder = f"__{name.upper()}__"
        if placeholder not in html:
            print(f"placeholder manquant dans le template : {placeholder}", file=sys.stderr)
            return 1
        html = html.replace(placeholder, js_json(data))
    weeks = load_weeks(args.weeks)
    html = html.replace("__SEMAINES__", js_json(weeks))
    DIST.parent.mkdir(parents=True, exist_ok=True)
    DIST.write_text(html, encoding="utf-8")
    print(f"{DIST.relative_to(ROOT)} écrit : {len(html):,} caractères, {len(weeks)} semaine(s) embarquée(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
