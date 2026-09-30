"use strict";
const $ = (id) => document.getElementById(id);
const CLE = "popup-carnet-v1";
let carnet = {notes: {}, preuves: {}, essais: {}, brouillons: {}};
let stockageDisponible = true;
try { carnet = {...carnet, ...JSON.parse(localStorage.getItem(CLE) || "{}")}; } catch (_) { stockageDisponible = false; }
let courant = 0, moteur = "mongo", indice = 0, dernier = null;
const modeles = {
  find: {filter: {}, projection: {}, sort: {}, limit: 10},
  explain: {filter: {}, sort: {}},
  aggregate: {pipeline: []},
  updateOne: {filter: {_id: "IDENTIFIANT"}, update: {$set: {champ: "valeur"}}},
  updateMany: {filter: {champ: {$type: "string"}}, update: [{$set: {champ: {$toInt: "$champ"}}}]},
  insertOne: {document: {_id: "NOUVEAU", nom: "À compléter"}},
  createIndex: {keys: {champ: 1}, name: "mon_index"}
};
function sauver() {
  try { localStorage.setItem(CLE, JSON.stringify(carnet)); } catch (_) { stockageDisponible = false; }
  $("save-state").textContent = stockageDisponible ? "Carnet enregistré dans ce navigateur." : "Stockage indisponible : exportez votre carnet avant de fermer.";
}
function brouillon() {
  carnet.brouillons[MISSIONS[courant].id] = {moteur, base: $("base").value, collection: $("collection").value, operation: $("operation").value, method: $("method").value, path: $("path").value, texte: $("payload").value};
  sauver();
}
function tabs(choix) {
  moteur = choix;
  $("tab-mongo").setAttribute("aria-selected", choix === "mongo");
  $("tab-elastic").setAttribute("aria-selected", choix === "elastic");
  $("mongo-controls").hidden = choix !== "mongo";
  $("elastic-controls").hidden = choix !== "elastic";
  $("syntax-note").textContent = choix === "mongo" ? "JSON strict : clés entre guillemets, sans commentaire. Ce corps est transmis au pilote MongoDB." : "JSON strict : choisissez la méthode HTTP et le chemin. L'identifiant MongoDB correspond au _id Elasticsearch.";
}
function preparer() {
  const m = MISSIONS[courant];
  tabs(m.moteur);
  if (m.moteur === "mongo") { $("base").value = m.base; $("collection").value = m.collection; $("operation").value = m.operation; }
  else { $("method").value = m.method; $("path").value = m.path; }
  $("payload").value = JSON.stringify(m.depart, null, 2);
  brouillon();
}
function navigation() {
  $("mission-list").replaceChildren();
  MISSIONS.forEach((m, i) => {
    const bouton = document.createElement("button");
    bouton.className = `mission-nav${i === courant ? " active" : ""}${carnet.preuves[m.id] ? " done" : ""}`;
    bouton.setAttribute("aria-current", i === courant ? "step" : "false");
    const numero = document.createElement("span"); numero.className = "nav-number"; numero.textContent = carnet.preuves[m.id] ? "✓" : m.id;
    const titre = document.createElement("span"); titre.textContent = m.court;
    bouton.append(numero, titre); bouton.addEventListener("click", () => ouvrir(i)); $("mission-list").append(bouton);
  });
  const n = MISSIONS.filter(m => carnet.preuves[m.id]).length;
  $("progress").textContent = `${n} / ${MISSIONS.length}`; $("progress-bar").value = n;
}
function ouvrir(i) {
  courant = i; indice = 0; dernier = null;
  const m = MISSIONS[i];
  $("mission-number").textContent = `Mission ${m.id} / ${MISSIONS.length}`;
  $("mission-time").textContent = `Environ ${m.minutes} min`;
  $("mission-title").textContent = m.titre; $("mission-concept").textContent = m.concept;
  $("mission-person").textContent = m.personne; $("mission-story").textContent = m.histoire;
  $("mission-tasks").replaceChildren(...m.taches.map(t => {const li = document.createElement("li"); li.textContent = t; return li;}));
  $("mission-proof").textContent = m.preuve; $("notes").value = carnet.notes[m.id] || "";
  $("hint").hidden = true; $("hint-counter").textContent = ""; $("indice").disabled = false;
  $("scene").hidden = m.id !== 8;
  $("suivante").disabled = i === MISSIONS.length - 1;
  $("consigner").textContent = carnet.preuves[m.id] ? "Actualiser ma preuve" : "Consigner ma preuve";
  const d = carnet.brouillons[m.id];
  if (d) { tabs(d.moteur); for (const key of ["base", "collection", "operation", "method", "path"]) $(key).value = d[key]; $("payload").value = d.texte; }
  else preparer();
  $("result-cards").replaceChildren(); $("result-json").textContent = "Les requêtes de cette mission apparaîtront ici."; $("result-meta").textContent = "";
  feedback("Prédisez un résultat, puis interrogez la base."); navigation();
}
function feedback(texte, type = "") { $("feedback").textContent = texte; $("feedback").className = "feedback" + (type ? " " + type : ""); }
async function api(chemin, demande) {
  const response = await fetch(chemin, demande ? {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(demande)} : {});
  const data = await response.json();
  if (!response.ok) throw new Error(data.erreur || `Erreur HTTP ${response.status}`);
  return data;
}
function carte(doc, id, score) {
  const c = document.createElement("div"); c.className = "result-card";
  const top = document.createElement("div"); top.className = "card-top";
  const nom = document.createElement("span"); nom.className = "card-name"; nom.textContent = doc.nom || (typeof doc._id === "string" ? doc._id : "Résultat");
  const ident = document.createElement("span"); ident.className = "card-id"; ident.textContent = id || (typeof doc._id === "string" ? doc._id : ""); top.append(nom, ident); c.append(top);
  const champs = document.createElement("pre"); champs.className = "card-fields";
  const contenu = {...doc}; if (score !== undefined) contenu._score = score;
  champs.textContent = JSON.stringify(contenu, null, 2); c.append(champs); return c;
}
function afficher(data) {
  dernier = data; const r = data.resultat;
  $("result-json").textContent = JSON.stringify(r, null, 2);
  $("result-meta").textContent = data.duree_ms === undefined ? data.source || "" : `${data.duree_ms} ms côté atelier`;
  $("result-cards").replaceChildren();
  let docs = [], info;
  if (r && Array.isArray(r.documents)) {docs = r.documents.map(d => carte(d)); info = r.total === undefined ? `${r.documents.length} résultats affichés${r.tronque ? " (limite de 50 atteinte)" : ""}.` : `${r.total} documents correspondent au filtre, ${r.documents.length} affichés.`;}
  else if (r && r.hits) {docs = r.hits.hits.map(d => carte(d._source, d._id, d._score)); const total = r.hits.total; info = `${total?.value ?? total} résultats de recherche${total?.relation === "gte" ? " ou plus" : ""}.`;}
  else if (r && r.tokens) {docs = r.tokens.map(d => carte(d)); info = `${r.tokens.length} termes produits par l'analyseur.`;}
  else if (r && r.executionStats) {const e = r.executionStats; docs = [carte({nReturned: e.nReturned, totalDocsExamined: e.totalDocsExamined, totalKeysExamined: e.totalKeysExamined, executionTimeMillis: e.executionTimeMillis})]; info = "Plan réel : les compteurs se trouvent ci-dessous et dans la réponse JSON.";}
  else if (r && r.message) info = r.message;
  else if (r && r.matchedCount !== undefined) info = `${r.matchedCount} documents correspondent, ${r.modifiedCount ?? 0} modifiés.`;
  else info = "Requête exécutée. Consultez la réponse JSON.";
  if (r && r.accepte === false) info = r.message;
  feedback(info, "success"); $("result-cards").append(...docs);
  if (!docs.length) $("raw-detail").open = true;
}
function garder(demande, data, missionId) {
  const liste = carnet.essais[missionId] || [];
  liste.push({heure: new Date().toLocaleTimeString("fr-FR"), moteur, demande, resultat: JSON.stringify(data.resultat, null, 2).slice(0, 5000)});
  carnet.essais[missionId] = liste.slice(-20); sauver();
}
let occupe = false;
function attente(actif) {occupe = actif; $("executer").disabled = actif; $("executer").textContent = actif ? "Requête en cours..." : "Exécuter la requête"; document.querySelectorAll("[data-action]").forEach(b => b.disabled = actif);}
async function executer() {
  if (occupe) return;
  const missionId = MISSIONS[courant].id;
  let demande;
  try {
    const payload = JSON.parse($("payload").value || "{}");
    demande = moteur === "mongo" ? {base: $("base").value, collection: $("collection").value, operation: $("operation").value, payload} : {method: $("method").value, path: $("path").value, payload};
  } catch (e) {feedback(`Le JSON n'est pas valide : ${e.message}\nVérifiez les guillemets, virgules et accolades.`, "error"); return;}
  brouillon(); attente(true); feedback("La base exécute votre requête...");
  try {const data = await api(`/api/${moteur === "mongo" ? "mongo" : "elastic"}`, demande); garder(demande, data, missionId); if (MISSIONS[courant].id === missionId) afficher(data); await statut();}
  catch (e) {feedback(e.message, "error");}
  finally {attente(false);}
}
async function statut() {
  try {const e = await api("/api/status"); $("connection").textContent = e.mongo && e.elastic ? `MongoDB connecté · Elasticsearch connecté` : "Une base ne répond pas : consultez les journaux Docker."; $("stock-mongo").textContent = e.stock_mongo ?? "absent"; $("stock-elastic").textContent = e.stock_elastic ?? "absent";}
  catch (_) {$("connection").textContent = "Atelier inaccessible : vérifiez Docker.";}
}
async function scene(nom, acheteur) {
  if (occupe) return;
  const missionId = MISSIONS[courant].id; attente(true);
  try {const data = await api("/api/action", {action: nom}); if (acheteur) data.resultat.message = `${acheteur} : ${data.resultat.message}`; afficher(data); garder({action: nom, acheteur}, data, missionId); await statut();}
  catch (e) {feedback(e.message, "error");}
  finally {attente(false);}
}
async function exporter() {
  let texte = "# Carnet de bord : Panique au Pop-up\n\nBinôme : \n\n";
  MISSIONS.forEach(m => {texte += `## Mission ${m.id} : ${m.titre}\n\nPreuve consignée : ${carnet.preuves[m.id] ? "oui" : "non"}\n\n${carnet.notes[m.id] || "À compléter."}\n\n`; (carnet.essais[m.id] || []).forEach((e, i) => {texte += `### Essai ${i + 1} (${e.heure})\n\nDemande :\n\n\`\`\`json\n${JSON.stringify(e.demande, null, 2)}\n\`\`\`\n\nRéponse conservée (5 000 caractères maximum) :\n\n\`\`\`json\n${e.resultat}\n\`\`\`\n\n`;});});
  $("exporter").disabled = true;
  try {
    const exportation = await api("/api/export", {markdown: texte});
    $("export-link").href = exportation.url;
    $("export-link").hidden = false;
    $("save-state").textContent = "Carnet prêt. Cliquez sur Télécharger reponses.md dans la barre du haut.";
  } catch (e) { feedback(`Export impossible : ${e.message}`, "error"); }
  finally { $("exporter").disabled = false; }
}
$("charger").addEventListener("click", preparer);
$("indice").addEventListener("click", () => {const m = MISSIONS[courant]; if (indice < m.indices.length) {$("hint").hidden = false; $("hint").textContent = m.indices.slice(0, ++indice).map((h, i) => `${i + 1}. ${h}`).join("\n\n"); $("hint-counter").textContent = `${indice} / ${m.indices.length} indices`; $("indice").disabled = indice === m.indices.length;}});
$("tab-mongo").addEventListener("click", () => {tabs("mongo"); $("payload").value = JSON.stringify(modeles[$("operation").value], null, 2); brouillon();});
$("tab-elastic").addEventListener("click", () => {tabs("elastic"); $("payload").value = JSON.stringify({query: {match_all: {}}, size: 10}, null, 2); brouillon();});
$("modele").addEventListener("click", () => {$("payload").value = JSON.stringify(moteur === "mongo" ? modeles[$("operation").value] : {query: {match_all: {}}, size: 10}, null, 2); brouillon();});
for (const id of ["base", "collection", "operation", "method", "path"]) $(id).addEventListener("change", brouillon);
$("payload").addEventListener("input", brouillon);
$("payload").addEventListener("keydown", e => {if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {e.preventDefault(); executer();}});
$("executer").addEventListener("click", executer);
$("notes").addEventListener("input", () => {carnet.notes[MISSIONS[courant].id] = $("notes").value; sauver();});
$("consigner").addEventListener("click", () => {const id = MISSIONS[courant].id; if (!$("notes").value.trim()) {$("save-state").textContent = "Ajoutez votre preuve et votre explication avant de la consigner."; $("notes").focus(); return;} carnet.notes[id] = $("notes").value; carnet.preuves[id] = true; sauver(); navigation(); $("consigner").textContent = "Actualiser ma preuve"; $("save-state").textContent = "Preuve consignée. Exportez le carnet pour le rendre.";});
$("suivante").addEventListener("click", () => {if (courant < MISSIONS.length - 1) {ouvrir(courant + 1); $("mission-title").scrollIntoView({block: "start"});}});
document.querySelectorAll("[data-action]").forEach(b => b.addEventListener("click", () => scene(b.dataset.action, b.dataset.client)));
$("exporter").addEventListener("click", exporter);
$("restaurer").addEventListener("click", () => $("reset-dialog").showModal());
$("annuler-reset").addEventListener("click", () => $("reset-dialog").close());
$("confirmer-reset").addEventListener("click", async () => {$("reset-dialog").close(); await scene("restaurer_cours");});
ouvrir(0); statut(); setInterval(statut, 15000);
