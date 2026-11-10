# Gabriel Fortin — site personnel

Site personnel de Gabriel Fortin, conseiller d'arrondissement du
Plateau-Mont-Royal (district de Jeanne-Mance) : blogue, cartes, données,
applications et parcours, sur l'urbanisme, le transport et la mobilité à
Montréal. C'est aussi la porte d'entrée vers tous ses autres sites.

**En ligne :** [gabfortin.com](https://gabfortin.com)

## Contenu

| Section | Ce qu'elle montre |
|---|---|
| **Accueil** (`/`) | Présentation, projets en vedette (Compteurs Vélo Montréal, Avant / Après), déclaration « à la une » si besoin, accès aux sections |
| **Blogue** (`/articles/`) | Articles et plans, avec recherche et filtre par catégorie ; flux RSS (`articles/feed.xml`) |
| **Cartes** (`/cartes/`) | Cartes hébergées ici (réseau artériel, élections 2025, modes rapides et fréquents) et liens vers les cartes autonomes |
| **Données** (`/donnees/`) | Tableaux de bord (Compteurs Vélo Montréal, ARTM, Déchets, 311) et résultats des élections 2025 |
| **Applications** (`/applications/`) | Outils autonomes (Compteurs Vélo Montréal, Pistes, Stationnement, Déchets) |
| **Parcours** (`/parcours/`) | Formation, carrière, dossiers portés comme conseiller, déclarations et résolutions |
| **Projets intéressants** (`/projets/`) | Projets créés par des ami·es |
| **Don** (`/don/`) | Faire un don |

Liste détaillée des pages et de leurs liens : [ARCHITECTURE.md](ARCHITECTURE.md).

## Données

Le site n'a pas de robot. Les cartes et données hébergées ici (élections
2025, réseau artériel…) indiquent leur source dans leur page ; les
déclarations et résolutions sont des PDF dans `fichiers/`.

## Utilisation locale

```bash
python3 -m http.server 8000   # http://localhost:8000
```

Les liens sont relatifs, sauf dans `404.html` (chemins absolus) : un serveur
est nécessaire pour l'afficher correctement.

## Architecture

| Fichier | Rôle |
|---|---|
| `index.html` et un dossier par section | Pages (HTML statique) |
| `css/site.css` | Styles communs (style A) |
| `articles/feed.xml` | Flux RSS, mis à jour à la main |
| `fichiers/` | PDF des déclarations et résolutions |
| `fonts/` | Police Inter hébergée dans le dépôt (SIL OFL) |
| `scripts/favicon.py`, `scripts/og-image.html` | Icônes d'onglet, gabarit des images de partage |
| `404.html` | Page « introuvable » |
| `llms.txt`, `link.json`, `sitemap.xml`, `robots.txt` | Référencement, fiche Person de référence |

**Style A (éditorial)** de [DESIGN-PAGES.md](../DESIGN-PAGES.md). Pas de
bouton « i » : le site est lui-même la présentation de son auteur. Arborescence
complète, pages, favicon, notes techniques : [ARCHITECTURE.md](ARCHITECTURE.md).

## Publication

GitHub Pages, branche `main`, domaine `gabfortin.com` dans `CNAME`. (Ce site
n'a pas de numéro de version x.y.z.)

**À chaque nouvelle page ou article** : métadonnées, JSON-LD, flux RSS,
`sitemap.xml` et `llms.txt`, selon la liste de [CONTENU.md](CONTENU.md),
« SEO ».

## Confidentialité

Aucun cookie ni compte.

| Quand | Ce qui est envoyé | À qui |
|---|---|---|
| Chaque visite | Page, site d'origine, appareil, pays | GoatCounter (mesure d'audience anonyme) |
| Ouverture d'une carte interactive | Bibliothèques et tuiles de la carte | Selon la carte (CDN, OpenStreetMap) |

La page [/confidentialite/](confidentialite/index.html) décrit ce que le site
collecte : **la mettre à jour (avec sa date)** si on ajoute un outil ou un
service externe (formulaire, infolettre, vidéo intégrée…).

## Auteur

Développé par Gabriel Fortin.

## Documentation détaillée

| Fichier | Contenu |
|---|---|
| [CONTENU.md](CONTENU.md) | Déclaration « à la une », liste SEO pour une nouvelle page, identité et homonymes, statistiques de visite |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Arborescence, pages et leurs liens, mise en page des sections, favicon, chemins, notes techniques |
