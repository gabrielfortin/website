# Structure et pages — gabfortin.com

Vue d'ensemble : [README.md](README.md) ; procédures : [CONTENU.md](CONTENU.md).

## Structure du site

```
/
├── index.html                          # Page d'accueil
├── applications/
│   └── index.html                      # Hub des applications
├── cartes/
│   └── index.html                      # Cartes interactives
├── donnees/
│   └── index.html                      # Données ouvertes
├── plans/
│   ├── index.html                      # Redirection vers le blogue (anciens liens)
│   ├── pum-2050/  metro-2025/  reb-2025/   # Plans, listés dans le blogue
├── articles/
│   ├── index.html                      # Liste des articles
│   ├── velo-hiver/
│   │   └── index.html                  # Article: Le vélo d'hiver et les données
│   ├── avant-apres/
│   │   └── index.html                  # Article: Outil Avant / Après
│   ├── feed.xml                        # Flux RSS du blogue (mis à jour à la main)
│   ├── parc-1/
│   │   └── index.html                  # Article: Sécuriser l'avenue du Parc
│   ├── refonte-stm-2026/
│   │   └── index.html                  # Article: Refonte STM 2026
│   └── le-rem-et-le-plateau/
│       └── index.html                  # Article: REM et Plateau
├── parcours/
│   └── index.html                      # Parcours professionnel et engagements
├── projets/
│   └── index.html                      # Projets intéressants créés par des amis
├── don/
│   └── index.html                      # Faire un don
├── confidentialite/
│   └── index.html                      # Politique de confidentialité (Loi 25)
├── fichiers/                           # PDF des déclarations/résolutions
├── fonts/                              # Police Inter (woff2) + licence
├── 404.html                            # Page « introuvable » (chemins absolus, voir « Liens et chemins »)
├── llms.txt                            # Résumé du site destiné aux IA
├── link.json                           # Fiche Person (schema.org) de référence
├── sitemap.xml
└── robots.txt
```

## Pages et navigation

### Accueil (`/index.html`)
Page principale avec présentation et navigation (section "Explorer") vers:
- **Compteurs Vélo Montréal** (featured) → https://compteurvelo.com
- **Avant / Après** (featured, badge "Nouveau") → https://avant-apres.ca — comparaison avant/après des améliorations de l'espace public réalisées par Projet Montréal
- **Blogue** → Analyses et propositions sur la mobilité, le transport collectif et l'espace public
- **Cartes Interactives** → Élections 2025, réseau artériel, modes rapides et fréquents
- **Données Ouvertes** → Ensembles de données publiques et visualisations
- **Parcours** → Formation, carrière chez Bell et dossiers portés comme conseiller

Navigation principale: Blogue, Cartes, Données, Parcours.

### Contenu principal

#### Cartes (`/cartes/`)

1. **Avant / Après** → https://avant-apres.ca
2. **Carte accessibilité universelle** — encore grisée, non cliquable (`<div class="carte-item is-disabled">`, pas un `<a>`), alors que le projet `carte-au` est en ligne sur https://montrealaccessible.ca (novembre 2026 : à relier). Icône : `img/carte-au.svg`.
3. **Réseau Artériel de Montréal** → `./reseau-arteriel/carte.html`
4. **Collisions et réseau artériel** → `./collisions-reseau-arteriel/` (réutilise les tronçons de `reseau-arteriel/data/` ; méthode dans son `NOTES.md`)
5. **Pistes cyclables Plateau** → https://pistes.gabfortin.com
6. **Résultats Élections 2025** → `./elections-2025/ParSectionDeVote.html`
7. **Modes Rapides et Fréquents**
8. **Stationnement Plateau** → https://parking.gabfortin.com

Pour ajouter une carte « à venir » (grisée, non cliquable) : utiliser un `<div class="carte-item is-disabled" aria-disabled="true">` au lieu d'un `<a>`, et remplacer la flèche « Explorer la carte » par `<span class="carte-arrow">Bientôt disponible</span>`. Le style `.is-disabled` (opacité réduite, `grayscale`, pas de hover) est défini dans le `<style>` de `cartes/index.html`.


**Mode sombre des cartes verre** : `cartes/reseau-arteriel/carte.html`, `cartes/collisions-reseau-arteriel/index.html`, `cartes/modes-rapides-et-frequents/map.html` et les deux cartes `cartes/elections-2025/Par*.html` chargent `cartes/carte-sombre.css` **après** leur `<style>`. Cette feuille ne contient que les règles sombres (jetons du dashboard verre, tuiles inversées, textes de marque, popups) ; le mode clair reste dans chaque page. Une nouvelle carte de `cartes/` doit la relier aussi, et toute couleur claire écrite en dur dans une carte doit y être surchargée. Recette : `~/Developer/MAP-DESIGN-SYSTEM.md`, section « Mode sombre ».
#### Données (`/donnees/`)

1. **Compteurs Vélo Montréal** → https://compteurvelo.com
2. **Mobilité Montréal (ARTM)** → https://artm.gabfortin.com
3. **Déchets Montréal** → https://dechets.gabfortin.com
4. **Résultats élections municipales Montréal 2025** → `./elections-2025/resultats.html`
5. **Requêtes 311** → https://311.gabfortin.com

#### Blogue (`/articles/`) : articles et plans

Articles :
1. **Le vélo d'hiver et les données** — `/articles/velo-hiver/index.html`
2. **Avant / Après : voir comment l'espace public se transforme** — `/articles/avant-apres/index.html`
3. **Proposition pour sécuriser un tronçon dangereux de l'avenue du Parc** — `/articles/parc-1/index.html`
4. **L'impact de la refonte STM 2026 au Plateau-Mont-Royal** — `/articles/refonte-stm-2026/index.html`
5. **L'arrivée du REM et son impact sur le Plateau** — `/articles/le-rem-et-le-plateau/index.html`

Plans (catégorie « Plan ») :
4. **Prolongement du métro** (15 octobre 2025) — `/plans/metro-2025/index.html`
5. **Réseau Express Bus** (14 octobre 2025) — `/plans/reb-2025/index.html`
6. **PUM 2050** (septembre 2025) — `/plans/pum-2050/index.html`

Les plans gardent leurs adresses sous `/plans/`, mais sont listés dans le blogue et le flux RSS, et leur fil d'Ariane pointe vers le Blogue. L'ancienne page `/plans/` redirige vers `/articles/` (redirection HTML, GitHub Pages ne permettant pas les redirections serveur). Pour un nouveau plan : le créer sous `/plans/NOM/` et l'ajouter au blogue comme un article.

**Recherche et filtre par catégorie** : `articles/index.html` a une barre de recherche (filtre en direct sur le titre, le texte et la catégorie de chaque article, via JS vanilla, pas de dépendance) et des « chips » de filtre par catégorie (Tous, Vélo, Espace public, Mobilité, Environnement, Transport, Élections, Plan). Les deux filtres se combinent. Pour une nouvelle catégorie d'article : ajouter un bouton `<button class="filter-chip" data-category="nom-en-minuscules">Nom</button>` dans `#articles-filters`, la valeur de `data-category` doit correspondre (en minuscules) au texte de `.article-category` de l'article.

#### Parcours (`/parcours/`)

Formation, carrière (incl. passage chez Bell) et dossiers portés comme conseiller d'arrondissement (plan propreté 2026, mobilité durable & Vision Zéro, itinérance et sécurité des écoles — district de Jeanne-Mance).

#### Projets intéressants (`/projets/`)

Projets créés par des amis:
1. **Simulateur TC — ARTM** → https://live-transit.regardemon.site
2. **Carte des trajets Bixi** → https://etienneld.com/bixi-trajets-2025/
3. **CartoMTL : le GeoGuessr de Montréal** → https://cartomtl.com

#### Don (`/don/`)

Page pour faire un don.

### Applications (`/applications/`)

- **Compteurs Vélo Montréal** → https://compteurvelo.com
- **Pistes cyclables Plateau** → https://pistes.gabfortin.com
- **Stationnement Plateau** → https://parking.gabfortin.com
- **Déchets Montréal** → https://dechets.gabfortin.com

## Mise en page des sections de contenu

Les pages `cartes/`, `donnees/` et `articles/` n'ont plus de `<h2 class="section-label">` au-dessus de leur grille/liste (ex. « Cartes Disponibles », « Ensembles de Données », « Articles et plans ») — retiré pour alléger la page. Leur `<section class="section">` principale porte en plus la classe `.section-top-tight` (définie dans `css/site.css`, à côté de `.section`), qui réduit le `padding-top` de `3.5rem` à `2rem` pour compenser l'absence du label. Si un label est réintroduit sur une de ces pages, retirer `.section-top-tight` pour revenir à l'espacement standard.

## Favicon

Les icônes d'onglet sont la photo de Gabriel en cercle, générées par `scripts/favicon.py` à partir de `img/Gabriel Fortin.png` (recadrage centré sur le visage, réglable en tête du script) :

- `favicon.ico` (16/32/48 px) : à la racine, pour les outils qui le cherchent sans lire le HTML
- `favicon-48.png`, `favicon-192.png` : icônes d'onglet et de résultats Google (cercle sur fond transparent)
- `apple-touch-icon.png` (180 px) : écran d'accueil iOS ; photo carrée pleine, car iOS arrondit les coins lui-même et remplit la transparence en noir

La barre de navigation n'affiche plus de logo : un lien texte « Accueil » (`.nav-home`, `aria-current="page"` sur l'accueil) est à gauche, les autres liens à droite. L'image du flux RSS reste l'ancien logo : `favicon-96.png`, dérivé de `favico.png` (1254 px, 1,4 Mo, plus chargé par les pages). Le script n'y touche pas.

Chaque page doit inclure, à la fin du `<head>` :

```html
<script data-goatcounter="https://gabfortin.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
```

La page `/confidentialite/` décrit ce que le site collecte. **La mettre à jour (et changer la date en bas de page) si on ajoute un outil ou un service externe** : formulaire, infolettre, vidéo intégrée, autre outil de statistiques, etc. Un lien « Confidentialité » figure dans le pied de page de chaque page.

Les cartes interactives ouvertes dans une fenêtre modale sont comptées comme des pages vues distinctes, ce qui permet de voir quelles cartes sont consultées.

## Liens et chemins
- Tous les liens utilisent des chemins relatifs
- **Exception : `404.html`** utilise des chemins absolus (`/css/site.css`), car GitHub Pages la sert à n'importe quelle URL introuvable, peu importe sa profondeur. Elle ne s'affiche donc correctement qu'en ligne ou via un serveur local (`python3 -m http.server`). Les visites de pages introuvables apparaissent dans GoatCounter avec le préfixe `404`, ce qui permet de repérer les liens brisés.
- Les images sous la ligne de flottaison ont `loading="lazy"` (chargement différé). Ne pas le mettre sur le logo ni sur la première image visible d'une page.
- Les fils d'Ariane relient chaque page à sa section ; la barre de navigation est sur chaque page.

## Notes techniques

- **Base** : HTML, CSS et JavaScript sans framework ni étape de build
- **Mise en page adaptative** : ordinateur, tablette, téléphone
- **Animations** : keyframes CSS (fadeIn, slideIn, glow, float, badgePulse)
- **Verre dépoli** : `blur`, `backdrop-filter`
- **Accessibilité** : fils d'Ariane, navigation logique, HTML sémantique
- **Statistiques** : GoatCounter (voir [CONTENU.md](CONTENU.md), « Statistiques de visite »)
- **SEO / IA** : Open Graph, JSON-LD (schema.org), `sitemap.xml`, `llms.txt`, flux RSS
- **Performance** : aucune dépendance externe (sauf les bibliothèques des cartes interactives)
- **Police** : Inter variable hébergée localement dans `fonts/` (licence SIL OFL, `fonts/OFL.txt`), déclarée en haut de `css/site.css`. Ne pas remettre le lien Google Fonts.
- **Images** : les balises `<img>` utilisent des fichiers `.webp` redimensionnés à la taille d'affichage (×2 à ×3 pour les écrans Retina). Les originaux PNG/JPG sont conservés pour `og:image`, le JSON-LD et le flux RSS, car certains réseaux sociaux acceptent mal le WebP. Pour une nouvelle image : la convertir en WebP (qualité 85) et garder l'original à côté si elle sert d'aperçu de partage.
- **Images de partage de l'accueil et de `/don`** : `img/og-accueil.jpg` et `img/og-don.jpg` (1200 × 630, même famille que celles d'avantapres et de montrealaccessible.ca) sont faites à partir du gabarit `scripts/og-image.html` (`?page=don` pour la seconde). Pour les modifier, éditer le gabarit, puis suivre les étapes en commentaire en tête du fichier.
