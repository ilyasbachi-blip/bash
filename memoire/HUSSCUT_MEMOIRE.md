# Mémoire éditoriale — Husscut (boucherie-charcuterie halal)

> À relire au début de CHAQUE session, avant tout montage.
> Statut : **ANALYSE DU COMPTE @husscut PAS ENCORE FAITE** (créée le 2026-11-13).
> L'instagram n'a pas pu être consulté depuis la session cloud (réseau bloqué, pas de navigateur).
> Tant que les sections « Observé » sont vides, AUCUN montage ne doit prétendre reproduire le style Husscut.

Légende des niveaux de preuve (à respecter dans chaque section) :
- **[OBS]** observé directement sur une vidéo du compte : citer la vidéo (date ou lien) et le timecode.
- **[PERF]** semble lié aux bonnes performances : citer les vues / interactions qui le justifient.
- **[HYP]** hypothèse à vérifier.

---

## 0. Corpus analysé

| # | Date de publication | Lien / ID | Format | Durée | Vues | J'aime | Commentaires | Pourquoi retenue |
|---|---|---|---|---|---|---|---|---|
| — | à remplir | | | | | | | |

Priorités d'analyse : vidéos récentes, vidéos les plus vues, vidéos avec le plus d'interactions, formats différents, vidéos les plus représentatives de l'identité.

## 1. Identité visuelle
- [OBS] à remplir
- [PERF] à remplir
- [HYP] à remplir

## 2. Hooks (3 premières secondes)
| Vidéo | Type de hook (plan spectaculaire / tranche / question / texte / résultat final…) | Texte affiché | Son | Vues |
|---|---|---|---|---|

## 3. Rythme et montage
- Durée moyenne des plans : [OBS] à mesurer (détection de plans ffmpeg sur les vidéos de référence)
- Durée totale moyenne : 
- Zooms (type, vitesse, sur quoi) : 
- Ralentis (quand, quel facteur) : 
- Accélérations : 
- Transitions : 
- Respirations entre produits : 

## 4. Prise de vue
- Façon de filmer la viande / la charcuterie : 
- Cadrages récurrents (plongée sur billot, plan serré mains, plan large comptoir…) : 
- Mise en valeur des visages, mains, couteaux, produits : 

## 5. Colorimétrie (référence d'étalonnage)
- Contraste : 
- Saturation : 
- Balance des blancs / température : 
- Rendu des rouges : 
- Rendu des blancs / peau : 
- Mesures objectives (à extraire des vidéos de référence : luminance moyenne, saturation moyenne, histogramme) : 

## 6. Typographie — référence unique
| Élément | Valeur | Niveau de preuve |
|---|---|---|
| Famille de police | à identifier | |
| Police de remplacement locale si non disponible | à choisir par comparaison visuelle, pas au hasard | |
| Graisse | | |
| Casse | | |
| Interlettrage | | |
| Interligne | | |
| Taille (% hauteur d'écran) | | |
| Couleur texte / couleur mot mis en avant | | |
| Contour (couleur, épaisseur) | | |
| Ombre | | |
| Position (zone verticale, % depuis le haut) | | |
| Animation d'entrée / de sortie | | |
| Nb de mots par écran | | |
| Variantes par format | | |

Le fichier de style de sous-titres (`memoire/style_soustitres.ass`) sera créé à partir de ce tableau, puis utilisé tel quel dans toutes les vidéos.

## 7. Sous-titrage
- Style des sous-titres : 
- Mots mis en avant (quels mots, comment) : 
- Découpage des phrases : 

## 8. Sound design et musique
- Musiques utilisées (style, tendances, volume relatif à la voix) : 
- Sons naturels mis en avant : 
- Effets sonores ajoutés : 

## 9. Formats récurrents
| Format | Exemples | Durée typique | Performance |
|---|---|---|---|

## 10. Ce qui semble le mieux fonctionner
- [PERF] à remplir après analyse des chiffres

## 11. Erreurs à éviter
- (issues de l'analyse du compte) à remplir
- Toujours valables (règles du client) : voir section 12.

---

## 12. Règles imposées par le client (source : brief du 2026-11-13 — ce ne sont PAS des observations)

Montage
- Ne jamais couper une phrase au milieu. Ne jamais retirer une étape ou un geste important.
- Garder une action intéressante assez longtemps pour être comprise ; en cas de doute, garder plus de matière.
- Retirer : réglages caméra, hésitations inutiles, rangements, essuyages, temps morts.
- Plans de coupe qui illustrent précisément ce qui est dit.
- Un seul projet par vidéo, jamais de « final », « final 2 », « dernière version ».
- Ne pas présumer d'une voix off : utiliser la parole existante quand elle est exploitable.
- Respirations visuelles entre deux produits / deux idées.
- Rythme dynamique mais gestes du boucher lisibles.
- Ralentis uniquement s'ils valorisent un geste, une texture, une découpe. Zooms uniquement vers un détail précis.
- Aucun texte sur le produit, les mains ou l'action importante.
- Jamais de prix, horaire, composition, promotion ou info commerciale sans source fiable.

Début de vidéo
- Commencer par : plan le plus spectaculaire / tranche révélée / découpe nette / texture gourmande / phrase intrigante / question fréquente / promesse claire / résultat final avant la préparation.
- Compréhensible dès le premier plan, sans le son. Pas d'intro lente ni de salutations longues.

Sous-titres
- Synchronisés, corrigés à la main, groupes de mots naturels, lisibles sur téléphone, dans les zones sûres Instagram/TikTok, cohérents d'une vidéo à l'autre.
- Vérifier l'orthographe des viandes, morceaux, charcuteries, spécialités (lexique en section 13).

Son et couleur
- Nettoyer la parole si nécessaire ; valoriser les sons naturels (découpe, couteau, trancheuse, emballage, grésillement, manipulation, vitrine, papier) sans effet sur chaque coupe.
- −14 LUFS intégré, true peak ≤ −1 dBTP, aucune saturation.
- Rouges naturels, blancs propres, peau crédible, pas de saturation excessive. Harmoniser Sony FX30 et iPhone.

Exports (sauf raison contraire observée sur le compte)
- 1080×1920, 9:16, H.264, 25 i/s, AAC 48 kHz, −14 LUFS → `outils/export_reel.sh`.
- Livrable par vidéo : MP4 prêt à publier + titre interne + hook + proposition de légende + infos à vérifier + liste des rushs.

Rushs
- Ne JAMAIS modifier, déplacer, renommer ou supprimer les rushs originaux. Tout ce qui est produit va dans `projets/` et `exports/`.

Zones sûres 1080×1920 (repère de travail, à confirmer)
- Haut : éviter les ~220 px supérieurs (nom du compte, bouton).
- Bas : éviter les ~420 px inférieurs (légende, musique, boutons).
- Droite : éviter les ~140 px de droite (boutons j'aime/commentaire/partage).

## 13. Lexique métier (orthographe de référence pour les sous-titres)
À compléter avec les termes réellement employés dans les vidéos et rushs (noms de produits Husscut, morceaux, spécialités). Aucun nom de produit Husscut ne doit être inventé.
