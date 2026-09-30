# Mémo : bases orientées documents

**UE 1 · Chapitre 2 · MongoDB et Elasticsearch**

## Trois interfaces, deux syntaxes

Le site utilise des corps JSON stricts : clés entre guillemets doubles,
pas de commentaires, pas de virgule finale. Vous sélectionnez l'opération
MongoDB séparément. Compass dispose de champs Filter, Project et Sort ;
son shell intégré utilise la syntaxe JavaScript de mongosh.

| Opération MongoDB du site | Corps JSON |
| --- | --- |
| `find` | `{ "filter": {}, "projection": {}, "sort": {}, "limit": 10 }` |
| `aggregate` | `{ "pipeline": [] }` |
| `updateOne`, `updateMany` | `{ "filter": {}, "update": {} }` ; `update` peut aussi être un tableau d'étapes |
| `insertOne` | `{ "document": {} }` |
| `createIndex` | `{ "keys": {}, "name": "mon_index" }` |
| `explain` | filtre, projection et tri comme `find` ; omettre `limit` pour mesurer toute la requête |

Dans Elasticvue et l'éditeur Elasticsearch : méthode HTTP, chemin et
corps JSON se renseignent séparément. Exemples de chemins :
`/catalogue/_mapping`, `/catalogue/_analyze`, `/catalogue/_search`.

## Lire des documents MongoDB

```js
db.produits.find(
  { categorie: "maison", prix: { $gte: 20, $lte: 60 } },
  { nom: 1, prix: 1, _id: 0 }
).sort({ prix: 1, _id: 1 }).limit(3)
db.produits.countDocuments({ tags: "bio" })
db.produits.distinct("categorie")
```

| Écriture dans un filtre | Sens |
| --- | --- |
| `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte` | comparaisons ; le type de la valeur compte |
| `{ "categorie": { "$in": ["audio", "maison"] } }` | une valeur dans la liste |
| `{ "$or": [{}, {}] }` | au moins un des filtres ; plusieurs champs dans un filtre : ET |
| `{ "note.moyenne": { "$gte": 4 } }` | accès à un champ imbriqué |
| `{ "tags": "bio" }` | un élément du tableau porte la valeur |
| `{ "tags": { "$all": ["bio", "équitable"] } }` | le tableau contient toutes les valeurs |
| `{ "auteurs": { "$size": 3 } }` | le tableau compte trois éléments |
| `{ "variantes": { "$elemMatch": { "couleur": "noir", "taille": "L" } } }` | un même élément vérifie les deux conditions |
| `{ "prix": { "$type": "string" } }` | le champ est du texte |
| `{ "stock": { "$exists": false } }` | le champ est absent |
| `{ "stock": { "$type": "null" } }` | le champ existe et vaut `null` |

Une projection inclut les champs à `1` ou exclut ceux à `0`. Elle ne
mélange pas les deux modes, sauf pour exclure `_id` dans une inclusion.
Le tri utilise `1` pour croissant et `-1` pour décroissant.

Pièges à vérifier :

- Une clé répétée écrase sa valeur précédente ; grouper les bornes d'un champ dans le même objet.
- `{ "stock": null }` trouve le champ nul **ou absent** ; `$ne: 0` peut aussi trouver un champ absent.
- L'égalité avec un sous-document compare le sous-document entier, ordre des champs compris.
- Une date BSON se compare à une date BSON : `ISODate(...)` dans mongosh, pas une simple chaîne.

## Modifier sans écraser

```js
db.produits.updateOne(
  { _id: "M-700" },
  { $set: { prix: 39 }, $addToSet: { tags: "promo" } }
)
db.produits.updateMany(filtre, modification)
db.produits.insertOne(document)
db.produits.deleteOne(filtre)
```

| Opérateur | Effet |
| --- | --- |
| `$set`, `$unset`, `$rename` | fixer une valeur, supprimer un champ, le renommer |
| `$inc` | ajouter un nombre sur le serveur |
| `$push`, `$addToSet`, `$pull` | ajouter, ajouter si absent, retirer du tableau |
| `"variantes.$.stock"` | modifier l'élément associé au filtre |
| `"variantes.$[].stock"` | modifier tous les éléments |

Une modification peut être un pipeline :
`[ { $set: { poidsGrammes: { $toInt: "$poidsGrammes" } } } ]`.
Le préfixe `$` de `"$poidsGrammes"` désigne la valeur du champ du document.

`matchedCount` compte les documents trouvés ; `modifiedCount` ceux qui
ont changé. Une répétition peut trouver un document sans rien modifier.
`replaceOne` remplace le document entier, sauf `_id`.

Une écriture sur **un document** est atomique. Pour éviter une rupture
incohérente, mettre la condition de stock dans le filtre de l'écriture,
puis vérifier le résultat. Une transaction peut garantir ensemble la
modification du stock et la création d'un autre document de commande.

## Construire un pipeline

```js
db.commandes.aggregate([
  { $match: { "adresse.ville": "Ajaccio" } },
  { $unwind: "$lignes" },
  { $group: {
    _id: "$lignes.produit",
    articles: { $sum: "$lignes.quantite" }
  } },
  { $sort: { articles: -1, _id: 1 } }
])
```

| Étape ou expression | Rôle |
| --- | --- |
| `$match` | filtrer les documents qui arrivent à cette étape |
| `$unwind: "$tableau"` | produire un document par élément |
| `$group` | regrouper ; `_id` est la clé du groupe |
| `$sum: 1`, `$sum: "$champ"`, `$avg` | compter, additionner, faire une moyenne |
| `{ "$multiply": ["$prix", "$quantite"] }` | multiplier deux valeurs |
| `$project`, `$set` | projeter ou ajouter des champs calculés |
| `$sort`, `$limit`, `$count` | trier, limiter, compter |
| `{ "$type": "$prix" }` | obtenir le type d'une valeur dans une expression |
| `$lookup` | relier les documents à une autre collection |

L'ordre change le sens : `$match` avant `$group` filtre les documents,
après `$group` filtre les groupes. `$sort` avant `$limit` garde les
premiers selon le tri. Mettre `$limit` avant choisit d'abord un sous-ensemble.

## Mesurer les lectures

```js
db.produits.createIndex({ categorie: 1, nom: 1 }, { name: "categorie_nom" })
db.produits.find(filtre).sort(tri).explain("executionStats")
db.produits.getIndexes()
```

| Indicateur | Ce qu'il mesure |
| --- | --- |
| `nReturned` | documents renvoyés |
| `totalDocsExamined` | documents lus |
| `totalKeysExamined` | entrées d'index lues |
| `COLLSCAN`, `IXSCAN`, `FETCH`, `SORT` | lecture complète, index, accès aux documents, tri |

Les étapes peuvent être imbriquées dans le plan. Comparer la **même
requête** avant et après. Un index composé sert ses préfixes. ESR :
égalité, puis tri, puis intervalle, selon les accès à confirmer par
`explain`. Chaque index occupe de l'espace et ajoute du travail aux écritures.

## Chercher avec Elasticsearch

| Type du mapping | Usage |
| --- | --- |
| `text` | texte analysé pour retrouver des mots |
| `keyword` | valeur exacte pour filtre, tri ou facette |
| `integer` | nombre entier, notamment pour une borne de prix |

| Clause | Rôle |
| --- | --- |
| `match` | analyser le texte recherché et contribuer au score |
| `term` | rechercher un terme exact, adapté ici à `keyword` |
| `range` | poser une borne avec `gt`, `gte`, `lt`, `lte` |
| `bool.must` | exiger une clause qui contribue au score |
| `bool.filter` | exiger des critères sans contribuer au score |
| `aggs` avec `terms` | compter des documents par valeur, par exemple une catégorie |

Exemple générique de forme longue :

```json
{
  "query": {
    "match": {
      "nom": {
        "query": "lampe bureau",
        "operator": "and"
      }
    }
  }
}
```

Par défaut, `match` combine les termes avec OU ; `operator: "and"`
exige tous les termes. `fuzziness: "AUTO"` active une tolérance aux
fautes. Elle n'est pas implicite.
[Référence : match](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-match-query).

`POST /catalogue/_analyze` avec
`{ "field": "nom", "text": "Lampe Bureau" }` montre les termes analysés.

Une recherche affiche une copie du catalogue. Le rafraîchissement
Elasticsearch rend visibles les changements déjà indexés ; la
synchronisation transmet les changements depuis MongoDB. Le stock réel
se vérifie dans l'écriture métier sur MongoDB.
[Référence : refresh](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/refresh-parameter).

## Choisir les copies

| Besoin | Choix à discuter |
| --- | --- |
| quelques variantes lues avec la fiche | imbrication bornée |
| avis nombreux et croissants | collection séparée, référence au produit |
| conserver le prix payé | copie figée dans la commande |
| afficher un nom de marque copié | propager ses changements si nécessaire |

BSON est typé ; un document MongoDB fait au plus 16 Mio. Un schéma souple
laisse l'application responsable de ses attentes ; un validateur peut
les rendre explicites côté base.
