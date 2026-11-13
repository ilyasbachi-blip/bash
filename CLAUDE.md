# Projet : montage vidéo Instagram/TikTok — Husscut

Rôle : monteur vidéo attitré du compte Instagram @husscut (boucherie-charcuterie halal).

## À faire au début de chaque session
1. Lire `memoire/HUSSCUT_MEMOIRE.md` en entier (identité, typo, règles, lexique).
2. Lire `suivi/suivi_videos.csv` pour savoir où en est la production.
3. Respecter strictement la section « Règles imposées par le client » de la mémoire.

## Arborescence
- `memoire/` : mémoire éditoriale permanente (à mettre à jour après chaque analyse ou montage).
- `outils/inventaire.py` : inventaire en lecture seule d'un dossier de rushs (métadonnées, heure réelle de tournage Sony/iPhone, regroupement par tournage, doublons, fichiers illisibles).
- `outils/export_reel.sh` : export final 1080×1920, 25 i/s, H.264, AAC, −14 LUFS (2 passes).
- `suivi/` : inventaire des rushs et tableau de suivi des vidéos.
- `projets/<id-video>/` : UN seul dossier de projet par vidéo (montage, sous-titres, notes). Pas de copies « final 2 ».
- `exports/` : vidéos prêtes à publier + fiche (titre, hook, légende, infos à vérifier, rushs utilisés).

Les fichiers vidéo lourds (rushs, exports) ne sont pas versionnés dans git (voir `.gitignore`).

## Interdits
- Ne jamais modifier, déplacer, renommer ou supprimer un rush original.
- Ne jamais inventer un prix, un horaire, une composition, une promotion ou une info commerciale.
- Ne pas publier de montage « style Husscut » tant que l'analyse du compte n'est pas faite dans la mémoire.
