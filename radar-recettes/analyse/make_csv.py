import os
import json, csv, hashlib
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out") + os.sep
rows = json.load(open(OUT + 'base_publications.json'))

PIL = {'ALG': 'Cuisine algérienne', 'MAG': 'Maghreb (Tunisie, Maroc)', 'MONDE': 'Recettes du monde', 'FR': 'Cuisine française / de saison',
       'VOYAGE': 'Voyage / mini-vlog', 'PERSO': 'Personnel / livre', 'COLLAB': 'Commercial', '?': 'à classer'}

cols = [('plateforme', 'Plateforme'), ('type', 'Type'), ('date', 'Date'), ('heure', 'Heure (Paris)'), ('jour_semaine', 'Jour'), ('age_jours', 'Âge au relevé (j)'),
        ('periode', 'Période'), ('titre', 'Titre court'), ('pilier', 'Pilier'), ('format', 'Format'), ('repost', 'Re-tournage'), ('statut', 'Statut'),
        ('visibilite', 'Visibilité'), ('duree', 'Durée'), ('vues', 'Vues'), ('pct_vues_non_followers', '% vues non-followers'), ('reach', 'Spectateurs (reach)'),
        ('interactions', 'Interactions'), ('likes', 'Likes'), ('commentaires', 'Commentaires'), ('enregistrements', 'Enregistrements'), ('partages', 'Partages'),
        ('comptes_engages', 'Comptes engagés'), ('nouveaux_followers', 'Nouveaux followers'), ('likes_1000v', 'Likes /1000 vues'), ('comm_1000v', 'Comm. /1000 vues'),
        ('saves_1000v', 'Enreg. /1000 vues'), ('partages_1000v', 'Partages /1000 vues'), ('follows_1000v', 'Followers /1000 vues'),
        ('duree_moyenne_s', 'Durée moy. regardée (s)'), ('pct_duree_regardee', '% de la vidéo regardée'), ('completion_pct', '% vu en entier'),
        ('pct_pour_toi', '% trafic Pour toi'), ('pct_recherche', '% trafic Recherche'), ('revenus_est_eur', 'Revenus est. (€)'), ('lien', 'Lien'), ('titre_public', 'Titre public')]

def fmt(v):
    if v is None: return ''
    if isinstance(v, float):
        return str(int(v)) if v.is_integer() else str(round(v, 2))
    return str(v)

out = []
for r in rows:
    if r['plateforme'] == 'TikTok' and r['date'] < '2024-11-01':
        continue  # 24 mois d'historique TikTok dans la base
    r = dict(r)
    if r['plateforme'] == 'Instagram':
        r['partages'] = r.get('partages_derives')
        r['heure'] = ''; r['jour_semaine'] = ''
    if r['plateforme'] == 'YouTube':
        t = r['titre'].lower(); note = (r.get('note') or '')
        r['repost'] = ''
        r['statut'] = 'sponsorisé/collab' if 'collab' in note else 'organique'
        if any(k in t for k in ['polyn', 'fakarava', 'moorea', 'kayma', 'vanille', 'piment', 'couscous de la mer', 'djerba', 'can ', 'algérie avec mon père', "traversé l'algérie", 'oran', 'raï', 'street food', 'vlog', 'psg']):
            r['pilier'] = 'VOYAGE'; r['format'] = 'voyage' if r['type'] == 'Short' else 'vlog / documentaire'
        elif any(k in t for k in ['livre', "saveurs d'alg"]):
            r['pilier'] = 'PERSO'; r['format'] = 'annonce'
        elif 'collab' in note or 'portugais' in t:
            r['pilier'] = 'COLLAB'; r['format'] = 'recette'
        elif any(k in t for k in ['loubia', 'tajine', 'citron confit', 'chakchouka', 'frite omelette', 'couscous', 'makrout', 'chwa', 'cherbet', 'hmiss', 'rechta', 'berkoukes', 'bourek']):
            r['pilier'] = 'ALG'; r['format'] = 'recette'
        elif any(k in t for k in ['omek houria', 'rfissa', 'amlou']):
            r['pilier'] = 'MAG'; r['format'] = 'recette'
        elif any(k in t for k in ['poulet', 'tatin', 'butternut', 'tapenade', 'omelette', 'burger']):
            r['pilier'] = 'FR'; r['format'] = 'recette'
        elif r['type'] == 'Short' and r['titre'].startswith('('):
            r['pilier'] = '?'; r['format'] = 'recette'
        else:
            r['pilier'] = 'MONDE'; r['format'] = 'recette'
        if r['type'] == 'Vidéo longue' and r['pilier'] != 'VOYAGE' and r['format'] == 'recette': r['format'] = 'recette longue'
        if 'test' in t or 'doublon' in t: r['format'] = 'test / doublon'
    r['pilier'] = PIL.get(r.get('pilier'), r.get('pilier', ''))
    tp = (r.get('titre_public') or '')
    r['titre_public'] = tp[:90]
    out.append([fmt(r.get(k)) for k, _ in cols])

out.sort(key=lambda x: (x[0], x[2]), reverse=True)
path = OUT + 'base_publications_sheet.csv'
with open(path, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    w.writerow([h for _, h in cols])
    w.writerows(out)
import os
print(len(out), 'rows;', os.path.getsize(path), 'bytes; sha256', hashlib.sha256(open(path, 'rb').read()).hexdigest())
