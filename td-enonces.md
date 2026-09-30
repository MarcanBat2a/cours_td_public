# Panique au Pop-up : la boutique ouvre dans trois heures

**UE 1 · Bases orientées documents · MongoDB et Elasticsearch**

Marcu-Andria Battesti · Bachelor CLIC · 2026-2027

Le Pop-up prépare une vente exceptionnelle. Le catalogue est chargé,
la caisse attend et les clients arrivent. Mais la taille M est annoncée
disponible à tort, certains prix viennent d'un import douteux et la barre
de recherche reste silencieuse devant une faute de frappe.

Votre binôme constitue l'équipe de permanence. Votre objectif est de
livrer huit preuves que la boutique peut ouvrir. Chaque preuve contient
une requête, une observation et une explication courte.

## Le contrat de l'équipe

Une personne écrit la requête, l'autre annonce le résultat qu'elle
attend avant l'exécution. Inversez les rôles à chaque mission. Un retour
sans erreur n'est pas encore une preuve : vérifiez qu'il répond à la
demande du client.

Les indices du site sont disponibles si vous bloquez. Notez dans le
journal les requêtes que vous avez choisies, y compris une tentative
instructive qui a échoué. Les cases de progression sont déclaratives.
À la pause et avant de quitter, cliquez sur **Exporter mon carnet**, puis
sur **Télécharger reponses.md**.

| Temps prévu | Mission |
| --- | --- |
| 10 min | briefing et inspection des données |
| 15 min | 1. Le cadeau de dernière minute |
| 20 min | 2. La taille M fantôme |
| 25 min | 3. L'import qui a tout mélangé |
| 25 min | 4. La caisse veut ses chiffres |
| 25 min | 5. La recherche qui lit trop |
| 15 min | 6. Le client écrit « casqe » |
| 20 min | 7. Une vraie barre de recherche |
| 20 min | 8. Le dernier casque |
| 5 min | débriefing et export |

Total : **180 minutes**, hors installation et pause. Les bonus sont
facultatifs et la suite n'en dépend pas.

## Avant le briefing

Suivez le [démarrage de l'atelier](manip/README.md), puis ouvrez
[http://localhost:8000](http://localhost:8000). Le site exécute vos
requêtes sur MongoDB 7.0 et Elasticsearch 8.19.22.

Vous pouvez travailler dans le site ou utiliser les outils suivants :

- Compass : `mongodb://localhost:27018/?directConnection=true`.
- Elasticvue : cluster `http://localhost:9200`, sans identifiant ni mot de passe.

Inspectez un document de chacune des trois collections `produits`,
`commandes` et `avis` de la base `cours`. Puis inspectez le mapping de
`catalogue` dans Elasticsearch. Le stock et les commandes ont pour
référence MongoDB. Elasticsearch reçoit une copie dédiée à la recherche.

| Ensemble | État initial |
| --- | --- |
| MongoDB `cours` | 7 produits, 4 commandes et 4 avis |
| MongoDB `boutique` | 20 000 produits, avec des anomalies d'import |
| Elasticsearch `catalogue` | les 7 produits de `cours`, avec le même identifiant |

Dans l'éditeur MongoDB du site, choisissez la base, la collection et
l'opération. Le corps est du **JSON strict**. Exemple de lecture sans
filtre, limité à deux documents :

```json
{
  "filter": {},
  "projection": {},
  "sort": { "_id": 1 },
  "limit": 2
}
```

L'opération `aggregate` reçoit `{ "pipeline": [] }`. Les formats des
autres opérations figurent dans le [mémo](memo-a4.md). Dans le shell
Compass ou mongosh, écrivez au contraire des appels comme
`db.produits.find(...)`.

Dans l'éditeur Elasticsearch ou dans la vue REST d'Elasticvue, renseignez
séparément la méthode HTTP, le chemin et le corps JSON. Le chemin ne
contient pas `http://localhost:9200`.

## Mission 1 : le cadeau de dernière minute

**15 min · MongoDB `cours.produits` · `find`**

« Je cherche un livre à 35 € maximum. Je veux repartir avec aujourd'hui.
Montrez-moi seulement son nom et son prix, du moins cher au plus cher. »

1. Écrivez un filtre qui combine la catégorie, le budget et un stock
   strictement positif.
2. Ajoutez la projection demandée, sans `_id`, puis le tri par prix.
3. Comparez avec une recherche qui ne vérifie pas le stock.

**Preuve à garder :** votre requête, les produits obtenus et une phrase
sur le livre numérique. Pourquoi le document qui n'a pas de champ
`stock` ne doit-il pas être interprété comme un article physique
disponible ?

## Mission 2 : la taille M fantôme

**20 min · MongoDB `cours.produits` · `find`**

Une cliente signale : « Le T-shirt apparaît quand je coche taille M
disponible. Pourtant, sa fiche dit que le M est épuisé. » Le filtre actuel
est le suivant :

```json
{
  "filter": {
    "categorie": "vetement",
    "variantes.taille": "M",
    "variantes.stock": { "$gt": 0 }
  },
  "projection": { "nom": 1, "variantes": 1 },
  "sort": { "_id": 1 }
}
```

1. Prévoyez les identifiants retournés, puis exécutez le filtre.
2. Repérez pour `T-100` les éléments du tableau qui satisfont chacune
   des deux conditions.
3. Réécrivez le filtre pour qu'une **même variante** soit en taille M
   et disponible. Vérifiez le résultat.

**Preuve à garder :** les deux filtres, les identifiants de chaque
résultat et une phrase qui explique le faux positif. Le sweat `T-200`
doit pouvoir rester proposé à la cliente.

## Mission 3 : l'import qui a tout mélangé

**25 min · MongoDB `boutique.produits`, puis `cours.produits`**

Le fournisseur affirme avoir envoyé des prix numériques. Le site semble
ignorer certains articles lorsqu'il applique une borne de prix.

1. Dans `boutique.produits`, écrivez un pipeline qui compte les produits
   par type BSON du champ `prix`, avec `$type`, `$group` et `$sum`.
2. Retrouvez les produits dont le prix est du texte et inspectez deux
   exemples. Le nombre initial de ces produits doit être **40** :
   c'est un repère pour vérifier votre diagnostic.
3. Écrivez une mise à jour ciblant seulement ces produits. Utilisez un
   pipeline de mise à jour et `$toInt` pour convertir la valeur de
   chaque document. Exécutez-la avec `updateMany` dans le site, ou avec
   `db.produits.updateMany(...)` dans le shell intégré de Compass.
4. Relancez le comptage des types, puis rejouez votre réparation.
   Comparez les nombres de documents trouvés et modifiés.
5. Dans `cours.produits`, comparez ces trois filtres :
   `{ "stock": null }`, `{ "stock": { "$exists": false } }` et
   `{ "stock": { "$type": "null" } }`. Ajoutez une recherche du stock
   égal à zéro. Inspectez les documents concernés.

**Preuve à garder :** le diagnostic avant et après, votre mise à jour,
les compteurs de ses deux exécutions, puis les identifiants trouvés par
les quatre filtres de stock. Expliquez la différence entre produit
numérique, précommande et rupture de stock.

Les autres anomalies du grand catalogue, notamment le champ `categori`,
restent un prolongement dans [le TD d'approfondissement](https://github.com/MarcanBat2a/cours_td_public/tree/tp/ue1-02-orientees-documents).

## Mission 4 : la caisse veut ses chiffres

**25 min · MongoDB `cours.commandes` · `aggregate`**

La responsable veut classer les produits par chiffre d'affaires. Elle
compte uniquement les commandes de statut `expediee` ou `livree`.
Les commandes en préparation ne doivent pas entrer dans ce bilan.

1. Écrivez un pipeline qui sélectionne les commandes retenues.
2. Transformez les lignes de commande en documents séparés.
3. Regroupez par identifiant de produit et additionnez, pour chaque
   ligne, le prix payé multiplié par la quantité.
4. Triez le chiffre d'affaires par ordre décroissant, puis `_id` par
   ordre croissant pour départager les égalités.
5. Expliquez pourquoi un `$match` sur le statut placé après `$group`
   ne joue plus le même rôle. Comparez aussi « trier puis limiter »
   et « limiter puis trier ».

**Preuve à garder :** votre pipeline, le classement complet et un calcul
manuel sur un produit pour vérifier le résultat. Quel prix doit servir
au calcul : le prix actuel du produit ou celui de la ligne de commande ?

## Mission 5 : la recherche qui lit trop

**25 min · MongoDB `boutique.produits` · `explain`, puis `createIndex`**

La page audio demande les produits de catégorie `audio` à 150 € maximum,
triés par prix croissant puis par `_id` croissant. Mesurez d'abord la
requête complète, sans limite de résultats.

1. Écrivez le filtre et le tri. Exécutez `explain` avec ces paramètres.
   Conservez les statistiques et repérez les étapes du plan.
2. Concevez un index composé répondant à cette demande avec les champs
   `categorie`, `prix` et `_id`. Choisissez leur ordre et donnez un nom
   à votre index.
3. Créez-le, puis refaites exactement la même mesure.
4. Vérifiez que les deux mesures renvoient le même nombre de résultats.

| Mesure | Avant l'index | Après l'index |
| --- | --- | --- |
| `nReturned` | | |
| `totalDocsExamined` | | |
| `totalKeysExamined` | | |
| étapes du plan, dont un éventuel `SORT` | | |

**Preuve à garder :** la requête, les clés de l'index, le tableau et votre
explication du gain constaté. Pourquoi le champ de catégorie vient-il
en tête ? Quel coût l'index ajoute-t-il aux écritures ?

Un temps de quelques millisecondes dépend de la machine et du cache.
La preuve principale est le nombre de lectures et le plan, pas une
promesse de rapidité. Si l'index existait déjà à votre arrivée, signalez
le fait dans le journal et demandez un état initial avant la comparaison.

## Mission 6 : le client écrit « casqe »

**15 min · Elasticsearch `catalogue`**

« Je sais qu'il y a un casque, mais votre moteur ne trouve rien. »

1. Consultez le mapping avec `GET /catalogue/_mapping`. Quel type a le
   champ `nom` ?
2. Avec `POST /catalogue/_analyze`, analysez le texte `Casque Nomade`
   sur le champ `nom`. Notez les termes produits.
3. Avec `GET /catalogue/_search`, cherchez `casqe` dans `nom` avec
   `match`, d'abord sans tolérance, puis avec `fuzziness: "AUTO"`.
4. Écrivez en mots la différence entre une recherche `match` sur
   `casque nomade` avec son opérateur par défaut et avec
   `operator: "and"`.

**Preuve à garder :** le corps d'analyse, les termes observés, les deux
recherches et leurs identifiants. Expliquez pourquoi la recherche et
une égalité exacte sur un champ n'ont pas le même objectif.

`match` utilise OU par défaut entre les termes analysés, tandis que
`and` exige chaque terme. Sur le petit jeu initial, les deux recherches
peuvent avoir le même résultat : cela ne les rend pas équivalentes.
Vous n'avez pas de valeur précise de `_score` à retrouver.
[Référence officielle : match](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-match-query).

## Mission 7 : une vraie barre de recherche

**20 min · Elasticsearch `catalogue` · `GET /catalogue/_search`**

Le client veut chercher `casque nomade`, uniquement dans la catégorie
audio, avec un budget strictement inférieur à 150 €.

1. Dans une requête `bool`, placez la recherche textuelle dans `must`.
2. Ajoutez dans `filter` un `term` pour la catégorie et un `range` pour
   le prix. Vérifiez votre résultat.
3. Refaites la recherche avec un budget strictement inférieur à 100 €.
   Changez seulement ce filtre et observez la différence.
4. Associez à chaque champ du mapping son usage : `text`, `keyword`
   et `integer`. Pourquoi la catégorie se prête-t-elle à `term` ?

**Preuve à garder :** les deux corps JSON, les identifiants obtenus et
deux phrases : quelle clause contribue à la pertinence, quelles clauses
imposent des contraintes sans contribuer au score ?

## Mission 8 : le dernier casque

**20 min · MongoDB `cours.produits` et Elasticsearch `catalogue`**

Il reste un casque `A-400`. Deux clients le veulent. Ne synchronisez pas
le catalogue avant d'avoir observé l'écart.

1. Vérifiez le stock de `A-400` dans MongoDB et dans la copie
   Elasticsearch. Au départ, les deux indiquent 1.
2. Écrivez l'opération `updateOne` qui tente une vente : elle doit
   chercher ce produit, vérifier qu'au moins un exemplaire reste, puis
   décrémenter le stock dans **une seule écriture**. Gardez-la dans le
   journal pour expliquer ce que doit faire la caisse, **sans l'exécuter
   avant les boutons d'achat**.
3. Dans la mission du site, utilisez le bouton d'achat pour le premier
   client, puis pour le second. Le bouton réalise cette réservation
   atomique sur MongoDB. Notez la vente et le refus.
4. Relisez le stock dans les deux systèmes. Rafraîchissez uniquement
   Elasticsearch, puis relisez. L'écart a-t-il disparu ?
5. Lancez la **synchronisation manuelle** du catalogue dans le site,
   puis relisez. Expliquez ce qui a été copié et dans quel sens.

| Observation | MongoDB | Elasticsearch |
| --- | --- | --- |
| avant les achats | | |
| après les deux tentatives | | |
| après le seul rafraîchissement Elasticsearch | | |
| après synchronisation du catalogue | | |

**Preuve à garder :** l'opération que vous avez écrite, les deux réponses
de la caisse, le tableau et votre décision : quel système doit confirmer
la vente ? Pourquoi « lire le stock, puis le décrémenter » dans deux
opérations séparées ne garantit-il pas ce résultat ?

Le rafraîchissement rend les changements déjà indexés visibles à la
recherche. Il ne lit pas MongoDB. La synchronisation transmet les
changements entre les systèmes.
[Référence officielle : refresh](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/refresh-parameter).

Avant de quitter, ajoutez une phrase sur les commandes historiques :
si le prix du casque change demain, faut-il modifier le prix déjà payé
dans les anciennes lignes de commande ? Justifiez selon le rôle de
chaque copie.

## Les cinq minutes avant l'ouverture

Choisissez ensemble la preuve dont vous êtes le plus fiers et une
erreur qui vous a appris quelque chose. Vérifiez que les huit missions
ont leurs requêtes et explications, puis exportez `reponses.md`.

L'enseignant peut vous demander de rejouer une requête et d'expliquer
un résultat. Les cases cochées seules ne suffisent pas à rendre le travail.

## Bonus indépendants

### La différence entre OU et ET devient visible

Dans `cours.produits`, insérez deux petits produits audio fictifs, avec
un prix numérique et un stock positif : `A-410`, nom `Casque Studio`,
et `A-420`, nom `Micro Nomade`. Synchronisez manuellement le catalogue.
Comparez `match` sur `casque nomade` avec l'opérateur par défaut puis
avec `operator: "and"`.

**Preuve :** les deux ensembles d'identifiants et leur explication.
Ces insertions ne sont pas nécessaires aux huit missions.

### Des facettes pour naviguer

Dans Elasticsearch, ajoutez une agrégation `terms` sur `categorie` à une
recherche large. Comparez les catégories et leurs comptes aux résultats.
Que compte une facette si vous appliquez un filtre de budget à la
requête ? Pourquoi `keyword` convient-il à cette agrégation ?

### Une suppression doit aussi voyager

Après le bonus des deux nouveaux produits, supprimez `A-410` dans
Compass, base `cours`, avec `deleteOne`. Observez la copie Elasticsearch
avant puis après synchronisation manuelle. Un traitement qui copie
uniquement les insertions et mises à jour peut-il suffire ?

### Un modèle pour la fiche produit

Décidez où ranger les variantes, les avis et le prix payé d'une commande.
Justifiez chaque décision par l'accès, la taille et la garantie métier.
Quel tableau peut rester borné, lequel peut grandir sans limite ?

### Aller plus loin avec MongoDB

Le [TD d'approfondissement](https://github.com/MarcanBat2a/cours_td_public/tree/tp/ue1-02-orientees-documents) conserve les exercices
sur les index, les transactions, les validateurs, les répliques et les
pannes. Il utilise mongosh et les scripts Docker, avec le même grand
catalogue. Remettez les données à zéro avant de recommencer un exercice
qui attend l'état initial.
