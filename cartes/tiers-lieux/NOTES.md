# Accès aux tiers lieux — notes

Carte des lots résidentiels de la Ville de Montréal, colorés de rouge à vert selon la distance
à pied de la ruelle verte, de la place publique et du parc les plus proches. Créée le
20 novembre 2026.

## Décisions de Gabriel (20 novembre 2026)

- **Territoire** : toute la Ville de Montréal (les 19 arrondissements), découpée par
  arrondissement (carte lourde). Arrondissement par défaut : Le Plateau-Mont-Royal
  (`?arr=<clé>` pour un autre).
- **Distance** : à pied, par les rues (Géobase), pas à vol d'oiseau.
- **Note** : selon la variété. Chaque type coché donne 1 point jusqu'au quart du temps de
  marche, puis linéairement 0 point à la limite ; la note est la moyenne **pondérée** des types
  cochés, **le parc comptant double** (ruelle verte 1, place publique 1, parc 2).
- **Temps de marche** (20 novembre 2026, deuxième demande) : sélecteur 5 / 10 / 15 min dans le
  panneau, **10 min par défaut**, le même pour toute la ville (`?temps=5` ou `15` dans
  l'adresse), à 80 m/min : limites 400 / 800 / 1 200 m, pleins points jusqu'à 100 / 200 / 300 m.
  Écarté : un temps par défaut différent selon l'arrondissement, et des couleurs relatives à
  l'arrondissement (comparaisons faussées). À 10 min, le Plateau est presque tout vert (72 % des
  logements en « bon accès », 0 % sans lieu) : 5 min y montre mieux les écarts.
  Calculée dans la page (`points()`, `note()`), pour que les cases à cocher recolorent sans
  recharger. Les distances, elles, viennent du script.

## Méthode (script/preparer_tiers_lieux.py)

| Étape | Règle |
|---|---|
| Lots | Unités d'évaluation foncière de la Ville (`MUNICIPALITE` = « 50 ») avec `NOMBRE_LOGEMENT` > 0. Les unités d'une copropriété ont la même géométrie : un seul lot, logements additionnés (398 993 unités → 253 045 lots, 940 467 logements). Arrondissement : `NO_ARROND_ILE_CUM` = `CODEMAMH` des limites. |
| Parcs | `TYPO1` « Grand parc », et « Parc d'arrondissement » avec `TYPO2` « Parc de quartier », « Parc de voisinage », « Parc linéaire » ou « Square » (1 031). Exclus : îlots de verdure, parcs-écoles, bandes riveraines, espaces « En cours de validation » (270, sans nom ni type). |
| Places publiques | `TYPO2` « Place publique » (138). |
| Ruelles vertes | Toutes (1 262). |
| Réseau | Tronçons de la Géobase de `CLASSE` 0 à 7 (sans autoroutes, 8, ni rues projetées, 9), dans les deux sens : 45 862 tronçons. |
| Accès à un lieu | Tout tronçon qui passe à 30 m ou moins de son contour (ou le traverse) ; la distance compte le bout de tronçon et l'écart. Plusieurs sources par type : un seul Dijkstra par type, limité à 2,3 km. |
| Distance d'un lot | Du centre du lot (plus grand anneau) au tronçon le plus proche (300 m au plus), puis par les rues ; si un lieu du même type est sur ce même tronçon, le trajet direct le long du tronçon compte aussi. Un lot à 10 m ou moins d'un lieu (cour sur une ruelle verte) prend la distance en ligne droite de son centre au lieu, si elle est plus courte. Au-delà de 2 km : `null`. |

Format de `data/arrondissements/<clé>.json` :
`lots` = `[polygones, logements, adresse, unités, d_ruelle, d_place, d_parc, id_ruelle, id_place, id_parc]` ;
`lieux.<type>` = `[id, nom, polygones, dans l'arrondissement (1/0)]` (lieux de l'arrondissement,
des environs à 1 km et ceux nommés par un lot) ; `contour`. Géométries en entiers relatifs
(millionièmes de degré, `code_anneaux()`), donc les 6 décimales de la règle commune, écrites plus
court : 0,15 à 1,0 Mo compressé par arrondissement (0,57 Mo pour le Plateau).

## Limites connues (aussi dans la modale « i »)

- Sentiers de parc, passages piétons et ruelles ordinaires absents de la Géobase.
- **153 ruelles vertes** n'ont aucune rue à 30 m : elles s'ouvrent sur une ruelle ordinaire.
  Mesuré : toutes entre 30 et 50 m d'une rue. Seuil gardé à 30 m (à 40-50 m, la rue parallèle
  derrière les maisons compterait comme une entrée) : elles ne comptent que pour les lots qui
  les bordent. **56 parcs** sans rue à 30 m : surtout parcs-nature et berges (Bois-de-Saraguay,
  Ruisseau-De Montigny).
- Le jeu des ruelles vertes est très inégal : 436 à Rosemont, 281 au Plateau, **1 seule à
  Ville-Marie**, aucune dans plusieurs arrondissements (vérifié dans la source,
  `PROPRIETAIRE_REF`).
- Les lieux des villes liées ne sont pas dans les jeux de la Ville.

## Vérification (script/verifier_tiers_lieux.py)

Recombine `data/` et compare aux sources : lots, logements et unités par arrondissement,
géométries identiques (arrondies), aucun lot en double ; chaque distance ≥ ligne droite du centre
au lieu nommé − 30 m ; chaque lieu nommé présent. Le 20 novembre 2026 : 253 045 lots,
537 387 distances, **0 écart**. Page : `verifier_page.py` (clair, sombre, 375 et 1280 px), sans
erreur ; les 3 avertissements « Expected value to be of type number » viennent du style
OpenFreeMap (mêmes sur la carte des collisions).

## Refaire les données

```bash
cd cartes/tiers-lieux
python3 script/preparer_tiers_lieux.py --telecharger   # environ 280 Mo dans script/sources/ (ignoré par git), ~1 min de calcul
python3 script/verifier_tiers_lieux.py
```
