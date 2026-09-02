# Mémo - la matière de votre A4

**UE 1 - Persistance & Systèmes Distribués (NoSQL) · Chapitre 5**
Distribué en fin de séance · le dernier du module

> Ce mémo clôt votre **feuille A4 manuscrite** : cinq chapitres, quatre
> grilles, et la méthode. **Recopiez-le à la main** - c'est le dernier
> exercice du module, et le plus rentable des trois semaines qui viennent.

## L'anatomie

```text
le site ─► mongos (routeur) ─► shard1 · shard2 · ...
               │
            cfg : la carte  (clé → morceau → fragment)
```

| | |
| --- | --- |
| **fragment** (*shard*) | une part des données - en production, un replica set complet |
| **morceau** (*chunk*) | un intervalle de la clé de partition ; l'**équilibreur** les déménage |
| collection non coupée | vit **entière** sur le fragment *primaire* de la base - on ne coupe que ce qui le mérite |
| répliquer / couper | des copies complètes (la panne, les lectures) / chacun sa part (la taille, les écritures) |

## Ciblée, dispersée

| | Ciblée | Dispersée (*scatter-gather*) |
| --- | --- | --- |
| le filtre | contient la clé de partition | ne la contient pas |
| le routeur | lit la carte, interroge **un** fragment (`SINGLE_SHARD`) | interroge **tous** les fragments, fusionne (`SHARD_MERGE`) |
| à 20 fragments | une machine travaille | vingt travaillent, pour une réponse |

Sans erreur, sans avertissement : ça « marche », et tout le cluster paie. La
clé de partition décide donc **quelles requêtes restent bon marché**. *La clé
est le seul chemin - troisième version, après Redis et Cassandra.*

## La clé : trois maladies

| Maladie | La clé | Ce qui se passe (mission 2) |
| --- | --- | --- |
| **cardinalité faible** | `plateforme` (3 valeurs) | 2 morceaux, 120 000 / 0 : jamais plus de morceaux que de valeurs |
| **monotone** | `date` | le dernier morceau (`… → MaxKey`) reçoit **toutes** les écritures du samedi soir, sur **un** fragment |
| **chaude** | `contenu_id` | `p001` reçoit 352 écoutes par semaine, `l034` deux : un fragment surchargé, l'autre dort |

Le remède commun : **hacher** (`{ utilisateur_id: "hashed" }`) - les
écritures se répartissent (62 174 / 57 826)… et toute requête par
**intervalle** sur la clé devient dispersée. Aucune maladie ne se soigne en
ajoutant des machines : il n'y a pas de bonne clé dans l'absolu, il y a **la
clé de vos requêtes**.

| Clé | Écritures samedi soir | « u17 » | « la semaine » | « a001 » |
| --- | --- | --- | --- | --- |
| `utilisateur_id` haché | réparties | **ciblée** | dispersée | dispersée |
| `date` | **sur un seul** | dispersée | **ciblée** | dispersée |
| `contenu_id` | `p001` chaud | dispersée | dispersée | **ciblée** |

La clé se choisit **avant** le premier document (changer après :
`reshardCollection`, ou une copie complète), et **avec les autres bases dans
la pièce** : le Top est en Redis, le compteur en Cassandra, donc la clé de
`ecoutes` peut se consacrer à la page Moi.

## Trois régions

- **Lire près de soi** : une copie locale (chapitre 1), un cache local
  (chapitre 3) - avec le retard qu'on connaît.
- **Écrire près de soi** : la région **entre dans la clé**
  (`{ region: 1, utilisateur_id: 1 }`), les morceaux `CA` vivent à
  Montréal : 1 ms au lieu de 80.
- **La coupure inter-régions** (le samedi soir noir) : le local continue ;
  ce qui a son original de l'autre côté est **refusé ou mis de côté** ; ce
  qui s'écrit des deux côtés **diverge**, et « le dernier gagne » perd des
  écritures en silence (chapitre 1, mission 5 C).
- Chaque ligne du tableau est une **décision prise avant** la coupure : où
  vit l'original, où vivent les copies, quel curseur.

## La méthode du module - la colonne de l'A4

1. **Comment on la lit ?** (une clé, un filtre, un saut, un intervalle) → la famille (carte du ch. 4)
2. **Comment on l'écrit ?** (rarement, sans arrêt, par un seul, par tous) → le modèle (ch. 2, 4)
3. **Que coûte le périmé ?** (rien, un agacement, de l'argent) → le curseur C ou A par opération (ch. 1, 3, 4)
4. **Que coûte la perte ?** (rien, on rejoue, c'est irréparable) → la source de vérité (ch. 3)
5. **Où est-elle lue ?** (une ville, trois continents) → la clé, la région (ch. 5)

Il n'y a pas de sixième question. Et quand ça casse un samedi soir, la
réponse est **écrite d'avance**, page par page.

## Les commandes du cluster shardé

```js
sh.status()                                              // la carte : fragments, bases, morceaux
sh.enableSharding("ondine")
sh.shardCollection("ondine.ecoutes", { utilisateur_id: "hashed" })   // sur une collection VIDE
db.ecoutes_src.aggregate([{ $merge: "ecoutes" }])        // verser : routé à l'écriture
db.ecoutes.getShardDistribution()                        // documents et morceaux par fragment
db.ecoutes.find({ utilisateur_id: "u17" }).explain().queryPlanner.winningPlan   // cherchez « shards »
db.getSiblingDB("config").chunks.find({ ns: "ondine.ecoutes" }, { min: 1, max: 1, shard: 1 })
```

Le site parle au routeur : `MONGO_URL=mongodb://mongos:27017`. Un fragment
s'interroge en direct (`docker compose exec shard1 mongosh ondine`) pour
**mesurer**, jamais pour servir une page.
