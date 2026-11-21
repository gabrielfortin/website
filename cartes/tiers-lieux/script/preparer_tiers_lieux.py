#!/usr/bin/env python3
"""Accès aux tiers lieux : distance à pied de chaque lot résidentiel de la Ville de Montréal
à la ruelle verte, à la place publique et au parc les plus proches. Écrit ../data/.

Sources (données ouvertes de la Ville de Montréal, CC BY 4.0), dans script/sources/ (non
versionné ; `--telecharger` les récupère) :
  - Unités d'évaluation foncière (extrait géographique) : les lots et leur nombre de logements ;
  - Ruelles vertes ;
  - Grands parcs, parcs d'arrondissements et espaces publics : parcs et places publiques ;
  - Géobase - réseau routier : le réseau de rues où l'on marche ;
  - Limites administratives de l'agglomération : les 19 arrondissements.

Règles (décisions de Gabriel, 20 novembre 2026 ; détails dans ../NOTES.md) :
  - Lots : unités de la Ville de Montréal (MUNICIPALITE « 50 ») qui ont au moins un logement.
    Les unités d'un même lot (copropriétés) ont la même géométrie : elles forment un seul lot,
    dont les logements s'additionnent. Arrondissement : NO_ARROND_ILE_CUM (= CODEMAMH des limites).
  - Parcs : TYPO1 « Grand parc », et TYPO1 « Parc d'arrondissement » avec TYPO2 « Parc de
    quartier », « Parc de voisinage », « Parc linéaire » ou « Square ». Places publiques : TYPO2
    « Place publique ». Ruelles vertes : toutes.
  - Marche : tronçons de la Géobase de CLASSE 0 à 7 (sans les autoroutes, 8, ni les rues
    projetées, 9), dans les deux sens. Un lieu est atteint par tout tronçon qui passe à moins de
    ACCES m de son contour (ou le traverse) ; la distance compte le bout de tronçon et l'écart.
  - Distance d'un lot : du centre du lot au tronçon le plus proche, puis par les rues jusqu'au lieu.
    Un lot qui touche le lieu (moins de CONTACT m, ex. cour sur une ruelle verte) prend la distance
    à vol d'oiseau de son centre au lieu, si elle est plus courte.
  - Au-delà de MAX m, la distance n'est pas écrite (null).
La note de couleur (points par type, de 100 à 400 m) est calculée dans la page, à partir de ces
distances, pour que les cases à cocher fonctionnent sans recharger.

Transformations : coordonnées arrondies à 6 décimales et écrites en entiers relatifs
(millionièmes de degré, voir code_anneaux), JSON sans espaces, distances en mètres entiers. Le script vide data/ avant d'écrire et s'arrête s'il ne peut pas rattacher un lot.

    python3 script/preparer_tiers_lieux.py [--telecharger]
"""

import heapq
import io
import json
import math
import os
import re
import shutil
import sys
import unicodedata
import urllib.request
import zipfile
from collections import defaultdict
from datetime import date

ICI = os.path.dirname(os.path.abspath(__file__))
SOURCES = os.path.join(ICI, "sources")
DATA = os.path.join(ICI, "..", "data")

ACCES = 30.0      # m : un tronçon à moins de 30 m du contour d'un lieu y donne accès
CONTACT = 10.0    # m : lot qui touche le lieu
MAX = 2000        # m : au-delà, distance non écrite
SNAP = 300.0      # m : distance maximale du centre d'un lot au réseau
CELLULE = 100.0   # m : maille des index spatiaux

FICHIERS = {
    "uef": ("uef.geojson.zip", "https://donnees.montreal.ca/dataset/4ad6baea-4d2c-460f-a8bf-5d000db498f7/resource/866a3dbc-8b59-48ff-866d-f2f9d3bbee9d/download/uniteevaluationfonciere.geojson.zip", "unites-evaluation-fonciere"),
    "ruelles": ("ruelles-vertes.geojson", "https://donnees.montreal.ca/fr/dataset/ab3ce7bb-09a7-49d7-8f76-461ed4c39937/resource/15883136-0180-4061-9860-d7ce3d46c73c/download/ruelles-vertes.geojson", "ruelles-vertes"),
    "espaces": ("espace_vert.json", "https://donnees.montreal.ca/dataset/2e9e4d2f-173a-4c3d-a5e3-565d79baa27d/resource/35796624-15df-4503-a569-797665f8768e/download/espace_vert.json", "grands-parcs-parcs-d-arrondissements-et-espaces-publics"),
    "geobase": ("geobase.json", "https://donnees.montreal.ca/dataset/984f7a68-ab34-4092-9204-4bdfcca767c5/resource/9d3d60d8-4e7f-493e-8d6a-dcd040319d8d/download/geobase.json", "geobase"),
    "limites": ("limites.geojson", "https://donnees.montreal.ca/dataset/9797a946-9da8-41ec-8815-f6b276dec7e9/resource/e18bfd07-edc8-4ce8-8a5a-3b617662a794/download/limites-administratives-agglomeration.geojson", "limites-administratives-agglomeration"),
}
TYPES = ["ruelle", "place", "parc"]
PARCS_ARR = {"Parc de quartier", "Parc de voisinage", "Parc linéaire", "Square"}


def stop(msg):
    sys.exit("preparer_tiers_lieux.py : " + msg)


def chemin(cle):
    return os.path.join(SOURCES, FICHIERS[cle][0])


def telecharger():
    os.makedirs(SOURCES, exist_ok=True)
    for cle, (nom, url, _) in FICHIERS.items():
        print("Téléchargement :", nom)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (gabfortin.com)"})
        with urllib.request.urlopen(req, timeout=600) as r, open(os.path.join(SOURCES, nom), "wb") as f:
            shutil.copyfileobj(r, f)


def dates_sources():
    """Date de mise à jour de chaque jeu (API du portail) ; vide si hors ligne."""
    dates = {}
    for cle, (_, _, jeu) in FICHIERS.items():
        try:
            with urllib.request.urlopen("https://donnees.montreal.ca/api/3/action/package_show?id=" + jeu, timeout=30) as r:
                dates[cle] = json.load(r)["result"]["metadata_modified"][:10]
        except Exception:
            pass
    return dates


# ── Géométrie (mètres, projection locale équirectangulaire autour de Montréal) ─────────────────
LON0, LAT0 = -73.6, 45.55
KX, KY = 111320.0 * math.cos(math.radians(LAT0)), 110574.0


def proj(lon, lat):
    return ((lon - LON0) * KX, (lat - LAT0) * KY)


def r6(v):
    return round(v, 6)


def dist_point_seg(px, py, ax, ay, bx, by):
    """Distance du point au segment, et position t (0..1) du point le plus proche sur le segment."""
    dx, dy = bx - ax, by - ay
    l2 = dx * dx + dy * dy
    t = 0.0 if l2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
    qx, qy = ax + t * dx, ay + t * dy
    return math.hypot(px - qx, py - qy), t


def se_croisent(a, b, c, d):
    def o(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return (o(a, b, c) * o(a, b, d) < 0) and (o(c, d, a) * o(c, d, b) < 0)


def dedans(px, py, anneaux):
    """Point dans un polygone (pair-impair sur tous les anneaux : trous compris)."""
    c = False
    for ring in anneaux:
        n = len(ring)
        j = n - 1
        for i in range(n):
            xi, yi = ring[i]
            xj, yj = ring[j]
            if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
                c = not c
            j = i
    return c


class Grille:
    def __init__(self, cellule=CELLULE):
        self.c = cellule
        self.d = defaultdict(list)

    def cles(self, x0, y0, x1, y1):
        c = self.c
        for i in range(int(math.floor(x0 / c)), int(math.floor(x1 / c)) + 1):
            for j in range(int(math.floor(y0 / c)), int(math.floor(y1 / c)) + 1):
                yield (i, j)

    def ajouter(self, obj, x0, y0, x1, y1):
        for k in self.cles(x0, y0, x1, y1):
            self.d[k].append(obj)

    def chercher(self, x0, y0, x1, y1):
        vus = set()
        for k in self.cles(x0, y0, x1, y1):
            for o in self.d.get(k, ()):
                if id(o) not in vus:
                    vus.add(id(o))
                    yield o


def polygones(geom):
    """Liste de polygones, chacun liste d'anneaux en coordonnées géographiques."""
    if geom is None:
        return []
    if geom["type"] == "Polygon":
        return [geom["coordinates"]]
    if geom["type"] == "MultiPolygon":
        return list(geom["coordinates"])
    stop("géométrie inattendue : " + geom["type"])


def centre(anneau):
    """Centroïde d'un anneau (aire), en mètres."""
    a = cx = cy = 0.0
    pts = [proj(*p[:2]) for p in anneau]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        f = x1 * y2 - x2 * y1
        a += f
        cx += (x1 + x2) * f
        cy += (y1 + y2) * f
    if abs(a) < 1e-9:
        return pts[0], 0.0
    return (cx / (3 * a), cy / (3 * a)), abs(a) / 2


# ── Lieux ──────────────────────────────────────────────────────────────────────────────────────
class Lieu:
    __slots__ = ("type", "id", "nom", "anneaux", "geo", "bbox", "segs")

    def __init__(self, type_, id_, nom, geom):
        self.type, self.id, self.nom = type_, id_, nom
        self.geo = polygones(geom)
        self.anneaux = [[proj(*p[:2]) for p in ring] for poly in self.geo for ring in poly]
        xs = [p[0] for r in self.anneaux for p in r]
        ys = [p[1] for r in self.anneaux for p in r]
        self.bbox = (min(xs), min(ys), max(xs), max(ys))
        self.segs = Grille(50.0)
        for r in self.anneaux:
            for a, b in zip(r, r[1:]):
                self.segs.ajouter((a, b), min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))

    def distance_point(self, x, y, rayon):
        """Distance du point au lieu (0 dedans) ; None si plus loin que rayon."""
        b = self.bbox
        if x < b[0] - rayon or x > b[2] + rayon or y < b[1] - rayon or y > b[3] + rayon:
            return None
        if dedans(x, y, self.anneaux):
            return 0.0
        best = None
        for a, c in self.segs.chercher(x - rayon, y - rayon, x + rayon, y + rayon):
            d, _ = dist_point_seg(x, y, a[0], a[1], c[0], c[1])
            if best is None or d < best:
                best = d
        return best if best is not None and best <= rayon else None


def lire_lieux():
    lieux = {t: [] for t in TYPES}
    for f in json.load(open(chemin("ruelles"), encoding="utf-8"))["features"]:
        p = f["properties"]
        if f["geometry"]:
            lieux["ruelle"].append(Lieu("ruelle", len(lieux["ruelle"]), p.get("RUELLE_ID") or "", f["geometry"]))
    for f in json.load(open(chemin("espaces"), encoding="utf-8"))["features"]:
        p = f["properties"]
        if not f["geometry"]:
            continue
        t1, t2 = p.get("TYPO1"), p.get("TYPO2")
        if t2 == "Place publique":
            t = "place"
        elif t1 == "Grand parc" or (t1 == "Parc d'arrondissement" and t2 in PARCS_ARR):
            t = "parc"
        else:
            continue
        lieux[t].append(Lieu(t, len(lieux[t]), (p.get("Nom") or "").strip(), f["geometry"]))
    for t in TYPES:
        print(f"Lieux {t} : {len(lieux[t])}")
    return lieux


# ── Réseau de marche ───────────────────────────────────────────────────────────────────────────
class Troncon:
    __slots__ = ("a", "b", "pts", "cum", "long")

    def __init__(self, a, b, pts):
        self.a, self.b, self.pts = a, b, pts
        self.cum = [0.0]
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            self.cum.append(self.cum[-1] + math.hypot(x2 - x1, y2 - y1))
        self.long = self.cum[-1]

    def plus_proche(self, x, y):
        """(écart, position le long du tronçon) du point le plus proche."""
        best = (float("inf"), 0.0)
        for i, ((x1, y1), (x2, y2)) in enumerate(zip(self.pts, self.pts[1:])):
            d, t = dist_point_seg(x, y, x1, y1, x2, y2)
            if d < best[0]:
                best = (d, self.cum[i] + t * (self.cum[i + 1] - self.cum[i]))
        return best


def lire_reseau():
    noeuds, troncons = {}, []
    grille = Grille()
    for f in json.load(open(chemin("geobase"), encoding="utf-8"))["features"]:
        p, g = f["properties"], f["geometry"]
        if g is None or p.get("CLASSE") is None or int(p["CLASSE"]) > 7:
            continue
        coords = g["coordinates"]
        ka, kb = (r6(coords[0][0]), r6(coords[0][1])), (r6(coords[-1][0]), r6(coords[-1][1]))
        a = noeuds.setdefault(ka, len(noeuds))
        b = noeuds.setdefault(kb, len(noeuds))
        t = Troncon(a, b, [proj(*c[:2]) for c in coords])
        troncons.append(t)
        xs = [q[0] for q in t.pts]
        ys = [q[1] for q in t.pts]
        grille.ajouter(t, min(xs), min(ys), max(xs), max(ys))
    voisins = [[] for _ in range(len(noeuds))]
    for t in troncons:
        voisins[t.a].append((t.b, t.long))
        voisins[t.b].append((t.a, t.long))
    print(f"Réseau de marche : {len(troncons)} tronçons, {len(noeuds)} nœuds")
    return troncons, voisins, grille


def acces(lieu, grille):
    """Tronçons qui donnent accès au lieu : [(tronçon, position, écart)]."""
    b = lieu.bbox
    res = []
    for t in grille.chercher(b[0] - ACCES, b[1] - ACCES, b[2] + ACCES, b[3] + ACCES):
        best = None   # (écart, position)
        for i, (p, q) in enumerate(zip(t.pts, t.pts[1:])):
            for k, pt in ((0, p), (1, q)):
                if b[0] - ACCES <= pt[0] <= b[2] + ACCES and b[1] - ACCES <= pt[1] <= b[3] + ACCES and dedans(pt[0], pt[1], lieu.anneaux):
                    cand = (0.0, t.cum[i + k])
                    if best is None or cand < best:
                        best = cand
            x0, y0 = min(p[0], q[0]) - ACCES, min(p[1], q[1]) - ACCES
            x1, y1 = max(p[0], q[0]) + ACCES, max(p[1], q[1]) + ACCES
            L = t.cum[i + 1] - t.cum[i]
            for a, c in lieu.segs.chercher(x0, y0, x1, y1):
                if se_croisent(p, q, a, c):
                    # position du croisement : point de (p,q) le plus proche du milieu de (a,c), approché
                    _, tt = dist_point_seg((a[0] + c[0]) / 2, (a[1] + c[1]) / 2, p[0], p[1], q[0], q[1])
                    cand = (0.0, t.cum[i] + tt * L)
                else:
                    d1, tt1 = dist_point_seg(a[0], a[1], p[0], p[1], q[0], q[1])
                    d2, tt2 = dist_point_seg(c[0], c[1], p[0], p[1], q[0], q[1])
                    d3, _ = dist_point_seg(p[0], p[1], a[0], a[1], c[0], c[1])
                    d4, _ = dist_point_seg(q[0], q[1], a[0], a[1], c[0], c[1])
                    cand = min((d1, t.cum[i] + tt1 * L), (d2, t.cum[i] + tt2 * L), (d3, t.cum[i]), (d4, t.cum[i + 1]))
                if cand[0] <= ACCES and (best is None or cand < best):
                    best = cand
        if best is not None:
            res.append((t, best[1], best[0]))
    return res


def dijkstra(nb, voisins, departs):
    """departs : {nœud: (distance, id du lieu)} ; rend (dist, lieu) par nœud, jusqu'à MAX + SNAP."""
    dist = [math.inf] * nb
    lab = [-1] * nb
    tas = []
    for n, (d, i) in departs.items():
        if d < dist[n]:
            dist[n], lab[n] = d, i
            heapq.heappush(tas, (d, n))
    limite = MAX + SNAP
    while tas:
        d, n = heapq.heappop(tas)
        if d > dist[n] or d > limite:
            continue
        for m, w in voisins[n]:
            nd = d + w
            if nd < dist[m]:
                dist[m], lab[m] = nd, lab[n]
                heapq.heappush(tas, (nd, m))
    return dist, lab


# ── Lots ───────────────────────────────────────────────────────────────────────────────────────
def adresse(p):
    deb, fin = (p.get("CIVIQUE_DEBUT") or "").strip(), (p.get("CIVIQUE_FIN") or "").strip()
    rue = re.sub(r"\s+", " ", (p.get("NOM_RUE") or "").strip())
    num = deb if not fin or fin == deb else f"{deb}-{fin}"
    return f"{num} {rue}".strip()


def lire_lots(codes):
    lots = {}          # clé géométrie → lot
    sources = 0
    logements_source = 0
    z = zipfile.ZipFile(chemin("uef"))
    nom = [n for n in z.namelist() if n.endswith(".geojson")][0]
    for ligne in io.TextIOWrapper(z.open(nom), encoding="utf-8"):
        ligne = ligne.strip().rstrip(",")
        if not ligne.startswith('{ "type": "Feature"'):
            continue
        f = json.loads(ligne)
        p = f["properties"]
        if p.get("MUNICIPALITE") != "50":
            continue
        n = int(p.get("NOMBRE_LOGEMENT") or 0)
        if n <= 0:
            continue
        sources += 1
        logements_source += n
        arr = p.get("NO_ARROND_ILE_CUM")
        if arr not in codes:
            stop(f"unité {p.get('ID_UEV')} : arrondissement {arr!r} inconnu des limites")
        if f["geometry"] is None:
            stop(f"unité {p.get('ID_UEV')} sans géométrie")
        polys = [[[[r6(x), r6(y)] for x, y, *_ in ring] for ring in poly] for poly in polygones(f["geometry"])]
        cle = json.dumps(polys, separators=(",", ":"))
        lot = lots.get(cle)
        if lot is None:
            lot = lots[cle] = {"polys": polys, "arr": arr, "log": 0, "adr": adresse(p), "n": 0}
        elif lot["arr"] != arr:
            stop(f"lot {p.get('MATRICULE83')} dans deux arrondissements ({lot['arr']}, {arr})")
        lot["log"] += n
        lot["n"] += 1
    print(f"Unités lues : {sources} ({logements_source} logements) ; lots distincts : {len(lots)}")
    return list(lots.values()), sources, logements_source


def distances_lot(lot, grille, lieux_idx, reseau):
    troncons, D, L, seeds_troncon = reseau
    # centre : celui du plus grand anneau extérieur
    meilleur = None
    for poly in lot["polys"]:
        c, a = centre(poly[0])
        if meilleur is None or a > meilleur[1]:
            meilleur = (c, a)
    (x, y) = meilleur[0]
    # tronçon le plus proche
    proche = None
    r = CELLULE
    while proche is None and r <= SNAP:
        for t in grille.chercher(x - r, y - r, x + r, y + r):
            e, s = t.plus_proche(x, y)
            if e <= r and (proche is None or e < proche[1]):
                proche = (t, e, s)
        r *= 2
    sommets = [proj(*pt) for poly in lot["polys"] for pt in poly[0]]
    res = {}
    for typ in TYPES:
        best = (math.inf, -1)
        if proche:
            t, e, s = proche
            for n, along in ((t.a, s), (t.b, t.long - s)):
                d = D[typ][n] + along + e
                if d < best[0]:
                    best = (d, L[typ][n])
            for (sd, gd, i) in seeds_troncon[typ].get(id(t), ()):   # lieu sur le même tronçon
                d = abs(s - sd) + gd + e
                if d < best[0]:
                    best = (d, i)
        # lot qui touche le lieu
        for lieu in lieux_idx[typ].chercher(x - 200, y - 200, x + 200, y + 200):
            if any(lieu.distance_point(sx, sy, CONTACT) is not None for sx, sy in sommets):
                d = lieu.distance_point(x, y, 400.0)
                if d is not None and d < best[0]:
                    best = (d, lieu.id)
        res[typ] = (None, -1) if best[0] > MAX else (int(round(best[0])), best[1])
    return res


def code_anneaux(polys):
    """Géométrie compacte : par polygone, par anneau, entiers en millionièmes de degré
    [x0, y0, dx1, dy1, …] (mêmes 6 décimales, seulement écrites autrement ; la page refait les
    coordonnées). Les points répétés de suite sont retirés."""
    out = []
    for poly in polys:
        anneaux = []
        for ring in poly:
            plat, px, py = [], None, None
            for x, y, *_ in ring:
                ix, iy = int(round(x * 1e6)), int(round(y * 1e6))
                if px is None:
                    plat += [ix, iy]
                elif (ix, iy) != (px, py):
                    plat += [ix - px, iy - py]
                else:
                    continue
                px, py = ix, iy
            anneaux.append(plat)
        out.append(anneaux)
    return out


def slug(nom):
    s = unicodedata.normalize("NFD", nom).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def ecrire(chemin_rel, obj):
    p = os.path.join(DATA, chemin_rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    texte = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    with open(p, "w", encoding="utf-8") as f:
        f.write(texte)
    return len(texte.encode("utf-8"))


def main():
    if "--telecharger" in sys.argv:
        telecharger()
    for cle in FICHIERS:
        if not os.path.exists(chemin(cle)):
            stop(f"source absente : {chemin(cle)} (lancer avec --telecharger)")

    # Arrondissements
    arrs = {}
    for f in json.load(open(chemin("limites"), encoding="utf-8"))["features"]:
        p = f["properties"]
        if p.get("TYPE") == "Arrondissement":
            arrs[p["CODEMAMH"]] = {"nom": p["NOM"], "slug": slug(p["NOM"]), "geo": polygones(f["geometry"])}
    if len(arrs) != 19:
        stop(f"{len(arrs)} arrondissements dans les limites (19 attendus)")

    lieux = lire_lieux()
    troncons, voisins, grille = lire_reseau()

    # Accès aux lieux, puis distances par les rues
    D, L, seeds_troncon, lieux_idx = {}, {}, {}, {}
    for typ in TYPES:
        departs = {}
        st = defaultdict(list)
        idx = Grille(200.0)
        sans = 0
        for lieu in lieux[typ]:
            idx.ajouter(lieu, *lieu.bbox)
            a = acces(lieu, grille)
            if not a:
                sans += 1
            for t, s, e in a:
                st[id(t)].append((s, e, lieu.id))
                for n, d in ((t.a, s + e), (t.b, t.long - s + e)):
                    if n not in departs or d < departs[n][0]:
                        departs[n] = (d, lieu.id)
        D[typ], L[typ] = dijkstra(len(voisins), voisins, departs)
        seeds_troncon[typ], lieux_idx[typ] = st, idx
        print(f"  {typ} : {len(departs)} nœuds d'accès ; {sans} lieux sans tronçon à moins de {ACCES:.0f} m")

    lots, n_sources, log_source = lire_lots(set(arrs))
    reseau = (troncons, D, L, seeds_troncon)

    # data/ vidé avant d'écrire
    if os.path.isdir(DATA):
        shutil.rmtree(DATA)
    os.makedirs(DATA)

    par_arr = defaultdict(list)
    for k, lot in enumerate(lots):
        par_arr[lot["arr"]].append(lot)
        if k % 20000 == 0:
            print(f"  distances : {k}/{len(lots)}")
        lot["d"] = distances_lot(lot, grille, lieux_idx, reseau)

    manifeste = []
    total_lots = total_log = 0
    for code, a in sorted(arrs.items(), key=lambda kv: kv[1]["nom"]):
        lst = par_arr.get(code, [])
        # lieux à montrer : ceux qui touchent l'arrondissement élargi de 1 km
        pts = [proj(*pt[:2]) for poly in a["geo"] for ring in poly for pt in ring]
        bx = (min(p[0] for p in pts) - 1000, min(p[1] for p in pts) - 1000, max(p[0] for p in pts) + 1000, max(p[1] for p in pts) + 1000)
        utiles = {t: set() for t in TYPES}
        for lot in lst:
            for t in TYPES:
                if lot["d"][t][1] >= 0:
                    utiles[t].add(lot["d"][t][1])
        anneaux_arr = [[proj(*pt[:2]) for pt in ring] for poly in a["geo"] for ring in poly]
        montres = {}
        for t in TYPES:
            montres[t] = []
            for lieu in lieux[t]:
                b = lieu.bbox
                if lieu.id in utiles[t] or not (b[2] < bx[0] or b[0] > bx[2] or b[3] < bx[1] or b[1] > bx[3]):
                    # 1 si le centre du lieu est dans l'arrondissement (compteur du panneau), 0 s'il est aux environs
                    (cx, cy), _ = max((centre(poly[0]) for poly in lieu.geo), key=lambda c: c[1])
                    montres[t].append([lieu.id, lieu.nom, code_anneaux(lieu.geo), 1 if dedans(cx, cy, anneaux_arr) else 0])
        donnees = {
            "code": code, "nom": a["nom"],
            "contour": code_anneaux(a["geo"]),
            # lieu : [id, nom, polygones, dans l'arrondissement (1/0)]
            # lot : [polygones, logements, adresse, unités, d_ruelle, d_place, d_parc, id_ruelle, id_place, id_parc]
            "lots": [[code_anneaux(l["polys"]), l["log"], l["adr"], l["n"]] + [l["d"][t][0] for t in TYPES] + [l["d"][t][1] for t in TYPES] for l in lst],
            "lieux": montres,
        }
        taille = ecrire(f"arrondissements/{a['slug']}.json", donnees)
        nlog = sum(l["log"] for l in lst)
        total_lots += len(lst)
        total_log += nlog
        manifeste.append({"cle": a["slug"], "code": code, "nom": a["nom"], "lots": len(lst), "logements": nlog, "octets": taille})
        print(f"  {a['nom']:45} {len(lst):6} lots {nlog:7} logements {taille / 1e6:5.2f} Mo")

    if total_lots != len(lots) or total_log != log_source:
        stop(f"totaux écrits ({total_lots} lots, {total_log} logements) ≠ lus ({len(lots)}, {log_source})")
    ecrire("manifeste.json", {"arrondissements": manifeste, "lots": total_lots, "logements": total_log, "unites": n_sources,
                              "regles": {"acces_m": ACCES, "contact_m": CONTACT, "max_m": MAX},
                              "lieux": {t: len(lieux[t]) for t in TYPES}})
    sources = dates_sources()
    ecrire("meta.json", {"donneesMisesAJour": date.today().isoformat(), "sources": sources})
    print(f"Total : {total_lots} lots, {total_log} logements ({n_sources} unités d'évaluation)")


if __name__ == "__main__":
    main()
