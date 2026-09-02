# Missions - Ondine passe l'Atlantique

**UE 1 - Persistance & Systèmes Distribués (NoSQL) · Chapitre 5**
Marcu-Andria Battesti · Bachelor CLIC · 2026-2027

> **Où on en est.** Plus rien ne tourne sur la base de Tom. Le samedi soir est
> à 27 ms. Reste la dernière ligne du mail de Léa : « on ouvre à Montréal en
> janvier ». Une séance : couper, choisir la clé, tenir sur deux continents.
>
> **Le terrain.** `manip/ondine/` : l'appli complète, tous corrigés compris.
> Le cluster shardé se lève par `bash cluster/shards.sh` (une minute). Rien de
> nouveau à télécharger.
>
> **Quatre missions**, deux au clavier, une sur papier, une pour clore. ★
> marque la question qui prépare l'écrit - et la mission 3 **est** l'écrit,
> en répétition : la carte des quatre familles, et la coupure page par page.
>
> **Mémoire.** Arrêtez ce qui ne sert plus avant de lever le cluster :
> `docker compose stop cass1 cass2 cass3 cassandra neo4j`. Le cluster fait
> quatre processus MongoDB.

---

# Mission 1 - Couper `ecoutes` en deux

**35 minutes · en binôme · sur machine**

## Étape 0 - Assembler *(6 min)*

```bash
docker compose stop mongo
bash cluster/shards.sh
```

Quatre processus : `cfg` (la carte), `shard1`, `shard2`, `mongos` (le
routeur). Le script les assemble et abaisse la taille de morceau à 1 Mo -
lisez son en-tête pour savoir pourquoi.

Dans `.env` : `MONGO_URL=mongodb://mongos:27017`, `docker compose up -d web`,
puis `charger mongo` : la base est chargée **à travers le routeur**. Le site
tourne. Sur quel fragment sont les 400 contenus ?

```bash
docker compose exec mongos mongosh --quiet ondine
```

```js
sh.status()
```

Cherchez `primary` dans la partie `databases` : c'est le fragment qui reçoit
tout ce qui n'est pas coupé.

## Étape 1 - Couper *(12 min)*

On ne coupe pas une collection pleine (le script vous dit pourquoi) : on
coupe une collection **vide**, puis on y verse.

```js
db.ecoutes.renameCollection("ecoutes_src")
sh.enableSharding("ondine")
sh.shardCollection("ondine.ecoutes", { utilisateur_id: "hashed" })
db.ecoutes_src.aggregate([{ $merge: "ecoutes" }])
db.ecoutes.countDocuments()
```

Chaque écoute est partie, à l'écriture, vers le fragment que désigne le
hash de son `utilisateur_id`. Puis :

```js
db.ecoutes.getShardDistribution()
```

Deux fragments, combien de documents chacun, combien de morceaux ? Notez.
Posez les index du chapitre 2 (`{ date: 1 }`, `{ utilisateur_id: 1, date: -1 }`,
`{ contenu_id: 1, date: 1 }`) - ils se posent à travers le routeur, sur
chaque fragment.

## Étape 2 - Ciblée, dispersée ★ *(12 min)*

```js
db.ecoutes.find({ utilisateur_id: "u17" }).explain().queryPlanner.winningPlan
db.ecoutes.find({ contenu_id: "a001" }).explain().queryPlanner.winningPlan
```

Dans chaque plan, cherchez `shards` : combien de fragments ont été
interrogés ? Puis l'accueil du site : le Top de la semaine est un `$match`
sur `date`. Ciblé, ou dispersé ?

★ Trois requêtes du site, trois verdicts, et pour chacune : à vingt fragments
au lieu de deux, ce qui se passerait.

## Étape 3 - La preuve physique *(5 min)*

Les fragments s'interrogent en direct (c'est un instrument de mesure, jamais
un geste de production) :

```bash
docker compose exec shard1 mongosh --quiet ondine --eval 'db.ecoutes.countDocuments({ utilisateur_id: "u17" })'
docker compose exec shard2 mongosh --quiet ondine --eval 'db.ecoutes.countDocuments({ utilisateur_id: "u17" })'
```

Toutes les écoutes de u17 sont **au même endroit**. Refaites-le avec
`contenu_id: "a001"` : elles sont **partout**. Une phrase : ce que la clé a
décidé.

Le site, pendant tout ça : rechargez **Moi** et une fiche. Il n'a rien vu.

---

# Mission 2 - La mauvaise clé

**25 minutes · en binôme · sur machine**

## Étape 1 - Cardinalité 3 *(8 min)*

Une seconde collection, coupée par plateforme :

```js
sh.shardCollection("ondine.ecoutes_plateforme", { plateforme: 1 })
db.ecoutes_src.aggregate([{ $merge: "ecoutes_plateforme" }])
db.ecoutes_plateforme.getShardDistribution()
```

Combien de morceaux ? Combien peuvent-ils être, au maximum, avec cette clé ?
★ À vingt fragments, combien travailleraient ?

## Étape 2 - La clé qui ne fait que croître ★ *(12 min)*

```js
sh.shardCollection("ondine.ecoutes_date", { date: 1 })
db.ecoutes_src.aggregate([{ $merge: "ecoutes_date" }])
db.ecoutes_date.getShardDistribution()
```

Regardez la répartition, puis les bornes des morceaux :

```js
db.getSiblingDB("config").chunks.find({ ns: "ondine.ecoutes_date" }, { min: 1, max: 1, shard: 1 }).sort({ min: 1 })
```

Le dernier morceau va de quelle date à `MaxKey` ? Sur quel fragment ?
★ Le samedi soir, chaque nouvelle écoute a une date **plus grande que toutes
les autres**. Où va-t-elle ? Une phrase sur ce que vaut la coupure ce
soir-là.

Puis « les écoutes de la semaine » (`find({ date: { $gte: ISODate("2026-12-14") } })`)
sous `explain` : ciblée ou dispersée ? Comparez avec la même requête sur
`ecoutes` (hachée par utilisateur).

## Étape 3 - Le tableau, ensemble *(5 min)*

Au tableau, tous ensemble, à la correction :

| Clé | Écritures du samedi soir | « les écoutes de u17 » | « les écoutes de la semaine » | « combien pour a001 » |
| --- | --- | --- | --- | --- |
| `{ utilisateur_id: "hashed" }` | | | | |
| `{ plateforme: 1 }` | | | | |
| `{ date: 1 }` | | | | |
| `{ contenu_id: 1 }` (sans la créer) | | | | |

Pour les écritures, *réparties* ou *sur un seul* ; pour les lectures,
*ciblée* ou *dispersée*. ★ Aucune ligne n'est bonne partout.
Laquelle choisissez-vous pour Ondine, et **quelle requête acceptez-vous de
payer** ?

Nettoyage : `db.ecoutes_plateforme.drop()`, `db.ecoutes_date.drop()`,
`db.ecoutes_src.drop()`.

---

# Mission 3 - La carte, et le samedi soir noir

**40 minutes · en groupes de trois · papier**

## Contexte

> **De :** Léa · **Objet :** janvier
>
> On ouvre à Montréal et à Tunis. Un serveur dans chaque ville. Je veux que
> les Montréalais écoutent à Montréal. Avant ça, la carte complète : chaque
> donnée, sa base, et pourquoi. Et je veux savoir **exactement** ce qui se
> passe si le câble tombe un samedi soir - page par page, pas « ça dépend ».

## Partie A - La carte ★ *(15 min)*

Huit données d'Ondine. Pour chacune : la **famille** (et la base), la
**forme** (document, clé, nœud, table), **où vit l'original** (une ville, ou
chaque ville pour sa part), **où vivent les copies**, et **la clé** s'il y a
coupure.

| Donnée | Famille, base | Forme | Original | Copies | Clé |
| --- | --- | --- | --- | --- | --- |
| la fiche d'un album, avec ses pistes (modifiée à Paris par l'équipe) | | | | | |
| le Top 50 de la semaine (par ville ? mondial ?) | | | | | |
| « les amis de mes amis ont aimé » | | | | | |
| les 20 dernières écoutes de u17 (chaque ville écrit, sans arrêt) | | | | | |
| les avis d'un podcast | | | | | |
| la session de l'utilisateur connecté | | | | | |
| « combien de personnes écoutent en ce moment » | | | | | |
| les paiements d'abonnement | | | | | |

★ Pour chaque ligne, une phrase : ce qu'on perd si on la met dans la
mauvaise famille. La dernière ligne n'a pas de bonne réponse parmi les quatre
familles : dites pourquoi, et où elle va.

## Partie B - Samedi 20 h 00 ★ *(10 min)*

Tout va bien. Un Montréalais écoute un titre, lit une fiche, publie un avis,
s'abonne. Pour chaque geste : quelle ville répond, en combien de temps
(80 ms Paris-Montréal, 1 ms local), et quelle base.

## Partie C - Samedi 20 h 40, le câble tombe ★ *(15 min)*

Quarante minutes sans Paris. Pour chaque **page** du site vue de Montréal
(accueil, catalogue, fiche, Moi, l'abonnement) : ce qu'elle affiche - normal,
un peu vieux, ou refusé - et la **décision prise à l'avance** qui l'explique
(où était l'original, quel curseur).

Puis la ligne que Léa lira sur son téléphone : trois phrases, pas une de plus,
qui disent ce qui marche, ce qui est en pause, et ce qui reprendra tout seul
au retour du câble.

---

# Mission 4 - Le score final

**15 minutes · en binôme · sur machine**

## Étape 1 - L'architecture complète *(8 min)*

Dans `.env` : `CATALOGUE=mongo` (à travers `mongos`), `TOP=redis`,
`CACHE=redis`, `RECO=neo4j`, `HISTORIQUE=cassandra` - démarrez ce qu'il faut
(`--profile redis --profile graphe --profile colonne`, et `charger` chaque
base si elle est vide). La page **État** doit n'afficher aucun `sql`.

```bash
docker compose exec web python -m outils.samedi_soir --clients 60
```

Le p95, le débit. À côté des chiffres du chapitre 1.

## Étape 2 - La base de Tom *(4 min)*

```bash
docker compose stop pg
```

Rechargez l'accueil, une fiche, Moi. Rien n'a bougé. Une phrase dans le
journal, la dernière : ce qu'il aurait fallu pour arriver là **sans** casser
le site une seule fois - et si vous l'avez fait.

## Étape 3 - Tout ranger *(3 min)*

```bash
docker compose --profile '*' down
```

Le site s'arrête, les données restent. `docker compose --profile '*' down -v`
pour tout effacer. Gardez le dépôt : l'épreuve porte sur ce que vous avez
fait dedans.
