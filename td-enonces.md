# TD - Bases orientées documents

**UE 1 - Persistance et systèmes distribués · Chapitre 2**
Marcu-Andria Battesti · Bachelor CLIC · 2026-2027

Chaque étape se termine par un paragraphe **Résultat attendu** : c'est ce
que vous présentez à la correction. Notez vos réponses dans un fichier
`reponses.md`, avec le numéro du TD et de l'étape, et gardez-y les requêtes
que vous écrivez. Les bonus sont regroupés en fin de fiche. Ils sont
facultatifs, et la suite n'en dépend pas.

> **★** : les étapes dont la réponse doit tenir en une phrase juste ou
> une mesure propre.

Le [cours Google Slides](https://docs.google.com/presentation/d/1pXYPldXk5FG3wOKq7AKBOIYKKKiDrf_AXJA9DDLEUBE/edit)
a donné la syntaxe et les règles sur sept produits. Ici, vous les appliquez
à une boutique de 20 000 produits, et vous mesurez ce que le cours a
annoncé sans le chiffrer.

## Avant la séance : préparer Docker

Installez [Docker Desktop](https://www.docker.com/products/docker-desktop/)
et lancez-le.

```bash
cd manip
docker compose build
docker compose pull --ignore-buildable    # télécharge MongoDB
```

## Le décor : quatre machines

| Machine | Rôle |
| --- | --- |
| `mongo-a` | MongoDB 7. Au départ, c'est le primaire : il reçoit les écritures. |
| `mongo-b`, `mongo-c` | MongoDB 7. Deux copies de `mongo-a` : les secondaires. |
| `atelier` | Il forme le replica set, charge les données et porte trois scripts Python. |

Les trois machines MongoDB forment un replica set nommé `rs0` et se parlent
par un réseau nommé `ue1-boutique`. Jusqu'au TD 8, vous n'avez à penser
qu'à `mongo-a`.

## Deux bases

| Base | Contenu | Usage |
| --- | --- | --- |
| `cours` | les 7 produits, 4 commandes et 4 avis des diapositives | rejouer une diapositive, prévoir un résultat à la main |
| `boutique` | 20 000 produits, 20 000 clients, 50 000 commandes, plus de 100 000 avis | mesurer |

Les données sont générées avec une graine fixe : tous les postes ont
exactement les mêmes documents, donc les mêmes comptes. La base `boutique`
a vécu : elle contient des défauts, que vous allez trouver.

Pour remettre les données dans leur état initial, dans le terminal
**principal** :

```bash
docker compose exec atelier python charger.py cours      # instantané
docker compose exec atelier python charger.py boutique   # quelques secondes
```

## Vos terminaux

Tous vos terminaux s'ouvrent **dans le dossier `manip/`**. La fiche les
désigne par leur nom :

| Nom | Ce qui s'y tape | Pour l'ouvrir |
| --- | --- | --- |
| **principal** | les commandes `docker` | votre terminal habituel, dans `manip/`, hors de tout conteneur |
| **mongosh** | les requêtes | `docker compose exec mongo-a mongosh boutique` |
| **atelier** | les scripts Python | `docker compose exec atelier bash` |

Sous Windows, utilisez PowerShell pour le terminal **principal**. Les
requêtes se tapent toujours dans **mongosh**, jamais directement dans
PowerShell.

Dans **mongosh**, `use cours` et `use boutique` changent de base ; l'invite
affiche la base courante. Chaque étape précise la base à utiliser. Une
requête peut s'écrire sur plusieurs lignes : mongosh attend la parenthèse
fermante. Pour quitter **mongosh** ou **atelier**, tapez `exit`.

---

# TD 0 - Démarrer la boutique

**Objectif : lancer les quatre machines et ouvrir un premier mongosh.**

## Étape 1 - Lancer *(6 min)*

Dans le terminal **principal** :

```bash
docker compose up -d --build
docker compose logs -f atelier
```

Attendez la ligne `Boutique prête.`, puis quittez l'affichage avec Ctrl+C.

```bash
docker compose ps
```

**Résultat attendu :** quatre lignes à l'état `Up`, et le nombre de
documents chargés dans chaque collection, lu dans le journal de l'atelier.

## Étape 2 - Un premier mongosh *(5 min)*

Ouvrez **mongosh** :

```bash
docker compose exec mongo-a mongosh boutique
```

Puis, dans **mongosh** :

```js
show collections
db.produits.countDocuments()
db.produits.findOne()
use cours
db.produits.find({ categorie: "livre" })
use boutique
```

**Résultat attendu :** les identifiants renvoyés par la requête sur
`cours`, comparés à ceux de la diapositive « find : le filtre est un
document », et la catégorie du premier produit de `boutique`.

## Étape 3 - Trois machines *(4 min)*

Dans **mongosh** :

```js
rs.status().members.forEach(m => print(m.name, m.stateStr))
```

**Résultat attendu :** l'état des trois membres, et votre réponse : d'après
la diapositive « Un replica set MongoDB », laquelle des trois machines
reçoit vos écritures ?

---

# TD 1 - Des tables au document

**Objectif : écrire un document à partir de lignes relationnelles, puis
constater ce qu'un schéma souple laisse passer.** Diapositives « En
relationnel : une fiche, cinq tables », « Ce que contient un document »
et « Schéma souple ne veut pas dire sans schéma ».

## Étape 1 - La fiche de la platine *(12 min)*

La boutique reçoit un nouveau produit. Voici ses lignes dans l'ancienne
base relationnelle :

| Table | Lignes pour A-700 |
| --- | --- |
| `produits` | A-700, Platine Sillon, audio, 189 €, stock 6 |
| `marques` | Sonar |
| `caracteristiques` | vitesses = 33;45 ; bluetooth = 5.2 ; poids_grammes = 4200 |
| `produit_tags` | vinyle ; bluetooth |
| `avis` | 41 avis, note moyenne 4,5 |

La table `caracteristiques` est une table attribut-valeur : une ligne par
caractéristique, toutes les valeurs stockées en texte.

Dans **mongosh**, base `cours`, regardez comment est rangé le casque, puis
écrivez le document de la platine et insérez-le :

```js
use cours
db.produits.findOne({ _id: "A-400" })
db.produits.insertOne({ _id: "A-700", /* à vous */ })
```

Contrôlez ensuite les types que vous avez choisis. Toujours dans
**mongosh**, base `cours`, cette requête doit renvoyer 1 :

```js
db.produits.countDocuments({
  _id: "A-700",
  prix: { $type: "number" },
  "caracteristiques.poidsGrammes": { $type: "number" },
  tags: { $type: "array" }
})
```

Si elle renvoie 0, supprimez votre document avec
`db.produits.deleteOne({ _id: "A-700" })` et recommencez.

**Résultat attendu :** votre document, et pour chacune des cinq tables ce
qu'elle est devenue : champ simple, sous-document, tableau, ou rien.
Comment avez-vous rangé les deux vitesses ?

## Étape 2 - Le même identifiant, deux fois *(3 min)*

Dans **mongosh**, base `cours`, relancez exactement le même `insertOne`.

**Résultat attendu :** le message d'erreur, et le nom de l'index qui a
refusé l'insertion.

## Étape 3 - Des produits qui ne se ressemblent pas *(8 min)*

Dans **mongosh**, passez sur `boutique` et affichez un produit de chacune
des cinq catégories `vetement`, `livre`, `audio`, `epicerie` et `maison` :

```js
use boutique
db.produits.findOne({ categorie: "vetement" })
```

Puis lancez ce pipeline, qui liste les noms de champs rencontrés dans
chaque catégorie :

```js
db.produits.aggregate([
  { $project: { categorie: 1, champs: { $objectToArray: "$$ROOT" } } },
  { $unwind: "$champs" },
  { $group: { _id: "$categorie", champs: { $addToSet: "$champs.k" } } }
])
```

**Résultat attendu :** les champs propres à chaque catégorie, ceux que
toutes partagent, et la ligne que vous n'attendiez pas.

## Étape 4 - Le schéma implicite a des trous ★ *(12 min)*

Le catalogue a été alimenté pendant trois ans par plusieurs programmes et
par des fichiers de fournisseurs. Dans **mongosh**, base `boutique`,
répondez par des requêtes :

1. Combien de produits n'ont pas de champ `categorie` ? Quel champ
   portent-ils à la place ?
2. Quels sont les types du champ `prix` dans la collection ? Ce pipeline
   les compte :

   ```js
   db.produits.aggregate([{ $group: { _id: { $type: "$prix" }, n: { $sum: 1 } } }])
   ```

3. Combien de produits le filtre `{ prix: { $gt: 0 } }` renvoie-t-il ?
   Comparez au nombre de produits du catalogue.

Ne corrigez rien : le TD 4 s'en charge.

**Résultat attendu :** les trois nombres, puis trois phrases. Que voit un
client qui ouvre la page d'une catégorie ? Que voit celui qui filtre par
prix ? La base a-t-elle signalé une erreur au moment où ces documents ont
été écrits ?

---

# TD 2 - Lire

**Objectif : écrire des filtres, des projections et des tris, et repérer
deux pièges silencieux.** Diapositives « Combiner des conditions », « La
notation pointée », « Projeter, trier, limiter » et « La même question en
SQL et avec find ».

Dans le terminal **principal**, remettez d'abord le jeu du cours à zéro :

```bash
docker compose exec atelier python charger.py cours
```

## Étape 1 - Prévoir, puis vérifier *(8 min)*

Dans **mongosh**, base `cours` (`use cours`). Pour chaque filtre, écrivez
d'abord sur papier les identifiants que vous attendez, à l'aide des
diapositives « Le jeu d'exemple : sept produits » et « Leurs champs
propres, étiquettes et notes ». Exécutez seulement ensuite
`db.produits.find(filtre)`.

| | Filtre |
| --- | --- |
| a | `{ categorie: "audio", stock: { $gt: 0 } }` |
| b | `{ $or: [ { prix: { $lt: 10 } }, { "note.moyenne": { $gte: 4.8 } } ] }` |
| c | `{ prix: { $gte: 20 }, prix: { $lte: 50 } }` |
| d | `{ note: { nb: 21, moyenne: 4.6 } }` |
| e | `{ categorie: { $nin: ["vetement", "livre"] }, prix: { $lte: 79 } }` |

Passez ensuite sur `boutique` (`use boutique`) et comptez les produits
renvoyés par le filtre c, puis par sa version correcte :

```js
db.produits.countDocuments({ prix: { $gte: 20 }, prix: { $lte: 50 } })
```

**Résultat attendu :** pour chaque filtre, votre prévision et le résultat
obtenu. Pour c et d, l'explication de l'écart et le filtre corrigé. Les
deux comptes relevés sur `boutique`.

## Étape 2 - Trois demandes du service client *(12 min)*

Dans **mongosh**, base `boutique`. Écrivez une requête par demande.

1. Combien de produits appartiennent aux catégories audio ou épicerie ?
2. Les cinq produits en stock les moins chers : le nom et le prix, sans
   `_id`, du moins cher au plus cher et, à prix égal, dans l'ordre des
   `_id`.
3. Le nom et l'autonomie des produits audio de la marque Sonar vendus plus
   de 380 €, sans `_id`.

**Résultat attendu :** les trois requêtes, le nombre obtenu à la première,
les cinq produits de la deuxième, le nombre de produits de la troisième.
Que constatez-vous sur certains produits de la troisième, et la requête
a-t-elle échoué pour autant ?

## Étape 3 - Dans les sous-documents *(8 min)*

Dans **mongosh**, base `boutique`.

1. Combien de produits ont une note moyenne d'au moins 4 sur au moins
   100 avis ?
2. Combien de commandes livrées l'ont été à Ajaccio ? Le statut vaut
   `"livree"`, la ville est dans le sous-document `adresse`.
3. Le produit le plus commenté du catalogue a pour note
   `{ moyenne: 3.9, nb: 9538 }`. Retrouvez-le de deux façons : par égalité
   avec le sous-document entier, puis avec la notation pointée. Essayez
   ensuite `{ note: { nb: 9538, moyenne: 3.9 } }`.

**Résultat attendu :** les deux nombres, le nom du produit, et ce que
renvoie le dernier filtre. Laquelle des deux écritures utiliseriez-vous
dans un programme, et pourquoi ?

## Étape 4 - Compter et lister *(5 min)*

Dans **mongosh**, base `boutique`. Avec `distinct` :

1. la liste des catégories de produits ;
2. le nombre de villes de livraison différentes dans les commandes ;
3. la liste des statuts de commande.

**Résultat attendu :** les trois réponses. Les 15 produits sans champ
`categorie` du TD 1 apparaissent-ils dans la première liste ?

## Étape 5 - Des dates *(5 min)*

Diapositive « Comparer des dates ». Dans **mongosh**, base `boutique`.
Les dates des commandes sont dans le champ `date`.

1. Combien de commandes ont été passées en juillet 2026 ?
2. Combien le 14 juillet 2026 ?
3. Refaites la première requête en écrivant les deux bornes comme des
   chaînes : `"2026-07-01"` et `"2026-08-01"`.

**Résultat attendu :** les trois nombres, et la raison du troisième.

## Étape 6 - Du SQL à find ★ *(7 min)*

Traduisez cette requête pour la collection `produits` de `boutique` :

```sql
SELECT nom, prix
FROM produits
WHERE categorie = 'maison' AND prix BETWEEN 20 AND 30 AND stock > 0
ORDER BY prix DESC, nom
LIMIT 3;
```

**Résultat attendu :** votre requête, les trois produits obtenus, et le
nombre de produits qui vérifient la clause `WHERE`.

---

# TD 3 - Tableaux et champs absents

**Objectif : interroger des tableaux sans se tromper d'élément, et
distinguer un champ absent d'un champ nul.** Diapositives « Chercher dans
un tableau », « $elemMatch : les conditions sur un même élément » et
« Absent ou null ? ».

## Étape 1 - Chercher dans un tableau *(8 min)*

Dans **mongosh**, base `boutique`. Comptez :

1. les produits qui portent l'étiquette `bio` ;
2. ceux qui portent à la fois `bio` et `équitable` ;
3. ceux que renvoie le filtre `{ tags: ["bio", "équitable"] }` ;
4. les livres écrits par exactement trois auteurs ;
5. les vêtements dont au moins une variante est noire.

**Résultat attendu :** les cinq nombres, et la raison de l'écart entre le
deuxième et le troisième.

## Étape 2 - Deux conditions sur un tableau ★ *(12 min)*

Le site veut afficher les vêtements **disponibles en taille M**.

Dans **mongosh**, base `cours` (`use cours`), exécutez les deux requêtes
de la diapositive « $elemMatch : les conditions sur un même élément » et
vérifiez ses deux résultats :

```js
db.produits.find({ "variantes.taille": "M", "variantes.stock": { $gt: 0 } })
db.produits.find({ variantes: { $elemMatch: { taille: "M", stock: { $gt: 0 } } } })
```

Revenez sur `boutique` (`use boutique`) et comptez les produits renvoyés
par chacune des deux écritures. Trouvez ensuite, dans `boutique`, un
produit renvoyé par la première et pas par la seconde, et affichez son nom
et ses variantes. Cette projection aide à parcourir les résultats :

```js
db.produits.find({ "variantes.taille": "M", "variantes.stock": { $gt: 0 } },
                 { nom: 1, variantes: 1 })
```

**Résultat attendu :** les deux comptes, leur différence, le produit trouvé
avec ses variantes, et une phrase : que se passe-t-il pour le client qui
clique sur ce produit ?

## Étape 3 - Absent ou null *(12 min)*

Dans **mongosh**, base `boutique`. Complétez, avec `countDocuments` :

| Filtre | Produits |
| --- | --- |
| `{ stock: null }` | |
| `{ stock: { $exists: false } }` | |
| `{ stock: { $type: "null" } }` | |
| `{ stock: 0 }` | |
| `{ stock: { $gt: 0 } }` | |
| `{ stock: { $ne: 0 } }` | |

Affichez un produit sans champ `stock`, puis un produit dont le stock vaut
`null`.

**Résultat attendu :** le tableau, et quatre réponses. Quels produits n'ont
pas de champ `stock` ? Lesquels ont un stock nul, au sens de `null` ?
Retrouve-t-on les 20 000 produits en additionnant quatre lignes du
tableau, et lesquelles ? Le site affiche le bandeau « En stock » avec le
filtre `{ stock: { $ne: 0 } }` : combien de produits le portent à tort ?

## Étape 4 - Trier quand le champ manque *(8 min)*

Dans **mongosh**, base `boutique`. La page « Maison » propose un tri par
note.

1. Affichez le nom et la note des trois premiers produits de la catégorie
   `maison`, triés par `note.moyenne` croissante puis par `_id`.
2. Combien de produits `maison` n'ont pas de note ?
3. Écrivez la requête des trois produits `maison` les moins bien notés
   parmi ceux qui ont au moins 20 avis, avec le même tri.

**Résultat attendu :** les trois produits de la première requête, le
nombre, votre requête et ses trois produits. Où le tri range-t-il les
documents qui n'ont pas le champ ?

---

# TD 4 - Écrire sans survendre

**Objectif : modifier des documents avec des opérateurs, réparer le
catalogue, puis vendre dix casques à cinquante acheteurs.** Diapositives
« Modifier : un filtre, puis des opérateurs », « Modifier un élément de
tableau », « Le dernier casque, vendu deux fois », « Tester et décrémenter
en une opération » et « Un avis par client : l'index unique ».

Dans le terminal **principal**, remettez le jeu du cours à zéro :

```bash
docker compose exec atelier python charger.py cours
```

## Étape 1 - Modifier sans écraser *(10 min)*

Dans **mongosh**, base `cours` (`use cours`). Exécutez dans l'ordre, et notez ce que répond chaque
commande :

| Ordre | Commande |
| --- | --- |
| 1 | `db.produits.updateOne({ _id: "T-100" }, { $set: { prix: 27 } })` |
| 2 | la même, une seconde fois |
| 3 | `db.produits.updateOne({ _id: "T-100" }, { nom: "T-shirt" })` |
| 4 | `db.produits.replaceOne({ _id: "T-200" }, { nom: "Sweat" })` |
| 5 | `db.produits.findOne({ _id: "T-200" })` |
| 6 | `db.produits.updateOne({ _id: "T-100" }, { $addToSet: { tags: "bio" } })` |

**Résultat attendu :** `matchedCount` et `modifiedCount` de chaque
écriture, le message de l'ordre 3, ce qu'il reste du Sweat à l'ordre 5, et
la raison du `modifiedCount` obtenu aux ordres 2 et 6.

## Étape 2 - Un élément de tableau *(8 min)*

Dans **mongosh**, base `cours`. Un client achète un T-shirt T-100 en
taille L.

1. Écrivez **un seul** `updateOne` qui retire 1 au stock de la variante L
   et 1 au stock total.
2. Un réassort arrive : écrivez un seul `updateOne` qui ajoute 10 au stock
   de chaque variante et 30 au stock total.

Contrôlez après chaque écriture :

```js
db.produits.findOne({ _id: "T-100" }, { variantes: 1, stock: 1 })
```

**Résultat attendu :** vos deux écritures, et les stocks après chacune.
Pourquoi le stock de la variante et le stock total ne peuvent-ils pas se
contredire, même si dix ventes arrivent en même temps ?

## Étape 3 - Réparer le catalogue *(8 min)*

Dans **mongosh**, base `boutique` (`use boutique`). Diapositive « Faire
évoluer des documents existants ». Corrigez les deux défauts trouvés au
TD 1 :

1. le champ `categori`, à renommer en `categorie` ;
2. les prix enregistrés en texte, à convertir en entiers.

Contrôlez avec le pipeline des types du TD 1 :

```js
db.produits.aggregate([{ $group: { _id: { $type: "$prix" }, n: { $sum: 1 } } }])
```

Puis **relancez vos deux corrections une seconde fois**.

**Résultat attendu :** vos deux écritures et leur `modifiedCount`, le
nombre de produits que renvoie maintenant `{ prix: { $gt: 0 } }`, et ce
que répondent les deux corrections à la seconde exécution. Pourquoi est-ce
rassurant ?

## Étape 4 - Le dernier casque, à deux *(10 min)*

Ouvrez deux terminaux côte à côte sur votre machine, dans `manip/`, et
lancez dans chacun la même commande : l'un sera **Alice**, l'autre
**Karim**.

```bash
docker compose exec mongo-a mongosh cours
```

Il reste un seul casque A-400. Tapez les quatre commandes **dans cet
ordre**, en changeant de terminal à chaque ligne :

| Ordre | Terminal | Commande |
| --- | --- | --- |
| 1 | Alice | `db.produits.findOne({ _id: "A-400" }).stock` |
| 2 | Karim | `db.produits.findOne({ _id: "A-400" }).stock` |
| 3 | Alice | `db.produits.updateOne({ _id: "A-400" }, { $set: { stock: 0 } })` |
| 4 | Karim | `db.produits.updateOne({ _id: "A-400" }, { $set: { stock: 0 } })` |

Chacun a lu « 1 » avant d'écrire : le site envoie une confirmation à
chacun.

Remettez le stock à 1, dans **Alice** :

```js
db.produits.updateOne({ _id: "A-400" }, { $set: { stock: 1 } })
```

Écrivez maintenant l'`updateOne` qui retire un casque **seulement s'il en
reste**, et exécutez-le dans **Alice**, puis dans **Karim**.

**Résultat attendu :** ce qu'affiche chaque commande de la première
séquence et le nombre de casques vendus, votre `updateOne`, ce qu'il
répond à Alice puis à Karim, et une phrase : comment le programme de Karim
sait-il qu'il doit afficher « rupture de stock » ?

## Étape 5 - La vente flash ★ *(10 min)*

Cinquante acheteurs veulent, au même instant, l'un des dix casques d'une
vente flash. Ouvrez **atelier** :

```bash
docker compose exec atelier bash
```

Puis, dans **atelier**, lancez les trois modes :

```bash
python vente_flash.py naif
python vente_flash.py inc
python vente_flash.py conditionnel
```

Lisez ensuite les trois fonctions `acheter_...` du script, dans
`manip/atelier/vente_flash.py`.

| Mode | Commandes confirmées | Stock final |
| --- | --- | --- |
| `naif` | | |
| `inc` | | |
| `conditionnel` | | |

Relancez le troisième mode avec deux cents acheteurs :

```bash
python vente_flash.py conditionnel --acheteurs 200
```

**Résultat attendu :** le tableau, puis pour chacun des deux premiers
modes le calcul qui explique le stock final. Pourquoi le troisième ne
survend-il jamais, quel que soit le nombre d'acheteurs ? Aucune des trois
fonctions n'ouvre de transaction : qu'est-ce qui garantit le résultat ?

## Étape 6 - Un avis par client *(14 min)*

Dans **mongosh**, base `boutique`. La règle : un client ne note un produit
qu'une fois.

1. Posez l'index unique de la diapositive « Un avis par client : l'index
   unique » sur la collection `avis` :

   ```js
   db.avis.createIndex({ produit: 1, client: 1 }, { unique: true })
   ```
2. Cherchez les couples produit-client présents plusieurs fois :

   ```js
   const doublons = db.avis.aggregate([
     { $group: { _id: { produit: "$produit", client: "$client" },
                 n: { $sum: 1 }, ids: { $push: "$_id" } } },
     { $match: { n: { $gt: 1 } } }
   ]).toArray()
   doublons.length
   doublons[0]
   ```

3. Supprimez le second avis de chaque couple :

   ```js
   doublons.forEach(d => db.avis.deleteOne({ _id: d.ids[1] }))
   ```

4. Posez de nouveau l'index, avec la même commande, puis tentez d'insérer
   un second avis du client `U-07615` sur le produit `E-10701` :

   ```js
   db.avis.insertOne({ produit: "E-10701", client: "U-07615", note: 1, texte: "Déçu" })
   ```

**Résultat attendu :** le message obtenu à la première tentative, le
nombre de couples en double, le nombre d'avis restants, le message de la
dernière insertion. Pourquoi la base a-t-elle refusé de créer l'index, et
qu'est-ce que ces doublons disent du programme qui enregistrait les avis ?

---

# TD 5 - Agréger

**Objectif : répondre aux questions du marketing avec un pipeline, et
constater que l'ordre des étapes change le résultat.** Diapositives « Le
pipeline d'agrégation », « $group : regrouper et calculer », « $unwind :
un document par élément », « L'ordre des étapes compte » et « $lookup :
une jointure quand il le faut ».

Pour que tous les postes repartent du même état, **rechargez la boutique**
dans le terminal **principal**. Les réparations du matin disparaissent :
c'est voulu.

```bash
docker compose exec atelier python charger.py boutique
```

Tout le TD se passe dans **mongosh**, base `boutique`.

## Étape 1 - Les questions du marketing *(12 min)*

1. Par catégorie : le nombre de produits et le prix moyen, de la catégorie
   la plus fournie à la moins fournie.
2. Par ville : le chiffre d'affaires et le nombre de commandes **livrées**,
   pour les cinq villes au plus fort chiffre d'affaires. Le montant d'une
   commande est dans `total`.

**Résultat attendu :** vos deux pipelines et leurs résultats. Dans le
premier, d'où vient la ligne dont le `_id` vaut `null` ? Les 40 produits
dont le prix est enregistré en texte comptent-ils dans le nombre de
produits ? Et dans le prix moyen ?

## Étape 2 - Les trois produits les plus vendus ★ *(14 min)*

Écrivez le pipeline qui donne les trois produits les plus vendus **en
quantité**, parmi les commandes **expédiées ou livrées**, avec leur nom.
À quantité égale, classez par identifiant de produit. Les statuts sont
`"preparation"`, `"expediee"`, `"livree"` et `"annulee"`.

Faites ensuite deux essais, en ne changeant qu'une chose à la fois :

- retirez le filtre sur le statut ;
- remettez-le, et remplacez la somme des quantités par `{ $sum: 1 }`.

Enfin, comptez les documents qui sortent de votre étape `$unwind`, en
plaçant `{ $count: "n" }` juste après elle.

**Résultat attendu :** votre pipeline, les trois produits et leur
quantité ; les quantités obtenues dans chacun des deux essais, avec ce que
chaque nombre compte réellement ; le nombre de documents après `$unwind`,
pour 50 000 commandes.

## Étape 3 - L'ordre des étapes *(8 min)*

Exécutez ces deux pipelines :

```js
db.commandes.aggregate([
  { $sort: { total: -1, _id: 1 } }, { $limit: 3 }, { $project: { total: 1 } }
])
db.commandes.aggregate([
  { $limit: 3 }, { $sort: { total: -1, _id: 1 } }, { $project: { total: 1 } }
])
```

Reprenez ensuite votre pipeline par ville de l'étape 1 et ne gardez que
les villes dont le chiffre d'affaires livré dépasse 500 000 €.

**Résultat attendu :** les deux résultats et ce que calcule chacun ; votre
pipeline et les villes obtenues. Où avez-vous placé le second `$match`, et
à quel mot-clé SQL correspond-il ?

## Étape 4 - Par mois *(6 min)*

Diapositive « Comparer des dates ». Pour chaque mois de 2026 : le nombre
de commandes **non annulées** et leur chiffre d'affaires, dans l'ordre des
mois.

**Résultat attendu :** votre pipeline, le mois le plus fort et son chiffre
d'affaires.

## Étape 5 - Une jointure pour la modération *(10 min)*

L'équipe de modération relit les avis à une étoile déposés depuis le
25 septembre 2026. Elle veut, pour chacun, la note, le client, la date et
le **nom du produit**, du plus récent au plus ancien.

**Résultat attendu :** votre pipeline, le nombre d'avis et les deux
premiers. Combien de recherches dans `produits` votre pipeline
déclenche-t-il ? Combien en déclencherait-il si le filtre était placé
après la jointure ?

---

# TD 6 - Indexer

**Objectif : lire un plan d'exécution, créer les index qui servent, et
mesurer ce qu'ils coûtent.** Diapositives « Sans index, la base lit
tout », « Lire un plan d'exécution », « Index composé : l'ordre des
champs », « Égalité, tri, intervalle », « Une requête couverte : l'index
suffit » et « Le prix d'un index ».

Tout le TD se passe dans **mongosh**, base `boutique`. Collez-y d'abord
cette fonction : elle résume un plan en une ligne.

```js
function resume(curseur) {
  const e = curseur.explain("executionStats"), s = e.executionStats
  const etapes = []
  let p = e.queryPlanner.winningPlan
  for (p = p.queryPlan || p; p; p = p.inputStage)
    etapes.push(p.indexName ? `${p.stage}(${p.indexName})` : p.stage)
  return { plan: etapes.join(" <- "), renvoyes: s.nReturned,
           cles: s.totalKeysExamined, documents: s.totalDocsExamined }
}
```

Si vous fermez **mongosh**, il faudra la coller de nouveau.

## Étape 1 - Sans index *(8 min)*

Alice Martin, `U-00017`, est la meilleure cliente de la boutique. Sa page
« Mes commandes » lance :

```js
db.commandes.find({ "client.id": "U-00017" }).explain("executionStats")
```

Retrouvez dans la réponse les champs de la diapositive « Lire un plan
d'exécution ». Comparez avec :

```js
resume(db.commandes.find({ "client.id": "U-00017" }))
```

**Résultat attendu :** l'étape du plan, le nombre de documents renvoyés,
le nombre de documents lus, le nombre d'entrées d'index lues. Combien de
documents la base lit-elle pour chaque commande affichée ?

## Étape 2 - Créer un index *(6 min)*

Créez l'index qui sert cette requête, puis relancez `resume`.

```js
db.commandes.getIndexes()
```

**Résultat attendu :** votre `createIndex`, le nouveau plan et ses trois
compteurs.

## Étape 3 - Mes commandes, page 1 *(8 min)*

La page affiche les dix commandes les plus récentes :

```js
resume(db.commandes.find({ "client.id": "U-00017" }).sort({ date: -1 }).limit(10))
```

1. Relevez le plan. Que fait l'étape `SORT` ?
2. Créez l'index qui la fait disparaître, et relevez le nouveau plan.
3. Ajoutez `.skip(290)` avant `.limit(10)` pour afficher la page 30.

**Résultat attendu :** les trois plans et leurs compteurs, votre index, et
une phrase : que coûte un `skip`, même avec le bon index ?

## Étape 4 - Trois index pour une requête ★ *(14 min)*

La page de la catégorie « Vêtements » lance :

```js
db.produits.find({ categorie: "vetement", stock: { $gt: 0 } }).sort({ prix: 1 })
```

Créez trois index, que l'on nomme pour les reconnaître :

```js
db.produits.createIndex({ categorie: 1, stock: 1, prix: 1 }, { name: "A" })
db.produits.createIndex({ prix: 1, categorie: 1, stock: 1 }, { name: "B" })
db.produits.createIndex({ categorie: 1, prix: 1, stock: 1 }, { name: "C" })
```

`hint` impose un index. Pour chacun des trois :

```js
resume(db.produits.find({ categorie: "vetement", stock: { $gt: 0 } }).sort({ prix: 1 }).hint("A"))
```

La page n'affiche que vingt produits. Recommencez, pour chacun des trois
index, avec une limite :

```js
resume(db.produits.find({ categorie: "vetement", stock: { $gt: 0 } }).sort({ prix: 1 }).limit(20).hint("A"))
```

Enfin, laissez la base choisir :

```js
resume(db.produits.find({ categorie: "vetement", stock: { $gt: 0 } }).sort({ prix: 1 }))
```

| Index | Plan | Clés lues | Documents lus | Clés lues avec `limit(20)` |
| --- | --- | --- | --- | --- |
| A | | | | |
| B | | | | |
| C | | | | |

**Résultat attendu :** le tableau, l'index choisi par la base quand on la
laisse faire, et trois phrases : ce qui pénalise A, ce qui pénalise B, et
la règle de la diapositive « Égalité, tri, intervalle » que vos mesures
confirment.

## Étape 5 - L'index suffit *(6 min)*

Avec l'index C, comparez :

```js
resume(db.produits.find({ categorie: "livre", prix: { $lt: 15 } },
                        { _id: 0, categorie: 1, prix: 1 }).hint("C"))
resume(db.produits.find({ categorie: "livre", prix: { $lt: 15 } },
                        { _id: 0, nom: 1, prix: 1 }).hint("C"))
```

**Résultat attendu :** les deux plans et leurs compteurs. Qu'est-ce qui
oblige la seconde requête à lire les documents ?

## Étape 6 - Le prix d'un index *(8 min)*

Collez ce script : il insère 50 000 documents dans une collection sans
index, puis dans une collection qui en porte cinq.

```js
use essais
const docs = []
for (let i = 0; i < 50000; i++)
  docs.push({ _id: i, a: i * 7919 % 50000, b: "x" + (i * 31 % 1000),
              c: i % 97, d: new Date(1e12 + i * 1000), e: i * 13 % 5000 })
function inserer(nom, index) {
  db[nom].drop()
  index.forEach(cles => db[nom].createIndex(cles))
  const debut = Date.now()
  db[nom].insertMany(docs)
  return Date.now() - debut
}
inserer("sans", [])
inserer("avec", [{ a: 1 }, { b: 1 }, { c: 1 }, { d: 1 }, { e: 1, a: 1 }])
```

Lancez chaque mesure deux ou trois fois, puis comparez la taille des
données à celle des index :

```js
db.avec.stats().size
db.avec.stats().indexSizes
db.dropDatabase()
use boutique
```

**Résultat attendu :** les deux durées, leur rapport, la taille des données
et la taille cumulée des index. Reliez ces mesures à la diapositive « Le
prix d'un index ».

---

# TD 7 - Modéliser

**Objectif : peser les conséquences d'un choix de modèle, puis rendre le
schéma explicite.** Diapositives « L'anti-patron : le tableau sans
limite », « Copier pour lire vite, ou pour figer », « Quelques patrons de
conception », « Imposer un schéma : $jsonSchema » et « Niveau et action de
validation ».

Tout le TD se passe dans **mongosh**, base `boutique`.

## Étape 1 - Tous les avis dans le produit ? *(12 min)*

Un collègue propose de ranger les avis dans le document de leur produit :
« une seule lecture pour toute la fiche ». Construisez cette collection
pour la peser :

```js
db.avis.createIndex({ produit: 1, date: -1 })
db.produits.aggregate([
  { $lookup: { from: "avis", localField: "_id", foreignField: "produit", as: "avis" } },
  { $out: "produits_avec_avis" }
])
```

`$bsonSize` donne la taille d'un document en octets :

```js
db.produits_avec_avis.aggregate([
  { $project: { nom: 1, avis: { $size: "$avis" }, octets: { $bsonSize: "$$ROOT" } } },
  { $sort: { octets: -1 } },
  { $limit: 3 }
])
```

Mesurez de la même façon, dans `produits`, la taille du document du
produit arrivé en tête :

```js
db.produits.aggregate([
  { $match: { _id: "A-12987" } },
  { $project: { nom: 1, octets: { $bsonSize: "$$ROOT" } } }
])
```

Supprimez enfin la collection d'essai :

```js
db.produits_avec_avis.drop()
```

**Résultat attendu :** les trois plus gros documents, avec leur nombre
d'avis et leur taille ; la taille de la même fiche dans `produits` et le
rapport entre les deux. Combien d'octets pèse un avis en moyenne dans ce
document ? À combien d'avis ce produit atteindrait-il la limite de 16 Mo ?
Que transfère la base chaque fois que cette fiche est affichée ?

## Étape 2 - Les trois derniers avis *(8 min)*

Le patron « sous-ensemble » garde dans le produit les trois derniers avis
seulement. Exécutez **cinq fois** cette écriture, comme si cinq avis
arrivaient (flèche du haut, puis Entrée) :

```js
db.produits.updateOne(
  { _id: "A-12987" },
  { $push: { derniersAvis: { $each: [ { client: "U-00017", note: 5, date: new Date() } ],
                             $sort: { date: -1 }, $slice: 3 } },
    $inc: { "note.nb": 1 } })
```

Puis regardez le résultat :

```js
db.produits.findOne({ _id: "A-12987" }, { derniersAvis: 1, note: 1 })
```

**Résultat attendu :** la longueur de `derniersAvis` et la valeur de
`note.nb` après les cinq écritures. L'avis complet doit aussi être inséré
dans la collection `avis` : combien d'écritures cela fait-il par avis, sur
combien de documents ? Que se passe-t-il si le programme s'arrête entre
les deux, et quelle diapositive du cours y répond ?

## Étape 3 - Copier pour figer, copier pour lire *(8 min)*

1. La Radio Nomade, `A-10277`, coûte aujourd'hui 112 €. Relevez les prix
   auxquels elle a été payée :

   ```js
   db.commandes.aggregate([
     { $unwind: "$lignes" },
     { $match: { "lignes.produit": "A-10277" } },
     { $group: { _id: "$lignes.prix", lignes: { $sum: 1 } } },
     { $sort: { lignes: -1 } }
   ])
   ```

2. La marque Maille devient « Maille & Co ». Propagez le nouveau nom dans
   le catalogue avec un `updateMany`.

**Résultat attendu :** les prix payés et le nombre de lignes pour chacun ;
votre `updateMany` et son `modifiedCount`. Faut-il « corriger » les lignes
de commande qui n'affichent pas 112 € ? Pendant que l'`updateMany`
s'exécute, que voient les clients, et quel terme du chapitre 1 décrit cet
état ?

## Étape 4 - Modéliser la boutique ★ *(7 min)*

Sans machine. Pour chaque relation : imbriquer, référencer ou copier ?

| Relation | Volumes et usages |
| --- | --- |
| Produit et variantes | 2 à 20 par produit ; affichées sur la fiche, chacune avec son stock |
| Produit et avis | jusqu'à des milliers ; la fiche montre la note et les 3 derniers |
| Commande et produits achetés | le prix payé ne doit plus jamais changer |
| Client et commandes | s'accumulent d'année en année ; page « Mes commandes », 10 par page |

**Résultat attendu :** votre choix pour chaque relation, justifié par un
accès (« la fiche affiche… », « la page Mes commandes liste… ») et, pour
deux d'entre elles au moins, par une mesure relevée aujourd'hui.

## Étape 5 - Imposer un schéma *(10 min)*

Voici le schéma de la diapositive « Imposer un schéma : $jsonSchema » :

```js
const schema = {
  bsonType: "object",
  required: ["produit", "note", "texte"],
  properties: {
    produit: { bsonType: "string" },
    note: { bsonType: "int", minimum: 1, maximum: 5 }
  }
}
```

1. Avant de l'imposer, comptez les avis qui ne le respectent pas, et
   regardez-en quelques-uns :

   ```js
   db.avis.countDocuments({ $nor: [ { $jsonSchema: schema } ] })
   db.avis.find({ $nor: [ { $jsonSchema: schema } ] }, { note: 1, texte: 1 })
   ```

2. Posez le validateur sur la collection existante :

   ```js
   db.runCommand({ collMod: "avis", validator: { $jsonSchema: schema } })
   ```

3. Tentez ces trois écritures :

   ```js
   db.avis.insertOne({ produit: "A-12987", client: "U-00017", note: 6 })
   db.avis.insertOne({ produit: "A-12987", client: "U-00017", note: 4.5, texte: "Bien" })
   db.avis.updateOne({ _id: "AV-002521" }, { $set: { texte: "Corrigé" } })
   ```

4. Passez en niveau `moderate`, puis rejouez la troisième écriture :

   ```js
   db.runCommand({ collMod: "avis", validationLevel: "moderate" })
   ```

**Résultat attendu :** le nombre d'avis invalides et les défauts que vous
avez repérés ; pour chacune des trois écritures, acceptée ou refusée, et
la règle violée ; ce qui change en niveau `moderate`. Comment
introduiriez-vous ce validateur sur un site en production sans bloquer
personne ?

---

# TD 8 - Distribuer

**Objectif : observer sur trois machines ce que changent writeConcern,
readPreference et readConcern, puis provoquer deux pannes.** Diapositives
« Un replica set MongoDB », « Une élection vue de l'application »,
« writeConcern : quand confirmer ? », « readPreference : où lire ? »,
« readConcern : quelle garantie ? » et « Des réglages par opération ».

Gardez **mongosh**, branché sur le primaire `mongo-a`, et ouvrez deux
terminaux de plus sur votre machine, dans `manip/` :

| Nom | Pour l'ouvrir |
| --- | --- |
| **B** | `docker compose exec mongo-b mongosh boutique` |
| **C** | `docker compose exec mongo-c mongosh boutique` |

Dans **B**, puis dans **C**, précisez que vous lisez sur un secondaire :

```js
db.getMongo().setReadPref("secondary")
```

## Étape 1 - L'état du replica set *(4 min)*

Dans **mongosh** :

```js
rs.status().members.forEach(m => print(m.name, m.stateStr, m.optimeDate.toISOString()))
```

**Résultat attendu :** le rôle de chaque membre, et votre lecture de la
troisième colonne : les trois machines en sont-elles au même point ?

## Étape 2 - Un secondaire en retard *(9 min)*

`db.fsyncLock()` fige les écritures d'une machine : un secondaire figé ne
rejoue plus le journal du primaire. C'est une façon de fabriquer une copie
en retard.

| Ordre | Terminal | Commande |
| --- | --- | --- |
| 1 | C | `db.fsyncLock()` |
| 2 | mongosh | `db.produits.updateOne({ _id: "A-12987" }, { $set: { prix: 999 } })` |
| 3 | mongosh, puis B, puis C | `db.produits.findOne({ _id: "A-12987" }).prix` |
| 4 | C | `db.fsyncUnlock()` |
| 5 | C | `db.produits.findOne({ _id: "A-12987" }).prix` |

**Résultat attendu :** les trois prix lus à l'ordre 3, celui de l'ordre 5,
et deux réponses. L'écriture de l'ordre 2 a été confirmée alors que C
était figé : par combien de machines ? Quelle diapositive du chapitre 1
décrivait la lecture faite sur C ?

## Étape 3 - Confirmer, mais par qui ? *(10 min)*

Figez maintenant **les deux** secondaires. Dans **B**, puis dans **C** :

```js
db.fsyncLock()
```

Puis, dans **mongosh**, dans cet ordre :

| Ordre | Commande |
| --- | --- |
| 1 | `db.produits.updateOne({ _id: "A-12987" }, { $set: { prix: 111 } }, { writeConcern: { w: "majority", wtimeout: 3000 } })` |
| 2 | `db.produits.find({ _id: "A-12987" }, { prix: 1 }).readConcern("local")` |
| 3 | `db.produits.find({ _id: "A-12987" }, { prix: 1 }).readConcern("majority")` |
| 4 | `db.produits.updateOne({ _id: "A-12987" }, { $set: { prix: 222 } }, { writeConcern: { w: 1 } })` |
| 5 | la lecture de l'ordre 2, de nouveau |
| 6 | la lecture de l'ordre 3, de nouveau |

**Libérez les deux secondaires.** Dans **B**, puis dans **C** :

```js
db.fsyncUnlock()
```

Dans **mongosh**, refaites la lecture de l'ordre 3, puis remettez le prix
d'origine :

```js
db.produits.find({ _id: "A-12987" }, { prix: 1 }).readConcern("majority")
db.produits.updateOne({ _id: "A-12987" }, { $set: { prix: 273 } })
```

**Résultat attendu :** ce que répond chaque commande, avec sa durée
approximative pour les ordres 1 et 4, la lecture faite après la
libération, et trois réponses. L'écriture de
l'ordre 1 a répondu par une erreur : a-t-elle été appliquée ? Quelle
phrase du TD du chapitre 1 décrivait la même situation avec PostgreSQL ?
De quoi `readConcern: "majority"` protège-t-il le lecteur ?

## Étape 4 - Le primaire s'arrête *(8 min)*

Si vous avez fermé **atelier**, rouvrez-le avec
`docker compose exec atelier bash`. Dans **atelier**, lancez une caisse
qui encaisse quatre tickets par seconde, chacun confirmé par la majorité :

```bash
python ecrire_en_continu.py
```

Laissez-la tourner et, dans le terminal **principal**, arrêtez proprement
le primaire :

```bash
docker compose stop mongo-a
```

Observez la caisse une quinzaine de secondes, puis, toujours dans le
terminal **principal** :

```bash
docker compose start mongo-a
```

Attendez encore trente secondes. Dans **atelier**, arrêtez la caisse avec
Ctrl+C, puis comparez son carnet à la base :

```bash
python verifier_ecritures.py
```

**Résultat attendu :** le nombre d'erreurs vues par la caisse, la plus
longue interruption, la machine qui confirmait les tickets avant l'arrêt,
pendant, puis à la fin. Combien de tickets confirmés ont été perdus ?
Pourquoi `mongo-a` reprend-il son rôle à son retour ? La réponse est dans
cette commande, à taper dans **mongosh** :

```js
rs.conf().members.map(m => [m.host, m.priority])
```

## Étape 5 - Le primaire est isolé *(12 min)*

Cette fois, `mongo-a` ne s'arrête pas : il est coupé des deux autres. La
caisse, elle, continue de le joindre.

Premier essai, avec une confirmation par le seul primaire. Dans
**atelier** :

```bash
python ecrire_en_continu.py --w 1
```

Dans le terminal **principal**, coupez `mongo-a` des deux autres :

```bash
docker network disconnect ue1-boutique mongo-a
```

**Attendez 25 secondes**, puis rebranchez :

```bash
docker network connect ue1-boutique mongo-a
```

Attendez encore 20 secondes. Dans **atelier**, arrêtez la caisse avec
Ctrl+C, puis comparez son carnet à la base :

```bash
python verifier_ecritures.py
```

Second essai, avec une confirmation par la majorité. Dans **atelier** :

```bash
python ecrire_en_continu.py
```

Refaites exactement la même séquence : coupez, attendez 25 secondes,
rebranchez, attendez 20 secondes, arrêtez la caisse, puis lancez
`python verifier_ecritures.py`.

| Confirmation | Erreurs vues par la caisse | Plus longue interruption | Tickets confirmés puis perdus |
| --- | --- | --- | --- |
| `w: 1` | | | |
| `w: "majority"` | | | |

**Résultat attendu :** le tableau, puis quatre réponses. Qui a confirmé
les tickets perdus, et que sont-ils devenus quand la liaison est revenue ?
Pourquoi l'interruption est-elle plus longue ici qu'à l'étape 4 ? Quel
essai correspond au profil PA/EL du chapitre 1, lequel au profil PC/EC ?
Lequel choisissez-vous pour une caisse ?

## Étape 6 - Régler trois opérations ★ *(7 min)*

Sans machine. Diapositive « Des réglages par opération ».

| Opération | Écart toléré |
| --- | --- |
| Afficher la fiche d'un produit | une description ancienne de quelques secondes |
| Afficher le nombre d'avis | 57 affichés, 58 en base |
| Valider une commande et décrémenter le stock | aucun |

**Résultat attendu :** pour chaque opération, un `writeConcern`, une
`readPreference` ou un `readConcern`, le profil PACELC correspondant, et
la mesure de ce TD qui justifie votre choix.

## Ranger

Dans le terminal **principal** :

```bash
docker compose down -v
```

Cette commande arrête les machines et efface leurs données. La prochaine
fois, `docker compose up -d` rechargera une boutique neuve.

---

# Bonus

Les bonus sont facultatifs et indépendants.

## Bonus 1 - Une transaction

Diapositive « Deux documents, une transaction ». Dans la base `cours`,
ouvrez une session, décrémentez le stock du casque A-400 et insérez une
commande `CMD-1046`, **sans** valider. Dans un second mongosh, lisez le
stock du casque et cherchez la commande. Validez, puis relisez. Refaites
l'essai avec `abortTransaction()`.

## Bonus 2 - Rejouer sans dégât

Base `cours`. Exécutez trois fois l'`updateOne` avec `upsert: true` de la
diapositive « Créer si absent : upsert », puis trois fois
`db.produits.insertOne({ nom: "Café Moka 1 kg" })`. Combien de documents
chaque commande a-t-elle créés ? Laquelle peut-on rejouer après un
timeout ?

## Bonus 3 - La page de recherche en une requête

Avec `$facet`, renvoyez en un seul pipeline sur `produits`, pour les
produits qui portent l'étiquette `bio` : le nombre de produits par
catégorie, et le nombre de produits par tranche de prix (0 à 20, 20 à 50,
50 à 100, plus de 100) avec `$bucket`.

## Bonus 4 - Un panier qui expire

Dans la base `essais`, créez une collection `paniers` avec un index TTL de
60 secondes sur le champ `creeLe`, insérez un panier daté de maintenant,
et comptez les documents toutes les trente secondes. Au bout de combien de
temps le panier disparaît-il réellement ?

## Bonus 5 - Chercher par mots

Créez un index de texte sur le nom des produits, puis cherchez les
produits dont le nom contient « casque ». Comparez le plan avec celui de
`db.produits.find({ nom: /Casque/ })`.

## Bonus 6 - Lire sans jamais se tromper

Refaites l'étape 3 du TD 8 en lisant avec `readConcern("linearizable")`
pendant que les deux secondaires sont figés, avec `.maxTimeMS(3000)`. Que
répond la base ? Reliez ce comportement au théorème CAP.
