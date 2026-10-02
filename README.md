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
│   ├── refonte-stm-2026/
│   │   └── index.html                  # Article: Refonte STM 2026
│   └── le-rem-et-le-plateau/
│       └── index.html                  # Article: REM et Plateau
└── parcours/
    └── index.html                      # Parcours professionnel et engagements
└── projets/
    └── index.html                      # Projets intéressants créés par des amis
```

## Pages et Navigation

### Accueil (`/index.html`)
Page principale avec présentation et navigation (section "Explorer") vers:
- **Compteurs Vélo** (featured) → https://velo.gabfortin.com
- **Avant / Après** (featured, badge "Nouveau") → https://avantapres.gabfortin.com — comparaison avant/après des améliorations de l'espace public réalisées par Projet Montréal
- **Cartes Interactives** → Élections 2025, réseau artériel, modes rapides et fréquents
- **Données Ouvertes** → Ensembles de données publiques et visualisations
- **Plans** → PUM 2050, prolongement métro, REB Projet Montréal
- **Blogue** → Refonte STM 2026, REM et impact sur le Plateau
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

1. **L'impact de la refonte STM 2026 au Plateau-Mont-Royal** — `/articles/refonte-stm-2026/index.html`
2. **L'arrivée du REM et son impact sur le Plateau** — `/articles/le-rem-et-le-plateau/index.html`

#### Parcours (`/parcours/`)

Formation, carrière (incl. passage chez Bell) et dossiers portés comme conseiller d'arrondissement (plan propreté 2026, mobilité durable & Vision Zéro, itinérance et sécurité des écoles — district de Jeanne-Mance).

#### Projets intéressants (`/projets/`)

Projets créés par des amis:
1. **Simulateur TC — ARTM** → https://live-transit.regardemon.site
2. **Carte des trajets Bixi** → https://etienneld.com/bixi-trajets-2025/
3. **CartoMTL : le GeoGuessr de Montréal** → https://cartomtl.com

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
- **Performance**: Pas de dépendances externes (sauf polices Google)

## Contact & Liens

- 🌐 Site: www.gabfortin.com
- 📍 Engagement: Conseiller d'arrondissement, Plateau-Mont-Royal, Montréal
