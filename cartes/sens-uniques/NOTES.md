# Sens uniques et parcours traversants — notes techniques

Carte des rues locales à sens unique du Plateau-Mont-Royal : en rouge celles
qui font partie d'un parcours en auto permettant d'entrer par une artère et
de ressortir par une autre artère en ne roulant que sur des rues locales, en
vert les autres. Créée en novembre 2026, à partir du principe « on entre dans
une cellule et on en ressort par le réseau supérieur » et de l'indicateur
proposé : la part des cellules sans parcours traversant.

Plateau seulement (choix de Gabriel). Le calcul tient compte des cellules qui
débordent de l'arrondissement.

## Fichiers

- `index.html` : la carte. Le calcul des parcours se fait **dans le
  navigateur** (`analyser()`), parce qu'on choisit dans le panneau les
  collectrices à traiter comme des artères ; il se refait en ~10 ms à chaque
  case cochée. CSS repris de `../collisions-reseau-arteriel/`, mode sombre par
  `../carte-sombre.css` + jetons `--su-*`.
- `data/reseau.json` : réseau exporté (format plus bas).
- `data/resume.json` : totaux du Plateau avec le réglage par défaut, calculés
  en Python (contrôle : la page doit afficher les mêmes).
- `data/meta.json` : date de préparation, version de la source, réglage par
  défaut.
- `script/preparer_sens_uniques.py` : exporte le réseau et calcule la
  référence (stdlib seulement). Même règle que `analyser()` : toute
  modification de l'une doit être reportée dans l'autre.
- `apercu.png` : image Open Graph 1200 × 630.

## Source

**Géobase - réseau routier**, Ville de Montréal, CC BY 4.0 :
https://donnees.montreal.ca/dataset/geobase (ressource GeoJSON de ~43 Mo,
version du 4 novembre 2026). **Ne pas commiter le fichier brut.**

La Géobase porte la même classification `CLASSE` (0 à 9) que le réseau
artériel administratif, dans sa version courante (la carte
`../reseau-arteriel/` utilise la version 2023 : quelques classes peuvent
différer). Elle porte surtout `SENS_CIR` : 0 = double sens, 1 = sens du
tracé, -1 = sens inverse. Le sens de 1 et -1 n'est pas décrit sur la page du
jeu ; il a été vérifié sur des rues connues (boulevard Saint-Laurent : 1, vers
le nord ; rue Saint-Urbain : -1, vers le sud).

## Règle (décisions de Gabriel, novembre 2026)

1. **Artères** = CLASSE 6 à 8, plus les collectrices cochées dans le panneau
   (**aucune par défaut** ; Rachel l'a été un moment, puis Gabriel l'a
   décochée). Une voie est identifiée par `TYP_VOIE` +
   `LIE_VOIE` + `NOM_VOIE`, sans `DIR_VOIE` (Mont-Royal Est et Ouest = même
   avenue).
2. **Cellule** = îlot délimité par les artères **seulement** : rues locales
   et collectrices non cochées, reliées par des nœuds qui ne touchent pas une
   artère. Ainsi le petit Laurier (avenue Laurier, collectrice, à
   l'intérieur) forme une seule cellule avec les rues voisines jusqu'à la
   prochaine artère. De Brébeuf est une rue locale dans la Géobase : elle ne
   délimite rien.
3. On ne roule « à l'intérieur » que sur les rues locales (CLASSE 0). Un nœud
   touché par une collectrice ou une artère (CLASSE 5 à 8) est une *porte* :
   un parcours y commence ou s'y arrête, sans la traverser.
4. **Parcours traversant** : entre par une artère X et ressort par une autre
   artère Y. Ressortir sur une collectrice non cochée est acceptable (ex. rue
   Fabre, tête-bêche : on doit tourner sur une collectrice).
5. Pour chaque paire ordonnée d'artères X ≠ Y d'une cellule : entrées =
   portes sur X mais pas sur Y ; sorties = portes sur Y mais pas sur X. Un arc
   u → v est sur un parcours traversant si u est une entrée, ou un nœud
   intérieur atteignable depuis une entrée, et si v est une sortie, ou un nœud
   intérieur depuis lequel une sortie est atteignable. (Un arc ne part jamais
   d'une porte où un parcours s'est arrêté : corrigé le 12 novembre 2026, ce
   bogue reliait deux parcours séparés par une collectrice.)
6. Statut des rues locales : 0 sens unique sans parcours traversant (vert),
   1 sens unique traversant (rouge), 2 double sens sans parcours traversant,
   3 double sens traversant (orange pointillé).

7. **Rues locales comptées comme ruelles** (liste du panneau, cochées par
   défaut, choix de Gabriel) : rue Généreux, rue De Varennes, rue Simard,
   rue Barrette, rue La Mennais, rue Latreille, rue De Courville, avenue
   Bureau, rue Lionais (ajoutée le 12 novembre 2026). Ce sont des rues locales (CLASSE 0) dans la Géobase, mais
   des ruelles en pratique : retirées du calcul comme les voies qui ne
   servent pas de passage, et non comptées dans les totaux. Les décocher les
   remet dans le calcul. Le script s'arrête si un de ces noms n'existe plus
   au Plateau.
8. **Scénario « Mont-Royal piétonne »** (case du panneau, décochée par
   défaut) : les 32 tronçons de l'avenue du Mont-Royal entre le boulevard
   Saint-Laurent et l'avenue De Lorimier (champ `pieton` de l'export) sont
   retirés du réseau. On ne peut plus y rouler ni y tourner, et ce ne sont
   plus des portes : les rues qui la croisent restent reliées au carrefour,
   donc on la traverse du nord au sud. Un carrefour avec une artère (Saint-
   Denis, Papineau…) reste une porte. Repérage dans
   `marquer_mont_royal_pieton()` : milieu du tronçon projeté entre les
   carrefours Mont-Royal/Saint-Laurent et Mont-Royal/De Lorimier, à moins de
   40 m de l'axe. Prioritaire sur la case « Avenue du Mont-Royal » des
   collectrices comptées comme artères.

Indicateur : part des cellules (qui ont au moins une rue locale au Plateau)
dont aucune rue locale du Plateau n'est de statut 1 ou 3.

Historique : une première version comptait aussi « artère → collectrice »
comme traversant, puis les cellules ont été délimitées par les collectrices,
puis par les collectrices qui vont d'une artère à une autre. Gabriel a choisi
la règle ci-dessus (artères seulement, avec exceptions au choix).

### Exemple : rue Aylmer (Milton-Parc)

Rouge malgré le tête-bêche : dans la Géobase, ses deux sens se rencontrent à
Prince-Arthur (pas à Milton), et Milton est une rue locale à sens unique vers
l'ouest jusqu'à University. Sherbrooke → Aylmer → Milton → University est donc
un parcours d'artère à artère par des rues locales.

## Chiffres de contrôle (Géobase du 4 novembre 2026)

| Réglage | Cellules (sans parcours traversant) | Sens uniques rouges / verts | Double sens traversants / non |
|---|---|---|---|
| **Défaut** : aucune collectrice cochée, 9 ruelles (`resume.json`) | 65 (35, 54 %) | 256 / 339 | 85 / 74 |
| Défaut + Mont-Royal piétonne (`resume.json`, `mont_royal_pieton`) | 65 (35, 54 %) | 295 / 300 | 88 / 71 |
| Aucune collectrice, aucune ruelle | 64 (34, 53 %) | 286 / 314 | 104 / 97 |
| Rachel cochée, aucune ruelle | 75 (33, 44 %) | 382 / 218 | 138 / 63 |

Effet du scénario : les rues locales qui se terminaient sur Mont-Royal (une
sortie acceptable) continuent de l'autre côté et peuvent mener à une autre
artère, d'où plus de rouge. Les cellules ne changent pas : Mont-Royal, une
collectrice, n'en délimitait aucune.

Vérifiés identiques entre le script Python et le navigateur (le 12 novembre
2026 ; les deux dernières lignes avant l'ajout des ruelles). Retirer les
ruelles peut couper une cellule en deux : 65 cellules au lieu de 64.

## Export (`data/reseau.json`)

Les cellules délimitées par les seules artères de CLASSE 6 à 8 sont les plus
grandes possibles : cocher une collectrice ne peut que les découper. Le script
exporte donc les tronçons du Plateau, ceux de ces cellules qui touchent le
Plateau et les collectrices et artères qui touchent leurs nœuds (2 266
tronçons). Il vérifie que le calcul sur cet export donne les mêmes totaux que
sur toute l'île, et s'arrête sinon.

```json
{ "noms": ["Rue de Bordeaux", ...],
  "troncons": [[ID_TRC, [[lng, lat], ...], CLASSE, sens_unique, nom, noeud_A, noeud_B, plateau, pieton], ...] }
```

Constante `T` en tête du script de `index.html`. Le tracé et les nœuds A → B
d'un sens unique sont dans le sens de la circulation (les flèches et les arcs
en dépendent). `plateau` = 1 : tronçon affiché et compté.

## Affichage

- Le réseau supérieur est en ardoise (pas aux couleurs du réseau artériel)
  pour que le rouge et le vert restent sans ambiguïté ; une collectrice cochée
  est dessinée comme une artère, en tirets.
- Flèches de sens dessinées par un calque canevas (`ArrowLayer`) à partir du
  zoom 15, une tous les ~90 px.
- Clic sur une rue : popup avec les paires X → Y, et sa cellule mise en
  évidence (les autres rues locales pâlissent, le réseau supérieur reste
  visible) jusqu'à la fermeture du popup.
- Le popup se déplace en le glissant (souris ou doigt, `rendreDeplacable()`)
  pour dégager la cellule : le décalage est gardé dans `options.offset`, donc
  il suit la rue quand on déplace la carte ; sa pointe est masquée une fois
  déplacé. `autoPan` est coupé au premier glisser.

- **Vue « Cellules »** (choix Rues / Cellules en haut du panneau, ajoutée le
  12 novembre 2026 à la demande de Gabriel) : chaque cellule comptée dans
  l'indicateur est remplie d'une teinte de rouge (0 %) à vert (100 %) selon
  la part, **en longueur**, de ses rues locales à sens unique au Plateau qui
  sont vertes (statut 0 / statuts 0 + 1) ; le % est écrit dessus. Gris : aucun
  sens unique local (pas d'étiquette). La surface est calculée dans le
  navigateur sur une grille de 4 m (`calculerGrille()`) : chaque case prend
  la cellule de la rue la plus proche (rues locales et collectrices de la
  cellule, au Plateau), sans franchir une artère (murs) et à au plus 90 m
  d'une rue ; les cellules remplissent donc l'espace entre les artères, le
  milieu d'un grand parc reste vide et, au bord du Plateau sans artère (voie
  ferrée), la surface s'arrête à 90 m des rues. Image posée par
  `L.imageOverlay` dans le volet `cellules`, refaite seulement quand le
  calcul change ; l'étiquette va au point le plus éloigné du bord. Une première
  version (enveloppe convexe des rues) a été jugée trop approximative par
  Gabriel. Une étiquette n'est affichée que si la cellule mesure
  au moins 46 × 30 px à l'écran (`majEtiquettes()`, refait à chaque zoom).
  Même calcul que la vue Rues : les réglages du panneau s'appliquent.

## Limites (affichées dans la modale)

- Pas d'interdictions de virage ni d'accès réservés dans la Géobase ; des
  fermetures récentes (saillies, filtres modaux, inversions) peuvent manquer.
  Un rouge peut être fermé en réalité.
- La Ville avertit que la Géobase n'est pas nécessairement à jour partout.
- La carte montre les parcours possibles, pas les débits.

## Régénérer les données

```
cd script
python3 preparer_sens_uniques.py chemin/geobase.json 2026-11-04
```

(date = « Dernière modification des données » de la ressource GeoJSON). Le
script s'arrête sur une géométrie ou un `SENS_CIR` inattendus, ou si l'export
ne suffit pas au calcul. Comparer `resume.json` avec ce que la page affiche
(réglage par défaut), mettre à jour le tableau ci-dessus, puis refaire
`apercu.png`. Le réglage par défaut est écrit à deux endroits :
`DEFAUT_COMME_ARTERES` et `DEFAUT_RUELLES` dans le script, `state.commeArteres`
et `state.ruelles` dans `index.html`.
