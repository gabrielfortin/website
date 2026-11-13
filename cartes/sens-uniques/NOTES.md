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
   **Liens (12 novembre 2026)** : les voies où l'on ne roule pas (CLASSE 1 à
   4 et 9 : piétonnes, privées…) et les rues comptées comme ruelles, au
   Plateau, relient aussi les parties d'une cellule, sans servir de passage
   (`liens_cellules()` dans le script, boucle « Liens » dans `analyser()`).
   Sans elles, Sherbrooke / des Pins / Saint-Laurent / Saint-Denis donnait 4
   cellules (De Bullion, de l'Hôtel-de-Ville, Coloniale–Saint-Dominique,
   Laval–Henri-Julien), parce que Prince-Arthur y est piétonne ; De Courville
   rattache aussi Poitevin à sa cellule. Seulement au Plateau, parce que
   l'export ne contient pas ces voies ailleurs. Les statuts des rues ne
   changent pas (on ne roule pas sur les liens) ; 65 → 61 cellules.
3. On ne roule « à l'intérieur » que sur les rues locales (CLASSE 0). Un nœud
   touché par une collectrice ou une artère (CLASSE 5 à 8) est une *porte* :
   un parcours y commence ou s'y arrête, sans la traverser.
   **Exception (12 novembre 2026, choix de Gabriel)** : à un carrefour avec
   une collectrice non cochée (porte qui ne touche aucune artère), on
   traverse *tout droit* : une rue locale y continue sur la rue du même nom
   (`noeud()` dans `analyser()` et dans le script : le nœud est dédoublé par
   nom de rue). On n'y tourne pas sur une autre rue locale. « Tout droit » =
   même nom, faute d'information sur les mouvements dans la Géobase.
   Exemple : rue Marquette, Saint-Joseph → (Laurier) → Saint-Grégoire, rouge
   (elle était verte avant).
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
   3 double sens traversant (orange pointillé). Le statut 2 est en vert pointillé
   (gris avant le 12 novembre 2026, choix de Gabriel) ; le gris reste celui des
   cellules sans sens unique dans la vue Cellules.

7. **Rues locales comptées comme ruelles** (liste du panneau, cochées par
   défaut, choix de Gabriel) : rue Généreux, rue De Varennes, rue Simard,
   rue Barrette, rue La Mennais, rue Latreille, rue De Courville, avenue
   Bureau, rue Lionais (ajoutée le 12 novembre 2026), rue Saint-Christophe (ajoutée
   le 12 novembre 2026), ruelle Lavers (ajoutée le 12 novembre 2026). Ce sont des rues locales (CLASSE 0) dans la Géobase, mais
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

9. **Artères parallèles seulement** (case du panneau, **cochée par défaut**,
   12 novembre 2026, choix de Gabriel) : une paire X → Y n'est examinée que
   si X et Y sont parallèles, deux artères est-ouest ou deux nord-sud.
   Couper le coin entre une artère est-ouest et une nord-sud ne rend pas
   rouge ; relier deux artères parallèles est le rôle d'une collectrice, pas
   d'une rue locale. Orientation d'une artère = moyenne, en angle doublé, des
   tronçons de l'artère qui touchent les portes de la cellule (tracé de bout
   en bout, longitude × cos(latitude)) ; parallèles si l'écart est de moins
   de 45°. Au Plateau, les artères **est-ouest** sont à ~57° (Sherbrooke
   ~74°) et les **nord-sud** à ~147° : aucune près du seuil. Même règle dans
   `analyser()` (`state.paralleles`) et dans le script (`DEFAUT_PARALLELES`).

10. **Virages maximaux** (curseur du panneau, **3 par défaut** (5 au départ,
   puis 3, choix de Gabriel), 0 à 10, tout
   au bout = sans limite ; 12 novembre 2026, choix de Gabriel) : un parcours
   ne compte que s'il change de rue locale (nom différent ; un tronçon sans
   nom compte toujours comme un changement) au plus ce nombre de fois.
   Entrer et ressortir ne comptent pas ; traverser une collectrice tout droit
   non plus (même nom). Calcul par arc, parcours en largeur 0-1 :
   `virages()` dans la page et dans le script ; un arc compte si (virages
   minimaux depuis une entrée jusqu'à lui) + (virages minimaux de lui
   jusqu'à une sortie) ≤ maximum. Sans limite, on retombe sur `parcourir()`
   (vérifié : 100 virages = sans limite).
   Pourquoi pas une limite de détour en distance (essayée le même jour, puis
   retirée) : dans une grille, un zigzag n'est pas plus long qu'un détour par
   les artères ; même à 1 × la longueur par le réseau supérieur, seuls 5
   sens uniques passaient au vert. C'est le nombre de virages qui rend un
   zigzag improbable.
   Exemple, rue Boyer : à 5 virages, Gilford → Saint-Joseph devient vert (les
   parcours depuis Roy et Cherrier en demandaient 6 ou plus) ; Marie-Anne →
   Gilford reste rouge par Papineau → Marie-Anne → Boyer → Gilford → Chambord
   → Marie-Anne → Berri (4 virages : on contourne un îlot). À 3 virages
   (défaut), tout Boyer est vert.

Tableau calculé avant l'ajout de Saint-Christophe aux ruelles et des paires
artérielles (9 ruelles, sans exception) :

| Virages maximaux (défaut sinon) | 0 | 1 | 2 | 3 | 4 | **5** | 6 | 8 et + |
|---|---|---|---|---|---|---|---|---|
| Sens uniques rouges / verts | 165 / 430 | 180 / 415 | 271 / 324 | 297 / 298 | 356 / 239 | **356 / 239** | 359 / 236 | 362 / 233 |
| Cellules traversantes (sur 65) | 25 | 26 | 28 | 28 | 28 | **28** | 28 | 28 |

11. **Exception des paires artérielles** (case du panneau, **cochée par
   défaut**, 12 novembre 2026, choix de Gabriel) : De Lorimier + Papineau,
   Saint-Laurent + Saint-Urbain, Frontenac + D'Iberville sont des paires
   (une vers le nord, l'autre vers le sud). Une paire X → Y formée des deux
   artères d'une même paire n'est pas examinée : une rue locale peut les
   relier d'est en ouest. `PAIRES_ARTERIELLES` dans la page et dans le
   script ; le script s'arrête si un de ces noms n'est plus une artère au
   Plateau.

12. **Artères comptées comme rues locales** (cases du panneau, **cochées par
   défaut**, 12 novembre 2026, choix de Gabriel) : rue Jeanne-Mance et rue
   Léo-Pariseau. Leurs tronçons d'artère (CLASSE 7, entre Sherbrooke et des
   Pins) **au Plateau, et ceux qui touchent un nœud du Plateau** deviennent
   des rues locales (correction du 12 novembre 2026 : le bout de Jeanne-Mance
   au sud de Sherbrooke restait une artère, d'où une porte « Jeanne-Mance » et
   des paires Jeanne-Mance → du Parc / Saint-Urbain acceptées comme
   parallèles ; les statuts n'ont pas changé, mais le nom automatique de
   Milton-Parc est, oui : clé corrigée dans `noms-cellules.json`) : ils ne
   délimitent plus les cellules, on y roule et ils sont colorés. Page :
   `appliquerArteresLocales()` change `r[T.CLASSE]` avant `analyser()` (classe
   d'origine dans `r._c0`) ; script : `comme_locales()`. L'export prend les
   cellules avec ces rues locales (les plus grandes possibles). Le script
   s'arrête si un de ces noms n'est plus une artère au Plateau. Effet :
   61 → 59 cellules (Milton-Parc fusionne).

13. **Raccords** (12 novembre 2026) : la Géobase coupe la rue Clark à Bagg
   et à Saint-Cuthbert (deux nœuds à ~8 m, sans tronçon entre eux), ce qui
   séparait la cellule Saint-Laurent / Saint-Urbain / des Pins / Saint-Joseph
   en trois et coupait les parcours. `RACCORDS` dans le script ajoute un
   petit tronçon local à sens unique (dans le sens de Clark, vers le sud) à
   chaque endroit ; identifiants -1 et -2 dans l'export (ajoutés aussi à la
   main dans `data/reseau.json` le 12 novembre 2026, faute de Géobase brute :
   la prochaine régénération les recrée). Autres paires de nœuds locaux à
   moins de 9 m sans tronçon, non raccordées (à vérifier, certaines touchent
   des bouts piétons) : Napoléon / Saint-André (5,7 m), des Érables /
   Lafrance (7,6 m), Garnier / Gilford (8,1 m).
14. **Rues isolées** (12 novembre 2026, choix de Gabriel) : une cellule qui
   ne contient qu'une seule rue locale (un seul nom) est regroupée avec les
   autres dans une cellule « Rues isolées », comptée une fois dans
   l'indicateur, nommée et affichée comme une cellule. Les parcours restent
   calculés dans la vraie cellule. **Hors indicateur** (même jour, choix de
   Gabriel : ces rues ne correspondent pas au modèle) : « Rues isolées » ne
   compte pas comme une cellule, n'est ni dans la liste ni dans la vue
   Cellules ; ses tronçons restent colorés et comptés. `ISOLEES` (1e6 dans la page : la grille
   de la vue Cellules est en Int32 et -1 y veut dire « vide » ; "isolees"
   dans le script). Effet : 59 → 22 cellules ; l'indicateur passe de 69 % à
   41 %, car ces petites cellules étaient presque toutes vertes.

15. **Regroupement par nom** (12 novembre 2026, choix de Gabriel) : les
   cellules qui portent le même nom (choisi dans `data/noms-cellules.json`)
   sont regroupées dans la première, comme les rues isolées (compte, noms,
   affichage ; parcours inchangés). Sert à rattacher les bandes entre
   Saint-Laurent et Saint-Urbain (paire artérielle) à la cellule voisine à
   l'ouest : « des Pins / Saint-Laurent / Sherbrooke / Saint-Urbain » →
   Milton-Parc est, « Saint-Joseph / Saint-Laurent / des Pins / Saint-Urbain »
   → Parc Jeanne-Mance, « Saint-Laurent / Saint-Joseph / Saint-Urbain » →
   Mile-End ouest. Pour que le script donne les mêmes totaux, les noms
   automatiques y sont calculés de la même façon (`noms_automatiques()`,
   `regrouper_par_nom()` ; page : `nommerCellules()`), vérifiés identiques le
   12 novembre 2026. Effet : 22 → 19 cellules, 9 → 7 sans parcours
   traversant (41 % → 37 %).

16. **Parcours corrigeables** (case du panneau, **cochée par défaut**,
   12 novembre 2026, choix de Gabriel) : un parcours traversant ne compte que
   s'il traverse un *carrefour* où l'on pourrait le détourner : nœud
   intérieur où se rejoignent au moins trois tronçons de rues locales, ou
   croisement d'une collectrice non cochée (on peut y faire sortir les autos).
   Une rue qui va tout droit d'une artère à l'autre sans rien croiser n'a pas
   de solution par les sens uniques : elle reste verte. `virages()` suit deux
   états par arc (carrefour traversé ou non) ; un arc compte si
   min(av₁ + ap, av₀ + ap₁) ≤ maximum de virages. Sans limite de virages, on
   prend maintenant `virages()` avec une limite infinie (même résultat que
   `parcourir()`). Exemple : Square Saint-Louis, De Bullion et
   de l'Hôtel-de-Ville passent au vert ; Coloniale et Saint-Dominique restaient
   rouges (reliées par la ruelle Lavers) jusqu'à ce que la ruelle Lavers soit
   comptée comme ruelle (même jour) ; Laval reste rouge (croisée par la rue du Square-Saint-Louis, sens unique vers
   Saint-Denis). Marquette reste rouge dans le Petit Laurier (croisement de
   Laurier, collectrice). Effet : 263 / 336 → 254 / 345 sens uniques rouges /
   verts ; cellules inchangées.

17. **Artères comptées comme collectrices** (case du panneau, **cochée par
   défaut** depuis le 12 novembre 2026 au soir, choix de Gabriel ; cellule
   fusionnée nommée « Petit Laurier », les clés de l'ancien Petit Laurier et
   de Parc Ludger Duvernay restent dans `noms-cellules.json` pour l'option
   décochée ; le script vérifie l'export avec l'option décochée) : Saint-Grégoire
   (`ARTERES_COLLECTRICES` dans la page, `ARTERES_COLLECTRICES_POSSIBLES` et
   `comme_collectrices()` dans le script ; mêmes tronçons que pour les artères
   locales : au Plateau et ceux qui touchent un nœud du Plateau). Elle ne
   délimite plus les cellules et on la traverse tout droit. L'export prend les
   cellules avec cette option (les plus grandes possibles) et le script
   vérifie qu'il suffit aussi au calcul avec elle. Effet : le Petit Laurier
   rejoint la cellule au nord (Parc Ludger-Duvernay, jusqu'à Rosemont et
   Jean-Talon), à 100 % de sens uniques verts ; Plateau : 228 / 371,
   15 cellules (5 sans parcours traversant). Le nom choisi « Petit Laurier »
   ne s'applique plus à la cellule fusionnée (autre nom automatique).

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

## Chiffres de contrôle (Géobase du 4 novembre 2026, identiques avec celle du 12 novembre)

| Réglage | Cellules (sans parcours traversant) | Sens uniques rouges / verts | Double sens traversants / non |
|---|---|---|---|
| **Défaut** : artères parallèles, 3 virages, paires artérielles, Jeanne-Mance et Léo-Pariseau locales, Saint-Grégoire collectrice, raccords, rues isolées hors indicateur, cellules de même nom regroupées, parcours corrigeables, aucune collectrice cochée, 11 ruelles (`resume.json`) | 15 (5, 33 %) | 228 / 371 | 63 / 91 |
| Défaut + Mont-Royal piétonne (`resume.json`, `mont_royal_pieton`) | 15 (5, 33 %) | 228 / 371 | 63 / 91 |
| Défaut sans Saint-Grégoire collectrice | 18 (7, 39 %) | 247 / 352 | 65 / 89 |
| Défaut sans la ruelle Lavers ni Saint-Grégoire collectrice (10 ruelles) | 18 (7, 39 %) | 254 / 345 | 66 / 89 |
| Défaut sans « parcours corrigeables » | 18 (7, 39 %) | 263 / 336 | 67 / 88 |
| Défaut sans regroupement par nom | 22 (9, 41 %) | 263 / 336 | 67 / 88 |
| Défaut sans artères locales, sans regroupement par nom | 22 (9, 41 %) | 259 / 335 | 66 / 89 |
| Défaut à 5 virages | 22 (9, 41 %) | 320 / 279 | 91 / 64 |
| Défaut sans l'exception des paires | 22 (5, 23 %) | 298 / 301 | 76 / 79 |
| Défaut sans Saint-Christophe (9 ruelles) | 22 (9, 41 %) | 270 / 332 | 71 / 88 |
| Défaut, aucune ruelle | 22 (9, 41 %) | 291 / 316 | 104 / 97 |
| Défaut, Rachel cochée, aucune ruelle | 27 (7, 26 %) | 350 / 257 | 111 / 90 |

Les lignes « sans artères locales » et suivantes ont été calculées avant le
regroupement par nom (cellules : compter jusqu'à 3 de moins avec lui).

Avant les raccords et le regroupement des rues isolées : 59 cellules (41,
69 %), 263 / 334, 67 / 88.

Avant les liens entre parties de cellule, les mêmes réglages donnaient 65
cellules (42 sans parcours traversant au défaut).

Avant la traversée tout droit des collectrices (règle 3), le défaut donnait
65 (35, 54 %), 256 / 339, 85 / 74 ; avec Mont-Royal piétonne 295 / 300,
88 / 71. Depuis, le scénario Mont-Royal piétonne ne change plus les totaux :
on traversait déjà Mont-Royal tout droit, et la fermer n'ajoute pas de virage.

Chiffres de cette règle calculés avec le script sur `data/reseau.json` (la
Géobase brute n'était pas sur la machine) et vérifiés identiques dans le
navigateur le 12 novembre 2026. À la prochaine régénération, le script
revérifiera l'export sur toute l'île.

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

- **Noms des cellules** (12 novembre 2026) : `nommerCellules()` après
  `analyser()`. Nom automatique = artères qui bordent la cellule (portes des
  rues locales sur une artère, plus les artères touchées par les liens),
  triées par cap depuis le centre de la cellule, dans l'ordre nord, est,
  sud, ouest (nord de Montréal = ~147° depuis l'est, secteur de ±45°), sans
  le type de voie. Moins de 3 artères : la plus longue rue locale de la
  cellule au Plateau, puis les artères entre parenthèses. Doublons : (2),
  (3)… **Noms choisis** dans `data/noms-cellules.json` (`noms` : nom
  automatique → nom choisi ; facultatif). La clé est le nom automatique au
  réglage par défaut : si une règle change les artères d'une cellule, son
  nom choisi ne s'applique plus (vérifier la liste du panneau). Affichés
  dans le popup d'une rue (« Sa cellule »), la fiche d'une cellule, la vue
  Cellules (au-dessus du %, seulement si le nom tient dans la cellule à
  l'écran) et la liste « Cellules » du panneau (de la plus faible part de
  verts à la plus forte ; un clic centre la carte et ouvre la fiche).

## Limites (affichées dans la modale)

- Pas d'interdictions de virage ni d'accès réservés dans la Géobase ; des
  fermetures récentes (saillies, filtres modaux, inversions) peuvent manquer.
  Un rouge peut être fermé en réalité.
- La Ville avertit que la Géobase n'est pas nécessairement à jour partout.
- La carte montre les parcours possibles, pas les débits.

## Régénération du 12 novembre 2026

Données refaites avec la Géobase du 12 novembre 2026 (ressource GeoJSON
modifiée le jour même) : `reseau.json` identique à celui de la version du
4 novembre, totaux identiques. Correction du script au passage : dans la règle
des parcours corrigeables, les nœuds dédoublés (croisement d'une collectrice)
étaient reconnus parce que leur identifiant était un tuple ; or avec la
Géobase brute, tous les nœuds sont des tuples de coordonnées, donc tous
comptaient comme carrefours (258 / 341 au lieu de 247 / 352). Ils sont
maintenant marqués explicitement (`virtuels`). La page, qui lit l'export
(nœuds numérotés), n'était pas touchée.

## Utilisé par securite-plateau

`~/Developer/securite-plateau/scripts/preparer_donnees.py` importe ce script
et appelle `analyse_par_defaut()` (et `troncons_de_reseau()`) sur
`data/reseau.json` : tout le réglage par défaut, noms de cellules compris.
Il vérifie ses totaux contre `resume.json`. Après un changement de règle ou
de `noms-cellules.json`, relancer aussi ce script-là.

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
`DEFAUT_COMME_ARTERES`, `DEFAUT_RUELLES`, `DEFAUT_PARALLELES`,
`DEFAUT_VIRAGES`, `DEFAUT_PAIRES`, `DEFAUT_ARTERES_LOCALES`, `DEFAUT_ARTERES_COLLECTRICES` et `DEFAUT_CORRIGEABLES` dans le script, `state.commeArteres`,
`state.ruelles`, `state.paralleles`, `state.virages` et
`state.pairesArterielles`, `state.arteresLocales`, `state.arteresCollectrices`, `state.corrigeables` dans `index.html` (plus l'attribut `checked` de
`#parallelesToggle` et de `#pairesToggle`, la `value` de `#viragesRange` et le texte
de `#viragesValeur`).
