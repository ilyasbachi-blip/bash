---
name: radar-hebdo
description: Fait le relevé hebdomadaire du Radar recettes de CookWithBash (viraux sourcés, saison, classiques, astuces), écrit le fichier de la semaine dans radar-recettes/data/semaines et reconstruit la page. À utiliser quand Ilyes demande « fais le radar », « le radar de la semaine », ou le lundi.
---

# Radar hebdo

Objectif : produire le document de la semaine (`radar-recettes/data/semaines/AAAA-Wnn.json`) et reconstruire `radar-recettes/dist/radar-recettes.html`. Lire `radar-recettes/README.md` une fois pour la structure.

## Étapes

1. **Identifiant et squelette** : `python3 radar-recettes/scripts/semaine.py new` (crée le fichier de la semaine ISO en cours ; ne jamais écraser une semaine existante, la compléter).
2. **Relire la semaine précédente** (fichier précédent dans `data/semaines/`) pour ne pas reproposer les mêmes vidéos ni les mêmes « focus ».
3. **Viraux (8 à 10)** : chercher les vidéos food qui ont percé ces 14 derniers jours, France d'abord, puis Europe et monde. Sources par ordre : la liste virale du lundi (https://claude.ai/artifact/DQXpBfbUh6DLe7yNoMmVaF, à lire avec l'outil Artifact si la session l'a) ; vidIQ (`instagram_tiktok_outlier_search`, `outliers`) s'il y a des crédits ; sinon recherche web datée, et le dire dans `note`. Pour chaque vidéo : compte, plateforme, multiplicateur si connu, vues affichées, date de publication, lien https direct, pourquoi ça marche (mécanique d'ouverture, promesse), et « ta version » concrète pour CookWithBash (angle algérien ou halal, hook en une phrase à la voix d'Ilyes). Pas de vidéo sans chiffre relevé.
4. **Formats (3 à 5)** : mécaniques indépendantes du plat qui montent (ouverture sur le plat fini, série numérotée, roundup, son brut, « arrête d'acheter »…), avec la source.
5. **Focus (4 à 6)** = ce qu'il doit tourner cette semaine, en croisant : un ou deux viraux adaptables ; la saison (`data/catalogues/saison.json`, `dates.json` : Avent, Noël, galette 3-6 janv., Yennayer 12 janv., Chandeleur 2 févr., Ramadan 8 févr.-9 mars 2027, Aïd el-Fitr 9-10 mars, Pâques 28 mars) ; un classique « libre » de `classiques.json` ; une astuce de la saison dans `astuces.json`. Respecter la cadence : un classique mijoté de saison + une nouveauté. Jamais un classique « bloqué » ni une recette publiée depuis moins de 24 mois.
6. **Vérifier** : `python3 radar-recettes/scripts/semaine.py check radar-recettes/data/semaines/<id>.json` doit passer.
7. **Reconstruire** : `python3 radar-recettes/scripts/build_page.py`.
8. **Publier** : si la session a l'outil `ArtifactData`, écrire le même document dans la base de la page publiée (url https://claude.ai/artifact/ByEUqfxkt9FGEdzhYZo7ku, collection `radar`, doc_id = identifiant de la semaine ; `if_version` si le document existe). Sinon, si la session a l'outil `Artifact`, republier `dist/radar-recettes.html` sur la même url (sans repasser `capabilities` ni `icon`). Sinon, laisser le fichier dans le dépôt et le dire.
9. **Calendrier** : exporter la collection `statuts` de la page (ArtifactData, action `list`, `out_dir`), lancer `python3 radar-recettes/scripts/calendrier.py <dossier>` puis commit + push de `radar-recettes/dist/a-tourner.ics` sur `main` : c'est le fichier que lit l'abonnement Apple Calendrier d'Ilyes. Les lignes « À faire » sans jour ne s'y trouvent pas : les lui rappeler dans le bilan.
10. **Bilan en 8 lignes** : la vidéo la plus instructive et sa version CookWithBash, les 2 ou 3 focus avec leur hook, l'astuce de la semaine, ce qui n'a pas pu être relevé.

## Garde-fous

- Catalogues (`saison.json`, `classiques.json`, `astuces.json`, `dates.json`) : les mettre à jour quand Ilyes publie une recette (champ `fait` d'un classique, passage de « libre » à « bloqué ») ou quand une date approche ; une modification de catalogue demande un `build_page.py` et une republication de la page.
- Ne jamais inventer de vues, de date ou de compte. Une vidéo dont on n'a lu que la légende est signalée comme telle.
- Les statuts cochés par Ilyes sur la page (collection `statuts` de la base) priment : ne pas reproposer un « pas pour moi » ; un « À faire » priorité 1 sans jour fixé est le premier focus de la semaine.
