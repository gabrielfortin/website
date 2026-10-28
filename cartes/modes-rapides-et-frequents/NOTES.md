# Modes rapides et fréquents — notes techniques

Ce dossier contient la carte des lignes de transport collectif rapides et
fréquentes à Montréal (métro, REM, et le futur SRB/tramway Pie-IX). Ce
document résume la refonte faite à l'automne 2025, pour référence future.

## Fichiers du dossier

- `map.html` — la carte, seul fichier de ce dossier (pas de page d'accueil
  séparée ; elle est liée directement depuis la carte "Modes Rapides et
  Fréquents" sur `cartes/index.html`, sans modal).

## D'où viennent les données

`map.html` était à l'origine généré par Folium (`geopandas` + `folium`,
probablement à partir des shapes GTFS de la STM). Je n'ai pas le script
d'origine ni les données sources (GTFS) sous la main — seulement l'ancien
fichier HTML généré. Je l'ai donc reconstruit en extrayant directement les
`L.polyline(...)` déjà présents dans le JS généré par Folium (coordonnées,
couleur, tooltip, contenu du popup), plutôt qu'en repartant des données
brutes.

### Dédoublonnage

Les shapes GTFS incluent généralement un tracé par direction (aller/retour).
L'ancien fichier contenait donc deux fois chaque ligne de métro (ex. Ligne 1
en 27 points, puis exactement les 27 mêmes points à l'envers) — 31 tracés au
total pour seulement 8 lignes distinctes. J'ai dédoublonné en comparant
(étiquette, couleur, ensemble de points) : les tracés qui ne sont que le même
trajet inversé sont fusionnés, mais les segments réellement différents (ex.
les 6 tronçons du 439 Express Pie-IX, ou les 3-4 variantes de construction du
REM) sont conservés tels quels. Résultat : 21 tracés uniques (~10 500 points)
regroupés sous 8 lignes.

### Correction de données

Dans l'ancien fichier, les trois branches du REM (`A1`, `A4-A1`, `A3-A1`)
étaient étiquetées **"Métro"** dans leur popup — une erreur du script
d'origine. Je les ai recatégorisées en **"REM"** dans `carte.html`, pour que
la carte reflète la réalité (station Bois-Franc, Brossard, Deux-Montagnes,
Anse-à-l'Orme = REM, pas le métro de Montréal). Le `439 Express Pie-IX` reste
classé "Tramway / SRB", ce qui était déjà correct.

## Architecture

Contrairement aux cartes élections et réseau artériel, cette carte est
petite (8 lignes, ~220 Ko de données embarquées directement dans le HTML — 
pas de fetch séparé nécessaire, le jeu de données est trop petit pour que ça
vaille la peine).

- **Données** : tableau `LINES` embarqué dans `<script>`, un objet par ligne
  avec `num`, `name`, `mode`, `color`, `weight` et `segments` (liste de
  tracés — une ligne peut avoir plusieurs segments disjoints).
- **Calques** : une case à cocher par mode (Métro / REM / Tramway-SRB) dans
  la barre latérale, générée dynamiquement à partir des modes présents dans
  `LINES`. Toutes les cases sont cochées par défaut (le jeu de données est
  petit, pas besoin de masquer quoi que ce soit pour la fluidité).
- **Légende** : même source `LINES`, regroupée par mode.
- **Popup** : au clic sur une ligne, affiche le mode, le nom complet et
  l'identifiant (numéro de ligne), avec le même style et le même auto-pan
  dynamique (basé sur la hauteur réelle de l'en-tête) que les autres cartes.
- **Design** : même système que les cartes élections et réseau artériel
  (glassmorphism calqué sur le projet `avant-apres`).

## Intégration avec `cartes/index.html`

La carte "Modes Rapides et Fréquents" sur la page d'accueil des cartes
ouvrait auparavant cette page dans une modal/iframe (`onclick="openModal(...)"`).
Comme `map.html` a maintenant son propre en-tête avec un lien "← Toutes les
cartes", la carte a été changée pour un lien direct (`<a href="...">`), et le
markup/JS de la modal (devenu inutilisé sur cette page précise) a été retiré
de `cartes/index.html`. Le système de modal reste utilisé ailleurs sur le
site (`plans/reb-2025`, `plans/pum-2050`, `plans/metro-2025`), donc le CSS
partagé dans `css/site.css` n'a pas été touché.

## Régénérer les données

Il n'y a pas de script de régénération pour l'instant (les données ont été
extraites une fois depuis l'ancien fichier Folium). Si les tracés doivent
être mis à jour avec des données GTFS plus récentes, il faudrait soit
régénérer un nouveau fichier Folium puis répéter l'extraction, soit écrire un
script qui part directement des données GTFS/Pulsar de la STM et produit un
tableau `LINES` au même format que celui de `map.html` (voir le `<script>`
de `map.html` pour la structure exacte).
