#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
genmap3.py

Prépare les données des cartes des élections municipales de Montréal 2025
(ParSectionDeVote.html et ParDistrict.html) à partir des résultats officiels.

Les pages HTML ne contiennent aucune donnée : elles chargent, avec fetch(),
seulement les fichiers de ../data/ dont elles ont besoin (architecture des
« cartes lourdes », voir ~/Developer/MAP-DESIGN-SYSTEM.md) :

  data/manifeste.json          liste des groupes (arrondissements) et de leurs fichiers
  data/postes.json             libellé de chaque poste (clé « <arrondissement>.<poste> »)
  data/districts.json          contours des 58 districts électoraux
  data/metro.json              tracé du métro (calque optionnel)
  data/gagnants-districts.json gagnant de la mairie de Montréal par district (ParDistrict)
  data/resultats/<groupe>.json résultats de chaque section pour les postes du groupe
  data/sections/<groupe>.json  polygones des sections de vote de l'arrondissement
  img/gabriel.jpg, img/nicolas.jpg  photos du bandeau de crédits (84 px)

Groupe « 0 » : mairie de Montréal (toutes les sections). Les autres groupes
sont les arrondissements (code avant le point dans la clé du poste).

Les valeurs sont celles du CSV, sans modification. Seule transformation : les
coordonnées des polygones sont arrondies à 6 décimales (environ 11 cm), comme
dans cartes/reseau-arteriel, et le JSON est écrit sans espaces.

Dépendances : pandas, Pillow (photos du bandeau)
Usage : cd script && python3 genmap3.py
"""

import json
import shutil
import unicodedata
from pathlib import Path
from typing import Optional, Dict, Any

import pandas as pd


# --- Configuration des chemins ---

CSV_PATH = Path("../resultats-detailles-2025.csv")
POSTES_CSV_PATH = Path("postes.csv")
DISTRICTS_GEOJSON_PATH = Path("geojson/districts.geojson")
SECTIONS_GEOJSON_PATH = Path("geojson/sections.geojson")
METRO_GEOJSON_PATH_1 = Path("geojson/metro_route_1.geojson")
METRO_GEOJSON_PATH_2 = Path("geojson/metro_route_2.geojson")
METRO_GEOJSON_PATH_4 = Path("geojson/metro_route_4.geojson")
METRO_GEOJSON_PATH_5 = Path("geojson/metro_route_5.geojson")
DOSSIER_DONNEES = Path("../data")
DOSSIER_IMG = Path("../img")

PHOTOS_BANDEAU = {"gabriel.jpg": Path("img/Gabriel.JPG"), "nicolas.jpg": Path("img/nicolas.png")}
TAILLE_PHOTO = 84  # 3 × les 28 px affichés


# --- Utilitaires ---


def normalize_str(value: Any) -> str:
    """
    Normalise une chaîne en :
    - convertissant en str
    - retirant les caractères de contrôle parasites
    - normalisant les accents (NFC)
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    s = str(value)
    # retirer BOM et espaces insécables fréquents
    s = s.replace("\ufeff", "").replace("\xa0", " ")
    s = s.strip()
    # normalisation unicode (accents, etc.)
    s = unicodedata.normalize("NFC", s)
    return s


# --- Construction des données à partir du CSV de résultats ---


def build_results_index(csv_path: Path) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Construit RESULTS_INDEX[poste_code][code_section] = infos pour les popups et la couleur.

    - poste_code : PosteNorm (ex. "0.00", "1.00", "1.10", etc.)
    - code_section : "DDD-SSS" pour matcher CODE_SECTION du GeoJSON des sections
      (ex. "011-037")
    """
    df = pd.read_csv(csv_path, encoding="utf-8")

    # Normaliser Poste (0,00 -> 0.00)
    df["PosteNorm"] = df["Poste"].astype(str).str.replace(",", ".", regex=False)

    # Codes de district/section au format 'DDD-SSS' pour matcher CODE_SECTION du GeoJSON
    df["ElectoralDistrictID"] = pd.to_numeric(df["ElectoralDistrictID"], errors="coerce").astype(int)
    df["DistCode"] = df["ElectoralDistrictID"].astype(str).str.zfill(3)
    df["BureauStr"] = df["Bureau"].astype(str).str.zfill(3)
    df["SectionCode"] = df["DistCode"] + "-" + df["BureauStr"]

    # S'assurer que Votes et totaux sont numériques
    df["Votes"] = pd.to_numeric(df["Votes"], errors="coerce").fillna(0)

    for col in ["TotalValidVotes", "TotalRejectedVotes", "TotalVotes"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    results_index: Dict[str, Dict[str, Dict[str, Any]]] = {}

    # Grouper par poste et section
    group_cols = ["PosteNorm", "SectionCode"]
    for (poste, sec_code), grp in df.groupby(group_cols):
        section_key = sec_code

        # gagnant
        winner_row = grp.sort_values("Votes", ascending=False).iloc[0]

        total_valid = grp["TotalValidVotes"].max() if "TotalValidVotes" in grp.columns else None
        total_rejected = grp["TotalRejectedVotes"].max() if "TotalRejectedVotes" in grp.columns else None
        total_votes = grp["TotalVotes"].max() if "TotalVotes" in grp.columns else None

        # Base de pourcentage : privilégier les votes valides, sinon total
        total_for_pct: Optional[float] = None
        if total_valid is not None and not pd.isna(total_valid) and float(total_valid) > 0:
            total_for_pct = float(total_valid)
        elif total_votes is not None and not pd.isna(total_votes) and float(total_votes) > 0:
            total_for_pct = float(total_votes)

        breakdown = []
        for _, row in grp.iterrows():
            votes = int(row.get("Votes", 0))
            pct: Optional[float] = None
            if total_for_pct is not None and total_for_pct > 0:
                pct = votes * 100.0 / total_for_pct
            breakdown.append(
                {
                    "candidat": normalize_str(row.get("Candidat", "")),
                    "parti": normalize_str(row.get("Partie", "")),
                    "votes": votes,
                    "pct": pct,
                }
            )

        # Pour affichage dans le popup
        district_id = int(grp["ElectoralDistrictID"].iloc[0])
        bureau = str(grp["Bureau"].iloc[0])

        poste_dict = results_index.setdefault(str(poste), {})
        poste_dict[section_key] = {
            "winner_candidate": normalize_str(winner_row.get("Candidat", "")),
            "winner_party": normalize_str(winner_row.get("Partie", "")),
            "winner_votes": int(winner_row.get("Votes", 0)),
            "total_valid": int(total_valid) if total_valid is not None and not pd.isna(total_valid) else None,
            "total_rejected": int(total_rejected) if total_rejected is not None and not pd.isna(total_rejected) else None,
            "total_votes": int(total_votes) if total_votes is not None and not pd.isna(total_votes) else None,
            "district_id": str(district_id),
            "bureau": bureau,
            "breakdown": breakdown,
        }

    return results_index


# --- Chargement des noms de postes ---


def load_poste_labels(postes_csv: Path, poste_codes: Dict[str, Any]) -> Dict[str, str]:
    """
    Charge postes.csv et retourne un mapping:
      poste_code_norm (ex. "0.00", "1.10") -> label pour le dropdown.

    Format d'une entrée dans le dropdown :
      "<type> <poste>"

    Hypothèse sur postes.csv :
      - colonne "no" : numéro de poste (float ex. 0.0, 1.0, 1.1, etc.)
      - colonne "type" : type de poste ("Maire d'arrondissement", "Conseiller de ville", etc.)
      - colonne "poste" : libellé du poste (ex. "Jeanne-Mance")
    On corrige les accents et bizarreries via normalize_str().
    """
    if not postes_csv.exists():
        print(f"⚠️  postes.csv introuvable: {postes_csv} — les codes seront utilisés tels quels.")
        return {code: code for code in poste_codes.keys()}

    df_postes = pd.read_csv(postes_csv, encoding="utf-8")

    labels_raw: Dict[str, str] = {}
    for _, row in df_postes.iterrows():
        no_val = row.get("no")
        if pd.isna(no_val):
            continue
        try:
            f = float(no_val)
        except Exception:
            continue
        code = f"{f:.2f}"  # 1.1 → "1.10", 1.0 → "1.00", etc.

        type_str = normalize_str(row.get("type", ""))
        poste_name = normalize_str(row.get("poste", ""))

        if type_str and poste_name:
            label = f"{type_str} {poste_name}"
        elif type_str:
            label = type_str
        elif poste_name:
            label = poste_name
        else:
            label = code

        labels_raw[code] = label

    # S'assurer qu'on a un label pour tous les codes de RESULTS_INDEX
    final_labels: Dict[str, str] = {}
    for code in poste_codes.keys():
        if code in labels_raw:
            final_labels[code] = labels_raw[code]
        else:
            # fallback: le code lui-même
            final_labels[code] = code

    return final_labels


# --- Gagnant de la mairie de Montréal par district (ParDistrict.html) ---


def build_district_winners(csv_path: Path) -> Dict[str, Dict[str, Any]]:
    """Additionne les votes du poste 0,00 (mairie de Montréal) par district et
    retient le candidat qui en a le plus. S'arrête en cas d'égalité."""
    df = pd.read_csv(csv_path, encoding="utf-8")
    df = df[df["Poste"].astype(str) == "0,00"].copy()
    df["Votes"] = pd.to_numeric(df["Votes"], errors="coerce").fillna(0).astype(int)
    df["ElectoralDistrictID"] = pd.to_numeric(df["ElectoralDistrictID"], errors="coerce").astype(int)
    gagnants: Dict[str, Dict[str, Any]] = {}
    for district, grp in df.groupby("ElectoralDistrictID"):
        totaux = grp.groupby(["Candidat", "Partie"], as_index=False)["Votes"].sum().sort_values("Votes", ascending=False)
        if len(totaux) > 1 and totaux.iloc[0]["Votes"] == totaux.iloc[1]["Votes"]:
            raise SystemExit(f"Égalité au district {district} : gagnant impossible à déterminer")
        premier = totaux.iloc[0]
        gagnants[str(int(district))] = {
            "winner_candidate": normalize_str(premier["Candidat"]),
            "winner_party": normalize_str(premier["Partie"]),
            "winner_votes": int(premier["Votes"]),
        }
    return gagnants


# --- Écriture des fichiers de données ---


def arrondir(valeur: Any) -> Any:
    """Arrondit les coordonnées (nombres réels) à 6 décimales, récursivement."""
    if isinstance(valeur, float):
        return round(valeur, 6)
    if isinstance(valeur, list):
        return [arrondir(v) for v in valeur]
    return valeur


def alleger(fc: Dict[str, Any], features=None) -> Dict[str, Any]:
    """Copie d'une FeatureCollection, propriétés intactes, coordonnées arrondies."""
    return {
        **{k: v for k, v in fc.items() if k != "features"},
        "features": [
            {**f, "geometry": {**f["geometry"], "coordinates": arrondir(f["geometry"]["coordinates"])}}
            for f in (fc["features"] if features is None else features)
        ],
    }


def ecrire_json(chemin: Path, donnees: Any) -> int:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    texte = json.dumps(donnees, ensure_ascii=False, separators=(",", ":"))
    chemin.write_text(texte, encoding="utf-8")
    return len(texte.encode("utf-8"))


def groupe_de(poste: str) -> str:
    return poste.split(".")[0]


def repartir_sections(sections_geojson, results_index) -> Dict[str, list]:
    """Range chaque section de vote dans l'arrondissement (groupe) dont les
    postes en donnent les résultats. Une section sans résultat d'arrondissement
    suit les autres sections de son district."""
    groupe_section: Dict[str, str] = {}
    for poste, sections in results_index.items():
        g = groupe_de(poste)
        if g == "0":
            continue
        for code in sections:
            if groupe_section.setdefault(code, g) != g:
                raise SystemExit(f"Section {code} dans deux arrondissements ({groupe_section[code]} et {g})")
    groupe_district: Dict[str, str] = {}
    for code, g in groupe_section.items():
        district = code.split("-")[0]
        if groupe_district.setdefault(district, g) != g:
            raise SystemExit(f"District {district} dans deux arrondissements")
    par_groupe: Dict[str, list] = {}
    for f in sections_geojson["features"]:
        code = str(f["properties"].get("CODE_SECTION", ""))
        g = groupe_section.get(code) or groupe_district.get(code.split("-")[0])
        if g is None:
            raise SystemExit(f"Section {code} : arrondissement introuvable")
        par_groupe.setdefault(g, []).append(f)
    return par_groupe


def ecrire_donnees(districts_geojson, sections_geojson, results_index, poste_labels, metro, gagnants) -> None:
    if DOSSIER_DONNEES.exists():
        shutil.rmtree(DOSSIER_DONNEES)   # repartir de zéro : pas de fichier orphelin
    tailles: Dict[str, int] = {}
    tailles["postes.json"] = ecrire_json(DOSSIER_DONNEES / "postes.json", poste_labels)
    tailles["districts.json"] = ecrire_json(DOSSIER_DONNEES / "districts.json", alleger(districts_geojson))
    tailles["metro.json"] = ecrire_json(DOSSIER_DONNEES / "metro.json", metro)
    tailles["gagnants-districts.json"] = ecrire_json(DOSSIER_DONNEES / "gagnants-districts.json", gagnants)

    par_groupe = repartir_sections(sections_geojson, results_index)
    groupes = sorted({groupe_de(p) for p in results_index}, key=lambda g: int(g))
    manifeste = {"groupes": []}
    for g in groupes:
        resultats = {p: v for p, v in results_index.items() if groupe_de(p) == g}
        t_res = ecrire_json(DOSSIER_DONNEES / "resultats" / f"{g}.json", resultats)
        entree = {"cle": g, "postes": sorted(resultats), "resultats_octets": t_res}
        if g != "0":
            feats = par_groupe.get(g, [])
            entree["sections"] = len(feats)
            entree["sections_octets"] = ecrire_json(DOSSIER_DONNEES / "sections" / f"{g}.json", alleger(sections_geojson, feats))
        manifeste["groupes"].append(entree)
    if set(par_groupe) - set(groupes):
        raise SystemExit(f"Sections rangées dans des groupes sans poste : {set(par_groupe) - set(groupes)}")
    total_sections = sum(e.get("sections", 0) for e in manifeste["groupes"])
    if total_sections != len(sections_geojson["features"]):
        raise SystemExit(f"{total_sections} sections écrites sur {len(sections_geojson['features'])}")
    ecrire_json(DOSSIER_DONNEES / "manifeste.json", manifeste)

    for g in manifeste["groupes"]:
        print(f"  groupe {g['cle']:>2} : {len(g['postes'])} poste(s), {g.get('sections', '—')} sections, "
              f"résultats {g['resultats_octets'] // 1024} Ko, sections {g.get('sections_octets', 0) // 1024} Ko")
    for nom, t in tailles.items():
        print(f"  {nom} : {t // 1024} Ko")


def ecrire_photos() -> None:
    from PIL import Image, ImageOps
    DOSSIER_IMG.mkdir(exist_ok=True)
    for nom, source in PHOTOS_BANDEAU.items():
        img = ImageOps.exif_transpose(Image.open(source)).convert("RGB")
        img = ImageOps.fit(img, (TAILLE_PHOTO, TAILLE_PHOTO), Image.LANCZOS)
        img.save(DOSSIER_IMG / nom, "JPEG", quality=85, optimize=True, progressive=True)
        print(f"  img/{nom} : {(DOSSIER_IMG / nom).stat().st_size // 1024} Ko")


# --- main ---


def main() -> None:
    for chemin in (CSV_PATH, POSTES_CSV_PATH, DISTRICTS_GEOJSON_PATH, SECTIONS_GEOJSON_PATH):
        if not chemin.exists():
            raise SystemExit(f"Fichier introuvable : {chemin}")

    results_index = build_results_index(CSV_PATH)
    poste_labels = load_poste_labels(POSTES_CSV_PATH, results_index)
    gagnants = build_district_winners(CSV_PATH)
    districts_geojson = json.loads(DISTRICTS_GEOJSON_PATH.read_text(encoding="utf-8"))
    sections_geojson = json.loads(SECTIONS_GEOJSON_PATH.read_text(encoding="utf-8"))
    metro = {
        cle: json.loads(chemin.read_text(encoding="utf-8"))
        for cle, chemin in (("1", METRO_GEOJSON_PATH_1), ("2", METRO_GEOJSON_PATH_2),
                            ("4", METRO_GEOJSON_PATH_4), ("5", METRO_GEOJSON_PATH_5))
    }
    print("Écriture de ../data/ :")
    ecrire_donnees(districts_geojson, sections_geojson, results_index, poste_labels, metro, gagnants)
    print("Photos du bandeau :")
    ecrire_photos()


if __name__ == "__main__":
    main()
