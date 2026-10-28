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
- `script/` — script de génération (`genmap3.py`) et son `README.md`.

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

## Régénérer les données

Voir `script/README.md`. En résumé :

```
cd script
python3 genmap3.py
```

Le script lit `../resultats-detailles-2025.csv` et produit `genmap3.html`, qui contient
les blocs de données (`DATA_DISTRICTS`, `DATA_SECTIONS`, `RESULTS_INDEX`,
`POSTE_LABELS`, `METRO_GEO_*`, etc.) à reprendre si les résultats officiels sont
corrigés ou mis à jour.
