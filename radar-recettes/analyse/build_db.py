import re, csv, json, statistics as st
from datetime import date, datetime, timedelta
from collections import defaultdict

import os
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data") + os.sep  # relevés bruts (non versionnés)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out") + os.sep
import os; os.makedirs(OUT, exist_ok=True)

TODAY = date(2026, 11, 21)
P1_START = TODAY - timedelta(days=90)      # 2026-08-23
P0_START = P1_START - timedelta(days=90)   # 2026-05-25

def num(s):
    """'1 234' / '12,3 k' / '2.9M' / '1,267' -> float"""
    if s is None: return None
    s = str(s).strip().replace(' ', '').replace('\xa0', '')
    if s in ('', '--', '—', '-'): return None
    m = re.match(r'^([\d\s.,]+)\s*([kKM])?$', s)
    if not m: return None
    body, suf = m.group(1).replace(' ', ''), m.group(2)
    if suf:  # 12,3 k or 2.9M or 1.2K
        body = body.replace(',', '.')
        v = float(body)
        return v * (1000 if suf.lower() == 'k' else 1_000_000)
    # plain integer, comma = thousands sep (TikTok) or FR spaces
    body = body.replace(',', '')
    try: return float(body)
    except: return None

def period(d):
    if d >= P1_START: return 'P1 (90 j)'
    if d >= P0_START: return 'P0 (90 j précédents)'
    return 'avant'

# ---------- classification (manuelle, à partir des titres) ----------
# pilier: ALG=cuisine algérienne, MAG=Maghreb/Tunisie/Maroc, MONDE=autres cuisines du monde, FR=cuisine française/moderne,
#         VOYAGE=voyage/mini-vlog, PERSO=livre/annonce/personnel, COLLAB=contenu commercial
IG = {
 '4033234116210446850': ('Poulet rôti juteux comme en rôtisserie', 'FR', 'recette', 'non', ''),
 '4030101249288418111': ('Concours 6 repas (collab)', 'COLLAB', 'concours', 'non', 'sponsorisé'),
 '4030355127330182430': ('Loubia', 'ALG', 'recette', 'oui (nov. 2025, févr. 2025)', ''),
 '4028224380441324180': ('Citrons confits maison', 'ALG', 'recette', 'non', ''),
 '4026503757579592132': ('Collab Al Bayyinah (annonce 21 nov.)', 'COLLAB', 'annonce', 'non', 'sponsorisé'),
 '4025191743777515721': ('Tajine bœuf olives citron confit', 'ALG', 'recette', 'oui (déc. 2024)', ''),
 '4023594603984944661': ('Piment le plus cher du monde (Polynésie)', 'VOYAGE', 'voyage', 'non', ''),
 '4023720917253400026': ('Vanille de Polynésie', 'VOYAGE', 'voyage', 'non', ''),
 '4020149959079038213': ('Paysages Polynésie', 'VOYAGE', 'voyage', 'non', ''),
 '4017280258946778784': ('Journée en Polynésie (ce qu\'on mange)', 'VOYAGE', 'voyage', 'non', ''),
 '4015720651640201761': ('Butternut 3 recettes', 'FR', 'recette', 'non', ''),
 '4012834877609470400': ('Poisson cru au lait de coco (Moorea)', 'VOYAGE', 'recette-voyage', 'non', ''),
 '4008548404240395871': ('Poulet portugais churrasqueira', 'COLLAB', 'recette', 'non', 'sponsorisé'),
 '4005660023195485038': ('Carrousel California love', 'PERSO', 'carrousel', 'non', ''),
 '4004921710275192387': ('Dibi d\'agneau', 'MONDE', 'recette', 'oui (avr. 2025)', ''),
 '4003485226275805558': ('Chakchouka', 'ALG', 'recette', 'oui (juil. 2025, juil. 2024)', ''),
 '4000483877737122698': ('Mini tartes tatin salées', 'FR', 'recette', 'oui (sept. 2025)', ''),
 '4000397208575139025': ('Carrousel collab Solar (livre)', 'PERSO', 'carrousel', 'non', 'collab éditeur'),
 '3999622105543020713': ('Livre disponible (2)', 'PERSO', 'annonce', 'non', ''),
 '3998313683862420058': ('Livre disponible (1)', 'PERSO', 'annonce', 'non', ''),
 '3988030498026133386': ('Annonce Saveurs d\'Algérie (sortie 1er oct.)', 'PERSO', 'annonce', 'non', ''),
 '3982361315624412416': ('Carrousel « Il manquait un ingrédient »', 'PERSO', 'carrousel', 'non', ''),
 '3976639861682906851': ('Frite omelette', 'ALG', 'recette', 'non (févr. 2023)', ''),
 '3969371879611948095': ('Panuozzo', 'MONDE', 'recette', 'non', ''),
 '3967280790552910846': ('Omek Houria', 'MAG', 'recette', 'oui (juil. 2025)', ''),
 '3965129782079796466': ('Barbecue texan à volonté (US)', 'VOYAGE', 'voyage-resto', 'non', ''),
 '3962725243313838696': ('Sorbet coco antillais', 'MONDE', 'recette', 'non', ''),
 '3960066854188429364': ('Chwa (brochettes) recette', 'ALG', 'recette', 'non', ''),
 '3959337593680949911': ('Chwa en Algérie (explication)', 'VOYAGE', 'voyage', 'non', ''),
 '3954913135687875155': ('Dip feta pistache', 'MONDE', 'recette', 'oui (sept. 2025)', ''),
 '3951973994046072786': ('Sorbet melon', 'FR', 'recette', 'non', ''),
 '3949131407284693293': ('Collab Chef Pays patate douce', 'COLLAB', 'recette', 'non', 'collab'),
 '3946269606723863505': ('Amlou', 'MAG', 'recette', 'oui (janv. 2025)', ''),
 '3943833617044633358': ('Jollof rice', 'MONDE', 'recette', 'non', ''),
 '3941724189583730685': ('Gâteau renversé ananas antillais', 'MONDE', 'recette', 'non (janv. 2023)', ''),
 '3940460437618001812': ('Sauce toum', 'MONDE', 'recette', 'oui (sept. 2024)', ''),
 '3939775559758962137': ('Shish taouk', 'MONDE', 'recette', 'non (juil. 2024, 24 mois)', ''),
 '3933853863784889008': ('Pizza carrée', 'ALG', 'recette', 'non (févr. 2023)', ''),
 '3929567059669682266': ('Panuozzo maison (1)', 'MONDE', 'recette', 'non', ''),
 '3926692526810000435': ('Salade Shirazi', 'MONDE', 'recette', 'non (août 2023)', ''),
 '3922300199475869485': ('Cherbet', 'ALG', 'recette', 'oui (août 2025)', ''),
 '3921598046528417559': ('Mondial Pomozza (annonce)', 'PERSO', 'annonce', 'non', ''),
 '3917274142611606090': ('Documentaire Algérie en ligne (annonce)', 'PERSO', 'annonce', 'non', ''),
 '3915018873672372001': ('Tajine poulet olives citron', 'ALG', 'recette', 'oui (nov. 2025, nov. 2024)', ''),
 '3911425687906919705': ('Ribs de bœuf (US)', 'MONDE', 'recette', 'non', ''),
 '3909104133750233903': ('Poisson braisé & alloco (Désiré Doué)', 'MONDE', 'recette', 'non', ''),
 '3907853967470646427': ('Hmiss', 'ALG', 'recette', 'oui (août 2025, avr. 2023)', ''),
 '3905671844693461121': ('Makrout el louz', 'ALG', 'recette', 'non', ''),
 '3904888535520475905': ('Épaule d\'agneau confite (Aïd)', 'ALG', 'recette', 'oui (déc. 2025)', ''),
 '3904106521178592085': ('Limonade brésilienne', 'MONDE', 'recette', 'oui (juin 2025)', ''),
 '3902728198948027319': ('Shawarma bœuf', 'MONDE', 'recette', 'oui (juil. 2025)', ''),
}

# ---------- Instagram ----------
media = {}
with open(DB + 'ig_media_180d.tsv', encoding='utf-8') as f:
    for r in csv.DictReader(f, delimiter='\t'):
        media[r['pk']] = dict(date=r['date'], code=r['code'], kind=r['kind'], public_views=num(r['public_views']))
titles = {}
with open(DB + 'ig_titles.tsv', encoding='utf-8') as f:
    for r in csv.DictReader(f, delimiter='\t'):
        titles[r['code']] = r
ins = {}
with open(DB + 'ig_insights_raw.tsv', encoding='utf-8') as f:
    for r in csv.DictReader(f, delimiter='\t'):
        ins[r['pk']] = {k: (float(v) if v not in ('', None) else None) for k, v in r.items() if k != 'pk'}

def grab(txt, label, after=None):
    """value following a label in the compact innerText"""
    parts = txt.split('|')
    start = 0
    if after:
        for i, p in enumerate(parts):
            if p.strip() == after: start = i; break
    for i in range(start, len(parts)):
        if parts[i].strip() == label and i + 1 < len(parts):
            return parts[i + 1].strip()
    return None

with open(DB + 'ig_insights_compact.txt', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n')
        if '||' not in line: continue
        pk, txt = line.split('||', 1)
        pk = pk.strip()
        d = {}
        # views = second 'Vues' value
        parts = [p.strip() for p in txt.split('|')]
        idx = [i for i, p in enumerate(parts) if p == 'Vues' and i + 1 < len(parts) and num(parts[i + 1]) is not None]
        d['views'] = num(parts[idx[0] + 1]) if idx else None
        # followers % right after views
        try:
            j = idx[0] + 2
            d['pct_followers_views'] = num(parts[j + 1].replace('%', '')) if parts[j] == 'Followers' else None
        except: d['pct_followers_views'] = None
        d['reach'] = num(grab(txt, 'Spectateur(ice)s'))
        iidx = [i for i, p in enumerate(parts) if p == 'Interactions' and i + 1 < len(parts) and num(parts[i + 1]) is not None]
        d['interactions'] = num(parts[iidx[0] + 1]) if iidx else None
        try:
            j = iidx[0] + 2
            d['pct_followers_inter'] = num(parts[j + 1].replace('%', '')) if parts[j] == 'Followers' else None
        except: d['pct_followers_inter'] = None
        d['likes'] = num(grab(txt, 'Mentions J’aime'))
        d['comments'] = num(grab(txt, 'Commentaires', after='Mentions J’aime'))
        d['saves'] = num(grab(txt, 'Enregistrements'))
        d['accounts_engaged'] = num(grab(txt, 'Comptes ayant interagi'))
        pa = grab(txt, 'Activité du profil')
        d['profile_activity'] = num(pa)
        fo = grab(txt, 'Followers en plus')
        d['follows'] = num(fo) if fo and fo not in ('Publicité', 'Facebook') else None
        d['fb_views'] = num(grab(txt, 'Vues', after='Facebook')) if '|Facebook|' in txt else None
        d['from_home'] = num(grab(txt, 'Depuis la page d’accueil'))
        d['from_profile'] = num(grab(txt, 'Depuis le profil'))
        d['profile_visits'] = num(grab(txt, 'Visites du profil'))
        ins.setdefault(pk, {}).update({k: v for k, v in d.items() if v is not None or k not in ins.get(pk, {})})

rows = []
for pk, m in media.items():
    t = titles.get(m['code'], {})
    i = ins.get(pk, {})
    label, pillar, fmt, repost, spons = IG.get(pk, (t.get('title', ''), '?', '?', '?', ''))
    d = datetime.strptime(m['date'], '%Y-%m-%d').date()
    views = i.get('views') or m['public_views']
    likes = i.get('likes') or num(t.get('likes'))
    comments = i.get('comments') if i.get('comments') is not None else num(t.get('comments'))
    saves = i.get('saves'); inter = i.get('interactions')
    shares = (inter - likes - comments - saves) if None not in (inter, likes, comments, saves) else None
    if shares is not None and shares < 0: shares = 0
    follows = i.get('follows')
    reach = i.get('reach')
    age = (TODAY - d).days
    row = dict(
        plateforme='Instagram', type=('Carrousel' if m['kind'] == 'carousel' else 'Reel'),
        lien=f"https://www.instagram.com/{'p' if m['kind']=='carousel' else 'reel'}/{m['code']}/",
        date=m['date'], age_jours=age, periode=period(d), titre=label, titre_public=t.get('title', ''),
        pilier=pillar, format=fmt, repost=repost, statut=('sponsorisé/collab' if spons else 'organique'),
        vues=views, pct_vues_non_followers=(100 - i['pct_followers_views']) if i.get('pct_followers_views') is not None else None,
        reach=reach if age < 125 else None,  # reach tronqué au-delà de ~4 mois sur le web
        reach_brut=reach,
        interactions=inter, likes=likes, commentaires=comments, enregistrements=saves, partages_derives=shares,
        comptes_engages=i.get('accounts_engaged'), nouveaux_followers=follows, fb_vues=i.get('fb_views'),
        visites_profil=i.get('profile_visits'),
    )
    if views:
        row['likes_1000v'] = round(likes / views * 1000, 1) if likes is not None else None
        row['comm_1000v'] = round(comments / views * 1000, 2) if comments is not None else None
        row['saves_1000v'] = round(saves / views * 1000, 1) if saves is not None else None
        row['partages_1000v'] = round(shares / views * 1000, 1) if shares is not None else None
        row['follows_1000v'] = round(follows / views * 1000, 2) if follows is not None else None
        row['engagement_vues_pct'] = round(inter / views * 100, 2) if inter is not None else None
        row['engagement_reach_pct'] = round(inter / reach * 100, 2) if (inter is not None and row['reach']) else None
        row['vues_non_followers'] = round(views * row['pct_vues_non_followers'] / 100) if row['pct_vues_non_followers'] is not None else None
    rows.append(row)

# ---------- TikTok ----------
FR_MONTHS = {'janv.':1,'févr.':2,'mars':3,'avr.':4,'mai':5,'juin':6,'juil.':7,'août':8,'sept.':9,'oct.':10,'nov.':11,'déc.':12}
def tt_date(s):
    s = s.strip()
    m = re.match(r'(\d{1,2}) (\S+)(?: (\d{4}))?, (\d{2}):(\d{2})', s)
    day, mon, yr, hh, mm = m.groups()
    yr = int(yr) if yr else 2026
    return datetime(yr, FR_MONTHS[mon], int(day), int(hh), int(mm))

detail = {}
with open(DB + 'tiktok_detail.psv', encoding='utf-8') as f:
    for r in csv.DictReader(f, delimiter='|'):
        detail[r['id']] = r

TT_LABEL = {  # overrides for titles / pillars on recent videos
 '7709547667432410400': ('Poulet rôti juteux comme en rôtisserie', 'FR', 'recette', 'non', ''),
 '7708075699755650336': ('Loubia', 'ALG', 'recette', 'oui (nov. 2025)', ''),
 '7707936660968803617': ('Restaurant KASUMI (collab commerciale)', 'COLLAB', 'restaurant', 'non', 'sponsorisé'),
 '7706982751802641697': ('Citrons confits maison', 'ALG', 'recette', 'non', ''),
 '7705432788769590560': ('Tajine bœuf olives citron confit', 'ALG', 'recette', 'oui (déc. 2024)', ''),
 '7704618744533765409': ('Vanille de Polynésie', 'VOYAGE', 'voyage', 'non', ''),
 '7704610648923049249': ('Piment le plus cher du monde', 'VOYAGE', 'voyage', 'non', ''),
 '7701380858107710752': ('Journée en Polynésie (ce qu\'on mange)', 'VOYAGE', 'voyage', 'non', ''),
 '7700583403472588065': ('Butternut 3 recettes', 'FR', 'recette', 'non', ''),
 '7699105059635809568': ('Poisson cru au lait de coco', 'VOYAGE', 'recette-voyage', 'non', ''),
 '7696908527268269344': ('Poulet portugais churrasqueira', 'COLLAB', 'recette', 'non', 'sponsorisé'),
 '7695051356272413985': ('Dibi d\'agneau', 'MONDE', 'recette', 'oui (avr. 2025)', ''),
 '7692781712245345569': ('Mini tartes tatin salées', 'FR', 'recette', 'oui (sept. 2025)', ''),
 '7692332449904200993': ('Livre disponible (2)', 'PERSO', 'annonce', 'non', ''),
 '7691669917938093344': ('Livre disponible (1)', 'PERSO', 'annonce', 'non', ''),
 '7690173847064038689': ('Kayma San Francisco (Algérie en Californie)', 'VOYAGE', 'voyage-resto', 'non', ''),
 '7686406618656804128': ('Annonce Saveurs d\'Algérie', 'PERSO', 'annonce', 'non', ''),
 '7683514106833358112': ('Al hamdulilah (photo/perso)', 'PERSO', 'perso', 'non', ''),
 '7680574404614540577': ('Frite omelette', 'ALG', 'recette', 'non (févr. 2023)', ''),
 '7676856770488192289': ('Panuozzo', 'MONDE', 'recette', 'non', ''),
 '7675780439461678369': ('Omek Houria', 'MAG', 'recette', 'oui (juil. 2025)', ''),
 '7674679326515727648': ('Barbecue texan à volonté (US)', 'VOYAGE', 'voyage-resto', 'non', ''),
 '7673448671068884256': ('Sorbet coco antillais (passé en privé)', 'MONDE', 'recette', 'non', ''),
 '7672089318332108065': ('Chwa (brochettes) recette', 'ALG', 'recette', 'non', ''),
 '7669448424542047521': ('Dip feta pistache', 'MONDE', 'recette', 'oui (sept. 2025)', ''),
 '7667943795060739360': ('Sorbet melon', 'FR', 'recette', 'non', ''),
 '7666021807652212001': ('Amlou', 'MAG', 'recette', 'oui (janv. 2025)', ''),
 '7663772314697207073': ('Jollof rice', 'MONDE', 'recette', 'non', ''),
 '7662050282083274017': ('Sauce toum', 'MONDE', 'recette', 'oui (sept. 2024)', ''),
 '7662697193056357665': ('Gâteau renversé ananas (privé)', 'MONDE', 'recette', 'non', ''),
}

tt_rows = []
with open(DB + 'tiktok_all.psv', encoding='utf-8') as f:
    for r in csv.DictReader(f, delimiter='|'):
        dt = tt_date(r['date'])
        d = dt.date()
        views, likes, comments = num(r['views']), num(r['likes']), num(r['comments'])
        label, pillar, fmt, repost, spons = TT_LABEL.get(r['id'], (r['title'][:45], '?', '?', '?', ''))
        det = detail.get(r['id'], {})
        row = dict(plateforme='TikTok', type='Vidéo', lien=f"https://www.tiktok.com/@cookwithbash/video/{r['id']}",
                   date=d.isoformat(), heure=dt.strftime('%H:%M'), jour_semaine=['lun','mar','mer','jeu','ven','sam','dim'][d.weekday()],
                   age_jours=(TODAY - d).days, periode=period(d), titre=label, titre_public=r['title'],
                   pilier=pillar, format=fmt, repost=repost, statut=('sponsorisé/collab' if spons else 'organique'),
                   visibilite=('public' if r['privacy'] == 'T' else 'privé (Moi uniquement)'), epingle=r['pinned'],
                   duree=r['dur'], vues=views, likes=likes, commentaires=comments)
        if det:
            row.update(partages=num(det['shares']), enregistrements=num(det['saves']),
                       duree_moyenne_s=num(det['avg_watch_s'].replace('s', '')), completion_pct=num(det['full_pct'].replace('%', '')),
                       nouveaux_followers=num(det['new_followers']), revenus_est_eur=num(det['rewards_eur'].replace('€', '')),
                       chute_principale=det['drop_at'], sources_trafic=det['traffic'], recherches=det['searches'])
            m = re.search(r'Pour toi ([\d.]+)%', det['traffic']); row['pct_pour_toi'] = float(m.group(1)) if m else None
            m = re.search(r'Recherche ([\d.]+)%', det['traffic']); row['pct_recherche'] = float(m.group(1)) if m else None
        if views:
            row['likes_1000v'] = round(likes / views * 1000, 1)
            row['comm_1000v'] = round(comments / views * 1000, 2)
            if det and row.get('partages') is not None:
                row['partages_1000v'] = round(row['partages'] / views * 1000, 1)
                row['saves_1000v'] = round(row['enregistrements'] / views * 1000, 1)
                row['follows_1000v'] = round(row['nouveaux_followers'] / views * 1000, 2) if row['nouveaux_followers'] is not None else None
            dur = r['dur']
            if dur and row.get('duree_moyenne_s'):
                mm, ss = dur.split(':'); secs = int(mm) * 60 + int(ss)
                row['duree_s'] = secs
                row['pct_duree_regardee'] = round(row['duree_moyenne_s'] / secs * 100, 1)
        tt_rows.append(row)

# ---------- YouTube ----------
yt_rows = []
with open(DB + 'yt_shorts.tsv', encoding='utf-8') as f:
    for r in csv.DictReader(f, delimiter='\t'):
        d = datetime.strptime(r['date'], '%Y-%m-%d').date()
        yt_rows.append(dict(plateforme='YouTube', type='Short', date=r['date'], age_jours=(TODAY - d).days, periode=period(d),
                            titre=r['title'], duree=r['dur'], vues=num(r['views']), revenus_est_eur=num(r['revenue_eur']),
                            commentaires=num(r['comments']), visibilite=r['visibility'], note=r['note'],
                            comm_1000v=round(num(r['comments']) / num(r['views']) * 1000, 2) if num(r['views']) else None))
with open(DB + 'yt_videos.tsv', encoding='utf-8') as f:
    for r in csv.DictReader(f, delimiter='\t'):
        if r['date'].startswith('#'): continue
        d = datetime.strptime(r['date'], '%Y-%m-%d').date()
        yt_rows.append(dict(plateforme='YouTube', type='Vidéo longue', date=r['date'], age_jours=(TODAY - d).days, periode=period(d),
                            titre=r['title'], duree=r['dur'], vues=num(r['views']), revenus_est_eur=num(r['revenue_eur']),
                            commentaires=num(r['comments']), visibilite=r['visibility']))

# ---------- write base ----------
cols = ['plateforme','type','date','heure','jour_semaine','age_jours','periode','titre','pilier','format','repost','statut','visibilite','duree','lien',
        'vues','pct_vues_non_followers','vues_non_followers','reach','interactions','likes','commentaires','enregistrements','partages','partages_derives',
        'comptes_engages','nouveaux_followers','visites_profil','fb_vues','likes_1000v','comm_1000v','saves_1000v','partages_1000v','follows_1000v',
        'engagement_vues_pct','engagement_reach_pct','duree_s','duree_moyenne_s','pct_duree_regardee','completion_pct','chute_principale','pct_pour_toi','pct_recherche',
        'revenus_est_eur','sources_trafic','recherches','titre_public','note']
allrows = rows + tt_rows + yt_rows
allrows.sort(key=lambda r: (r['plateforme'], r['date']), reverse=True)
with open(OUT + 'base_publications.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore'); w.writeheader()
    for r in allrows: w.writerow(r)
json.dump(allrows, open(OUT + 'base_publications.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0, default=str)

# ---------- summaries ----------
def med(vals):
    vals = [v for v in vals if v is not None]
    return (round(st.median(vals)), len(vals)) if vals else (None, 0)

def summarize(label, rs, keys):
    out = {'n': len(rs)}
    for k in keys:
        m, n = med([r.get(k) for r in rs]); out[k] = m
    return out

S = {}
ig_reels = [r for r in rows if r['type'] == 'Reel']
S['IG reels P1 organiques'] = summarize('', [r for r in ig_reels if r['periode'].startswith('P1') and r['statut'] == 'organique'], ['vues','vues_non_followers','interactions','enregistrements','partages_derives','nouveaux_followers','saves_1000v','partages_1000v','follows_1000v','comm_1000v','engagement_vues_pct','pct_vues_non_followers'])
S['IG reels P0 organiques'] = summarize('', [r for r in ig_reels if r['periode'].startswith('P0') and r['statut'] == 'organique'], ['vues','vues_non_followers','interactions','enregistrements','partages_derives','nouveaux_followers','saves_1000v','partages_1000v','follows_1000v','comm_1000v','engagement_vues_pct','pct_vues_non_followers'])
for pil in ['ALG','MAG','MONDE','FR','VOYAGE','PERSO','COLLAB']:
    for per in ['P1','P0']:
        rs = [r for r in ig_reels if r['pilier'] == pil and r['periode'].startswith(per)]
        if rs: S[f'IG {per} pilier {pil}'] = summarize('', rs, ['vues','pct_vues_non_followers','saves_1000v','partages_1000v','follows_1000v','comm_1000v','engagement_vues_pct'])
for fmt in ['recette','voyage','voyage-resto','annonce','recette-voyage']:
    rs = [r for r in ig_reels if r['format'] == fmt and r['periode'].startswith('P1')]
    if rs: S[f'IG P1 format {fmt}'] = summarize('', rs, ['vues','pct_vues_non_followers','saves_1000v','partages_1000v','follows_1000v','comm_1000v','engagement_vues_pct'])
rs = [r for r in ig_reels if r['format'] == 'recette' and r['statut'] == 'organique' and r['repost'].startswith('oui')]
S['IG recettes RE-TOURNÉES (180 j)'] = summarize('', rs, ['vues','pct_vues_non_followers','saves_1000v','partages_1000v','follows_1000v','engagement_vues_pct'])
rs = [r for r in ig_reels if r['format'] == 'recette' and r['statut'] == 'organique' and r['repost'].startswith('non')]
S['IG recettes NOUVELLES (180 j)'] = summarize('', rs, ['vues','pct_vues_non_followers','saves_1000v','partages_1000v','follows_1000v','engagement_vues_pct'])
for per in ['P1','P0']:
    rs = [r for r in ig_reels if r['format'] == 'recette' and r['statut'] == 'organique' and r['periode'].startswith(per)]
    S[f'IG {per} recettes organiques'] = summarize('', rs, ['vues','pct_vues_non_followers','saves_1000v','partages_1000v','follows_1000v','engagement_vues_pct'])

tt_pub = [r for r in tt_rows if r['visibilite'] == 'public']
for per in ['P1','P0']:
    rs = [r for r in tt_pub if r['periode'].startswith(per)]
    S[f'TT {per} publiques'] = summarize('', rs, ['vues','likes_1000v','comm_1000v','partages_1000v','saves_1000v','follows_1000v','duree_moyenne_s','completion_pct','pct_duree_regardee'])
for pil in ['ALG','MAG','MONDE','FR','VOYAGE','PERSO','COLLAB']:
    rs = [r for r in tt_pub if r['pilier'] == pil and r['periode'].startswith('P1')]
    if rs: S[f'TT P1 pilier {pil}'] = summarize('', rs, ['vues','likes_1000v','comm_1000v','partages_1000v','saves_1000v','follows_1000v','duree_moyenne_s','completion_pct'])
# 12 mois TikTok par mois (vues médianes des vidéos publiques)
bym = defaultdict(list)
for r in tt_pub:
    if r['date'] >= '2025-11-01': bym[r['date'][:7]].append(r['vues'])
S['TT vues médianes par mois (publiques)'] = {k: (round(st.median(v)), len(v)) for k, v in sorted(bym.items())}
bym = defaultdict(list)
for r in tt_pub:
    if '2025-02-01' <= r['date'] <= '2026-10-31': bym[r['date'][:7]].append(r['vues'])
S['TT vues médianes par mois (depuis févr. 2025)'] = {k: (round(st.median(v)), len(v)) for k, v in sorted(bym.items())}
# heures TikTok (P1+P0 publiques)
byh = defaultdict(list)
for r in tt_pub:
    if r['periode'] != 'avant': byh[r['heure'][:2] + 'h'].append(r['vues'])
S['TT vues médianes par heure de publication (180 j)'] = {k: (round(st.median(v)), len(v)) for k, v in sorted(byh.items())}
byd = defaultdict(list)
for r in tt_pub:
    if r['periode'] != 'avant': byd[r['jour_semaine']].append(r['vues'])
S['TT vues médianes par jour (180 j)'] = {k: (round(st.median(v)), len(v)) for k, v in byd.items()}
# YouTube shorts
ys = [r for r in yt_rows if r['type'] == 'Short' and r['visibilite'] == 'public']
S['YT shorts P1'] = summarize('', [r for r in ys if r['periode'].startswith('P1')], ['vues','comm_1000v','revenus_est_eur'])
S['YT shorts P1 recettes vs voyage'] = {
    'recette': med([r['vues'] for r in ys if r['periode'].startswith('P1') and r['note'] not in ('voyage','voyage/resto','livre','doc')]),
    'voyage': med([r['vues'] for r in ys if r['periode'].startswith('P1') and r['note'] in ('voyage','voyage/resto')]),
    'livre': med([r['vues'] for r in ys if r['periode'].startswith('P1') and r['note'] == 'livre']),
}

json.dump(S, open(OUT + 'summary.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(S, ensure_ascii=False, indent=1))

# tables for diagnostic
print('\n=== IG reels 180 j triés par follows/1000 vues ===')
for r in sorted([r for r in ig_reels if r.get('follows_1000v') is not None], key=lambda r: -r['follows_1000v']):
    print(f"{r['date']} | {r['titre'][:38]:38} | {r['pilier']:6} | vues {r['vues']:>9.0f} | nonF {r['pct_vues_non_followers']:>5} | saves/1k {r['saves_1000v']:>5} | part/1k {r['partages_1000v']:>5} | fol/1k {r['follows_1000v']:>5} | eng {r['engagement_vues_pct']}")
print('\n=== TikTok détail triés par follows/1000 ===')
for r in sorted([r for r in tt_rows if r.get('follows_1000v') is not None], key=lambda r: -r['follows_1000v']):
    print(f"{r['date']} {r['heure']} {r['jour_semaine']} | {r['titre'][:38]:38} | {r['pilier']:6} | vues {r['vues']:>9.0f} | avg {r.get('duree_moyenne_s')}s/{r.get('duree_s')}s ({r.get('pct_duree_regardee')}%) | full {r.get('completion_pct')}% | saves/1k {r.get('saves_1000v')} | part/1k {r.get('partages_1000v')} | fol/1k {r['follows_1000v']} | rech {r.get('pct_recherche')}% | €{r.get('revenus_est_eur')}")
