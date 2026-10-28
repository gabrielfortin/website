#!/usr/bin/env python3
"""Extrait le GeoJSON embarqué dans reseau-arteriel.html (sortie Folium) et
produit un fichier JSON compact par arrondissement, pour un chargement
paresseux (fetch) depuis la carte reconstruite.

Chaque segment de rue est encodé comme un tableau compact plutot qu'un objet
GeoJSON complet, pour minimiser la taille des fichiers :

    [ [[lng, lat], ...], classe, artere, "Nom de la voie" ]

Un segment est inclus dans le fichier d'un arrondissement si celui-ci
correspond a ARRONDISSEMENT_O_D ou ARRONDISSEMENT_O_G (les rues limitrophes
apparaissent donc des deux cotes).

Usage:
    python3 extract_data.py
"""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "reseau-arteriel.html"
OUT_DIR = ROOT / "data"


def slugify(name: str) -> str:
    n = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    n = n.lower().strip()
    n = re.sub(r"[^a-z0-9]+", "-", n)
    return n.strip("-")


def extract_balanced(data: str, start: int) -> str:
    depth = 0
    i = start
    in_str = False
    esc = False
    while i < len(data):
        c = data[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c in "{[":
                depth += 1
            elif c in "}]":
                depth -= 1
                if depth == 0:
                    return data[start:i + 1]
        i += 1
    raise ValueError("unbalanced")


def main():
    print(f"Lecture de {SOURCE} ...")
    data = SOURCE.read_text(encoding="utf-8")

    marker = '_add({"bbox"'
    idx = data.find(marker)
    if idx == -1:
        raise SystemExit("marqueur GeoJSON introuvable")
    start = idx + len(marker) - len('{"bbox"')
    obj_str = extract_balanced(data, start)
    geojson = json.loads(obj_str)
    features = geojson["features"]
    print(f"{len(features)} segments charges")

    by_arrond: dict[str, list] = {}

    def add(name, row):
        if not name:
            return
        by_arrond.setdefault(name, []).append(row)

    for feat in features:
        p = feat["properties"]
        geom = feat["geometry"]
        if geom.get("type") != "LineString":
            continue
        coords = [[round(lng, 6), round(lat, 6)] for lng, lat in geom["coordinates"]]
        try:
            classe = int(p.get("CLASSE"))
        except (TypeError, ValueError):
            classe = -1
        artere = 1 if p.get("ARTERE") == 1 or p.get("ARTERE") == 1.0 else 0
        nom = p.get("NOM_VOIE") or ""
        row = [coords, classe, artere, nom]

        ad = p.get("ARRONDISSEMENT_O_D") or ""
        ag = p.get("ARRONDISSEMENT_O_G") or ""
        seen = set()
        for name in (ad, ag):
            if name and name not in seen:
                seen.add(name)
                add(name, row)

    OUT_DIR.mkdir(exist_ok=True)
    manifest = []
    for name, rows in sorted(by_arrond.items()):
        slug = slugify(name)
        out_path = OUT_DIR / f"{slug}.json"
        out_path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        size_kb = out_path.stat().st_size / 1024
        print(f"{name:45s} -> {slug}.json  {len(rows):6d} segments  {size_kb:8.1f} Ko")
        manifest.append({"name": name, "slug": slug, "count": len(rows)})

    manifest.sort(key=lambda m: m["name"])
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=0), encoding="utf-8"
    )
    print(f"\n{len(manifest)} arrondissements ecrits dans {OUT_DIR}")


if __name__ == "__main__":
    main()
