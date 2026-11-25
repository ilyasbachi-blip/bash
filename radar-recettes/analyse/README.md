# Analyse des comptes

Scripts utilisés pour le diagnostic du 21 novembre 2026 (Instagram, TikTok, YouTube). Ils attendent des relevés bruts dans `analyse/data/` (voir le README du dossier parent pour les noms de fichiers) et écrivent dans `analyse/out/`. Ces deux dossiers ne sont pas versionnés : ils contiennent des statistiques privées des comptes.

- `build_db.py` : construit `out/base_publications.csv` / `.json` (une ligne par publication et par plateforme) et `out/summary.json` (médianes P1 / P0, par pilier, re-tournages, par mois, par heure).
- `make_csv.py` : prépare `out/base_publications_sheet.csv` pour l'import dans le Google Sheet de suivi.

Pour refaire un relevé, voir `claude/diagnostic-provisoire-90-jours-novembre-2026.md` dans le projet Cookwithbash (méthode, limites des métriques, dictionnaire).
