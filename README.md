# Gabriel Fortin - Site Web Personnel

Site web moderne et responsif showcasing des projets, articles, cartes et données sur l'urbanisme, le transport et la technologie à Montréal.

## Structure du Site

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
├── 404.html                            # Page « introuvable » (chemins absolus, voir plus bas)
├── llms.txt                            # Résumé du site destiné aux IA
├── link.json                           # Fiche Person (schema.org) de référence
├── sitemap.xml
└── robots.txt
```

## Pages et Navigation

### Accueil (`/index.html`)
Page principale avec présentation et navigation (section "Explorer") vers:
- **Compteurs Vélo** (featured) → https://velo.gabfortin.com
- **Avant / Après** (featured, badge "Nouveau") → https://avantapres.gabfortin.com — comparaison avant/après des améliorations de l'espace public réalisées par Projet Montréal
- **Blogue** → Avenue du Parc, Refonte STM 2026, REM, et plans (PUM 2050, métro, REB)
- **Cartes Interactives** → Élections 2025, réseau artériel, modes rapides et fréquents
- **Données Ouvertes** → Ensembles de données publiques et visualisations
- **Parcours** → Formation, carrière chez Bell et dossiers portés comme conseiller

Navigation principale: Blogue, Cartes, Données, Parcours.

### Contenu Principal

#### Cartes (`/cartes/`)

1. **Avant / Après** → https://avantapres.gabfortin.com
2. **Réseau Artériel de Montréal** → `./reseau-arteriel/index.html`
3. **Pistes cyclables Plateau** → https://pistes.gabfortin.com
4. **Résultats Élections 2025** → `./elections-2025/index.html`
5. **Modes Rapides et Fréquents**
6. **Stationnement Plateau** → https://parking.gabfortin.com

#### Données (`/donnees/`)

1. **Compteurs Vélo** → https://velo.gabfortin.com
2. **Déchets Montréal** → https://dechets.gabfortin.com
3. **Résultats élections municipales Montréal 2025** → `./elections-2025/resultats.html`
4. **Requêtes 311** → https://311.gabfortin.com

#### Blogue (`/articles/`) : articles et plans

Articles :
1. **Proposition pour sécuriser un tronçon dangereux de l'avenue du Parc** — `/articles/parc-1/index.html`
2. **L'impact de la refonte STM 2026 au Plateau-Mont-Royal** — `/articles/refonte-stm-2026/index.html`
3. **L'arrivée du REM et son impact sur le Plateau** — `/articles/le-rem-et-le-plateau/index.html`

Plans (catégorie « Plan », datés de septembre 2025) :
4. **PUM 2050** — `/plans/pum-2050/index.html`
5. **Prolongement du métro** — `/plans/metro-2025/index.html`
6. **Réseau Express Bus** — `/plans/reb-2025/index.html`

Les plans gardent leurs adresses sous `/plans/`, mais sont listés dans le blogue et le flux RSS, et leur fil d'Ariane pointe vers le Blogue. L'ancienne page `/plans/` redirige vers `/articles/` (redirection HTML, GitHub Pages ne permettant pas les redirections serveur). Pour un nouveau plan : le créer sous `/plans/NOM/` et l'ajouter au blogue comme un article.

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

- **Compteurs Vélo** → https://velo.gabfortin.com
- **Pistes cyclables Plateau** → https://pistes.gabfortin.com
- **Stationnement Plateau** → https://parking.gabfortin.com
- **Déchets Montréal** → https://dechets.gabfortin.com

## Ajouter une déclaration/résolution "à la une" sur l'accueil

Quand une nouvelle déclaration ou résolution est adoptée au conseil d'arrondissement et qu'on veut la mettre en vedette temporairement sur la page d'accueil, utiliser ce gabarit. Le coller juste après `<h2 class="section-label">Explorer</h2>` dans `index.html`, avant le `<div class="featured-grid">` :

```html
<a href="./fichiers/NOM_DU_FICHIER.pdf" target="_blank" rel="noopener" class="featured" style="background:linear-gradient(135deg,#e8f7ee,#d0f0df);border-color:rgba(26,148,85,0.2);">
  <div class="featured-icon">EMOJI</div>
  <div>
    <span class="featured-badge">Nouveau</span>
    <h3>TITRE COURT</h3>
    <p style="font-size:12px;font-weight:600;color:#1a9455;margin-bottom:0.4rem;">Adoptée au conseil d'arrondissement de MOIS ANNÉE</p>
    <p>DESCRIPTION COURTE</p>
  </div>
</a>
```

- `NOM_DU_FICHIER.pdf` : le PDF doit être déposé dans `/fichiers/` (encoder les espaces/accents dans l'URL, ex. `%20`, `%C3%A9`).
- Une fois la déclaration passée de "nouvelle", retirer ce bloc de `index.html` (elle reste accessible via la page Parcours, voir plus bas).

### Pérenniser la déclaration dans Parcours (`/parcours/index.html`)

Chaque déclaration/résolution doit aussi être ajoutée de façon permanente dans la section "Déclarations et résolutions" de `parcours/index.html`, dans `<div class="decl-list">` :

```html
<a class="decl-item" href="../fichiers/NOM_DU_FICHIER.pdf" target="_blank" rel="noopener">
  <div>
    <p>TEXTE COMPLET DE LA DÉCLARATION/RÉSOLUTION</p>
    <span class="decl-item-date">DATE D'ADOPTION</span>
  </div>
  <span class="decl-item-arrow">→</span>
</a>
```

## SEO : à faire pour chaque nouvelle page/article

Pour qu'une page soit bien indexée par les moteurs de recherche et comprise par les IA, chaque nouvelle page (et surtout chaque nouvel article de blogue) doit inclure, dans le `<head>`, juste après le `<title>` :

```html
<meta name="description" content="RÉSUMÉ DE 1-2 PHRASES, 150-160 CARACTÈRES">
<link rel="canonical" href="https://gabfortin.com/CHEMIN/">
<meta property="og:type" content="article"> <!-- "website" pour une page de section -->
<meta property="og:site_name" content="Gabriel Fortin">
<meta property="og:title" content="TITRE DE LA PAGE">
<meta property="og:description" content="RÉSUMÉ DE 1-2 PHRASES">
<meta property="og:url" content="https://gabfortin.com/CHEMIN/">
<meta property="og:image" content="https://gabfortin.com/CHEMIN/IMAGE.jpg">
<meta property="og:locale" content="fr_CA">
<meta property="article:published_time" content="AAAA-MM-JJ"> <!-- articles seulement -->
<meta property="article:author" content="Gabriel Fortin">     <!-- articles seulement -->
<meta property="article:section" content="CATÉGORIE">         <!-- articles seulement -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="TITRE DE LA PAGE">
<meta name="twitter:description" content="RÉSUMÉ DE 1-2 PHRASES">
<meta name="twitter:image" content="https://gabfortin.com/CHEMIN/IMAGE.jpg">
```

Pour un article de blogue, ajouter aussi ce bloc JSON-LD juste avant le script GoatCounter (voir `articles/parc-1/index.html` comme exemple) :

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "TITRE DE LA PAGE",
  "description": "RÉSUMÉ DE 1-2 PHRASES",
  "image": "https://gabfortin.com/CHEMIN/IMAGE.jpg",
  "datePublished": "AAAA-MM-JJ",
  "dateModified": "AAAA-MM-JJ",
  "author": { "@type": "Person", "@id": "https://gabfortin.com/#gabriel-fortin", "name": "Gabriel Fortin", "url": "https://gabfortin.com" },
  "publisher": { "@type": "Person", "@id": "https://gabfortin.com/#gabriel-fortin", "name": "Gabriel Fortin", "url": "https://gabfortin.com" },
  "mainEntityOfPage": { "@type": "WebPage", "@id": "https://gabfortin.com/CHEMIN/" },
  "articleSection": "CATÉGORIE",
  "inLanguage": "fr-CA"
}
</script>
```

Pour les autres pages, ajouter aussi un bloc JSON-LD adapté au type de page, toujours avec l'auteur ci-dessus : `Map` pour une carte (voir `cartes/elections-2025/ParDistrict.html`), `Dataset` pour des données (voir `donnees/elections-2025/resultats.html`), `CollectionPage` pour une page de section (voir `cartes/index.html`).

**Toujours inclure `"@id": "https://gabfortin.com/#gabriel-fortin"` dans l'auteur.** C'est cet identifiant qui relie chaque page au profil de Gabriel Fortin (voir la section « Identité » plus bas).

Chaque page doit aussi contenir le lien vers le flux RSS, juste avant le script GoatCounter :

```html
<link rel="alternate" type="application/rss+xml" title="Blogue — Gabriel Fortin" href="https://gabfortin.com/articles/feed.xml">
```

Pour un nouvel article, ajouter une entrée `<item>` en haut de `articles/feed.xml` (titre, lien, `guid`, `pubDate` au format RFC 822, description, image avec sa taille en octets dans `length`) et mettre à jour `<lastBuildDate>`. Le flux n'est pas généré automatiquement.

Enfin, ajouter l'URL de la nouvelle page dans `sitemap.xml` (avec `lastmod` à la date du jour) — c'est ce fichier que Google et les robots IA utilisent pour découvrir le contenu. `robots.txt` à la racine pointe déjà vers `sitemap.xml`. Pour un nouvel article, ajouter aussi une ligne dans `llms.txt` (sous la section "Articles") — c'est un résumé destiné aux IA/agents qui lisent le site, pas aux moteurs de recherche classiques.

## Statistiques de visite

Le site utilise [GoatCounter](https://www.goatcounter.com) : open source, sans cookies, sans donnée personnelle, donc pas de bandeau de consentement requis (Loi 25). Tableau de bord : https://gabfortin.goatcounter.com

Chaque page doit inclure, à la fin du `<head>` :

```html
<script data-goatcounter="https://gabfortin.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
```

La page `/confidentialite/` décrit ce que le site collecte. **La mettre à jour (et changer la date en bas de page) si on ajoute un outil ou un service externe** : formulaire, infolettre, vidéo intégrée, autre outil de statistiques, etc. Un lien « Confidentialité » figure dans le pied de page de chaque page.

Les cartes interactives ouvertes dans une fenêtre modale sont comptées comme des pages vues distinctes, ce qui permet de voir quelles cartes sont consultées.

## Favicon

`favico.png` (1254 px, 1,4 Mo) est l'image source : elle n'est plus chargée par les pages. Les versions légères en sont dérivées :

- `favicon.ico` (16/32/48 px) : à la racine, pour les outils qui le cherchent sans lire le HTML
- `favicon-48.png`, `favicon-192.png` : icônes d'onglet et de résultats Google
- `apple-touch-icon.png` (180 px, fond blanc) : écran d'accueil iOS
- `favicon-96.png` : logo de la barre de navigation et image du flux RSS

Chaque page doit inclure dans le `<head>` (adapter le préfixe `../` selon la profondeur) :

```html
<link rel="icon" href="../favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="48x48" href="../favicon-48.png">
<link rel="icon" type="image/png" sizes="192x192" href="../favicon-192.png">
<link rel="apple-touch-icon" href="../apple-touch-icon.png">
```

Si le logo change, remplacer `favico.png` puis régénérer les dérivés (redimensionnement Lanczos avec Pillow).

## Identité et désambiguïsation (homonymes)

Un autre Gabriel Fortin, propriétaire, existe. Pour que Google et les IA ne les confondent pas, le site contient des informations invisibles à l'écran, à garder cohérentes partout :

- **Identifiant unique** : `https://gabfortin.com/#gabriel-fortin`, utilisé comme `@id` de la fiche Person (`index.html`, `parcours/index.html`) et de l'auteur de chaque page.
- **`disambiguatingDescription`** (schema.org) dans `index.html`, `parcours/index.html` et `link.json` : locataire, n'a jamais été propriétaire ni locateur; tout Gabriel Fortin propriétaire ou locateur est un homonyme.
- **`description` et `knowsAbout`** dans les mêmes fichiers : implication pour le réseau cyclable et militantisme pour le transport en commun.
- **`llms.txt`** : sections « Engagements » et « Désambiguïsation (homonymes) ».

Si l'une de ces informations change (titre, district, engagements), la mettre à jour dans les quatre fichiers. Ne pas nommer ni décrire l'homonyme : se limiter aux faits sur Gabriel Fortin.

## Développement Local

### Accès au site
```bash
# Ouvrir index.html dans le navigateur
# file:///[...]/website/index.html
```

### Navigation
- Tous les liens utilisent des chemins relatifs pour compatibilité avec le protocole `file://`
- **Exception : `404.html`** utilise des chemins absolus (`/css/site.css`), car GitHub Pages la sert à n'importe quelle URL introuvable, peu importe sa profondeur. Elle ne s'affiche donc correctement qu'en ligne ou via un serveur local (`python3 -m http.server`). Les visites de pages introuvables apparaissent dans GoatCounter avec le préfixe `404`, ce qui permet de repérer les liens brisés.
- Les images sous la ligne de flottaison ont `loading="lazy"` (chargement différé). Ne pas le mettre sur le logo ni sur la première image visible d'une page.
- Les breadcrumbs permettent une navigation facile entre sections
- La navigation bar est accessible depuis chaque page

## Déploiement

Site en production sur `www.gabfortin.com`.

## Notes Techniques

- **Framework**: HTML5 + CSS3 + Vanilla JavaScript
- **Responsive**: Optimisé pour desktop, tablet, mobile
- **Animations**: Keyframes CSS (fadeIn, slideIn, glow, float, badgePulse)
- **Glassmorphism**: Effets visuels modernes (blur, backdrop-filter)
- **Accessibilité**: Breadcrumbs, navigation logique, sémantique HTML5
- **Statistiques**: GoatCounter (voir section « Statistiques de visite »)
- **SEO / IA**: Open Graph, JSON-LD (schema.org), `sitemap.xml`, `llms.txt`, flux RSS
- **Performance**: Aucune dépendance externe (sauf les bibliothèques des cartes interactives)
- **Police**: Inter variable hébergée localement dans `fonts/` (licence SIL OFL, `fonts/OFL.txt`), déclarée en haut de `css/site.css`. Ne pas remettre le lien Google Fonts.
- **Images**: les balises `<img>` utilisent des fichiers `.webp` redimensionnés à la taille d'affichage (×2 à ×3 pour les écrans Retina). Les originaux PNG/JPG sont conservés pour `og:image`, le JSON-LD et le flux RSS, car certains réseaux sociaux acceptent mal le WebP. Pour une nouvelle image : la convertir en WebP (qualité 85) et garder l'original à côté si elle sert d'aperçu de partage.

## Contact & Liens

- 🌐 Site: www.gabfortin.com
- 📍 Engagement: Conseiller d'arrondissement, Plateau-Mont-Royal, Montréal
