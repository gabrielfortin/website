# Collisions et réseau artériel — notes techniques

Carte des collisions routières de Montréal superposées au réseau artériel
administratif, avec la part des collisions par type de voie (artères,
collectrices, rues locales…). Créée en novembre 2026.

## Fichiers

- `index.html` : la carte (gabarit de `../reseau-arteriel/carte.html`, même
  système « verre », mode sombre par `../carte-sombre.css`).
- `data/<slug>.json` : collisions d'un arrondissement (format plus bas).
- `data/resume.json` : totaux de contrôle (`compte`), kilomètres de rues par
  classe (`km`, pour la colonne « des km de rues ») et nombre de collisions par
  fichier.
- `data/meta.json` : date de préparation, version de la source, période,
  libellés de `GRAVITE`.
- `script/preparer_collisions.py` : produit tout `data/` (stdlib seulement).
- `apercu.png` : image Open Graph 1200 × 630 (capture de la carte).

Les tracés de rues ne sont **pas** copiés ici : la carte lit
`../reseau-arteriel/data/<slug>.json`. Toucher à ces fichiers change aussi le
rattachement des collisions : relancer le script ensuite.

## Sources

- **Collisions routières**, Ville de Montréal (SPVM, à partir des rapports
  de la SAAQ), CC BY 4.0 : https://donnees.montreal.ca/dataset/collisions-routieres
  Ressource GeoJSON (~380 Mo, une collision par ligne), version du
  6 octobre 2022, collisions de 2012 à 2021. **Ne pas commiter le fichier
  brut.**
- Dictionnaires de la même page : « Dictionnaire de données SAAQ complet »
  (codes `GRAVITE`, `CD_CATEG_ROUTE`…) et « Dictionnaire de données Montréal »
  (`LOC_COTE_QD`, `LOC_COTE_PD`, `LOC_DETACHEE`, `LOC_IMPRECISION`).
- **Réseau artériel administratif** : voir `../reseau-arteriel/NOTES.md`.

## Méthode de rattachement

1. On ne garde que les collisions de la Ville de Montréal
   (`CD_MUNCP = 66023`, 197 761 collisions). Les 20 511 autres sont dans les
   villes liées, que le réseau artériel ne couvre pas.
2. Hors du calcul, selon les champs de la source :
   - `LOC_COTE_PD = 4`, « Précision nulle. Accident localisé au centroïde de
     la limite du poste de quartier » : 5 316 collisions, **non dessinées**
     (elles s'empileraient au centre des PDQ), mentionnées seulement dans
     « Tous les arrondissements » ;
   - `LOC_DETACHEE = O`, collision détachée du réseau routier par la Ville
     (stationnement, ruelle, terrain privé, etc.) : 29 139 collisions,
     dessinées mais hors des pourcentages ;
   - sans coordonnées : 6.
3. Pour les autres, on cherche les tronçons à 60 m ou moins. Si un tronçon à
   30 m ou moins porte le même nom que `RUE_ACCDN` (rue inscrite au rapport),
   il est retenu ; sinon, le plus proche. Sans ce choix par le nom, une
   collision à une intersection irait à la rue transversale au hasard :
   la règle a changé la classe retenue pour 33 590 collisions.
   - Comparaison des noms : majuscules sans accents, types de voie
     (`RUE`, `BD`, `AV`, `CH`…) et points cardinaux retirés, abréviations
     développées (`ST` → `SAINT`, `N-D` → `NOTRE DAME`, `GDES` → `GRANDES`,
     `MT` → `MONT`…), lettres collées (`DELORIMIER` = « De Lorimier »).
     Liste exacte dans `cles_nom()`.
   - Résultat : 142 702 collisions rattachées par le nom, les autres par
     proximité (autoroutes, voies « Non-nommée », rues renommées comme
     Amherst → Atateken). Distance médiane au tronçon : 0,3 m (la Ville a
     géolocalisé les collisions sur son propre réseau).
   - Aucun tronçon à 60 m : 749 collisions « non rattachées », hors calcul.
4. Le type de voie est la `CLASSE` du tronçon (libellés de
   `../reseau-arteriel/carte.html`). Regroupement affiché :
   **Artères** = 7 (principale) + 6 (secondaire) ; **Collectrices** = 5 ;
   **Rues locales** = 0 ; **Autoroutes** = 8 ; **Autres voies** = 1, 2, 3, 4, 9.
   Ligne à part : part sur le **réseau artériel administratif**
   (`ARTERE = 1`), qui contient presque toutes les collectrices et
   ~6 000 tronçons de classe « rue locale » : ce n'est donc pas la même chose
   que « Artères ».
5. Arrondissement : celui du tronçon retenu. Un tronçon limitrophe est dans
   deux fichiers (voir `../reseau-arteriel/NOTES.md`), donc la collision
   aussi : elle compte dans les deux arrondissements, et une seule fois dans
   « Tous » (dédoublonnage par numéro `NO_SEQ_COLL` dans le navigateur).
   Collision non rattachée ou détachée : arrondissement du tronçon le plus
   proche à 500 m ou moins (770 n'en ont aucun et sont écartées).

Chiffres de contrôle, toute la ville, 2012-2021, toutes gravités (ce
qu'affiche « Tous les arrondissements » une fois les cinq gravités cochées) : 161 781 collisions rattachées à
une rue ; artères 74 333 (45,9 %), collectrices 30 614 (18,9 %), rues
locales 56 122 (34,7 %), autoroutes 264, autres voies 448 ; réseau artériel
administratif 76,5 % des collisions pour 43,3 % des km.

## Limites (affichées dans la modale)

- **Autoroutes** : la Ville exclut de la géolocalisation les collisions du
  réseau autoroutier. Leur part (0,2 %) ne reflète pas la réalité.
- La géolocalisation est automatisée par la Ville et peut contenir des
  erreurs (mise en garde de son dictionnaire). `LOC_IMPRECISION = O`
  (16 633 collisions de la Ville, à des carrefours complexes) est gardé tel quel.
- Les tronçons viennent de la version 2023 du réseau artériel ; les
  collisions vont de 2012 à 2021. Une rue reclassée entre-temps est comptée
  selon sa classe de 2023.
- 2012 et 2013 comptent ~28 500 collisions dans la Ville contre ~19 500 de
  2014 à 2018 (et ~12 500 en 2020-2021, pandémie), tel quel dans la source
  (pas corrigé).

## Format de `data/<slug>.json`

```json
{ "noms": ["SHERBROOKE O ET UNION", "Sherbrooke", ...],
  "collisions": [[10406, -73.572957, 45.50555, "2012-01-13", 4, 6, 1, 0, 0, 0, 0, 0, 0, -1, 0, 1, 0.7], ...] }
```

Position des champs : constante `COL` en tête du script de `index.html`
(numéro de `NO_SEQ_COLL`, lng, lat, `DT_ACCDN`, index de `GRAVITE`, classe du
tronçon ou -1 détachée / -3 non rattachée, `ARTERE`, méthode 1 = nom /
0 = proximité, `NB_MORTS`, `NB_BLESSES_GRAVES`, `NB_BLESSES_LEGERS`,
`NB_VICTIMES_PIETON`, `NB_VICTIMES_VELO`, puis index dans `noms` de
`RUE_ACCDN`, `ACCDN_PRES_DE` et du nom du tronçon, distance en m, et
`NB_VICTIMES_MOTO`). Les
noms gardent l'orthographe de la source (fautes comprises).

Taille : ~15 Mo pour les 19 fichiers (Ville-Marie, le plus gros : 2 Mo).
« Tous les arrondissements » charge tout, d'où « (lent) » dans le menu.

## Affichage

Les collisions sont dessinées par un petit calque canevas maison
(`PointsLayer`) plutôt qu'en `L.circleMarker` : Leaflet devient lent au-delà
de quelques dizaines de milliers de marqueurs, et « Tous » en compte
~190 000. Positions projetées une seule fois au zoom 0, puis mises à
l'échelle à chaque déplacement ; les plus graves sont dessinées en dernier.
Taille et opacité diminuent aux petits zooms pour ne pas cacher les rues.
Au clic, la collision visible la plus proche (9 px) l'emporte sur la rue.

Les pourcentages sont recalculés dans le navigateur selon l'arrondissement,
les années et les gravités cochées. Par défaut, les deux gravités « Dommages matériels… » sont
décochées : la carte s'ouvre sur les collisions avec victimes (Mortel, Grave,
Léger).
Le filtre « Victimes » (tous types, piétons, cyclistes, motocyclistes) garde
les collisions où le champ `NB_VICTIMES_PIETON`, `_VELO` ou `_MOTO` est
supérieur à zéro ; la source ne compte pas à part les autres victimes
(occupants des véhicules). Les cases des rues ne changent que
l'affichage.

## Régénérer les données

1. Télécharger la ressource GeoJSON « Collisions routières » (hors du dépôt).
2. Noter sa date « Dernière modification des données » sur
   donnees.montreal.ca.
3. Lancer :

```
cd script
python3 preparer_collisions.py ~/Downloads/collisions_routieres.geojson 2022-10-06
```

Le script s'arrête sur un `NO_SEQ_COLL` d'un format inattendu ou en double,
ou sur une `GRAVITE` inconnue, plutôt que de publier un chiffre faux. Il
affiche les totaux de contrôle à la fin : les comparer avec ceux ci-dessus,
puis mettre à jour cette section et l'image `apercu.png` si les chiffres
changent.
