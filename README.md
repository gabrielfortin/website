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
│   └── index.html                      # Plans urbains
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
├── fichiers/                           # PDF des déclarations/résolutions
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
- **Cartes Interactives** → Élections 2025, réseau artériel, modes rapides et fréquents
- **Données Ouvertes** → Ensembles de données publiques et visualisations
- **Plans** → PUM 2050, prolongement métro, REB Projet Montréal
- **Blogue** → Avenue du Parc, Refonte STM 2026, REM et impact sur le Plateau
- **Parcours** → Formation, carrière chez Bell et dossiers portés comme conseiller

Navigation principale: Cartes, Données, Plans, Blogue, Parcours.

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

#### Plans (`/plans/`)

1. **PUM 2050** → `./pum-2050/index.html`
2. **Prolongement métro** → `./metro-2025/index.html`
3. **Réseau Express Bus** → `./reb-2025/index.html`

#### Articles (`/articles/`)

1. **Proposition pour sécuriser un tronçon dangereux de l'avenue du Parc** — `/articles/parc-1/index.html`
2. **L'impact de la refonte STM 2026 au Plateau-Mont-Royal** — `/articles/refonte-stm-2026/index.html`
3. **L'arrivée du REM et son impact sur le Plateau** — `/articles/le-rem-et-le-plateau/index.html`

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

Pour un article de blogue, ajouter aussi ce bloc JSON-LD juste avant le script Google Analytics (voir `articles/parc-1/index.html` comme exemple) :

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

Chaque page doit aussi contenir le lien vers le flux RSS, juste avant le script Google Analytics :

```html
<link rel="alternate" type="application/rss+xml" title="Blogue — Gabriel Fortin" href="https://gabfortin.com/articles/feed.xml">
```

Pour un nouvel article, ajouter une entrée `<item>` en haut de `articles/feed.xml` (titre, lien, `guid`, `pubDate` au format RFC 822, description, image avec sa taille en octets dans `length`) et mettre à jour `<lastBuildDate>`. Le flux n'est pas généré automatiquement.

Enfin, ajouter l'URL de la nouvelle page dans `sitemap.xml` (avec `lastmod` à la date du jour) — c'est ce fichier que Google et les robots IA utilisent pour découvrir le contenu. `robots.txt` à la racine pointe déjà vers `sitemap.xml`. Pour un nouvel article, ajouter aussi une ligne dans `llms.txt` (sous la section "Articles") — c'est un résumé destiné aux IA/agents qui lisent le site, pas aux moteurs de recherche classiques.

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
- **Analytics**: Google Analytics (gtag)
- **SEO / IA**: Open Graph, JSON-LD (schema.org), `sitemap.xml`, `llms.txt`, flux RSS
- **Performance**: Pas de dépendances externes (sauf polices Google)

## Contact & Liens

- 🌐 Site: www.gabfortin.com
- 📍 Engagement: Conseiller d'arrondissement, Plateau-Mont-Royal, Montréal
