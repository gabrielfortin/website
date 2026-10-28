# Réseau artériel — notes techniques

Ce dossier contient la carte du réseau artériel administratif de Montréal. Ce
document résume la refonte faite à l'automne 2025, pour référence future.

## Fichiers du dossier

- `index.html` — page d'accueil de la section (lien vers la carte).
- `carte.html` — **la carte**, reconstruite et allégée (voir plus bas).
- `arteriel-seulement.html`, `reseau-arteriel.html` — **obsolètes**, conservés
  uniquement comme redirections (meta-refresh) vers `carte.html`, pour ne pas
  casser d'anciens liens. Ils contenaient auparavant les deux cartes complètes
  générées par Folium (21 Mo et 31 Mo).
- `data/` — un fichier JSON compact par arrondissement (voir plus bas),
  consommé par `carte.html` via `fetch()`.
- `script/extract_data.py` — script qui a produit les fichiers de `data/` à
  partir de l'ancien `reseau-arteriel.html`.

## D'où viennent les données

Les deux anciennes cartes (`arteriel-seulement.html` et `reseau-arteriel.html`)
étaient générées par un script Python (`geopandas` + `folium`) à partir du
geopackage `reseau-arteriel-administratif-2023.gpkg` (données ouvertes de la
Ville de Montréal). En pratique, les deux cartes contenaient le **même jeu de
47 826 tronçons de rue** — `reseau-arteriel.html` montrait tout, et
`arteriel-seulement.html` ne gardait que les tronçons où `ARTERE == 1`.

Comme je n'avais plus le fichier `.gpkg` source sous la main, `extract_data.py`
reconstruit les données à partir du GeoJSON déjà embarqué dans
`reseau-arteriel.html` (c'est pour ça que ce fichier doit être conservé même
s'il n'est plus utilisé directement comme page — c'est la source de vérité
pour régénérer `data/`).

### Champs utilisés

- `CLASSE` (0 à 9) : classification de la voie. Voir `CLASSE_NAMES` dans
  `carte.html` pour les libellés exacts (fournis par Gabriel depuis son script
  de génération d'origine — la Ville ne documente pas ces codes publiquement
  sur donnees.montreal.ca) :
  0 Rue locale · 1 Voie piétonnière · 2 Place d'affaires · 3 Quai ·
  4 Voie privée · 5 Collectrice · 6 Artère secondaire · 7 Artère principale ·
  8 Autoroute · 9 Rue projetée.
- `ARTERE` (0 ou 1) : fait partie du réseau artériel administratif de la
  Ville ou non. Contrôle le calque "Afficher toutes les rues" (hors réseau
  artériel = trait plus fin et plus pâle, masqué par défaut).
- `ARRONDISSEMENT_O_D` / `ARRONDISSEMENT_O_G` : arrondissement à droite/gauche
  du tronçon. Utilisés uniquement côté serveur (dans `extract_data.py`) pour
  répartir les tronçons par fichier — un tronçon limitrophe entre deux
  arrondissements apparaît dans les deux fichiers.

## Architecture de `carte.html`

Avant : deux fichiers HTML autonomes de 21 et 31 Mo, avec tout le GeoJSON
embarqué dans le `<script>` de la page (comme pour l'ancienne carte élections
avant sa fusion).

Maintenant : `carte.html` est un gabarit léger (~27 Ko) qui ne contient aucune
donnée géographique. Au chargement, il va chercher **uniquement** le fichier
JSON de l'arrondissement sélectionné dans `data/`, via `fetch()`. Chaque
fichier fait entre 60 et 550 Ko selon la taille de l'arrondissement (Plateau :
~163 Ko), donc le chargement initial est quasi instantané comparé aux anciens
fichiers.

- **Arrondissement par défaut** : Le Plateau-Mont-Royal.
- **Menu déroulant** : liste les 19 arrondissements + une option "Tous les
  arrondissements" (charge et combine les 19 fichiers via `Promise.all`,
  nettement plus lourd — environ 5 Mo et 47 800 tronçons d'un coup — donc plus
  lent à charger, mais mis en cache après le premier chargement).
- **Mise en cache** : chaque fichier chargé est gardé en mémoire
  (`dataCache`), donc changer d'arrondissement puis y revenir ne refait pas de
  requête réseau.
- **Format compact** : chaque tronçon est encodé comme un tableau plutôt qu'un
  objet GeoJSON complet, pour éviter de répéter les noms de champs :
  `[[[lng, lat], ...], classe, artere, "Nom de la voie"]`.
- **Rendu** : `L.map('map', { preferCanvas: true })` pour que Leaflet dessine
  les tronçons sur un `<canvas>` plutôt qu'en SVG (beaucoup plus rapide avec
  plusieurs milliers de segments).

### Limite connue

En mode "Tous les arrondissements", les tronçons limitrophes entre deux
arrondissements sont dessinés deux fois (une fois par fichier où ils
apparaissent). Comme les deux tracés sont rigoureusement identiques, ça ne se
voit pas visuellement — c'est juste un peu de travail de rendu en plus. Pas
corrigé, l'impact étant négligeable.

### Design

Même système que la carte élections (`cartes/elections-2025/ParSectionDeVote.html`)
et donc que le projet `avant-apres` : verre dépoli (glassmorphism), en-tête
flottant avec sélecteur d'arrondissement, barre latérale rétractable pour les
calques et la légende, popup (pas de panneau latéral) au clic sur une rue avec
auto-pan dynamique pour ne jamais être caché par l'en-tête.

## Régénérer les données

Si jamais le jeu de données officiel est mis à jour (nouveau `.gpkg`), il faut
soit relancer le script Python d'origine (`geopandas` + `folium`) pour
produire un nouveau `reseau-arteriel.html`, soit adapter `extract_data.py`
pour lire directement un GeoJSON exporté du nouveau `.gpkg`. Ensuite :

```
cd script
python3 extract_data.py
```

Ça régénère tous les fichiers de `data/`, y compris `manifest.json`. Si la
liste des arrondissements change, il faut aussi mettre à jour le tableau
`MANIFEST` codé en dur dans `carte.html` (`name`/`slug` pour chacun) — voir
`slugify()` dans `extract_data.py` pour la règle de génération des slugs.
