/* ═══════════════════════════════════════════════════════════════════════════
   Animation d'attente des cartes de gabfortin.com/cartes/ : une scène liée aux
   données de chaque carte, au centre de la carte, pendant le chargement d'un
   arrondissement. Base commune : vendor/chargement.js + vendor/chargement.css
   (modèle ~/Developer/outils/communs/) ; scènes : chargement-scenes.css.

     const attente = attenteCarte("urne", "Dépouillement des résultats…");
     attente.montrer("Le Plateau-Mont-Royal");   // ou attente.erreur("…")
     attente.cacher();
   =========================================================================== */
(function () {
  "use strict";
  const SCENES = {
    // Élections : bulletins dans l'urne, pastilles des partis
    urne: '<span class="u-parti u-p1"></span><span class="u-parti u-p2"></span><span class="u-parti u-p3"></span>' +
      '<span class="u-parti u-p4"></span><span class="u-bulletin"></span><span class="u-bulletin u-b2"></span>' +
      '<span class="u-bulletin u-b3"></span><span class="u-urne"></span>',
    // Réseau artériel : les rues se tracent des artères principales aux rues locales
    rues: '<span class="r-plan"><i class="r-locale r-h6"></i><i class="r-locale r-h7"></i><i class="r-v r-locale r-v6"></i>' +
      '<i class="r-v r-locale r-v7"></i><i class="r-collectrice r-h4"></i><i class="r-collectrice r-h5"></i>' +
      '<i class="r-v r-collectrice r-v4"></i><i class="r-v r-collectrice r-v5"></i><i class="r-secondaire r-h2"></i>' +
      '<i class="r-secondaire r-h3"></i><i class="r-v r-secondaire r-v2"></i><i class="r-v r-secondaire r-v3"></i>' +
      '<i class="r-principale r-h1"></i><i class="r-v r-principale r-v1"></i></span><span class="r-curseur"></span>',
    // Collisions : deux voitures, l'impact, les points de collision
    carrefour: '<span class="k-route-h"></span><span class="k-route-v"></span><span class="k-point k-pt1"></span>' +
      '<span class="k-point k-pt2"></span><span class="k-point k-pt3"></span><span class="k-point k-pt4"></span>' +
      '<span class="k-auto k-a1"></span><span class="k-auto k-a2"></span><span class="k-onde"></span><span class="k-choc"></span>',
    // Tiers lieux : autour d'un parc, les lots passent du rouge au vert, du plus proche au plus loin
    tiers: '<span class="t-rues"></span><i class="t-lot t-l1"></i><i class="t-lot t-l2"></i><i class="t-lot t-l3"></i><i class="t-lot t-l4"></i><i class="t-lot t-l5"></i><i class="t-lot t-l6"></i><i class="t-lot t-l7"></i><i class="t-lot t-l8"></i><i class="t-lot t-l9"></i><i class="t-lot t-l10"></i><i class="t-lot t-l11"></i><i class="t-lot t-l12"></i><span class="t-parc"></span><span class="t-onde"></span><span class="t-onde t-o2"></span>',
  };

  window.attenteCarte = function (scene, titre) {
    let ch = null;
    const creer = (detail) => Chargement.creer({ scene: SCENES[scene], classe: "ch-" + scene, mode: "flottant", titre, detail });
    return {
      montrer(detail) {
        if (!window.Chargement) return;
        if (ch && !ch.element.classList.contains("ch-erreur")) { ch.detail(detail); return; }
        if (ch) ch.fermer();
        ch = creer(detail);
      },
      cacher() { if (ch) { ch.fermer(); ch = null; } },
      erreur(message) {
        if (!window.Chargement) return;
        if (!ch) ch = creer("");
        ch.erreur(message || "Données indisponibles. Rechargez la page.");
      },
    };
  };
})();
