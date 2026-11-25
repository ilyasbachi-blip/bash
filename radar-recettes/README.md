# Radar recettes

Veille hebdomadaire de CookWithBash : ce qui a percé sur les réseaux, ce que la saison appelle, les classiques toujours recherchés, les astuces du moment. Une page HTML, quatre rubriques, une semaine = un fichier.

## Arborescence

```
radar-recettes/
  page/template.html          la page, avec des emplacements __SAISON__, __DATES__, __CLASSIQUES__, __ASTUCES__, __SEMAINES__
  data/catalogues/            saison.json, dates.json, classiques.json, astuces.json (référence, modifiée à la main)
  data/semaines/AAAA-Wnn.json une semaine = un fichier (semaine ISO, lundi = start)
  scripts/semaine.py          id | new | check  (identifiant ISO, squelette, vérification de structure)
  scripts/build_page.py       assemble dist/radar-recettes.html à partir du template, des catalogues et des semaines
  dist/radar-recettes.html    la page construite (à republier sur claude.ai)
  analyse/                    scripts d'analyse des comptes (Instagram, TikTok, YouTube) ; leurs données restent hors git
```

## Comment la page lit ses données

La page publiée (https://claude.ai/artifact/ByEUqfxkt9FGEdzhYZo7ku) déclare les capacités `db` et `user` :

- collection `radar` : un document par semaine, mêmes champs que les fichiers de `data/semaines/`. Quand la base répond, elle remplace les semaines embarquées dans la page.
- collection `statuts` : les cases « À faire / Fait / Pas pour moi » cochées par Ilyes (doc par ligne : `id`, `st`, `ts`).

Les semaines embarquées par `build_page.py` sont donc un secours (page lisible même sans base) et une sauvegarde versionnée. Pour qu'une nouvelle semaine apparaisse sur la page publiée sans republier, écrire le document dans la collection `radar` (outil `ArtifactData` côté claude.ai, ou la tâche planifiée « Radar recettes du lundi », 9 h 52 Paris).

## Structure d'une semaine

```json
{
  "start": "2026-11-23", "label": "Semaine du 23 novembre 2026", "releve": "25 novembre 2026",
  "note": "sources et limites du relevé",
  "viral":   [{"id": "cesar-bocal", "t": "…", "src": "@compte · plateforme (multiplicateur)", "vues": "11,4 M", "date": "20 oct.", "tags": ["sauce"], "meca": "pourquoi ça marche", "moi": "ta version", "url": "https://…"}],
  "formats": [{"t": "…", "src": "…", "d": "…"}],
  "focus":   [{"t": "…", "q": "quand", "d": "pourquoi"}]
}
```

Identifiants de ligne utilisés par les statuts : `v:<id>` pour un viral, `f:<semaine>:<index>` pour un focus, `s:<mois>:<index>` saison, `c:<titre>` classique, `a:<hiver|ete>:<index>` astuce.

## Cycle hebdomadaire

1. `python3 scripts/semaine.py new` puis remplir le fichier (ou lancer la skill `radar-hebdo`).
2. `python3 scripts/semaine.py check data/semaines/<id>.json`
3. `python3 scripts/build_page.py`
4. Écrire la semaine dans la base de la page (ArtifactData) ou republier `dist/radar-recettes.html` sur la même url.

## Catalogues

- `saison.json` : par mois (`"11"`, `"12"`, `"1"`, `"2"`…), titre, plats `[nom, pourquoi]`, produits. Ajouter les mois manquants au fil de l'année.
- `dates.json` : `[date, quoi, la vidéo]`.
- `classiques.json` : `t`, `fait` (dernière publication connue), `ok` (libre = jamais fait ou plus de 24 mois), `q` (quand), `a` (angle).
- `astuces.json` : `hiver` et `ete`, `[titre, détail]`. La page bascule sur été de mai à septembre.

## Analyse des comptes (`analyse/`)

`build_db.py` construit la base « une ligne par publication et par plateforme » à partir de relevés bruts (Instagram Insights, TikTok Studio, YouTube Studio) placés dans `analyse/data/` : `ig_media_180d.tsv`, `ig_titles.tsv`, `ig_insights_raw.tsv`, `ig_insights_compact.txt`, `tiktok_all.psv`, `tiktok_detail.psv`, `yt_shorts.tsv`, `yt_videos.tsv`. `make_csv.py` prépare l'import Google Sheets. Ces données sont privées : `analyse/data/` et `analyse/out/` sont ignorés par git. La base vivante est le Google Sheet « CookWithBash — Base publications & suivi éditorial ».
