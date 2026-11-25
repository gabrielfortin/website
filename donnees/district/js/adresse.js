// Lecture d'une adresse montréalaise collée telle quelle, et recherche dans
// le registre « Adresse ponctuelle » préparé par scripts/preparer_district.py.
// Aucune requête vers un service externe : tout se passe dans le navigateur.
//
// Formes reconnues (exemples) :
//   4801 rue Saint-Denis · 4801, St-Denis · 3-4801 Saint-Denis (app. 3)
//   4843-45 Saint-Denis (plage) · 201 Laurier E., Montréal (Québec) H2T 3E6
//   61 Rachel Ouest app. 2 · 1234 1ère Avenue · 5000 Sherbrooke St W

// Même règle que normaliser() dans scripts/preparer_district.py.
const ORDINAL = /^(\d+)(?:er|re|ere|eme|ieme|e)$/;

export function normaliser(texte) {
  const t = texte
    .toLowerCase()
    .replace(/œ/g, "oe")
    .replace(/æ/g, "ae")
    .normalize("NFD")
    .replace(/\p{Mn}/gu, "")
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
  if (!t) return "";
  return t
    .split(" ")
    .map((m) => {
      if (m === "st") return "saint";
      if (m === "ste") return "sainte";
      const o = m.match(ORDINAL);
      return o ? o[1] + "e" : m;
    })
    .join(" ");
}

export const fichierDe = (cle) => (cle[0] >= "a" && cle[0] <= "z" ? cle[0] : "0");

// Mots qui ne font pas partie du nom de la rue (après normalisation).
const GENERIQUES = {
  rue: "rue", r: "rue", street: "rue",
  avenue: "avenue", av: "avenue", ave: "avenue",
  boulevard: "boulevard", boul: "boulevard", bd: "boulevard", blvd: "boulevard", boulv: "boulevard",
  chemin: "chemin", ch: "chemin", road: "chemin", rd: "chemin",
  place: "place", pl: "place",
  croissant: "croissant", crois: "croissant", cr: "croissant",
  terrasse: "terrasse", terr: "terrasse",
  route: "route", allee: "allée", cercle: "cercle", cours: "cours",
  promenade: "promenade", carre: "carré", montee: "montée", impasse: "impasse",
  cote: "côte", passage: "passage", voie: "voie", ruelle: "ruelle",
};
const ORIENTATIONS = {
  est: "E", e: "E", east: "E",
  ouest: "O", o: "O", w: "O", west: "O",
  nord: "N", n: "N", north: "N",
  sud: "S", s: "S", south: "S",
};
const LIENS = new Set(["de", "du", "des", "la", "l", "d"]);
const AUTRES = new Set(["montreal", "mtl", "qc", "quebec", "canada", "saint", "ville"]);
const libre = (m) => m in GENERIQUES || m in ORIENTATIONS || LIENS.has(m) || AUTRES.has(m);

const NOM_ORIENTATION = { E: "Est", O: "Ouest", N: "Nord", S: "Sud" };

// Extrait le numéro civique (avec ses autres lectures possibles) et le reste.
export function analyser(brut) {
  let texte = ` ${brut} `
    .replace(/\s+/g, " ")
    // code postal
    .replace(/\b[a-z]\d[a-z] ?\d[a-z]\d\b/gi, " ")
    // appartement, bureau, local… : retiré avec son numéro
    // (le mot doit finir là : « Appleton » n'est pas « app. leton »)
    .replace(/\b(?:appartement|app|apt|unité|unite|unit|bureau|suite|local)(?=[\s.#]|\d)\.? ?#? ?[\w-]+/gi, " ")
    .replace(/#\s?\w+/g, " ");

  const numeros = [];
  // Numéro au début : « 4801 », « 4801A », « 4843-45 » (plage), « 3-4801 » (app. 3)
  const debut = texte.match(/^\s*(\d+)\s?[a-z]?\s?(?:[-–]\s?(\d+)[a-z]?)?(?=[\s,])/i);
  if (debut) {
    const [, a, b] = debut;
    if (b && b.length > a.length) numeros.push(+b, +a); // 3-4801 : app. 3 au 4801
    else numeros.push(+a); // 4843-45 : plage, on garde le premier
    texte = texte.slice(debut[0].length);
  } else {
    // Numéro ailleurs (« rue Saint-Denis 4801 ») : premier nombre qui n'est pas un ordinal.
    const ailleurs = texte.match(/(?:^|[\s,])(\d+)(?=[\s,]|$)/);
    if (ailleurs) {
      numeros.push(+ailleurs[1]);
      texte = texte.replace(ailleurs[0], " ");
    }
  }
  return { numeros, mots: normaliser(texte).split(" ").filter(Boolean) };
}

// Nom sans sa particule de tête : dans le registre, « De Lanaudière » a pour clé
// « de lanaudiere », mais on écrit souvent « 6800 Lanaudière ».
const sansParticule = (cle) => cle.replace(/^(?:(?:de|du|des|la|le|les|l|d)\s)+/, "");

// Forme sans particule → clés du registre. Construit une fois au chargement.
export function construireAlias(rues) {
  const alias = new Map();
  for (const cle of rues.keys()) {
    const forme = sansParticule(cle);
    if (forme === cle || !forme) continue;
    if (!alias.has(forme)) alias.set(forme, []);
    alias.get(forme).push(cle);
  }
  return alias;
}

// Cherche dans les mots la plus longue suite qui est un nom de rue connu.
// À longueur égale : la première (la rue suit le numéro, la ville vient après).
// Un nom écrit sans sa particule (« Lanaudière ») est reconnu s'il ne désigne
// qu'une rue du registre.
export function reperer(mots, rues, alias = null) {
  let meilleur = null;
  for (let i = 0; i < mots.length; i++) {
    for (let j = mots.length; j > i; j--) {
      const morceau = mots.slice(i, j);
      if (morceau.every(libre)) continue; // « avenue », « est », « montreal » seuls
      const texte = morceau.join(" ");
      const parAlias = alias?.get(texte);
      const cle = rues.has(texte) ? texte : parAlias?.length === 1 ? parAlias[0] : null;
      if (!cle) continue;
      if (!meilleur || morceau.length > meilleur.fin - meilleur.debut) meilleur = { cle, debut: i, fin: j };
      break;
    }
  }
  if (!meilleur) return null;
  const avant = mots.slice(0, meilleur.debut);
  const apres = mots.slice(meilleur.fin);
  const generique = [...avant, ...apres].map((m) => GENERIQUES[m]).find(Boolean) ?? null;
  // L'orientation suit le nom : « Laurier Est », « Sherbrooke St W ».
  const orientation = apres.map((m) => ORIENTATIONS[m]).find(Boolean) ?? null;
  return { cle: meilleur.cle, generique, orientation };
}

export function libelleRue([generique, lien, orientation, specifique]) {
  const o = NOM_ORIENTATION[orientation] ? ` ${NOM_ORIENTATION[orientation]}` : "";
  // Rue numérotée : « 1re Avenue », « 10e Rue »
  if (/^\d/.test(specifique) && generique) {
    return `${specifique} ${generique[0].toUpperCase()}${generique.slice(1)}${o}`;
  }
  const liaison = !lien ? "" : /'$/.test(lien) ? lien : `${lien} `;
  return `${generique ? generique + " " : ""}${liaison}${specifique}${o}`.trim();
}

const memeParite = (a, b) => a % 2 === b % 2;
const ECART_MAX = 20; // même règle que carte-au : numéro voisin du même côté de la rue

function dansPlage(n, [de, a]) {
  if (n < de || n > a) return false;
  return de === a || !memeParite(de, a) || memeParite(n, de);
}

// Position [latitude, longitude] d'un résultat, lue dans positions/<x>.json
// (même ordre que les variantes et leurs plages). Entiers écrits par
// scripts/preparer_district.py : longitude = -74 + x / 1e5, latitude = 45 + y / 1e5.
export function position(positionsRue, [i, j]) {
  const p = positionsRue?.[i]?.[j];
  return p ? [45 + p[1] / 1e5, -74 + p[0] / 1e5] : null;
}

// variantes : [[générique, lien, orientation, spécifique, [[de, a, zone], …]], …]
// Une même variante peut exister dans plusieurs secteurs (la « 1re Avenue » de
// Rosemont, de Lachine, de Verdun…) : on garde un résultat par territoire.
export function chercherNumero(variantes, repere, numeros) {
  const filtrer = (liste, champ, valeur) => {
    if (!valeur) return liste;
    const gardees = liste.filter((v) => v[champ] === valeur);
    return gardees.length ? gardees : liste; // indication ignorée si elle n'existe pas
  };
  let candidates = filtrer(variantes, 2, repere.orientation);
  candidates = filtrer(candidates, 0, repere.generique);

  for (const n of numeros) {
    const exacts = [];
    for (const v of candidates) {
      const parZone = new Map(); // zone → indice de la première plage qui contient le numéro
      v[4].forEach((plage, j) => { if (dansPlage(n, plage) && !parZone.has(plage[2])) parZone.set(plage[2], j); });
      for (const [zone, j] of parZone) {
        exacts.push({ rue: libelleRue(v), numero: n, zone, plage: [variantes.indexOf(v), j], approximatif: false });
      }
    }
    if (exacts.length) return exacts;
  }

  // Numéro absent du registre : le plus proche du même côté de la rue.
  const n = numeros[0];
  if (n === undefined) return [];
  const proches = [];
  for (const v of candidates) {
    const parZone = new Map(); // zone → voisin le plus proche
    for (const [j, [de, a, zone]] of v[4].entries()) {
      for (const voisin of [de, a]) {
        const ecart = Math.abs(voisin - n);
        const actuel = parZone.get(zone);
        if (memeParite(voisin, n) && ecart <= ECART_MAX && (!actuel || ecart < actuel.ecart)) {
          parZone.set(zone, { ecart, voisin, plage: [variantes.indexOf(v), j] });
        }
      }
    }
    for (const [zone, { ecart, voisin, plage }] of parZone) {
      proches.push({ rue: libelleRue(v), numero: n, voisin, zone, ecart, plage, approximatif: true });
    }
  }
  return proches.sort((a, b) => a.ecart - b.ecart);
}

// Plus petit et plus grand numéro de la rue, pour aider à corriger une faute.
export function etendue(variantes) {
  let min = Infinity, max = -Infinity;
  for (const v of variantes) for (const [de, a] of v[4]) { min = Math.min(min, de); max = Math.max(max, a); }
  return { min, max };
}

// Distance d'édition (insertion, suppression, substitution, inversion de deux
// lettres voisines), arrêtée dès qu'elle dépasse max.
function distance(a, b, max) {
  if (Math.abs(a.length - b.length) > max) return max + 1;
  let avant = null;
  let prec = Array.from({ length: b.length + 1 }, (_, j) => j);
  for (let i = 1; i <= a.length; i++) {
    const cour = [i];
    let minLigne = i;
    for (let j = 1; j <= b.length; j++) {
      let d = Math.min(prec[j] + 1, cour[j - 1] + 1, prec[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
      if (avant && i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) d = Math.min(d, avant[j - 2] + 1);
      cour.push(d);
      minLigne = Math.min(minLigne, d);
    }
    if (minLigne > max) return max + 1;
    avant = prec;
    prec = cour;
  }
  return prec[b.length];
}

const VILLES = new Set(["montreal", "mtl", "qc", "quebec", "canada", "ville"]);

// Propositions de rues pour la saisie en cours (menu de suggestions) et pour
// corriger une rue introuvable. Renvoie le numéro tel qu'écrit, le générique
// et l'orientation saisis, et les rues classées (meilleure d'abord) :
//   0 nom exact (avec ou sans particule) · 1 nom qui commence par la saisie ·
//   2 chaque mot saisi commence un mot du nom · 3 et plus : faute de frappe.
export function proposer(saisie, rues, max = 8) {
  const brut = saisie.match(/^\s*(\d+[a-z]?(?:\s?[-–]\s?\d+[a-z]?)?)/i);
  const { mots } = analyser(saisie);
  const generique = mots.map((m) => GENERIQUES[m]).find(Boolean) ?? null;
  const orientation = mots.map((m) => ORIENTATIONS[m]).find(Boolean) ?? null;
  const motsRue = mots.filter((m) => !(m in GENERIQUES) && !(m in ORIENTATIONS) && !VILLES.has(m) && !/^\d+$/.test(m));
  // « Sherbrooke St W » : « st » (lu « saint ») après le nom veut dire « street ».
  while (motsRue.length > 1 && motsRue.at(-1) === "saint") motsRue.pop();
  const q = motsRue.join(" ");
  const qCourt = sansParticule(q);
  const resultat = { numero: brut ? brut[1].replace(/\s/g, "") : null, generique, orientation, rues: [] };
  if (qCourt.replace(/\s/g, "").length < 2) return resultat;

  const motsQ = qCourt.split(" ");
  const tolerance = qCourt.length <= 5 ? 1 : 2;
  for (const cle of rues.keys()) {
    const court = sansParticule(cle);
    let score;
    if (cle === q || court === qCourt) score = 0;
    else if (cle.startsWith(q) || court.startsWith(qCourt)) score = 1;
    else {
      const motsCle = court.split(" ");
      if (motsQ.every((w) => motsCle.some((m) => m.startsWith(w)))) score = 2;
      else if (qCourt.length >= 4) {
        const d = distance(qCourt, court, tolerance);
        if (d <= tolerance) score = 2 + d;
      }
    }
    if (score !== undefined) resultat.rues.push({ cle, nom: rues.get(cle), score });
  }
  resultat.rues.sort((a, b) => a.score - b.score || a.cle.length - b.cle.length || a.cle.localeCompare(b.cle));
  resultat.rues = resultat.rues.slice(0, max);
  return resultat;
}

// Saisie réécrite avec la rue choisie : « 6800 lanaudière e » → « 6800 De Lanaudière Est ».
export function reecrire(proposition, rue) {
  const { generique } = proposition;
  // Rue numérotée : « 1re Avenue », comme libelleRue()
  const nom = /^\d/.test(rue.nom) && generique
    ? `${rue.nom} ${generique[0].toUpperCase()}${generique.slice(1)}`
    : [generique, rue.nom].filter(Boolean).join(" ");
  const morceaux = [proposition.numero, nom, NOM_ORIENTATION[proposition.orientation]];
  return morceaux.filter(Boolean).join(" ");
}

// Suggestions de rues quand le nom n'est pas trouvé : celles dont un mot
// commence comme le mot le plus long de la saisie, moins ses 3 dernières
// lettres (« Sherbroke » → « sherbr » → Sherbrooke).
export function suggerer(mots, rues, max = 6) {
  const mot = mots.filter((m) => !libre(m) && !/^\d+$/.test(m)).sort((a, b) => b.length - a.length)[0];
  if (!mot || mot.length < 3) return [];
  const debut = mot.slice(0, Math.max(3, mot.length - 3));
  const trouvees = [];
  for (const cle of rues.keys()) {
    if (cle.split(" ").some((m) => m.startsWith(debut))) {
      trouvees.push(cle);
      if (trouvees.length >= max) break;
    }
  }
  return trouvees;
}
