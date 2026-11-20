# Carte des élections 2025 — notes techniques

Ce dossier contient les cartes interactives des résultats de l'élection municipale
de Montréal 2025. Ce document résume l'audit des données et la refonte de la carte
par section de vote faits à l'automne 2025, pour référence future.

## Fichiers du dossier

- `index.html` — page d'accueil de la section "Élections 2025" (liens vers les cartes).
- `ParSectionDeVote.html` — carte principale : résultats par section de vote, avec le
  réseau du métro en calque optionnel. **C'est la carte fusionnée** (voir plus bas).
- `ParDistrict.html` — carte choroplèthe par district électoral (vue d'ensemble).
- `mairie2025-metro.html` — **obsolète**, conservé uniquement comme redirection
  (meta-refresh) vers `ParSectionDeVote.html`, pour ne pas casser d'anciens liens.
- `resultats-detailles-2025.csv` — résultats officiels finaux (source de vérité).
- `data/` — **les données des deux cartes**, découpées par arrondissement et
  écrites par `script/genmap3.py` (ne pas modifier à la main). Voir
  « Architecture : données chargées à la demande » plus bas.
- `img/` — photos du bandeau de crédits (84 px), écrites par le même script.
- `script/` — script de génération (`genmap3.py`), ses sources (GeoJSON,
  `postes.csv`, photos d'origine) et son `README.md`.

## Audit des données (résultats préliminaires → résultats finaux)

Les cartes avaient été construites avec des résultats préliminaires. Un audit complet
a comparé les données déjà embarquées dans les 3 fichiers HTML avec le CSV officiel
final (`resultats-detailles-2025.csv`, ~71 800 lignes). Deux problèmes ont été trouvés
et corrigés :

1. **`ParDistrict.html`** affichait le mauvais gagnant pour 2 districts (34 —
   Notre-Dame-de-Grâce, et 161 — Saint-Henri-Est/Petite-Bourgogne/Pointe-Saint-Charles/
   Griffintown), parce que la carte d'origine avait été construite à partir d'un seul
   bureau de vote arrivé tôt plutôt que de l'agrégat complet du district. Corrigé en
   repatchant les données de gagnant pour les 58 districts à partir du CSV, et en
   ajustant la liste de couleurs codée en dur dans le JS.

2. **Bug dans `script/genmap3.py`** : le script lisait la colonne `"Parti"` alors que
   la vraie colonne du CSV s'appelle `"Partie"`. Résultat : le champ parti était
   toujours vide, et la carte ne montrait aucune couleur de parti (tout en gris), même
   sur la mairie de Montréal. Corrigé (`row.get("Partie", "")`), régénéré, et revérifié
   — y compris le champ parti, qui n'était pas comparé dans la première passe de
   vérification (leçon apprise : toujours comparer *tous* les champs affichés, pas
   seulement candidat + votes).

## Fusion de la carte par section de vote et de la carte du métro

`ParSectionDeVote.html` et `mairie2025-metro.html` ont été fusionnées en une seule
page. Le réseau du métro est maintenant un calque optionnel qu'on active/désactive
dans la barre latérale, plutôt qu'une carte séparée. `mairie2025-metro.html` redirige
simplement vers la carte fusionnée.

Le style visuel a été repris du projet **avant-apres** (`avantapres.gabfortin.com`) :
verre dépoli (glassmorphism), en-tête flottant, barre latérale rétractable, polices
Inter/Poppins.

### Tracé du métro adouci

Le tracé du métro (GeoJSON) est rendu avec un lissage par **spline de Catmull-Rom** :
chaque segment entre deux points réels du tracé est remplacé par une courbe qui passe
exactement par ces points mais les relie en douceur plutôt qu'en ligne droite anguleuse
(fonction `catmullRomSmooth()` dans le JS de la page).

### Interaction au clic sur une section

Le clic sur une section de vote ouvre un **popup Leaflet** (pas un panneau latéral).
Le `autoPan` du popup est calculé dynamiquement à partir de la hauteur réelle de la
barre d'en-tête (`headerEl.offsetHeight`) au moment du clic, pour que le popup ne soit
jamais caché derrière la barre — y compris quand celle-ci s'étale sur plusieurs lignes
en mobile.

### Résultats globaux dans la barre latérale

La barre latérale (gauche) affiche, en plus du calque métro, les **résultats globaux
du poste sélectionné** : total des votes, votes valides/rejetés, et la liste des
candidat·es triée par votes, agrégée sur toutes les sections de vote concernées.
Ce calcul se fait entièrement côté client (JS) à partir des données déjà chargées
dans `RESULTS_INDEX` — aucune régénération de données n'est nécessaire.

### Sélecteur de poste en deux étapes

Le menu "Poste" (103 options à plat à l'origine) a été scindé en deux menus en
cascade : **Arrondissement**, puis **Poste** (limité aux postes de cet arrondissement,
5 à 7 options au plus). Le regroupement et les noms d'arrondissement sont dérivés
dynamiquement de `POSTE_LABELS` (clé = `"<code arrondissement>.<code poste>"`), pas
besoin de régénérer les données pour ça non plus.

**Problème connu, non corrigé** : l'entrée `POSTE_LABELS["3.00"]` contient un bug
d'encodage préexistant dans le CSV source — "Notre-Dame-de-Grâce" s'affiche
"Notre-Dame-de-GrÃ¢ce" (mojibake). À corriger dans le CSV/le script de génération si
souhaité.

## Page d'accueil des cartes (`index.html`)

L'ancien système de modal/iframe (avec sa barre noire et son bouton "X") a été retiré.
Les cartes s'ouvrent maintenant par navigation directe (`<a href="...">`), et le lien
"← Toutes les cartes" dans l'en-tête de chaque carte permet de revenir proprement à
cette page, sans dédoublement de barre.

## Mobile

Points vérifiés/corrigés spécifiquement pour le mobile (≤ 760px) :

- Le lien "← Toutes les cartes" reste visible (il avait été caché par erreur lors
  d'une itération précédente).
- Les deux menus Arrondissement/Poste sont groupés avec leur étiquette pour ne
  prendre que 2 lignes dans l'en-tête plutôt que 4.
- Le décalage anti-chevauchement du popup (voir plus haut) est calculé dynamiquement
  à partir de la hauteur réelle de l'en-tête, justement parce que celle-ci varie selon
  le nombre de lignes affichées sur petit écran.
- La largeur du contenu du popup est plafonnée par rapport à la largeur de l'écran
  (`min(280px, 100vw - 72px)`) pour éviter tout débordement sur les très petits
  téléphones.

## Architecture : données chargées à la demande (novembre 2026)

Avant : `ParSectionDeVote.html` pesait 29 Mo (6,9 Mo compressés) et
`ParDistrict.html` 6,3 Mo, avec tout le GeoJSON, les résultats et deux photos
en base64 dans la page. Maintenant, les deux pages ne contiennent plus
aucune donnée (42 Ko et 24 Ko) : elles chargent ce qu'il faut dans `data/`.
C'est le modèle des « cartes lourdes » de `~/Developer/MAP-DESIGN-SYSTEM.md`.

Fichiers de `data/` (tous écrits par `script/genmap3.py`) :

| Fichier | Contenu | Chargé par |
|---|---|---|
| `manifeste.json` | Groupes (clé, postes, nombre de sections, tailles) | ParSectionDeVote |
| `postes.json` | Libellé de chaque poste (`POSTE_LABELS`) | ParSectionDeVote |
| `districts.json` | Contours des 58 districts (avec `NOM_DISTRICT`, `NOM_ARR`) | les deux cartes |
| `metro.json` | Tracé du métro (lignes 1, 2, 4, 5) | ParSectionDeVote, à la 1re activation du calque |
| `gagnants-districts.json` | Gagnant de la mairie de Montréal par district (votes additionnés) | ParDistrict |
| `resultats/<groupe>.json` | Résultats par section pour les postes du groupe | ParSectionDeVote |
| `sections/<groupe>.json` | Polygones des sections de vote de l'arrondissement | ParSectionDeVote |

**Groupes** : le code avant le point dans la clé d'un poste. `0` = mairie de
Montréal (toutes les sections : la page charge alors les 19 fichiers de
sections) ; `1` à `19` = les arrondissements. Une section est rangée dans
l'arrondissement dont les postes en donnent les résultats ; le script
s'arrête si une section tombe dans deux arrondissements ou dans aucun.

**Comportement** : à l'ouverture, mairie de Montréal (3,0 Mo compressés au
total). Choisir un arrondissement charge seulement ses résultats et ses
sections (0,1 Mo de plus pour le Plateau), recentre la carte dessus et
n'affiche que ses sections. Avant, les sections des autres arrondissements
restaient dessinées en gris (sans données pour ce poste). Pendant le chargement,
une animation d'attente (urne et bulletins, `../chargement-cartes.js`) s'affiche au
centre de la carte. Chaque fichier est
gardé en mémoire : revenir à un arrondissement ne refait pas de requête.

**Transformations** : aucune sur les valeurs. Les coordonnées sont arrondies
à 6 décimales (environ 11 cm) et le JSON est écrit sans espaces.

**Vérification faite à la conversion** : le script reproduit exactement les
données de l'ancienne page (résultats des 103 postes, libellés, districts,
sections, métro) ; les fichiers recombinés sont identiques (géométries =
originales arrondies) ; un relevé dans un navigateur sans écran, avant et
après, donne les mêmes menus, résultats globaux, couleurs de sections,
popups (719 comparés) et districts (couleur et infobulle des 58) : 0 écart.

**ParDistrict** : la liste de districts à colorer en violet, codée en dur,
est remplacée par la règle « gagnant = Ensemble Montréal → violet, sinon
vert » (identique pour les 58 districts). Les bibliothèques chargées par
Folium et inutilisées (jQuery, Bootstrap, Font Awesome, awesome-markers)
sont retirées : la page ne contacte plus jsDelivr, cdnjs ni code.jquery.com.
Sans Bootstrap, l'en-tête et le bandeau reprennent la taille de texte des
autres cartes.

**Barre latérale** : elle suit la hauteur réelle de l'en-tête
(`--gf-header-h`), qui passe sur deux lignes avec un nom d'arrondissement
long ; avant, l'en-tête cachait le haut de la barre.

## Régénérer les données

Voir `script/README.md`. En résumé (pandas et Pillow nécessaires) :

```
cd script
python3 genmap3.py
```

Le script lit `../resultats-detailles-2025.csv`, `postes.csv` et les GeoJSON de
`geojson/`, vide `../data/` puis réécrit tous les fichiers (et `../img/`). Il
affiche la taille de chaque fichier. Les pages n'ont rien à modifier, sauf si
la liste des groupes change de nature.
