// Outil « Trouver le district » : adresse collée → district, arrondissement, élu·es.
// Données préparées par scripts/preparer_district.py (data/district/).
// Tout le texte affiché passe par textContent.

import { analyser, reperer, chercherNumero, etendue, suggerer, fichierDe, construireAlias, proposer, reecrire, position } from "./adresse.js"; // pas de ?v= : le hook ne le met pas à jour ; Cloudflare revalide chaque fichier (ETag)

const DONNEES = new URL("../data/", import.meta.url);
const formulaire = document.getElementById("formulaire");
const champ = document.getElementById("adresse");
const bouton = document.getElementById("bouton-trouver");
const zoneResultat = document.getElementById("resultat");

let rues = null; // Map : nom de rue normalisé → nom affiché
let alias = null; // nom sans particule (« lanaudiere ») → clés du registre
let territoires = null;
const fichiers = new Map(); // lettre → promesse du fichier de rues

function el(balise, attributs = {}, ...enfants) {
  const n = document.createElement(balise);
  for (const [k, v] of Object.entries(attributs)) {
    if (v === undefined || v === null || v === false) continue;
    if (k === "class") n.className = v;
    else if (k === "texte") n.textContent = v;
    else n.setAttribute(k, v === true ? "" : v);
  }
  for (const e of enfants.flat()) if (e) n.append(e);
  return n;
}

async function lireJson(chemin) {
  const r = await fetch(new URL(chemin, DONNEES));
  if (!r.ok) throw new Error(`${chemin} : HTTP ${r.status}`);
  return r.json();
}

function chargerFichier(cle) {
  const lettre = fichierDe(cle);
  if (!fichiers.has(lettre)) {
    const p = lireJson(`district/rues/${lettre}.json`);
    p.catch(() => fichiers.delete(lettre)); // réessayer à la prochaine recherche
    fichiers.set(lettre, p);
  }
  return fichiers.get(lettre);
}

// ------------------------------------------------------------------ copie
let annonce;
function annoncer(texte) {
  if (!annonce) {
    annonce = el("p", { class: "sr-only", "aria-live": "assertive" });
    document.body.append(annonce);
  }
  annonce.textContent = "";
  setTimeout(() => { annonce.textContent = texte; }, 30);
}

async function copier(texte, boutonCopie) {
  try {
    await navigator.clipboard.writeText(texte);
  } catch {
    const zone = el("textarea", { class: "sr-only" });
    zone.value = texte;
    document.body.append(zone);
    zone.select();
    document.execCommand("copy");
    zone.remove();
  }
  const libelle = boutonCopie.textContent;
  boutonCopie.textContent = "Copié ✓";
  boutonCopie.classList.add("copie-ok");
  annoncer("Copié dans le presse-papiers.");
  setTimeout(() => {
    boutonCopie.textContent = libelle;
    boutonCopie.classList.remove("copie-ok");
  }, 1600);
}

function boutonCopier(texte, libelle, description) {
  const b = el("button", { type: "button", class: "bouton-copier", texte: libelle, "aria-label": description });
  b.addEventListener("click", () => copier(texte, b));
  return b;
}

// --------------------------------------------------------------- affichage
function ligneElu(elu, note) {
  return el(
    "li",
    { class: "elu" },
    el(
      "div",
      { class: "elu-identite" },
      el("span", { class: "elu-nom", texte: elu.nom }),
      el("span", { class: "elu-role", texte: [elu.fonction, note, elu.parti].filter(Boolean).join(" · ") }),
    ),
    el(
      "div",
      { class: "elu-contact" },
      el("a", { href: `mailto:${elu.courriel}`, texte: elu.courriel }),
      boutonCopier(elu.courriel, "Copier", `Copier le courriel de ${elu.nom}`),
    ),
  );
}

function blocElus(titre, elus, notes) {
  if (!elus.length) return null;
  const courriels = elus.map((e) => e.courriel).join("; ");
  return el(
    "div",
    { class: "bloc-elus" },
    el(
      "div",
      { class: "bloc-elus-tete" },
      el("h3", { texte: titre }),
      elus.length > 1 ? boutonCopier(courriels, "Copier les courriels", `Copier les ${elus.length} courriels : ${titre}`) : null,
    ),
    el("ul", { class: "elus" }, elus.map((e) => ligneElu(e, notes.get(e)))),
  );
}

function adresseLisible(r) {
  return `${r.numero}, ${r.rue}`;
}

// ------------------------------------------------------------------ carte
// Petite carte à droite du résultat : épingle sur le bâtiment, pour valider
// d'un coup d'œil. Le résultat s'affiche d'abord ; la carte (composant commun
// vendor/carte/ : API de Leaflet dessinée par MapLibre) et les positions
// (positions/<x>.json) se chargent ensuite. Seul le fond de carte vient
// d'OpenFreeMap (voir /confidentialite/). Sur gabfortin.com, le composant
// est celui des cartes : cartes/vendor/carte/.
let carteActive = null;
let leaflet = null;
const positions = new Map(); // lettre → promesse du fichier de positions

function chargerLeaflet() {
  // Feuilles de style et scripts du composant de carte : MapLibre d'abord, puis carte.js (qui crée L)
  const charger = (n) => new Promise((ok, echec) => {
    n.onload = ok;
    n.onerror = echec;
    document.head.append(n);
  });
  const base = new URL("../../../cartes/vendor/carte/", import.meta.url);
  const fichier = (f) => new URL(f, base).href;
  leaflet ??= Promise.all([
    charger(el("link", { rel: "stylesheet", href: fichier("maplibre-gl.css") })),
    charger(el("link", { rel: "stylesheet", href: fichier("carte.css") })),
    charger(el("script", { src: fichier("maplibre-gl.js") })).then(() => charger(el("script", { src: fichier("carte.js") }))),
  ]).then(() => window.L, (e) => { leaflet = null; throw e; });
  return leaflet;
}

function chargerPositions(cle) {
  const lettre = fichierDe(cle);
  if (!positions.has(lettre)) {
    const p = lireJson(`district/positions/${lettre}.json`);
    p.catch(() => positions.delete(lettre));
    positions.set(lettre, p);
  }
  return positions.get(lettre);
}

function blocCarte(resultats) {
  const conteneur = el("div", { class: "carte-adresse", role: "img", "aria-label": "Carte de l’adresse" });
  monterCarte(conteneur, resultats).catch(() => conteneur.remove()); // sans carte, le résultat reste complet
  return conteneur;
}

async function monterCarte(conteneur, resultats) {
  const [L, ...fichiersPos] = await Promise.all([chargerLeaflet(), ...resultats.map((r) => chargerPositions(r.cle))]);
  if (!conteneur.isConnected) return; // autre recherche entre-temps
  const points = [];
  const vus = new Set();
  resultats.forEach((r, i) => {
    const pos = position(fichiersPos[i][r.cle], r.plage);
    if (!pos || vus.has(String(pos))) return;
    vus.add(String(pos));
    points.push({ position: pos, libelle: r.approximatif ? `${r.voisin}, ${r.rue} (adresse voisine)` : adresseLisible(r) });
  });
  if (!points.length) throw new Error("aucune position");
  conteneur.setAttribute("aria-label", `Carte : ${points.map((p) => p.libelle).join(" · ")}`);
  carteActive?.remove();
  const carte = L.map(conteneur, { scrollWheelZoom: false });
  // Fond OpenFreeMap (données OpenStreetMap), posé par le composant ; crédit affiché par le composant
  for (const p of points) {
    L.circleMarker(p.position, { radius: 9, weight: 3, color: "#fff", fillColor: "#dc2626", fillOpacity: 1 })
      .bindTooltip(p.libelle)
      .addTo(carte);
  }
  if (points.length === 1) carte.setView(points[0].position, 16);
  else carte.fitBounds(points.map((p) => p.position), { padding: [30, 30], maxZoom: 16 });
  carteActive = carte;
}

function carteZone(resultats) {
  const zone = territoires.zones[resultats[0].zone];
  const adresses = [...new Set(resultats.map(adresseLisible))];
  const tete = el(
    "div",
    { class: "resultat-tete" },
    el("p", { class: "eyebrow", texte: adresses.length > 1 ? "Adresses reconnues" : "Adresse reconnue" }),
    el("p", { class: "adresse-trouvee", texte: adresses.join(" · ") }),
  );
  const approx = resultats.filter((r) => r.approximatif);
  const avis = approx.length
    ? el("p", {
        class: "callout avis",
        texte: `Numéro absent du registre de la Ville : district de l’adresse la plus proche du même côté de la rue (${approx
          .map((r) => `${r.voisin}, ${r.rue}`)
          .join(" · ")}). Vérifier si l’adresse est près d’une limite de district.`,
      })
    : null;

  // Adresse et territoire à gauche, carte à droite.
  const haut = (...infos) => el("div", { class: "resultat-haut" }, el("div", { class: "resultat-infos" }, tete, avis, ...infos), blocCarte(resultats));

  if (zone.ville) {
    return el(
      "article",
      { class: "card carte-resultat" },
      haut(
        el(
          "div",
          { class: "territoire" },
          el("div", {}, el("span", { class: "territoire-libelle", texte: "Ville liée" }), el("strong", { texte: zone.ville })),
        ),
      ),
      el("p", {
        class: "callout",
        texte: `${zone.ville} est une ville liée de l’agglomération, pas un arrondissement : elle n’a pas de district de la Ville de Montréal, et ses élu·es ne sont pas dans la liste de la Ville.`,
      }),
    );
  }

  const district = territoires.districts[zone.district];
  const arrondissement = territoires.arrondissements[district.arrondissement] ?? { elus: [] };
  const maires = arrondissement.elus.filter((e) => e.fonction.startsWith("Maire"));
  // Conseiller·ère de la Ville élu·e pour tout l'arrondissement (Anjou, Lachine…)
  const pourTout = arrondissement.elus.filter((e) => !e.fonction.startsWith("Maire"));
  const notes = new Map(pourTout.map((e) => [e, "pour tout l’arrondissement"]));
  const elusDistrict = [...district.elus, ...pourTout].sort(
    (a, b) => Number(b.fonction.includes("Ville")) - Number(a.fonction.includes("Ville")),
  );

  return el(
    "article",
    { class: "card carte-resultat" },
    haut(
      el(
        "div",
        { class: "territoire" },
        el("div", {}, el("span", { class: "territoire-libelle", texte: "District" }), el("strong", { texte: district.nom })),
        el("div", {}, el("span", { class: "territoire-libelle", texte: "Arrondissement" }), el("strong", { texte: district.arrondissement })),
      ),
    ),
    blocElus("Élu·es du district", elusDistrict, notes),
    blocElus("Mairie de l’arrondissement", maires, new Map()),
  );
}

// ------------------------------------------------------------- chargement
// Radar sur un plan de rues : faisceau, adresses qui s'allument, épingle qui
// tombe. Décoratif (aria-hidden) ; le lecteur d'écran entend « Recherche… ».
let numeroRecherche = 0;

function chargement(saisie) {
  const blips = Array.from({ length: 7 }, (_, i) => el("span", { class: `radar-blip radar-blip-${i + 1}` }));
  return el(
    "div",
    { class: "card chargement", role: "status" },
    el(
      "div",
      { class: "radar", "aria-hidden": "true" },
      el("span", { class: "radar-rues" }),
      el("span", { class: "radar-anneaux" }),
      el("span", { class: "radar-faisceau" }),
      ...blips,
      el("span", { class: "radar-onde" }),
      el("span", { class: "radar-epingle" }),
      el("span", { class: "radar-ombre" }),
    ),
    el(
      "div",
      { class: "chargement-texte" },
      el("p", { class: "chargement-titre", texte: "Recherche dans le registre de la Ville…" }),
      el("p", { class: "chargement-saisie", texte: saisie }),
      el("span", { class: "chargement-barre", "aria-hidden": "true" }),
    ),
  );
}

function afficher(...noeuds) {
  carteActive?.remove();
  carteActive = null;
  zoneResultat.replaceChildren(...noeuds.filter(Boolean));
}

function message(titre, texte, ...extra) {
  return el("div", { class: "card message" }, el("h2", { texte: titre }), texte ? el("p", { texte }) : null, ...extra);
}

function nomZone(i) {
  const z = territoires.zones[i];
  if (z.ville) return `${z.ville} (ville liée)`;
  const d = territoires.districts[z.district];
  return `${d.nom} (${d.arrondissement})`;
}

// --------------------------------------------------------------- recherche
async function rechercher() {
  const saisie = champ.value.trim();
  if (!saisie || !rues) return;
  const { numeros, mots } = analyser(saisie);
  let repere = reperer(mots, rues, alias);
  let note = null;

  // Rue introuvable telle quelle : on prend la meilleure proposition (faute
  // de frappe, nom incomplet) et on le dit.
  if (!repere) {
    const p = proposer(saisie, rues, 1);
    if (p.rues.length) {
      const rue = p.rues[0];
      repere = { cle: rue.cle, generique: p.generique, orientation: p.orientation };
      note = el("p", { class: "callout avis", texte: `Rue corrigée : lu « ${rue.nom} ». Vérifier si ce n’est pas la bonne rue.` });
    }
  }
  const montrer = (...noeuds) => afficher(note, ...noeuds);

  if (!repere) {
    const pistes = suggerer(mots, rues);
    afficher(
      message(
        "Rue introuvable",
        pistes.length
          ? "Aucun nom de rue du registre de la Ville ne correspond. Vérifier l’orthographe, ou essayer une rue proche :"
          : "Aucun nom de rue du registre de la Ville ne correspond. Vérifier l’orthographe ; l’adresse est peut-être hors de l’agglomération de Montréal.",
        pistes.length
          ? el("ul", { class: "pistes" }, pistes.map((p) => el("li", { texte: rues.get(p) })))
          : null,
      ),
    );
    return;
  }
  if (!numeros.length) {
    montrer(message("Numéro manquant", "Ajouter le numéro civique : une même rue traverse souvent plusieurs districts."));
    return;
  }

  let variantes;
  const recherche = ++numeroRecherche;
  // Animation pendant le chargement. Si le fichier est déjà là, le résultat
  // la remplace avant le prochain affichage : elle ne clignote pas.
  montrer(chargement(champ.value.trim()));
  try {
    variantes = (await chargerFichier(repere.cle))[repere.cle] ?? [];
    if (recherche !== numeroRecherche) return; // une autre recherche a été lancée
  } catch (erreur) {
    montrer(message("Données indisponibles", `Impossible de charger les adresses (${erreur.message}). Réessayer.`));
    return;
  }
  const resultats = chercherNumero(variantes, repere, numeros);
  for (const r of resultats) r.cle = repere.cle; // pour retrouver la position

  if (!resultats.length) {
    const { min, max } = etendue(variantes);
    montrer(
      message(
        "Numéro introuvable",
        `La rue existe (${[...new Set(variantes.map((v) => v[3]))].join(", ")}), mais pas le numéro ${numeros[0]} : ` +
          `numéros de ${min} à ${max} dans le registre.`,
      ),
    );
    return;
  }

  // Regrouper par territoire : « 100 Notre-Dame Est » et « Ouest » dans le
  // même district donnent une seule réponse.
  const parZone = new Map();
  for (const r of resultats) {
    if (!parZone.has(r.zone)) parZone.set(r.zone, []);
    parZone.get(r.zone).push(r);
  }
  if (parZone.size === 1) {
    montrer(carteZone(resultats));
    return;
  }

  const details = el("div", { class: "choix-detail" });
  const choix = el(
    "div",
    { class: "card message" },
    el("h2", { texte: "Plusieurs adresses correspondent" }),
    el("p", { texte: "Préciser l’orientation (Est, Ouest…) ou choisir l’adresse :" }),
    el(
      "ul",
      { class: "choix" },
      [...parZone].map(([zone, liste]) => {
        const b = el(
          "button",
          { type: "button", class: "bouton-choix", "aria-pressed": "false" },
          el("span", { class: "choix-adresse", texte: [...new Set(liste.map(adresseLisible))].join(" · ") }),
          el("span", { class: "choix-zone", texte: nomZone(zone) }),
        );
        b.addEventListener("click", () => {
          choix.querySelectorAll(".bouton-choix").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
          details.replaceChildren(carteZone(liste));
        });
        return el("li", {}, b);
      }),
    ),
  );
  montrer(choix, details);
}

// ------------------------------------------------- menu de suggestions
// Dès que la saisie contient un chiffre et une lettre : rues proposées.
// Flèches pour choisir, Entrée prend la rue en surbrillance (sinon la
// première) et lance la recherche, Échap ferme.
const liste = document.getElementById("suggestions");
let propositions = null;
let actif = -1;

function fermerSuggestions() {
  liste.hidden = true;
  liste.replaceChildren();
  champ.setAttribute("aria-expanded", "false");
  champ.removeAttribute("aria-activedescendant");
  propositions = null;
  actif = -1;
}

function surligner(i) {
  actif = i;
  [...liste.children].forEach((li, j) => li.setAttribute("aria-selected", String(j === i)));
  if (i >= 0) {
    champ.setAttribute("aria-activedescendant", liste.children[i].id);
    liste.children[i].scrollIntoView({ block: "nearest" });
  } else champ.removeAttribute("aria-activedescendant");
}

function ouvrirSuggestions() {
  const saisie = champ.value;
  if (!rues || !/\d/.test(saisie) || !/\p{L}/u.test(saisie)) return fermerSuggestions();
  const p = proposer(saisie, rues);
  if (!p.rues.length) return fermerSuggestions();
  propositions = p;
  liste.replaceChildren(
    ...p.rues.map((rue, i) => {
      const li = el("li", { id: `suggestion-${i}`, role: "option", "aria-selected": "false", texte: reecrire(p, rue) });
      li.addEventListener("mousedown", (e) => {
        e.preventDefault(); // garder le focus dans le champ
        choisir(i);
      });
      return li;
    }),
  );
  liste.hidden = false;
  champ.setAttribute("aria-expanded", "true");
  surligner(-1);
}

function choisir(i) {
  if (!propositions) return;
  champ.value = reecrire(propositions, propositions.rues[i]);
  fermerSuggestions();
  rechercher();
}

let collage = false;
champ.addEventListener("input", () => {
  if (collage) { collage = false; return; } // un collage lance la recherche directement
  ouvrirSuggestions();
});
champ.addEventListener("keydown", (e) => {
  if (liste.hidden) return;
  const n = liste.children.length;
  if (e.key === "ArrowDown") { e.preventDefault(); surligner((actif + 1) % n); }
  else if (e.key === "ArrowUp") { e.preventDefault(); surligner(actif <= 0 ? n - 1 : actif - 1); }
  else if (e.key === "Enter") { e.preventDefault(); choisir(Math.max(actif, 0)); }
  else if (e.key === "Escape") { e.preventDefault(); fermerSuggestions(); }
});
champ.addEventListener("blur", () => setTimeout(fermerSuggestions, 0));

formulaire.addEventListener("submit", (e) => {
  e.preventDefault();
  fermerSuggestions();
  rechercher();
});
champ.addEventListener("paste", () => {
  collage = true;
  fermerSuggestions();
  setTimeout(rechercher, 0);
});

// --------------------------------------------------------------- démarrage
async function demarrer() {
  const fraicheur = document.getElementById("fraicheur");
  try {
    const [listeRues, terr, meta] = await Promise.all([
      lireJson("district/rues.json"),
      lireJson("district/territoires.json"),
      lireJson("meta.json").catch(() => null),
    ]);
    rues = new Map(Object.entries(listeRues));
    alias = construireAlias(rues);
    territoires = terr;
    bouton.disabled = false;
    const nbDistricts = Object.keys(territoires.districts).length;
    if (meta?.donneesMisesAJour) {
      // Midi : une date seule serait lue en UTC et reculerait d'un jour à Montréal.
      const date = new Date(`${meta.donneesMisesAJour}T12:00:00`).toLocaleDateString("fr-CA", {
        day: "numeric", month: "long", year: "numeric",
      });
      fraicheur.textContent = `Données préparées le ${date} · ${rues.size.toLocaleString("fr-CA")} rues, ${nbDistricts} districts`;
      document.getElementById("donnees-maj-date").textContent = date;
      document.getElementById("donnees-maj").hidden = false;
    } else {
      fraicheur.textContent = `${rues.size.toLocaleString("fr-CA")} rues, ${nbDistricts} districts`;
    }
    if (champ.value.trim()) rechercher();
  } catch (erreur) {
    fraicheur.textContent = "Données indisponibles.";
    afficher(message("Données indisponibles", `Impossible de charger les données (${erreur.message}).`));
  }
}

demarrer();

