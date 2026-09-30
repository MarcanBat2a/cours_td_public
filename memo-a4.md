# Mémo - Bases orientées documents

**UE 1 · Chapitre 2** · une feuille, recto verso

## Le vocabulaire

| Terme | Sens |
| --- | --- |
| Document, collection | objet BSON typé, 16 Mo au plus ; ensemble de documents |
| `_id` | identifiant obligatoire et unique, choisi ou généré (ObjectId) |
| Notation pointée | accès à un champ imbriqué : `"note.moyenne"`, entre guillemets |
| Pipeline | suite d'étapes d'agrégation, exécutées dans l'ordre écrit |
| COLLSCAN, IXSCAN | lecture de toute la collection ; lecture par un index |
| Imbriquer, référencer | ranger dans le document ; relier par un identifiant |
| Replica set | un primaire qui reçoit les écritures, des secondaires qui les rejouent |

## Lire

```js
db.produits.find({ categorie: "livre", prix: { $gte: 20, $lte: 50 } },   // filtre
                 { nom: 1, prix: 1, _id: 0 })                            // projection
           .sort({ prix: 1, _id: 1 }).limit(5)
db.produits.countDocuments({ stock: { $gt: 0 } })
db.produits.distinct("categorie")
```

| Opérateur | Sens |
| --- | --- |
| `$eq` `$ne` `$gt` `$gte` `$lt` `$lte` | comparaisons, sans mélange de types |
| `$in` `$nin` | dans la liste, hors de la liste |
| `$or: [ {…}, {…} ]` | l'un des filtres ; plusieurs champs dans un filtre : ET |
| `$exists: false` | le champ est absent |
| `$type: "string"` | le champ a ce type : `"int"`, `"double"`, `"null"`, `"array"`… |
| `{ tags: "bio" }` | le tableau contient la valeur |
| `$all: ["a", "b"]` | le tableau contient toutes ces valeurs |
| `$size: 3` | le tableau a exactement trois éléments |
| `$elemMatch: { taille: "M", stock: { $gt: 0 } }` | **un même** élément vérifie toutes les conditions |

Quatre pièges silencieux :

- `{ prix: { $gte: 20 }, prix: { $lte: 50 } }` : la seconde clé écrase la première ;
- `{ note: { nb: 21, moyenne: 4.6 } }` : égalité avec le sous-document entier, ordre compris ;
- `{ stock: null }` trouve aussi les documents sans le champ ; `{ stock: { $ne: 0 } }` aussi ;
- une date ne se compare qu'à une date : `ISODate("2026-07-01")`, pas `"2026-07-01"`.

## Écrire

```js
db.produits.updateOne({ _id: "T-100" }, { $set: { prix: 27 } })   // matchedCount, modifiedCount
db.produits.updateMany(filtre, modification)
db.produits.replaceOne(filtre, document)      // remplace tout, sauf _id
db.produits.updateOne(filtre, modification, { upsert: true })     // crée si absent
db.produits.deleteOne(filtre)
```

| Opérateur | Effet |
| --- | --- |
| `$set`, `$unset`, `$rename` | fixer, supprimer, renommer un champ |
| `$inc` | ajouter un nombre, sur le serveur |
| `$push`, `$addToSet`, `$pull` | ajouter, ajouter si absent, retirer d'un tableau |
| `"variantes.$.stock"` | l'élément trouvé par le filtre |
| `"variantes.$[].stock"` | tous les éléments |
| `[ { $set: { prix: { $toInt: "$prix" } } } ]` | modification écrite en pipeline : calcule depuis l'ancienne valeur |

Tester et décrémenter en une seule opération :

```js
db.produits.updateOne({ _id: "A-400", stock: { $gte: 1 } }, { $inc: { stock: -1 } })
// matchedCount 1 : vendu · matchedCount 0 : rupture de stock, réponse métier
```

Une écriture sur **un** document est atomique. Sur plusieurs documents :
`session.startTransaction()` … `session.commitTransaction()`.

## Agréger

```js
db.commandes.aggregate([
  { $match: { statut: { $in: ["expediee", "livree"] } } },     // WHERE
  { $unwind: "$lignes" },                                      // un document par élément
  { $group: { _id: "$lignes.produit",                          // GROUP BY
              quantite: { $sum: "$lignes.quantite" } } },
  { $match: { quantite: { $gte: 100 } } },                     // HAVING
  { $sort: { quantite: -1, _id: 1 } },
  { $limit: 3 }
])
```

| Étape | Rôle |
| --- | --- |
| `$project`, `$set` | choisir, renommer, calculer des champs |
| `$lookup: { from, localField, foreignField, as }` | jointure externe gauche |
| `$count: "n"` | compter les documents arrivés à cette étape |
| `$out: "collection"` | écrire le résultat dans une collection |

Accumulateurs : `$sum`, `$avg`, `$min`, `$max`, `$first`, `$push`,
`$addToSet`. `{ $sum: 1 }` compte des documents. `$avg` ignore les valeurs
non numériques.
Expressions : `$multiply`, `$toInt`, `$size`, `$bsonSize`,
`$dateToString: { format: "%Y-%m", date: "$date" }`.

## Indexer

```js
db.commandes.createIndex({ "client.id": 1, date: -1 })
db.avis.createIndex({ produit: 1, client: 1 }, { unique: true })
db.commandes.getIndexes()
db.commandes.find(filtre).explain("executionStats")
db.produits.find(filtre).hint("C")            // imposer un index
```

| Champ de `explain` | Question |
| --- | --- |
| `winningPlan.stage` | COLLSCAN, IXSCAN, FETCH, SORT, PROJECTION_COVERED ? |
| `nReturned` | combien de documents renvoyés ? |
| `totalKeysExamined` | combien d'entrées d'index lues ? |
| `totalDocsExamined` | combien de documents lus ? |

- Un index composé sert ses préfixes.
- Règle ESR : les champs d'**é**galité, puis ceux du tri (**s**ort), puis
  ceux d'intervalle (**r**ange).
- Requête couverte : filtre et projection dans l'index, `_id: 0`.
- Chaque index ralentit les écritures et occupe de la mémoire.

## Modéliser

| Relation | Choix par défaut |
| --- | --- |
| Un à quelques-uns, lus ensemble | tableau imbriqué |
| Un à beaucoup, sans limite | référence dans chaque élément |
| Donnée à figer (prix payé) | copie dans le document, jamais propagée |
| Donnée lue souvent (nom de la marque) | copie, à propager avec `updateMany` |

Partir des accès, pas des entités. Ce qui grandit sans limite se
référence.

```js
db.runCommand({ collMod: "avis",
  validator: { $jsonSchema: { bsonType: "object", required: ["produit", "note"],
    properties: { note: { bsonType: "int", minimum: 1, maximum: 5 } } } },
  validationLevel: "strict",        // ou "moderate" : épargne les documents déjà invalides
  validationAction: "error" })      // ou "warn" : accepte et journalise
```

## Distribuer

| Réglage | Valeurs | Choisit |
| --- | --- | --- |
| `writeConcern` | `{ w: 1 }`, `{ w: "majority", wtimeout: 3000 }` | qui doit avoir reçu l'écriture avant de confirmer |
| `readPreference` | `primary`, `secondary`, `secondaryPreferred`, `nearest` | le membre qui répond |
| `readConcern` | `local`, `majority`, `linearizable` | la garantie sur ce qui est lu |

- `w: 1` : rapide, toujours une réponse ; une écriture confirmée peut être
  annulée (rollback) si le primaire est isolé. Profil PA/EL.
- `w: "majority"` : attend, ou échoue ; rien de confirmé n'est perdu.
  Profil PC/EC.
- Une erreur de confirmation n'annule pas l'écriture sur le primaire.

```js
rs.status().members.forEach(m => print(m.name, m.stateStr))
db.produits.find(filtre).readConcern("majority")
db.getMongo().setReadPref("secondary")
```

## Docker

```bash
docker compose up -d --build                        # démarrer
docker compose logs -f atelier                      # suivre le chargement
docker compose exec mongo-a mongosh boutique        # ouvrir mongosh
docker compose exec atelier python charger.py       # remettre les données à zéro
docker compose stop mongo-a                         # arrêt propre
docker network disconnect ue1-boutique mongo-a      # partition
docker network connect ue1-boutique mongo-a         # fin de partition
docker compose down -v                              # tout arrêter et effacer
```
