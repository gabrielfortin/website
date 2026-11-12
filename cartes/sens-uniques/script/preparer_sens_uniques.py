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
  - On ne roule « à l'intérieur » que sur les rues locales (CLASSE 0). Un
    nœud qui touche une collectrice ou une artère (CLASSE 5 à 8) est une
    porte : un parcours y commence ou s'y arrête, sans la traverser.
  - Parcours TRAVERSANT : entre par une artère X et ressort par une autre
    artère Y (X ≠ Y). Ressortir sur une collectrice (non cochée) est
    acceptable, ex. une rue tête-bêche qui oblige à y tourner.
  - Pour une paire (X, Y) : entrées = portes sur X mais pas sur Y ; sorties
    = portes sur Y mais pas sur X. Un arc u → v est sur un parcours
    traversant si u est une entrée ou un nœud intérieur atteignable depuis
    une entrée, et si v est une sortie ou un nœud intérieur depuis lequel une
    sortie est atteignable.
  - Statut d'une rue locale : 0 sens unique sans parcours traversant (vert),
    1 sens unique traversant (rouge), 2 double sens sans parcours
    traversant, 3 double sens traversant.

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
import re
import sys
import unicodedata
from pathlib import Path

ICI = Path(__file__).resolve().parent
SORTIE = ICI.parent / "data"

LOCALE = 0
COLLECTRICE = 5
ARTERES = {6, 7, 8}
PORTES = {5, 6, 7, 8}
DEFAUT_COMME_ARTERES = set()   # collectrices traitées comme des artères par défaut (aucune)
MAX_PAIRES = 6
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


def cellules(troncons, comme_arteres):
    """Liste de cellules (listes d'index) : rues locales et collectrices non cochées,
    reliées par des nœuds qui ne touchent pas une artère."""
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


def analyser(troncons, comme_arteres):
    """{index: (statut, cellule, paires limitées, nombre de paires)} ; statut -1 pour les collectrices de cellule."""
    portes = set()
    arteres_au = collections.defaultdict(set)
    for t in troncons:
        if t["classe"] in PORTES:
            for n in (t["a"], t["b"]):
                portes.add(n)
                if est_artere(t, comme_arteres):
                    arteres_au[n].add(t["voie"] or f"#{t['id']}")

    resultat = {}
    for num, tous in enumerate(cellules(troncons, comme_arteres)):
        for i in tous:
            if troncons[i]["classe"] == COLLECTRICE:
                resultat[i] = (-1, num, [], 0)
        membres = [i for i in tous if troncons[i]["classe"] == LOCALE]
        arcs = []
        for i in membres:
            t = troncons[i]
            if t["sens"] in (0, 1):
                arcs.append((t["a"], t["b"], i))
            if t["sens"] in (0, -1):
                arcs.append((t["b"], t["a"], i))
        sortants = collections.defaultdict(list)
        entrants = collections.defaultdict(list)
        for u, v, _ in arcs:
            sortants[u].append(v)
            entrants[v].append(u)
        portes_art = {n for i in membres for n in (troncons[i]["a"], troncons[i]["b"]) if arteres_au.get(n)}
        noms = sorted(set().union(*(arteres_au[n] for n in portes_art))) if portes_art else []

        traversant = collections.defaultdict(list)
        for x in noms:
            for y in noms:
                if x == y:
                    continue
                entrees = {n for n in portes_art if x in arteres_au[n] and y not in arteres_au[n]}
                sorties = {n for n in portes_art if y in arteres_au[n] and x not in arteres_au[n]}
                if not entrees or not sorties:
                    continue
                avant = parcourir(entrees, sortants, portes)
                if not avant & sorties:
                    continue
                arriere = parcourir(sorties, entrants, portes)
                depart_ok = {n for n in avant if n in entrees or n not in portes}
                arrivee_ok = {n for n in arriere if n in sorties or n not in portes}
                for u, v, i in arcs:
                    if u in depart_ok and v in arrivee_ok and (x, y) not in traversant[i]:
                        traversant[i].append((x, y))
        for i in membres:
            sur = bool(traversant.get(i))
            statut = (1 if sur else 0) if troncons[i]["sens"] != 0 else (3 if sur else 2)
            paires = traversant.get(i, [])
            resultat[i] = (statut, num, paires[:MAX_PAIRES], len(paires))
    return resultat


def totaux(troncons, resultat):
    statuts = collections.Counter()
    cells, traversantes = set(), set()
    for i, t in enumerate(troncons):
        r = resultat.get(i)
        if not t["plateau"] or t["classe"] != LOCALE or not r:
            continue
        statuts[r[0]] += 1
        cells.add(r[1])
        if r[0] in (1, 3):
            traversantes.add(r[1])
    return {
        "troncons_locaux_par_statut": {str(s): n for s, n in sorted(statuts.items())},
        "cellules": len(cells),
        "cellules_traversantes": len(traversantes),
    }


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
            "voie": nom_voie(p), "coords": coords,
            "a": cle_noeud(coords[0]), "b": cle_noeud(coords[-1]),
            "plateau": ARRONDISSEMENT in arrs,
        })
    if not any(t["plateau"] for t in troncons):
        sys.exit(f"Aucun tronçon pour {ARRONDISSEMENT} : vérifier ARR_GCH / ARR_DRT")
    print(f"{len(troncons)} tronçons", file=sys.stderr)

    # Tronçons à exporter
    garder = {i for i, t in enumerate(troncons) if t["plateau"]}
    for groupe in cellules(troncons, set()):
        if any(troncons[i]["plateau"] for i in groupe):
            garder.update(groupe)
    noeuds = {n for i in garder for n in (troncons[i]["a"], troncons[i]["b"])}
    for i, t in enumerate(troncons):
        if t["classe"] in PORTES and (t["a"] in noeuds or t["b"] in noeuds):
            garder.add(i)
    sous_ensemble = [troncons[i] for i in sorted(garder)]

    # Référence : réglage par défaut, calculé sur le sous-ensemble exporté ET sur toute l'île
    ref = totaux(sous_ensemble, analyser(sous_ensemble, DEFAUT_COMME_ARTERES))
    ref_ile = totaux(troncons, analyser(troncons, DEFAUT_COMME_ARTERES))
    if ref != ref_ile:
        sys.exit(f"L'export ne suffit pas au calcul : {ref} ≠ {ref_ile}")

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
            noeud_idx(a), noeud_idx(b), 1 if t["plateau"] else 0,
        ])
    table = [None] * len(noms)
    for nom, j in noms.items():
        table[j] = nom

    SORTIE.mkdir(exist_ok=True)
    (SORTIE / "troncons.json").unlink(missing_ok=True)   # ancien format
    with open(SORTIE / "reseau.json", "w", encoding="utf-8") as f:
        json.dump({"noms": table, "troncons": rangees}, f, ensure_ascii=False, separators=(",", ":"))
    resume = {"reglage_par_defaut": sorted(DEFAUT_COMME_ARTERES), "troncons_exportes": len(rangees),
              "troncons_plateau": sum(1 for t in sous_ensemble if t["plateau"]), **ref}
    with open(SORTIE / "resume.json", "w", encoding="utf-8") as f:
        json.dump(resume, f, ensure_ascii=False, indent=1)
    with open(SORTIE / "meta.json", "w", encoding="utf-8") as f:
        json.dump({"donneesMisesAJour": datetime.date.today().isoformat(),
                   "versionSource": version_source,
                   "collectricesCommeArteres": sorted(DEFAUT_COMME_ARTERES)}, f, ensure_ascii=False, indent=1)
    json.dump(resume, sys.stderr, ensure_ascii=False, indent=1)
    print(file=sys.stderr)


if __name__ == "__main__":
    main()
