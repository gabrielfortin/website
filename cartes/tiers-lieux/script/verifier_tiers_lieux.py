#!/usr/bin/env python3
"""Vérifie data/ contre les sources (à lancer après preparer_tiers_lieux.py) :

  1. Recombine les fichiers des arrondissements : nombre de lots, de logements et d'unités par
     arrondissement = sources (unités de la Ville avec au moins un logement), géométries = sources
     arrondies à 6 décimales, aucun lot en double.
  2. Distances : une distance à pied ne peut pas être plus courte que la distance en ligne droite
     du centre du lot au lieu nommé, moins la marge d'accès (30 m). Compte les écarts.
  3. Lieux nommés : chaque identifiant de lieu d'un lot existe dans le fichier de l'arrondissement.

Code de sortie 1 s'il y a un écart.
"""

import io
import json
import os
import sys
import zipfile
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import preparer_tiers_lieux as P   # noqa: E402

DATA = P.DATA


def decoder(polys):
    out = []
    for poly in polys:
        anneaux = []
        for plat in poly:
            x = y = 0
            ring = []
            for i in range(0, len(plat), 2):
                x += plat[i]
                y += plat[i + 1]
                ring.append((x, y))
            anneaux.append(ring)
        out.append(anneaux)
    return out


def cle_source(polys):
    """Même clé que decoder() : entiers en millionièmes, points répétés de suite retirés."""
    out = []
    for poly in polys:
        anneaux = []
        for ring in poly:
            r = []
            for x, y, *_ in ring:
                q = (int(round(P.r6(x) * 1e6)), int(round(P.r6(y) * 1e6)))
                if not r or r[-1] != q:
                    r.append(q)
            anneaux.append(r)
        out.append(anneaux)
    return json.dumps(out)


def main():
    ecarts = 0
    man = json.load(open(os.path.join(DATA, "manifeste.json"), encoding="utf-8"))

    # Sources : lots et logements par arrondissement
    src = defaultdict(lambda: {"log": 0, "unites": 0, "cles": {}})
    z = zipfile.ZipFile(P.chemin("uef"))
    nom = [n for n in z.namelist() if n.endswith(".geojson")][0]
    for ligne in io.TextIOWrapper(z.open(nom), encoding="utf-8"):
        ligne = ligne.strip().rstrip(",")
        if not ligne.startswith('{ "type": "Feature"'):
            continue
        f = json.loads(ligne)
        p = f["properties"]
        if p.get("MUNICIPALITE") != "50" or int(p.get("NOMBRE_LOGEMENT") or 0) <= 0:
            continue
        a = src[p["NO_ARROND_ILE_CUM"]]
        a["log"] += int(p["NOMBRE_LOGEMENT"])
        a["unites"] += 1
        k = cle_source(P.polygones(f["geometry"]))
        a["cles"][k] = a["cles"].get(k, 0) + int(p["NOMBRE_LOGEMENT"])

    vus = set()
    viol = 0
    verifies = 0
    for e in man["arrondissements"]:
        d = json.load(open(os.path.join(DATA, "arrondissements", e["cle"] + ".json"), encoding="utf-8"))
        s = src[e["code"]]
        lots = d["lots"]
        log = sum(l[1] for l in lots)
        un = sum(l[3] for l in lots)
        if len(lots) != len(s["cles"]) or log != s["log"] or un != s["unites"]:
            print(f"ÉCART {e['nom']} : écrit {len(lots)} lots / {log} logements / {un} unités ; "
                  f"source {len(s['cles'])} / {s['log']} / {s['unites']}")
            ecarts += 1
        lieux = {t: {l[0]: l for l in d["lieux"][t]} for t in P.TYPES}
        geo_lieux = {}
        for l in lots:
            cle = json.dumps(decoder(l[0]))   # tuples écrits en listes : même forme que cle_source()
            if cle in vus:
                print(f"ÉCART lot en double : {l[2]}")
                ecarts += 1
            vus.add(cle)
            if cle not in s["cles"] or s["cles"][cle] != l[1]:
                print(f"ÉCART géométrie ou logements : {l[2]} ({e['nom']})")
                ecarts += 1
            # distances
            (cx, cy), _ = max((P.centre([(x / 1e6, y / 1e6) for x, y in poly[0]]) for poly in decoder(l[0])), key=lambda c: c[1])
            for i, t in enumerate(P.TYPES):
                dist, ident = l[4 + i], l[7 + i]
                if dist is None:
                    continue
                if ident not in lieux[t]:
                    print(f"ÉCART lieu {t} {ident} absent du fichier ({l[2]})")
                    ecarts += 1
                    continue
                if (t, ident) not in geo_lieux:
                    lieu = lieux[t][ident]
                    geo_lieux[(t, ident)] = [[P.proj(x / 1e6, y / 1e6) for x, y in ring] for poly in decoder(lieu[2]) for ring in poly]
                anneaux = geo_lieux[(t, ident)]
                if P.dedans(cx, cy, anneaux):
                    droite = 0.0
                else:
                    droite = min(P.dist_point_seg(cx, cy, a[0], a[1], b[0], b[1])[0]
                                 for r in anneaux for a, b in zip(r, r[1:]))
                verifies += 1
                if dist < droite - P.ACCES - 1:
                    viol += 1
                    if viol <= 5:
                        print(f"ÉCART distance {t} : {l[2]} à pied {dist} m < ligne droite {droite:.0f} m - {P.ACCES:.0f}")
        print(f"  {e['nom']:45} {len(lots):6} lots vérifiés")
    if viol:
        ecarts += viol
    print(f"Distances vérifiées : {verifies} ; plus courtes que la ligne droite : {viol}")
    print("Aucun écart." if not ecarts else f"{ecarts} écart(s).")
    sys.exit(1 if ecarts else 0)


if __name__ == "__main__":
    main()
