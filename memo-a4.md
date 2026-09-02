# Mémo - la matière de votre A4

**UE 1 - Persistance & Systèmes Distribués (NoSQL) · Chapitre 2**
Distribué en fin de séance 1 · à garder sous la main pendant toutes les missions

> Ce mémo récapitule toute la syntaxe du chapitre : pendant les séances, il vous
> évite de fouiller le deck. En fin de chapitre, il devient la matière de votre
> **feuille A4 manuscrite** autorisée à l'épreuve, à côté du tableau C ou A par
> opération du chapitre 1 (mission 5).
>
> **Recopiez-le à la main.** Ce n'est pas une formule de politesse : la recopie
> est la dernière mission du chapitre, et une antisèche photocopiée ne se
> retrouve pas sous stress - une antisèche écrite, si.

## Lire

```js
db.col.find(filtre, projection).sort({ champ: -1 }).limit(5)
```

| Besoin | Écriture |
| --- | --- |
| égalité | `{ type: "album" }` - la casse compte |
| ET | `{ type: "album", genres: "jazz" }` (virgule) |
| OU | `{ $or: [ {…}, {…} ] }` |
| comparaisons | `{ duree_s: { $gt: 3600 } }` · `$gte` `$lt` `$lte` `$ne` |
| liste | `{ type: { $in: ["album", "concert"] } }` |
| plage | `{ duree_s: { $gte: 1200, $lte: 3600 } }` |
| champ imbriqué | `{ "details.saison": 3 }` - guillemets obligatoires |
| contient (texte) | `{ titre: { $regex: "refuge", $options: "i" } }` |
| date | `ISODate("2026-12-14")` - **jamais** `"2026-12-14"` |
| projection | `{ titre: 1, _id: 0 }` - 1 garde, 0 exclut |
| tri | `.sort({ date_sortie: -1, _id: 1 })` - toujours un second critère |
| compter | `countDocuments(filtre)` |

**Les deux zéros sans erreur** : une date écrite en chaîne, et une égalité
là où on voulait « contient ». Zéro n'est pas une erreur, c'est une réponse -
et personne ne la voit.

## Tableaux, absent, null

| | |
| --- | --- |
| `{ genres: "jazz" }` | matche si **un** élément vaut jazz |
| `{ genres: { $all: [a, b] } }` | a **et** b |
| `{ genres: { $size: 3 } }` | exactement 3 éléments |
| `{ "details.pistes.duree_s": { $gt: 360 } }` | **une** piste de plus de 6 min (171) |
| `{ "details.pistes": { $elemMatch: { no: 1, duree_s: { $gt: 360 } } } }` | les deux conditions sur **le même** élément (41) |
| `{ champ: null }` | null **et** absent (le piège du 339) |
| `{ champ: { $exists: false } }` | absent seulement |
| `{ champ: { $type: "null" } }` | null explicite seulement |

Deux conditions sur un tableau → `$elemMatch`, ou vous répondez faux sans
le savoir.

## Écrire

| | |
| --- | --- |
| `insertOne(doc)` / `insertMany([…])` | créer - `_id` généré si absent |
| `updateOne(f, { $set: {…} })` | retoucher un champ · `$unset` le retire |
| `{ $inc: { n: 1 } }` | incrémenter, atomique |
| `{ $push / $addToSet }` | ajouter à un tableau - `$addToSet` seulement s'il n'y est pas |
| `{ "details.pistes.$.titre": … }` | `$` = l'élément qui a matché le filtre |
| `{ upsert: true }` | modifier, ou créer si absent - un seul geste |
| `replaceOne` | remplace **tout le document** - détruit les champs absents, sans un mot |
| `deleteOne` / `deleteMany` | supprimer |

Atomicité : **garantie sur un document, pas au-delà**. Ce qui doit changer
ensemble vit dans le même document.

## Agréger

```js
db.ecoutes.aggregate([
  { $match: { date: { $gte: ISODate("2026-12-14"), $lt: ISODate("2026-12-21T12:00") } } },
  { $group: { _id: "$contenu_id", nb: { $sum: 1 } } },
  { $sort: { nb: -1, _id: 1 } },
  { $limit: 50 }
])
```

| Étape | Rôle |
| --- | --- |
| `$match` | filtre (comme `find`) - **en premier** |
| `$group` | `_id` = clé de regroupement (`"$champ"`) ; `$sum` `$avg` `$min` `$max` `$push` ; compter = `{ $sum: 1 }` |
| `$sort` / `$limit` / `$project` | comme leurs homonymes |
| `$lookup` | la jointure - une par requête au plus, et on se demande pourquoi |

Avant d'exécuter : **quels documents entrent dans chaque étape ?** Un `$match`
sur `date` placé après le `$group` ne voit plus de champ `date` : vide, sans
erreur.

## Indexer

```js
db.ecoutes.createIndex({ date: 1 })
db.ecoutes.createIndex({ utilisateur_id: 1, date: -1 })   // égalité d'abord, tri ensuite
db.ecoutes.find(filtre).explain("executionStats")
```

Trois nombres à lire : `totalDocsExamined`, `nReturned`,
`executionTimeMillis` - et le stage : `COLLSCAN` (tout lire) ou `IXSCAN`
(l'index travaille). Gagné quand `docsExamined ≈ nReturned`. L'index est fait
**pour une requête** : le champ d'égalité d'abord, le champ de tri ensuite.
Chaque index se paie à **chaque écriture** : on n'en pose pas « au cas où ».

## Modéliser - trois questions

1. **Se lit-elle toujours avec son parent ?**
2. **Est-elle bornée ?**
3. **Se modifie-t-elle seule ?**

| Geste | Quand | Chez Ondine |
| --- | --- | --- |
| **imbriquer** | lu ensemble, borné, modifié ensemble | les pistes, les playlists |
| **référencer** | non borné, ou partagé, ou vit seul | les avis, les écoutes |
| **dupliquer** | une lecture veut un champ d'à côté | le `pseudo` dans l'avis |

Un seul non à la question 2 → référencer, toujours. Limite dure : **16 Mo par
document**. Ce qui grossit sans borne ne vit pas dans le document.

## Le garde-fou (démo)

```js
db.runCommand({ collMod: "contenus", validator: { $jsonSchema: {
  required: ["titre", "type", "artiste", "details"],
  properties: { type: { enum: ["album", "podcast", "livre_audio", "concert"] } } } },
  validationLevel: "moderate", validationAction: "error" })
```

`moderate` : les anciens documents non conformes restent ; on ne bloque que
les écritures nouvelles. On remet **la porte**, pas les 61 colonnes.

## Dans le site - mongosh → pymongo

Ce que vous tapez dans `mongosh` se traduit presque mot pour mot dans
`app/stockage/mongo.py`. Les clés deviennent des chaînes Python, les
opérateurs restent des chaînes, et `base()` remplace `db`.

| mongosh | pymongo |
| --- | --- |
| `db.contenus.find({ type: "album" })` | `base().contenus.find({"type": "album"})` |
| `.sort({ date_sortie: -1, _id: 1 })` | `.sort([("date_sortie", -1), ("_id", 1)])` |
| `.limit(60)` · projection `{ titre: 1 }` | `.limit(60)` · `find(filtre, {"titre": 1})` |
| `findOne({ _id: "a001" })` | `find_one({"_id": "a001"})` - `None` si absent |
| `countDocuments(filtre)` | `count_documents(filtre)` |
| `insertOne({...})` | `insert_one({...})` |
| `updateOne(filtre, { $set: {...} })` | `update_one(filtre, {"$set": {...}})` |
| `aggregate([ {...}, {...} ])` | `aggregate([{...}, {...}])` - un itérable |
| `ISODate("2026-12-14")` | `datetime(2026, 12, 14)` |
| un curseur | un itérable : `list(...)` ou `for c in ...` |

Deux réflexes :

- les fonctions du site attendent une clé `"id"` : `c["id"] = c.pop("_id")` ;
- après un changement de `.env`, `docker compose up -d web` ; après un
  changement de code, rien : le serveur se recharge tout seul.
