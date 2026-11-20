# Données des cartes des élections 2025

`genmap3.py` prépare les données des deux cartes (`../ParSectionDeVote.html`
et `../ParDistrict.html`) à partir des résultats officiels. Les pages ne
contiennent aucune donnée : elles chargent les fichiers de `../data/`.

```
cd script
python3 genmap3.py        # pandas et Pillow nécessaires
```

Sources lues : `../resultats-detailles-2025.csv`, `postes.csv`,
`geojson/districts.geojson`, `geojson/sections.geojson`,
`geojson/metro_route_{1,2,4,5}.geojson`, `img/Gabriel.JPG`, `img/nicolas.png`.

Écrit : `../data/` (vidé d'abord) et `../img/`. Détail des fichiers,
découpage par arrondissement et vérifications : `../NOTES.md`, section
« Architecture : données chargées à la demande ». Méthode générale :
`~/Developer/MAP-DESIGN-SYSTEM.md`, section « Carte lourde ».
