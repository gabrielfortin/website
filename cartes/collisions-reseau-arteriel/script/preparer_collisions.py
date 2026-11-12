#!/usr/bin/env python3
"""
Rattache chaque collision routière de la Ville de Montréal à un tronçon du
réseau artériel administratif, puis écrit un fichier compact par
arrondissement pour la carte « Collisions et réseau artériel ».

Sources :
  - « Collisions routières » (Ville de Montréal, SPVM / SAAQ), CC BY 4.0
    https://donnees.montreal.ca/dataset/collisions-routieres
    Fichier GeoJSON (~380 Mo, une collision par ligne) : NE PAS le commiter.
  - Les tronçons de ../reseau-arteriel/data/<slug>.json (même carte de base
    que « Réseau artériel de Montréal », format décrit dans son NOTES.md).

Méthode (détails et chiffres dans ../NOTES.md) :
  1. Seulement les collisions de la Ville de Montréal (CD_MUNCP = 66023) :
     le réseau artériel ne couvre pas les villes liées.
  2. Hors du calcul, avec les champs de la source :
       - LOC_COTE_PD = 4 : « Précision nulle », collision placée au centroïde
         du poste de quartier (non dessinée, comptée seulement au total) ;
       - LOC_DETACHEE = O : collision détachée du réseau routier par la Ville
         (stationnement, ruelle, terrain privé…), dessinée mais non rattachée.
  3. Les autres : tronçon le plus proche, sauf si un tronçon à 30 m ou moins
     porte le même nom que RUE_ACCDN (rue de la collision selon le rapport) ;
     celui-là est préféré, ce qui règle les intersections. Aucun tronçon à
     60 m ou moins : « non rattachée ».
  4. Arrondissement : celui (ou ceux) du tronçon retenu ; pour une collision
     non rattachée, celui du tronçon le plus proche dans un rayon de 500 m.

Sorties (dans ../data/) :
  <slug>.json   {"noms": [...], "collisions": [[...], ...]}, format en tête
                de ../index.html (constante COL)
  resume.json   totaux de contrôle et kilomètres de rues par classe
  meta.json     date de préparation, période et version de la source

Usage (la date est celle de la ressource GeoJSON sur donnees.montreal.ca,
« Dernière modification des données ») :
    python3 preparer_collisions.py ~/Downloads/collisions_routieres.geojson 2022-10-06
"""
import collections
import datetime
import glob
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

ICI = Path(__file__).resolve().parent
RACINE = ICI.parent
TRONCONS = RACINE.parent / "reseau-arteriel" / "data"
SORTIE = RACINE / "data"

VILLE_DE_MONTREAL = 66023
RAYON_NOM = 30        # m : tronçon du même nom préféré dans ce rayon
RAYON_MAX = 60        # m : au-delà, collision non rattachée
RAYON_ARRONDISSEMENT = 500  # m : pour placer une collision non rattachée

# Libellés de GRAVITE, du plus grave au moins grave (valeurs exactes de la source)
GRAVITES = [
    "Mortel",
    "Grave",
    "Léger",
    "Dommages matériels seulement",
    "Dommages matériels inférieurs au seuil de rapportage",
]
DETACHEE = -1      # LOC_DETACHEE = O
NON_RATTACHEE = -3  # aucun tronçon à RAYON_MAX m ou moins

# Projection locale en mètres (équirectangulaire autour de Montréal : erreur négligeable à 60 m)
LAT0 = 45.55
KX = 111320 * math.cos(math.radians(LAT0))
KY = 110574
CELLULE = 60


def xy(lng, lat):
    return lng * KX, lat * KY


# ---------- Normalisation des noms de rue ----------
# RUE_ACCDN : « ST DENIS », « BD LACORDAIRE », « N-D E », « DES GDES PRAIRIES »
# tronçons  : « Saint-Denis », « Lacordaire », « Notre-Dame », « Grandes-Prairies »
GENERIQUES = {
    "RUE", "BD", "BOUL", "BOULEVARD", "AV", "AVE", "AVEN", "AVENUE", "CH", "CHEMIN",
    "PL", "MONTEE", "MTEE", "TERR", "TERRASSE", "CROIS", "CROISSANT", "PROM",
    "PROMENADE", "RANG", "ALLEE", "IMPASSE", "SQ", "RTE", "FACE",
    "E", "O", "N", "S", "EST", "OUEST", "NORD", "SUD", "W",
}
ARTICLES = {"DE", "DU", "DES", "LA", "LE", "LES", "L", "D"}
ABREVIATIONS = {
    "ST": "SAINT", "STE": "SAINTE", "MT": "MONT", "GDES": "GRANDES", "GDE": "GRANDE",
    "RIV": "RIVIERE", "GAL": "GALERIES", "PT": "POINTE", "CTE": "COTE",
}


def cles_nom(nom):
    """Deux clés comparables (avec et sans articles), lettres collées."""
    if not nom:
        return set()
    s = unicodedata.normalize("NFKD", nom).encode("ascii", "ignore").decode().upper()
    s = re.sub(r"\bN[\s-]+D\b", "NOTRE DAME", s)
    mots = [ABREVIATIONS.get(m, m) for m in re.split(r"[^A-Z0-9]+", s) if m]
    mots = [m for m in mots if m not in GENERIQUES]
    avec = "".join(mots)
    sans = "".join(m for m in mots if m not in ARTICLES)
    return {k for k in (avec, sans) if k}


# ---------- Tronçons ----------
def charger_troncons():
    troncons = []          # [coords, classe, artere, nom, [slugs]]
    index = {}
    for f in sorted(glob.glob(str(TRONCONS / "*.json"))):
        slug = Path(f).stem
        if slug == "manifest":
            continue
        for coords, classe, artere, nom in json.load(open(f, encoding="utf-8")):
            cle = json.dumps(coords)
            if cle not in index:
                index[cle] = len(troncons)
                troncons.append([coords, classe, artere, nom, []])
            troncons[index[cle]][4].append(slug)
    return troncons


def construire_grille(troncons):
    grille = collections.defaultdict(list)
    for i, t in enumerate(troncons):
        pts = [xy(*c) for c in t[0]]
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            for cx in range(int(min(x1, x2) // CELLULE), int(max(x1, x2) // CELLULE) + 1):
                for cy in range(int(min(y1, y2) // CELLULE), int(max(y1, y2) // CELLULE) + 1):
                    grille[(cx, cy)].append((i, x1, y1, x2, y2))
    return grille


def distance_segment(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    l2 = dx * dx + dy * dy
    t = 0 if l2 == 0 else max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / l2))
    return math.hypot(px - x1 - t * dx, py - y1 - t * dy)


def voisins(grille, lng, lat, rayon):
    """[(index du tronçon, distance en m)] à `rayon` m ou moins, du plus proche au plus loin."""
    px, py = xy(lng, lat)
    meilleur = {}
    r = int(rayon // CELLULE) + 1
    cx, cy = int(px // CELLULE), int(py // CELLULE)
    for a in range(cx - r, cx + r + 1):
        for b in range(cy - r, cy + r + 1):
            for i, x1, y1, x2, y2 in grille.get((a, b), ()):
                d = distance_segment(px, py, x1, y1, x2, y2)
                if d <= rayon and d < meilleur.get(i, math.inf):
                    meilleur[i] = d
    return sorted(meilleur.items(), key=lambda t: t[1])


def longueur_km(coords):
    pts = [xy(*c) for c in coords]
    return sum(math.hypot(x2 - x1, y2 - y1) for (x1, y1), (x2, y2) in zip(pts, pts[1:])) / 1000


# ---------- Collisions ----------
def lire_collisions(chemin):
    """Une collision par ligne dans le GeoJSON de la Ville : lecture en continu."""
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.strip().rstrip(",")
            if ligne.startswith('{ "type": "Feature"'):
                yield json.loads(ligne)["properties"]


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    source = Path(sys.argv[1]).expanduser()
    version_source = datetime.date.fromisoformat(sys.argv[2]).isoformat()

    troncons = charger_troncons()
    grille = construire_grille(troncons)
    cles_troncons = [cles_nom(t[3]) for t in troncons]
    print(f"{len(troncons)} tronçons uniques", file=sys.stderr)

    par_slug = collections.defaultdict(list)
    noms_par_slug = collections.defaultdict(dict)
    compte = collections.Counter()
    annees = set()
    vus = set()

    def nom_idx(slug, nom):
        if nom is None:
            return -1
        table = noms_par_slug[slug]
        if nom not in table:
            table[nom] = len(table)
        return table[nom]

    for p in lire_collisions(source):
        if p["CD_MUNCP"] != VILLE_DE_MONTREAL:
            compte["autres_villes"] += 1
            continue
        compte["ville_de_montreal"] += 1

        m = re.fullmatch(r"SPVM _ (\d{4}) _ (\d+)", p["NO_SEQ_COLL"] or "")
        if not m or int(m.group(1)) != p["AN"]:
            sys.exit(f"NO_SEQ_COLL inattendu : {p['NO_SEQ_COLL']!r}")
        numero = int(m.group(2))
        if (p["AN"], numero) in vus:
            sys.exit(f"NO_SEQ_COLL en double : {p['NO_SEQ_COLL']!r}")
        vus.add((p["AN"], numero))
        if p["GRAVITE"] not in GRAVITES:
            sys.exit(f"GRAVITE inconnue : {p['GRAVITE']!r}")
        annees.add(p["AN"])

        if p["LOC_LONG"] is None or p["LOC_LAT"] is None:
            compte["sans_coordonnees"] += 1
            continue
        if str(p["LOC_COTE_PD"]) == "4":
            compte["precision_nulle"] += 1
            continue

        lng, lat = p["LOC_LONG"], p["LOC_LAT"]
        if p["LOC_DETACHEE"] == "O":
            categorie, artere, methode, troncon, dist = DETACHEE, 0, 0, None, None
        else:
            cand = voisins(grille, lng, lat, RAYON_MAX)
            if not cand:
                categorie, artere, methode, troncon, dist = NON_RATTACHEE, 0, 0, None, None
            else:
                cle_rue = cles_nom(p["RUE_ACCDN"])
                choix = None
                if cle_rue:
                    for i, d in cand:
                        if d <= RAYON_NOM and cle_rue & cles_troncons[i]:
                            choix, methode = (i, d), 1
                            break
                if choix is None:
                    choix, methode = cand[0], 0
                troncon, dist = troncons[choix[0]], choix[1]
                categorie, artere = troncon[1], troncon[2]

        if troncon is not None:
            slugs = troncon[4]
        else:
            proches = voisins(grille, lng, lat, RAYON_ARRONDISSEMENT)
            slugs = troncons[proches[0][0]][4] if proches else []
        if not slugs:
            compte["hors_arrondissements"] += 1
            continue

        compte["categorie_" + str(categorie)] += 1
        compte["methode_nom" if troncon is not None and methode == 1 else "methode_autre"] += 1
        for slug in slugs:
            par_slug[slug].append([
                numero,
                round(lng, 6), round(lat, 6),
                p["DT_ACCDN"],
                GRAVITES.index(p["GRAVITE"]),
                categorie, artere, methode,
                p["NB_MORTS"] or 0, p["NB_BLESSES_GRAVES"] or 0, p["NB_BLESSES_LEGERS"] or 0,
                p["NB_VICTIMES_PIETON"] or 0, p["NB_VICTIMES_VELO"] or 0,
                nom_idx(slug, p["RUE_ACCDN"]),
                nom_idx(slug, p["ACCDN_PRES_DE"]),
                nom_idx(slug, troncon[3]) if troncon is not None else -1,
                round(dist, 1) if dist is not None else None,
                p["NB_VICTIMES_MOTO"] or 0,
            ])

    # Kilomètres de rues par classe (tronçons dédoublonnés pour « Tous »)
    km_tous = collections.Counter()
    km_par_slug = collections.defaultdict(collections.Counter)
    km_artere_tous = 0.0
    km_artere_slug = collections.Counter()
    for t in troncons:
        km = longueur_km(t[0])
        km_tous[t[1]] += km
        if t[2] == 1:
            km_artere_tous += km
        for slug in t[4]:
            km_par_slug[slug][t[1]] += km
            if t[2] == 1:
                km_artere_slug[slug] += km

    SORTIE.mkdir(exist_ok=True)
    for slug, rangees in sorted(par_slug.items()):
        noms = [None] * len(noms_par_slug[slug])
        for nom, i in noms_par_slug[slug].items():
            noms[i] = nom
        with open(SORTIE / f"{slug}.json", "w", encoding="utf-8") as f:
            json.dump({"noms": noms, "collisions": rangees}, f, ensure_ascii=False, separators=(",", ":"))

    arrondi = lambda c: {str(k): round(v, 2) for k, v in sorted(c.items())}
    resume = {
        "compte": dict(sorted(compte.items())),
        "km": {
            "tous": {"classes": arrondi(km_tous), "artere": round(km_artere_tous, 2)},
            **{slug: {"classes": arrondi(c), "artere": round(km_artere_slug[slug], 2)}
               for slug, c in sorted(km_par_slug.items())},
        },
        "collisions_par_fichier": {slug: len(r) for slug, r in sorted(par_slug.items())},
    }
    with open(SORTIE / "resume.json", "w", encoding="utf-8") as f:
        json.dump(resume, f, ensure_ascii=False, indent=1)
    meta = {
        "donneesMisesAJour": datetime.date.today().isoformat(),
        "versionSource": version_source,
        "anneeDebut": min(annees),
        "anneeFin": max(annees),
        "gravites": GRAVITES,
    }
    with open(SORTIE / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)

    json.dump(resume["compte"], sys.stderr, ensure_ascii=False, indent=1)
    print(file=sys.stderr)


if __name__ == "__main__":
    main()
