# Modifier le contenu — gabfortin.com

Procédures pour ajouter ou changer du contenu. Vue d'ensemble : [README.md](README.md) ; structure et pages : [ARCHITECTURE.md](ARCHITECTURE.md).

## Ajouter une déclaration ou résolution « à la une » sur l'accueil

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

## SEO : à faire pour chaque nouvelle page ou article

Règles communes à tous les projets : [SEO-ET-PUBLICATION.md](../SEO-ET-PUBLICATION.md). Propre à gabfortin.com :

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

**Toujours inclure `"@id": "https://gabfortin.com/#gabriel-fortin"` dans l'auteur.** C'est cet identifiant qui relie chaque page au profil de Gabriel Fortin (voir « Identité et désambiguïsation » ci-dessous).

Chaque page doit aussi contenir le lien vers le flux RSS, juste avant le script GoatCounter :

```html
<link rel="alternate" type="application/rss+xml" title="Blogue — Gabriel Fortin" href="https://gabfortin.com/articles/feed.xml">
```

Pour un nouvel article, ajouter une entrée `<item>` en haut de `articles/feed.xml` (titre, lien, `guid`, `pubDate` au format RFC 822, description, image avec sa taille en octets dans `length`) et mettre à jour `<lastBuildDate>`. Le flux n'est pas généré automatiquement.

Enfin, ajouter l'URL de la nouvelle page dans `sitemap.xml` (avec `lastmod` à la date du jour) — c'est ce fichier que Google et les robots IA utilisent pour découvrir le contenu. `robots.txt` à la racine pointe déjà vers `sitemap.xml`. Pour un nouvel article, ajouter aussi une ligne dans `llms.txt` (sous la section "Articles") — c'est un résumé destiné aux IA/agents qui lisent le site, pas aux moteurs de recherche classiques.

## Identité et désambiguïsation (homonymes)

Un autre Gabriel Fortin, propriétaire, existe. Pour que Google et les IA ne les confondent pas, le site contient des informations invisibles à l'écran, à garder cohérentes partout :

- **Identifiant unique** : `https://gabfortin.com/#gabriel-fortin`, utilisé comme `@id` de la fiche Person (`index.html`, `parcours/index.html`) et de l'auteur de chaque page.
- **`disambiguatingDescription`** (schema.org) dans `index.html`, `parcours/index.html` et `link.json` : locataire, n'a jamais été propriétaire ni locateur; tout Gabriel Fortin propriétaire ou locateur est un homonyme. Précise aussi qu'il **n'est pas étudiant** (quelques cours de 2e cycle en urbanisme suivis en 2023-2024, en parallèle de sa carrière), car des IA le décrivaient comme étudiant en urbanisme. La fiche de l'accueil et `link.json` incluent aussi `worksFor`, `memberOf` (OIQ) et `hasOccupation` (conseiller depuis 2025-11).
- **`description` et `knowsAbout`** dans les mêmes fichiers : implication pour le réseau cyclable et militantisme pour le transport en commun.
- **`llms.txt`** : sections « Engagements » et « Désambiguïsation (homonymes) ».

Si l'une de ces informations change (titre, district, engagements), la mettre à jour dans les quatre fichiers. Ne pas nommer ni décrire l'homonyme : se limiter aux faits sur Gabriel Fortin.

## Statistiques de visite

Le site utilise [GoatCounter](https://www.goatcounter.com) : open source, sans cookies, sans donnée personnelle, donc pas de bandeau de consentement requis (Loi 25). Tableau de bord : https://gabfortin.goatcounter.com

Chaque page doit inclure, à la fin du `<head>` :

```html
<script data-goatcounter="https://gabfortin.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
```

La page `/confidentialite/` décrit ce que le site collecte. **La mettre à jour (et changer la date en bas de page) si on ajoute un outil ou un service externe** : formulaire, infolettre, vidéo intégrée, autre outil de statistiques, etc. Un lien « Confidentialité » figure dans le pied de page de chaque page.

Les cartes interactives ouvertes dans une fenêtre modale sont comptées comme des pages vues distinctes, ce qui permet de voir quelles cartes sont consultées.
