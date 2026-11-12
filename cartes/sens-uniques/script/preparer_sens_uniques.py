#!/usr/bin/env python3
"""
Prépare la carte « Sens uniques et parcours traversants » du Plateau-Mont-Royal
à partir de la Géobase de la Ville de Montréal.

Le calcul des parcours traversants se refait dans le navigateur (index.html,
fonction analyser()) parce qu'on peut y choisir les collectrices à traiter
comme des artères. Ce script :
  1. exporte le réseau nécessaire (data/reseau.json) ;
  2. fait le même calcul pour le réglage par défaut (DEFAUT_COMME_ARTERES) et
     écrit les totaux dans data/resume.json : la page doit afficher exactement
     ces chiffres avec ce réglage (contrôle).

Source :
  « Géobase - réseau routier », Ville de Montréal, CC BY 4.0
  https://donnees.montreal.ca/dataset/geobase
  Ressource GeoJSON (~43 Mo) : NE PAS la commiter.
  Champs utilisés : ID_TRC, CLASSE, SENS_CIR, TYP_VOIE, LIE_VOIE, NOM_VOIE,
  ARR_GCH, ARR_DRT.
  SENS_CIR : 0 = double sens, 1 = sens du tracé, -1 = sens inverse du tracé
  (vérifié sur le boulevard Saint-Laurent, vers le nord, et la rue
  Saint-Urbain, vers le sud).

Règle (choix de Gabriel, détails dans ../NOTES.md) :
  - « Artères » = CLASSE 6 à 8, plus les collectrices cochées dans la page
    (aucune par défaut). Une voie est identifiée par TYP_VOIE + LIE_VOIE + NOM_VOIE
    (sans DIR_VOIE : « Mont-Royal Est » et « Ouest » sont la même avenue).
  - Cellule = îlot délimité par les artères seulement : rues locales et
    autres collectrices reliées par des nœuds qui ne touchent pas une artère.
    Les voies où l'on ne roule pas (CLASSE 1 à 4 et 9) et les rues comptées
    comme ruelles, au Plateau, relient aussi les parties d'une cellule
    (ex. Prince-Arthur piétonne), sans servir de passage.
  - On ne roule « à l'intérieur » que sur les rues locales (CLASSE 0). Un
    nœud qui touche une collectrice ou une artère (CLASSE 5 à 8) est une
    porte : un parcours y commence ou s'y arrête, sans la traverser.
    Exception : à un carrefour avec une collectrice non cochée (sans
    artère), on traverse tout droit, c.-à-d. une rue locale y continue sur la
    rue du même nom (on n'y tourne pas).
  - Parcours TRAVERSANT : entre par une artère X et ressort par une autre
    artère Y (X ≠ Y). Ressortir sur une collectrice (non cochée) est
    acceptable, ex. une rue tête-bêche qui oblige à y tourner.
  - Pour une paire (X, Y) : entrées = portes sur X mais pas sur Y ; sorties
    = portes sur Y mais pas sur X. Un arc u → v est sur un parcours
    traversant si u est une entrée ou un nœud intérieur atteignable depuis
    une entrée, et si v est une sortie ou un nœud intérieur depuis lequel une
    sortie est atteignable.
  - Artères parallèles (DEFAUT_PARALLELES, case dans la page) : une paire
    (X, Y) n'est examinée que si X et Y sont parallèles (deux est-ouest ou
    deux nord-sud). Orientation = moyenne, en angle doublé, des tronçons de
    l'artère qui touchent les portes de la cellule (tracé de bout en bout,
    longitude × cos(latitude)) ; parallèles si l'écart est de moins de 45°.
  - Artères comptées comme rues locales (DEFAUT_ARTERES_LOCALES, cases dans
    la page) : leurs tronçons d'artère au Plateau sont traités comme des rues
    locales (CLASSE 0).
  - Paires artérielles (DEFAUT_PAIRES, case dans la page) : une paire (X, Y)
    de PAIRES_ARTERIELLES (une artère vers le nord, l'autre vers le sud)
    n'est pas examinée : une rue locale peut les relier d'est en ouest.
  - Virages maximaux (DEFAUT_VIRAGES, curseur dans la page) : un parcours ne
    compte que s'il change de rue locale (nom différent) au plus ce nombre de
    fois ; entrer et ressortir ne comptent pas. Un arc compte si virages
    minimaux depuis une entrée jusqu'à lui + virages minimaux de lui jusqu'à
    une sortie ≤ maximum.
  - Statut d'une rue locale : 0 sens unique sans parcours traversant (vert),
    1 sens unique traversant (rouge), 2 double sens sans parcours
    traversant, 3 double sens traversant.

Noms des cellules (noms_automatiques(), même méthode que la page) : les
  cellules qui portent le même nom choisi dans data/noms-cellules.json sont
  regroupées, pour le compte et l'affichage.

Rues isolées : une cellule qui ne contient qu'une seule rue locale (un seul
  nom) est regroupée avec les autres sous ISOLEES, qui ne compte pas comme
  une cellule (ses tronçons restent comptés) ; les parcours sont calculés
  dans la vraie cellule.

Raccords (RACCORDS) : petits tronçons ajoutés où la Géobase coupe une rue
  continue (rue Clark à Bagg et à Saint-Cuthbert : deux nœuds à ~8 m, sans
  tronçon entre eux). Identifiant négatif dans l'export.

Rues locales traitées comme des ruelles (DEFAUT_RUELLES, décochables dans la
  page) : retirées du calcul comme les autres voies qui ne servent pas de
  passage, et non comptées.

Scénario « Mont-Royal piétonne » (case dans la page, décochée par défaut) :
  les tronçons de l'avenue du Mont-Royal entre le boulevard Saint-Laurent et
  l'avenue De Lorimier (champ `pieton` de l'export) sont retirés du réseau.
  On ne peut plus y rouler ni y tourner, et ce ne sont plus des portes ; les
  rues qui la croisent restent reliées au carrefour (on la traverse du nord au
  sud). Un carrefour avec une artère reste une porte.

Export : les cellules délimitées par les artères de CLASSE 6 à 8 seulement
sont les plus grandes possibles (cocher une collectrice ne peut que les
découper). On exporte donc les tronçons du Plateau, ceux de ces cellules qui
touchent le Plateau, et les collectrices et artères qui touchent leurs nœuds
(pour les portes et les noms) : le calcul du navigateur est exact pour tout
réglage.

Sorties (dans ../data/) :
  reseau.json   {"noms": [...], "troncons": [[...], ...]}, format dans
                ../index.html (constante T) et ../NOTES.md
  resume.json   totaux du Plateau avec le réglage par défaut (contrôle)
  meta.json     date de préparation et version de la source

Usage (date « Dernière modification des données » de la ressource) :
    python3 preparer_sens_uniques.py chemin/geobase.json 2026-11-04
"""
import collections
import datetime
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

ICI = Path(__file__).resolve().parent
SORTIE = ICI.parent / "data"

LOCALE = 0
COLLECTRICE = 5
ARTERES = {6, 7, 8}
NON_CARROSSABLES = {1, 2, 3, 4, 9}   # voies où l'on ne roule pas : liens entre parties d'une cellule
PORTES = {5, 6, 7, 8}
MONT_ROYAL = ("avenue", "Mont-Royal")
MONT_ROYAL_BOUTS = ("Saint-Laurent", "De Lorimier")   # rues qui bornent le tronçon piéton
DEFAUT_COMME_ARTERES = set()   # collectrices traitées comme des artères par défaut (aucune)
DEFAUT_PARALLELES = True       # parcours traversant seulement entre artères parallèles (case cochée par défaut)
DEFAUT_VIRAGES = 3             # virages maximaux d'un parcours traversant (curseur de la page) ; None = sans limite
# Rues locales que Gabriel considère comme des ruelles (par défaut, retirées du calcul)
DEFAUT_RUELLES = {"Rue Généreux", "Rue De Varennes", "Rue Simard", "Rue Barrette",
                  "Rue La Mennais", "Rue Latreille", "Rue De Courville", "Avenue Bureau",
                  "Rue Lionais", "Rue Saint-Christophe"}
# Artères traitées comme des rues locales au Plateau (cases cochées par défaut dans la page)
DEFAUT_ARTERES_LOCALES = {"Rue Jeanne-Mance", "Rue Léo-Pariseau"}
DEFAUT_PAIRES = True           # exception des paires artérielles (case cochée par défaut)
# Paires artérielles (une vers le nord, l'autre vers le sud) : une rue locale peut les relier
PAIRES_ARTERIELLES = [("Avenue De Lorimier", "Avenue Papineau"), ("Boulevard Saint-Laurent", "Rue Saint-Urbain"),
                      ("Rue Frontenac", "Rue D'Iberville")]
# Raccords : tronçons ajoutés là où la Géobase coupe une rue continue (deux nœuds à quelques mètres, sans
# tronçon entre eux). (voie, [lng, lat] de départ, [lng, lat] d'arrivée), dans le sens de la circulation.
RACCORDS = [
    ("Rue Clark", [-73.578903, 45.515958], [-73.578804, 45.515991]),   # Clark coupée à Bagg (~8 m)
    ("Rue Clark", [-73.577695, 45.515512], [-73.577651, 45.515445]),   # Clark coupée à Saint-Cuthbert (~8 m)
]
MAX_PAIRES = 6
ISOLEES = "isolees"            # cellule commune des cellules d'une seule rue locale
ARRONDISSEMENT = "le-plateau-mont-royal"


def slugify(nom):
    n = unicodedata.normalize("NFKD", nom).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", n.lower()).strip("-")


def cle_noeud(c):
    return (round(c[0], 7), round(c[1], 7))


def nom_voie(p):
    morceaux = [p["TYP_VOIE"], p["LIE_VOIE"], p["NOM_VOIE"]]
    nom = " ".join(m.strip() for m in morceaux if m and m.strip())
    nom = nom.replace("' ", "'")   # LIE_VOIE « l' » ou « d' » suivi du nom
    return nom[:1].upper() + nom[1:] if nom else None


class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        racine = x
        while self.parent[racine] != racine:
            racine = self.parent[racine]
        while self.parent[x] != racine:
            self.parent[x], x = racine, self.parent[x]
        return racine

    def union(self, a, b):
        self.parent[self.find(a)] = self.find(b)


def est_artere(t, comme_arteres):
    return t["classe"] in ARTERES or (t["classe"] == COLLECTRICE and t["voie"] in comme_arteres)


def comme_locales(troncons, noms=DEFAUT_ARTERES_LOCALES):
    """Copie de la liste où les tronçons d'artère du Plateau nommés dans `noms` sont des rues locales."""
    return [dict(t, classe=LOCALE) if t["plateau"] and t["classe"] in ARTERES and t["voie"] in noms else t
            for t in troncons]


def ajouter_raccords(troncons):
    """Ajoute les RACCORDS : tronçon local à sens unique entre deux extrémités de tronçon existantes
    (à moins de 2 m des coordonnées données). S'arrête si une extrémité est introuvable."""
    def noeud(c):
        meilleur = None
        for t in troncons:
            for q, n in ((t["coords"][0], t["a"]), (t["coords"][-1], t["b"])):
                d = math.hypot((q[0] - c[0]) * 111320 * math.cos(math.radians(c[1])), (q[1] - c[1]) * 110574)
                if d < 2 and (meilleur is None or d < meilleur[0]):
                    meilleur = (d, n, q)
        if meilleur is None:
            sys.exit(f"Raccord : aucun nœud près de {c}")
        return meilleur[1], meilleur[2]
    for k, (voie, de, a) in enumerate(RACCORDS):
        na, qa = noeud(de)
        nb, qb = noeud(a)
        if not any(t["voie"] == voie and n in (t["a"], t["b"]) for t in troncons for n in (na, nb)):
            sys.exit(f"Raccord : {voie} ne touche pas ses deux nœuds")
        troncons.append({"id": -(k + 1), "classe": LOCALE, "sens": 1, "voie": voie, "coords": [qa, qb],
                         "typ": None, "nom": None, "a": na, "b": nb, "plateau": True})


def liens_cellules(troncons, ruelles=DEFAUT_RUELLES):
    """Voies où l'on ne roule pas (CLASSE 1 à 4 et 9, rues comptées comme ruelles), au Plateau : elles
    relient les parties d'une même cellule (ex. Prince-Arthur piétonne), sans servir de passage."""
    return [t for t in troncons if t["plateau"]
            and (t["classe"] in NON_CARROSSABLES or (t["classe"] == LOCALE and t["voie"] in ruelles))]


def cellules(troncons, comme_arteres, liens=()):
    """Liste de cellules (listes d'index) : rues locales et collectrices non cochées,
    reliées par des nœuds qui ne touchent pas une artère, ou par un des `liens`."""
    noeuds_artere = set()
    for t in troncons:
        if est_artere(t, comme_arteres):
            noeuds_artere.update((t["a"], t["b"]))
    uf = UnionFind()
    idx = [i for i, t in enumerate(troncons)
           if t["classe"] == LOCALE or (t["classe"] == COLLECTRICE and not est_artere(t, comme_arteres))]
    for i in idx:
        t = troncons[i]
        uf.find(("t", i))
        for n in (t["a"], t["b"]):
            if n not in noeuds_artere:
                uf.union(("t", i), ("n", n))
    for t in liens:
        if t["a"] not in noeuds_artere and t["b"] not in noeuds_artere:
            uf.union(("n", t["a"]), ("n", t["b"]))
    groupes = collections.defaultdict(list)
    for i in idx:
        groupes[uf.find(("t", i))].append(i)
    return list(groupes.values())


def parcourir(depart, voisins, portes):
    """Nœuds atteignables depuis `depart` ; une porte atteinte n'est pas dépassée."""
    vus = set(depart)
    pile = list(depart)
    while pile:
        n = pile.pop()
        if n in portes and n not in depart:
            continue
        for m in voisins.get(n, ()):
            if m not in vus:
                vus.add(m)
                pile.append(m)
    return vus


def virages(arcs, suivants, est_depart, portes, c_depart, c_suivant):
    """Virages minimaux, par arc (index), depuis un nœud de départ (entrée en avant, sortie en arrière).
    c_depart / c_suivant : extrémité de l'arc côté départ / côté suivant (0 = u, 1 = v). Un parcours
    ne dépasse pas une porte qui n'est pas un départ. Parcours en largeur 0-1 (coût 1 si le nom change)."""
    best = [math.inf] * len(arcs)
    file = collections.deque()
    for i, a in enumerate(arcs):
        if est_depart(a[c_depart]):
            best[i] = 0
            file.append(i)
    while file:
        i = file.popleft()
        n = arcs[i][c_suivant]
        if n in portes:
            continue
        nom_i = arcs[i][3]
        for j in suivants.get(n, ()):
            c = best[i] + (0 if nom_i is not None and arcs[j][3] == nom_i else 1)
            if c < best[j]:
                best[j] = c
                if c == best[i]:
                    file.appendleft(j)
                else:
                    file.append(j)
    return best


def analyser(troncons, comme_arteres, paralleles=DEFAUT_PARALLELES, max_virages=DEFAUT_VIRAGES,
             paires_arterielles=DEFAUT_PAIRES, liens=()):
    """{index: (statut, cellule, paires limitées, nombre de paires)} ; statut -1 pour les collectrices de cellule."""
    portes = set()
    arteres_au = collections.defaultdict(set)
    # Orientation des artères à chaque nœud, en angle doublé (les deux sens d'une droite s'additionnent)
    dir_au = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0, 0.0]))
    for t in troncons:
        if t["classe"] in PORTES:
            artere = est_artere(t, comme_arteres)
            if artere:
                (x0, y0), (x1, y1) = t["coords"][0][:2], t["coords"][-1][:2]
                a = 2 * math.atan2(y1 - y0, (x1 - x0) * math.cos(math.radians(y0)))
            for n in (t["a"], t["b"]):
                portes.add(n)
                if artere:
                    nom = t["voie"] or f"#{t['id']}"
                    arteres_au[n].add(nom)
                    v = dir_au[n][nom]
                    v[0] += math.cos(a)
                    v[1] += math.sin(a)

    resultat = {}
    for num, tous in enumerate(cellules(troncons, comme_arteres, liens)):
        membres = [i for i in tous if troncons[i]["classe"] == LOCALE]
        # Cellule d'une seule rue locale (un seul nom) : regroupée avec les autres dans « Rues isolées »
        # (pour le compte et l'affichage ; les parcours restent calculés dans la vraie cellule)
        if len({troncons[i]["voie"] for i in membres}) == 1:
            num = ISOLEES
        for i in tous:
            if troncons[i]["classe"] == COLLECTRICE:
                resultat[i] = (-1, num, [], 0)

        def noeud(n, t):
            # Carrefour avec une collectrice non cochée (porte sans artère) : on le traverse tout droit,
            # c.-à-d. la rue ne se raccorde qu'à elle-même (même nom) ; on n'y tourne pas
            if n in portes and n not in arteres_au:
                return (n, t["voie"] or f"#{t['id']}")
            return n

        arcs = []
        for i in membres:
            t = troncons[i]
            a, b = noeud(t["a"], t), noeud(t["b"], t)
            if t["sens"] in (0, 1):
                arcs.append((a, b, i, t["voie"]))
            if t["sens"] in (0, -1):
                arcs.append((b, a, i, t["voie"]))
        sortants = collections.defaultdict(list)
        entrants = collections.defaultdict(list)
        sortants_i = collections.defaultdict(list)
        entrants_i = collections.defaultdict(list)
        for k, (u, v, _, _) in enumerate(arcs):
            sortants[u].append(v)
            entrants[v].append(u)
            sortants_i[u].append(k)
            entrants_i[v].append(k)
        portes_art = {n for i in membres for n in (troncons[i]["a"], troncons[i]["b"]) if arteres_au.get(n)}
        noms = sorted(set().union(*(arteres_au[n] for n in portes_art))) if portes_art else []
        angle = {}
        for nom in noms:
            x = sum(dir_au[n][nom][0] for n in portes_art if nom in dir_au[n])
            y = sum(dir_au[n][nom][1] for n in portes_art if nom in dir_au[n])
            angle[nom] = math.atan2(y, x)

        def sont_paralleles(x, y):
            d = abs(angle[x] - angle[y]) % (2 * math.pi)
            return min(d, 2 * math.pi - d) < math.pi / 2   # angle doublé : π/2 = 45° d'écart réel

        traversant = collections.defaultdict(list)
        for x in noms:
            for y in noms:
                if x == y or (paralleles and not sont_paralleles(x, y)):
                    continue
                if paires_arterielles and ((x, y) in PAIRES_ARTERIELLES or (y, x) in PAIRES_ARTERIELLES):
                    continue
                entrees = {n for n in portes_art if x in arteres_au[n] and y not in arteres_au[n]}
                sorties = {n for n in portes_art if y in arteres_au[n] and x not in arteres_au[n]}
                if not entrees or not sorties:
                    continue
                avant = parcourir(entrees, sortants, portes)
                if not avant & sorties:
                    continue
                if max_virages is None:
                    arriere = parcourir(sorties, entrants, portes)
                    depart_ok = {n for n in avant if n in entrees or n not in portes}
                    arrivee_ok = {n for n in arriere if n in sorties or n not in portes}
                    sur = [u in depart_ok and v in arrivee_ok for u, v, _, _ in arcs]
                else:
                    avant_v = virages(arcs, sortants_i, entrees.__contains__, portes, 0, 1)
                    apres_v = virages(arcs, entrants_i, sorties.__contains__, portes, 1, 0)
                    sur = [a + b <= max_virages for a, b in zip(avant_v, apres_v)]
                for (u, v, i, _), ok in zip(arcs, sur):
                    if ok and (x, y) not in traversant[i]:
                        traversant[i].append((x, y))
        for i in membres:
            sur = bool(traversant.get(i))
            statut = (1 if sur else 0) if troncons[i]["sens"] != 0 else (3 if sur else 2)
            paires = traversant.get(i, [])
            resultat[i] = (statut, num, paires[:MAX_PAIRES], len(paires))
    return resultat


NORD_MTL = math.radians(147)   # direction des artères nord-sud au Plateau, depuis l'est


def longueur_m(coords):
    """Longueur en mètres (haversine, R = 6 371 000 m, comme Leaflet dans la page)."""
    m = 0.0
    for (x0, y0), (x1, y1) in zip(coords, coords[1:]):
        p0, p1 = math.radians(y0), math.radians(y1)
        a = math.sin((p1 - p0) / 2) ** 2 + math.cos(p0) * math.cos(p1) * math.sin(math.radians(x1 - x0) / 2) ** 2
        m += 2 * 6371000 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return m


def nom_court(nom):
    return re.sub(r"^(Rue|Avenue|Boulevard|Chemin|Place|Terrasse|Voie) ", "", nom)


def noms_automatiques(troncons, resultat, comme_arteres, liens):
    """{cellule: nom automatique} des cellules qui ont une rue locale au Plateau (même méthode que
    nommerCellules() dans la page) : artères qui bordent la cellule, dans l'ordre nord, est, sud, ouest ;
    moins de 3 artères : la plus longue rue locale au Plateau, puis les artères entre parenthèses."""
    cell_de = {i: r[1] for i, r in resultat.items()}
    ordre, au_plateau = [], set()
    for i, t in enumerate(troncons):
        if i in cell_de and t["classe"] == LOCALE:
            if cell_de[i] not in ordre:
                ordre.append(cell_de[i])
            if t["plateau"]:
                au_plateau.add(cell_de[i])
    arteres_au, coord = collections.defaultdict(set), {}
    for t in troncons:
        coord.setdefault(t["a"], t["coords"][0])
        coord.setdefault(t["b"], t["coords"][-1])
        if est_artere(t, comme_arteres):
            for n in (t["a"], t["b"]):
                arteres_au[n].add(t["voie"] or f"#{t['id']}")
    cellule_au = {}
    for i, t in enumerate(troncons):
        if i in cell_de:
            for n in (t["a"], t["b"]):
                if n not in arteres_au and n not in cellule_au:
                    cellule_au[n] = cell_de[i]
    change = True
    while change:
        change = False
        for t in liens:
            a, b = t["a"], t["b"]
            if a in arteres_au or b in arteres_au:
                continue
            if a in cellule_au and b not in cellule_au:
                cellule_au[b] = cellule_au[a]
                change = True
            elif b in cellule_au and a not in cellule_au:
                cellule_au[a] = cellule_au[b]
                change = True
    portes = collections.defaultdict(dict)   # cellule -> nœuds (dict : ordre d'insertion)
    centres = collections.defaultdict(lambda: [0.0, 0.0, 0])
    longueurs = collections.defaultdict(dict)
    for i, t in enumerate(troncons):
        if i not in cell_de or t["classe"] != LOCALE:
            continue
        c = cell_de[i]
        for n in (t["a"], t["b"]):
            if n in arteres_au:
                portes[c][n] = True
        m = t["coords"][len(t["coords"]) // 2]
        centres[c][0] += m[0]
        centres[c][1] += m[1]
        centres[c][2] += 1
        if t["plateau"] and t["voie"]:
            longueurs[c][t["voie"]] = longueurs[c].get(t["voie"], 0) + longueur_m(t["coords"])
    for t in liens:
        a, b = t["a"], t["b"]
        if (a in arteres_au) == (b in arteres_au):
            continue
        na, ni = (a, b) if a in arteres_au else (b, a)
        if ni in cellule_au:
            portes[cellule_au[ni]][na] = True

    def cap(v):
        return ((NORD_MTL - math.atan2(v[1], v[0]) + math.pi / 4) % (2 * math.pi) + 2 * math.pi) % (2 * math.pi)

    autos, vus = {}, collections.Counter()
    for c in ordre:
        if c not in au_plateau:
            continue
        if c == ISOLEES:
            autos[c] = "Rues isolées"
            continue
        x, y, k = centres[c]
        lng0, lat0 = x / k, y / k
        kx = math.cos(math.radians(lat0))
        pos = {}
        for n in portes[c]:
            q = coord[n]
            for a in sorted(arteres_au[n]):
                v = pos.setdefault(a, [0.0, 0.0])
                v[0] += (q[0] - lng0) * kx
                v[1] += q[1] - lat0
        auto = " / ".join(nom_court(a) for a, v in sorted(pos.items(), key=lambda av: cap(av[1])))
        if len(pos) < 3:
            rues = sorted(longueurs[c].items(), key=lambda kv: -kv[1])
            if rues:
                auto = nom_court(rues[0][0]) + (f" ({auto})" if auto else "")
            elif not auto:
                auto = "Cellule sans artère"
        vus[auto] += 1
        if vus[auto] > 1:
            auto += f" ({vus[auto]})"
        autos[c] = auto
    return autos


def regrouper_par_nom(resultat, autos, noms_choisis):
    """Cellules qui portent le même nom (choisi dans data/noms-cellules.json, sinon automatique) :
    regroupées dans la première (compte et affichage ; les parcours restent ceux de chaque cellule)."""
    par_nom, vers = {}, {}
    for c, auto in autos.items():
        nom = noms_choisis.get(auto) or auto
        if nom in par_nom:
            vers[c] = par_nom[nom]
        else:
            par_nom[nom] = c
    return {i: (r[0], vers.get(r[1], r[1]), *r[2:]) for i, r in resultat.items()}


def charger_noms_choisis():
    f = SORTIE / "noms-cellules.json"
    return json.load(open(f, encoding="utf-8")).get("noms", {}) if f.exists() else {}


def totaux(troncons, resultat):
    statuts = collections.Counter()
    cells, traversantes = set(), set()
    for i, t in enumerate(troncons):
        r = resultat.get(i)
        if not t["plateau"] or t["classe"] != LOCALE or not r:
            continue
        statuts[r[0]] += 1
        if r[1] == ISOLEES:          # rues isolées : comptées parmi les tronçons, pas comme une cellule
            continue
        cells.add(r[1])
        if r[0] in (1, 3):
            traversantes.add(r[1])
    return {
        "troncons_locaux_par_statut": {str(s): n for s, n in sorted(statuts.items())},
        "cellules": len(cells),
        "cellules_traversantes": len(traversantes),
    }


def marquer_mont_royal_pieton(troncons):
    """Marque t["pieton"] pour les tronçons de l'avenue du Mont-Royal entre Saint-Laurent et
    De Lorimier : milieu du tronçon projeté entre les deux carrefours, à moins de 40 m de l'axe."""
    sur_mr = [t for t in troncons if (t["typ"], t["nom"]) == MONT_ROYAL]
    noeuds_mr = {n for t in sur_mr for n in (t["a"], t["b"])}
    bouts = []
    for nom_bout in MONT_ROYAL_BOUTS:
        trouves = {n for t in troncons if t["nom"] == nom_bout for n in (t["a"], t["b"]) if n in noeuds_mr}
        if len(trouves) != 1:
            sys.exit(f"Carrefour Mont-Royal / {nom_bout} introuvable ou ambigu : {trouves}")
        bouts.append(trouves.pop())
    (x0, y0), (x1, y1) = bouts
    kx = 111320 * 0.70   # mètres par degré de longitude vers 45,5° de latitude (cos ≈ 0,70)
    ky = 110574
    ax, ay = (x1 - x0) * kx, (y1 - y0) * ky
    l2 = ax * ax + ay * ay
    for t in troncons:
        t["pieton"] = False
    for t in sur_mr:
        mx = (t["coords"][0][0] + t["coords"][-1][0]) / 2
        my = (t["coords"][0][1] + t["coords"][-1][1]) / 2
        px, py = (mx - x0) * kx, (my - y0) * ky
        u = (px * ax + py * ay) / l2
        dist = abs(px * ay - py * ax) / l2 ** 0.5
        if 0 <= u <= 1 and dist < 40:
            t["pieton"] = True
    n = sum(t["pieton"] for t in troncons)
    if not n:
        sys.exit("Aucun tronçon de Mont-Royal marqué piéton")
    return n


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    source = Path(sys.argv[1]).expanduser()
    version_source = datetime.date.fromisoformat(sys.argv[2]).isoformat()

    troncons = []
    for f in json.load(open(source, encoding="utf-8"))["features"]:
        p = f["properties"]
        coords = f["geometry"]["coordinates"]
        if f["geometry"]["type"] != "LineString" or len(coords) < 2:
            sys.exit(f"Géométrie inattendue : tronçon {p['ID_TRC']}")
        if p["SENS_CIR"] not in (0, 1, -1):
            sys.exit(f"SENS_CIR inattendu : {p['SENS_CIR']!r} (tronçon {p['ID_TRC']})")
        arrs = {slugify(a) for a in (p["ARR_GCH"], p["ARR_DRT"]) if a and a != "N/A"}
        troncons.append({
            "id": p["ID_TRC"], "classe": p["CLASSE"], "sens": p["SENS_CIR"],
            "voie": nom_voie(p), "coords": coords, "typ": p["TYP_VOIE"], "nom": p["NOM_VOIE"],
            "a": cle_noeud(coords[0]), "b": cle_noeud(coords[-1]),
            "plateau": ARRONDISSEMENT in arrs,
        })
    if not any(t["plateau"] for t in troncons):
        sys.exit(f"Aucun tronçon pour {ARRONDISSEMENT} : vérifier ARR_GCH / ARR_DRT")
    ajouter_raccords(troncons)
    print(f"{len(troncons)} tronçons ; {marquer_mont_royal_pieton(troncons)} tronçons de Mont-Royal piétonne", file=sys.stderr)

    # Tronçons à exporter
    garder = {i for i, t in enumerate(troncons) if t["plateau"]}
    # Cellules les plus grandes possibles : artères locales par défaut comprises (décocher ne peut que découper)
    for groupe in cellules(comme_locales(troncons), set(), liens_cellules(troncons, set())):
        if any(troncons[i]["plateau"] for i in groupe):
            garder.update(groupe)
    noeuds = {n for i in garder for n in (troncons[i]["a"], troncons[i]["b"])}
    for i, t in enumerate(troncons):
        if t["classe"] in PORTES and (t["a"] in noeuds or t["b"] in noeuds):
            garder.add(i)
    sous_ensemble = [troncons[i] for i in sorted(garder)]

    for nom in DEFAUT_ARTERES_LOCALES:
        if not any(t["voie"] == nom and t["classe"] in ARTERES and t["plateau"] for t in troncons):
            sys.exit(f"Artère comptée comme locale introuvable au Plateau : {nom}")
    for nom in DEFAUT_RUELLES:
        if not any(t["voie"] == nom and t["classe"] == LOCALE and t["plateau"] for t in troncons):
            sys.exit(f"Ruelle par défaut introuvable au Plateau : {nom}")

    for paire in PAIRES_ARTERIELLES:
        for nom in paire:
            if not any(t["voie"] == nom and t["classe"] in ARTERES and t["plateau"] for t in troncons):
                sys.exit(f"Artère d'une paire introuvable au Plateau : {nom}")

    def calcul(liste, pieton):
        liste = comme_locales(liste)
        # Réglage par défaut : ruelles retirées, Mont-Royal piétonne si demandé
        garde = [t for t in liste if not (t["classe"] == LOCALE and t["voie"] in DEFAUT_RUELLES)
                 and not (pieton and t["pieton"])]
        liens = liens_cellules(liste)
        res = analyser(garde, DEFAUT_COMME_ARTERES, liens=liens)
        # Noms des cellules et regroupement des cellules de même nom (comme la page)
        res = regrouper_par_nom(res, noms_automatiques(garde, res, DEFAUT_COMME_ARTERES, liens), charger_noms_choisis())
        return totaux(garde, res)

    # Références, calculées sur le sous-ensemble exporté ET sur toute l'île
    ref = calcul(sous_ensemble, False)
    if ref != calcul(troncons, False):
        sys.exit("L'export ne suffit pas au calcul (réglage par défaut)")
    ref_pieton = calcul(sous_ensemble, True)
    if ref_pieton != calcul(troncons, True):
        sys.exit("L'export ne suffit pas au calcul du scénario Mont-Royal piétonne")

    noms, ids_noeuds = {}, {}

    def nom_idx(nom):
        if nom is None:
            return -1
        return noms.setdefault(nom, len(noms))

    def noeud_idx(n):
        return ids_noeuds.setdefault(n, len(ids_noeuds))

    rangees = []
    for t in sous_ensemble:
        a, b, coords = t["a"], t["b"], t["coords"]
        if t["sens"] == -1:                       # tout remettre dans le sens de la circulation
            a, b, coords = b, a, coords[::-1]
        rangees.append([
            t["id"], [[round(c[0], 6), round(c[1], 6)] for c in coords], t["classe"],
            1 if t["sens"] != 0 else 0, nom_idx(t["voie"]),
            noeud_idx(a), noeud_idx(b), 1 if t["plateau"] else 0, 1 if t["pieton"] else 0,
        ])
    table = [None] * len(noms)
    for nom, j in noms.items():
        table[j] = nom

    SORTIE.mkdir(exist_ok=True)
    (SORTIE / "troncons.json").unlink(missing_ok=True)   # ancien format
    with open(SORTIE / "reseau.json", "w", encoding="utf-8") as f:
        json.dump({"noms": table, "troncons": rangees}, f, ensure_ascii=False, separators=(",", ":"))
    resume = {"reglage_par_defaut": {"collectrices_comme_arteres": sorted(DEFAUT_COMME_ARTERES),
                                     "arteres_paralleles_seulement": DEFAUT_PARALLELES,
                                     "virages_maximaux": DEFAUT_VIRAGES,
                                     "arteres_locales": sorted(DEFAUT_ARTERES_LOCALES),
                                     "paires_arterielles": [list(p) for p in PAIRES_ARTERIELLES] if DEFAUT_PAIRES else [],
                                     "ruelles": sorted(DEFAUT_RUELLES)},
              "troncons_exportes": len(rangees),
              "troncons_plateau": sum(1 for t in sous_ensemble if t["plateau"]), **ref,
              "mont_royal_pieton": {"troncons_retires": sum(1 for t in sous_ensemble if t["pieton"]), **ref_pieton}}
    with open(SORTIE / "resume.json", "w", encoding="utf-8") as f:
        json.dump(resume, f, ensure_ascii=False, indent=1)
    with open(SORTIE / "meta.json", "w", encoding="utf-8") as f:
        json.dump({"donneesMisesAJour": datetime.date.today().isoformat(),
                   "versionSource": version_source,
                   "collectricesCommeArteres": sorted(DEFAUT_COMME_ARTERES),
                   "arteresParallelesSeulement": DEFAUT_PARALLELES,
                   "viragesMaximaux": DEFAUT_VIRAGES,
                   "arteresLocales": sorted(DEFAUT_ARTERES_LOCALES),
                   "pairesArterielles": [list(p) for p in PAIRES_ARTERIELLES] if DEFAUT_PAIRES else [],
                   "ruelles": sorted(DEFAUT_RUELLES)}, f, ensure_ascii=False, indent=1)
    json.dump(resume, sys.stderr, ensure_ascii=False, indent=1)
    print(file=sys.stderr)


if __name__ == "__main__":
    main()
