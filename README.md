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
├── articles/
│   ├── index.html                      # Liste des articles
│   ├── refonte-stm-2026/
│   │   └── index.html                  # Article: Refonte STM 2026
│   └── le-rem-et-le-plateau/
│       └── index.html                  # Article: REM et Plateau
├── plans/
│   └── index.html                      # Plans urbains
└── donnees/
    └── index.html                      # Données ouvertes
```

## Pages et Navigation

### Accueil (`/index.html`)
Page principale avec présentation et navigation vers:
- **Cartes Interactives** → Élections 2025, réseau artériel, modes rapides et fréquents
- **Articles & Analyses** → Refonte STM 2026, REM et impact sur le Plateau
- **Plans Urbains** → PUM 2050, prolongement métro, REB Projet Montréal
- **Données Ouvertes** → Ensembles de données publiques et visualisations
- **Applications** → Projets et outils développés
- Domaines d'intérêt: Mobilité, Données, Urbanisme, Technologie
- Engagement civique: Projet Montréal, Conseil d'Arrondissement

### Contenu Principal

#### Articles (`/articles/`)

**Articles publiés:**

1. **L'impact de la refonte STM 2026 au Plateau-Mont-Royal**
   - 📅 Date: 15 FEV 2026
   - 📂 Catégorie: Transport
   - 📍 Chemin: `/articles/refonte-stm-2026/index.html`
   - ✅ Statut: À créer (lien setup, contenu pending)
   - Description: Analyses détaillées de l'impact des changements des lignes de la STM en prévision de la branche A3 du REM

2. **L'arrivée du REM et son impact sur le Plateau**
   - 📅 Date: 15 NOV 2025
   - 📂 Catégorie: Urbanisme
   - 📍 Chemin: `/articles/le-rem-et-le-plateau/index.html`
   - ✅ Statut: À créer (lien setup, contenu pending)
   - Description: Analyse complète de l'arrivée du REM et impacts sur le Plateau-Mont-Royal


#### Cartes (`/cartes/`)

**Cartes interactives disponibles:**

1. **Réseau Artériel de Montréal** ✅
   - 📍 Chemin: `/cartes/reseau-arteriel/index.html`
   - 🖼️ Images: `Arteriel.png`, `Tout.png`
   - Carte 1 — Réseau artériel seulement: `arteriel-seulement.html` (local)
   - Carte 2 — Toutes les rues: `reseau-arteriel.html` (local)
   - Données: https://donnees.montreal.ca/dataset/reseau-arteriel-administratif

2. **Résultats Élections 2025** ✅
   - 📍 Chemin: `/cartes/elections-2025/index.html`
   - Carte 1 — Sections de vote: `ParSectionDeVote.html` (local)
   - Carte 2 — Sections de vote avec métro: `mairie2025-metro.html` (local)
   - Carte 3 — Mairie par district: `ParDistrict.html` (local)

3. **Modes Rapides et Fréquents**
   - 🚌 Icon: 🚌
   - 🔗 Lien: `#` → Placeholder
   - URL à fournir: https://www.gabfortin.com/blogue/cartes/rapide-et-fréquent
   - Description: Données des modes fréquents et rapides (STM et Pulsar)

4. **Données Ouvertes ARTM** ✅
   - 🚆 Icon: 🚆
   - 🔗 Lien: https://gabrielfortin.github.io/artm-map (✅ LIVE)
   - Description: Données ouvertes des opérateurs ARTM (STM, STL, RTL, Pulsar, exo)

#### Plans (`/plans/`)

**Plans:**

1. **PUM 2050**
   - 🚆 Icon: 🚆
   - 🔗 Lien: `#` → Placeholder
   - URL à fournir: https://www.gabfortin.com/blogue/plans/pum-2050
   - Description: Le Plan d'Urbanisme et de Mobilité (PUM) 2050 présente entre autres une vision 2040 et une vision 2050 avec une carte incluant des lignes de tram, SRB et prolongements de Métro qui devraient être priorisés. Voici un plan métropolitain incluant quelques propositions tirées du PUM.

2. **Prolongement métro**
   - 🚆 Icon: 🚆
   - 🔗 Lien: `#` → Placeholder
   - URL à fournir: https://www.gabfortin.com/plans/métro-projet-montréal
   - Description: Dans la plateforme 2025 de Projet Montréal, 2 prolongements de métro sont proposés

3. **Réseau Express Bus**
    - 🚆 Icon: 🚆
    - 🔗 Lien: `#` → Placeholder
    - URL à fournir: https://www.gabfortin.com/plans/reb-projet-montréal
    - Description: Dans la plateforme 2025 de Projet Montréal, 11 axes sont identifiés comme futurs tramway ou SRB légers faisant partie du Réseau Express Bus (REB). Voici un plan des services lourds, fréquents et/ou rapides de la région métropolitaine de Montréal, incluant les lignes présentement en service ou en construction ainsi que les lignes proposées par Projet Montréal.

#### Données (`/donnees/`)

**Ensembles de données et statistiques:**

1. **Compteurs de Vélo**
   - 🚴 Icon: 🚴
   - 🔗 Lien: `#` → Placeholder
   - URL à fournir: https://velo.gabfortin.com
   - Description: Données détaillées des compteurs de vélo avec tendances et analyses en temps réel

2. **Résultats élections municipales Montréal 2025**
   - 👥 Icon: 👥
   - 🔗 Lien: `#` → Placeholder
   - URL à fournir: https://gabrielfortin.github.io/resultats
   - Description: Résultats des élections 2025.


### Applications (`/applications/`)

**Application phare:**

0. **Compteurs de Vélo Montréal** ⭐ ✅
   - 🚴 Icon: 🚴
   - 🔗 Lien: https://velo.gabfortin.com/ (✅ LIVE)
   - Description: Visualisation en temps réel des compteurs de vélo à Montréal avec tendances et comparaisons
   - Statut: Production

**Autres applications:**


## Développement Local

### Accès au site
```bash
# Ouvrir index.html dans le navigateur
# file:///Users/gabfortin/Developer/website/index.html
```

### Navigation
- Tous les liens utilisent des chemins relatifs pour compatibilité avec le protocole `file://`
- Les breadcrumbs permettent une navigation facile entre sections
- La navigation bar est accessible depuis chaque page

## Déploiement

Pour déployer en production sur `www.gabfortin.com`:
1. S'assurer que tous les placeholders sont remplacés par les URLs réelles
2. Mettre à jour les domaines d'accès (actuellement file://)
3. Uploader les fichiers vers l'hébergement web
4. Configurer les redirections DNS

## À Faire

- [ ] Implémenter contenu pour tous les articles placeholders
- [ ] Créer/lier les cartes interactives placeholders
- [ ] Créer/lier les plans placeholders
- [ ] Créer/lier les données/visualisations placeholders
- [ ] Implémenter les applications placeholders
- [ ] Déployer en production

## Notes Techniques

- **Framework**: HTML5 + CSS3 + Vanilla JavaScript
- **Responsive**: Optimisé pour desktop, tablet, mobile
- **Animations**: Keyframes CSS (fadeIn, slideIn, glow, float)
- **Glassmorphism**: Effets visuels modernes (blur, backdrop-filter)
- **Accessibilité**: Breadcrumbs, navigation logique, sémantique HTML5
- **Performance**: Pas de dépendances externes (sauf polices Google)

## Contact & Liens

- 📧 Email: info@gabfortin.com (à mettre à jour)
- 🌐 Site: www.gabfortin.com (en développement)
- 📍 Engagement: Plateau-Mont-Royal, Montréal
