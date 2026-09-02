# Mémo - la matière de votre A4

**UE 1 - Persistance & Systèmes Distribués (NoSQL) · Chapitre 4**
Distribué en fin de séance 1 · à garder sous la main pendant toutes les missions

> Ce mémo récapitule toute la syntaxe du chapitre : pendant les séances, il
> vous évite de fouiller le deck. En fin de chapitre, il rejoint la matière de
> votre **feuille A4 manuscrite** autorisée à l'épreuve, à côté des grilles
> des chapitres 1 (C ou A par opération), 2 (imbriquer ou référencer) et
> 3 (source de vérité, prix d'une perte).
>
> **Recopiez-le à la main.** Une antisèche photocopiée ne se retrouve pas
> sous stress - une antisèche écrite, si.

## Le graphe

```text
(u:Utilisateur {id: "u17"}) -[e:A_ECOUTE {date}]-> (c:Contenu)
   nœud : étiquette + propriétés    relation : type + SENS + propriétés
```

| | |
| --- | --- |
| `MATCH motif RETURN ...` | trouve **toutes** les occurrences du motif |
| `WHERE` · `ORDER BY` · `LIMIT` | comme on les devine ; égalités simples dans le motif |
| `count(*)`, `count(DISTINCT u)` | agrégats dans le `RETURN` : tout ce qui n'est pas agrégé groupe |
| `localdatetime("2026-12-14T00:00:00")` | une date - `"2026-12-14"` seul est une chaîne : le piège du chapitre 2 |
| `CREATE` / `MERGE` | poser le motif / ne le poser que s'il manque (l'upsert du graphe) |
| `shortestPath((a)-[:SUIT*..6]->(b))` | le chemin de longueur inconnue ; sans pointe de flèche, dans les deux sens |

**Le double saut** (« aussi écouté ») :

```text
MATCH (c:Contenu {id: "p001"})<-[e1:A_ECOUTE]-(u)-[e2:A_ECOUTE]->(autre:Contenu)
WHERE autre <> c AND e1.date >= $depuis AND e2.date >= $depuis
RETURN autre.id, count(DISTINCT u) AS fans ORDER BY fans DESC LIMIT 5
```

Les trois détails : exclure le point de départ, compter les **personnes**
(`DISTINCT`), les dates sur les **deux** arêtes.

- **Le sens de la flèche est la moitié du modèle** : `(u)-[:SUIT]->(v)` et
  `(u)<-[:SUIT]-(v)` sont deux questions différentes. Lire la flèche à voix
  haute, sujet-verbe-complément.
- **Nœud ou propriété ?** Ce par quoi on veut **parcourir** devient un nœud
  (Genre, Artiste) ; ce qu'on veut seulement lire reste une propriété
  (`titre`, `duree_s`). Ce qui décrit le lien va sur la relation (`date`).
- **Graphe, ou pas graphe ?** Ce qui se demande en **sauts** (les amis de mes
  amis, par qui je connais X) : oui. Ce qui se demande en **filtres** (le
  jazz de 2026) : non, c'est MongoDB. Le graphe n'est pas plus rapide : il est
  **possible** là où le reste ne l'est pas.

## Les colonnes

```sql
CREATE TABLE ecoutes_par_contenu (
  contenu_id text, date timestamp, utilisateur_id text, plateforme text,
  PRIMARY KEY (contenu_id, date)
) WITH CLUSTERING ORDER BY (date DESC);
```

| | |
| --- | --- |
| `PRIMARY KEY (partition, tri)` | la partition dit **où** vit la ligne (un nœud) ; la colonne de tri, l'**ordre** dedans - payé à l'écriture, gratuit à la lecture |
| `WHERE` | la partition d'abord, la colonne de tri ensuite - **rien d'autre** |
| `ORDER BY` | seulement sur la colonne de tri |
| `ALLOW FILTERING` | « je demande un balayage complet et je le sais » - jamais dans le code d'un site |
| `INSERT` | est un **upsert** : rejouer n'ajoute rien (le contraire de `ZINCRBY`) |
| jointure | n'existe pas - **une table par requête**, la donnée se duplique, l'application écrit N fois |

Trois questions, trois tables chez Ondine : `ecoutes_par_utilisateur`
(partition u17), `ecoutes_par_contenu` (partition a001), `ecoutes_par_jour`
(partition le jour). Une question sans table n'a **pas de réponse**, et c'est
voulu. Une partition unique `'tout'` = un seul nœud qui encaisse tout : la
partition chaude.

## L'anneau, et le curseur

- `hash(clé de partition)` → une position sur l'anneau ; le nœud responsable
  et les N-1 suivants stockent la ligne (facteur de réplication 3 : partout).
- **Sans chef** : tout nœud coordonne, pas d'élection, pas de bascule. Un
  nœud qui tombe laisse deux copies.

```text
W + R > N     ⇒  toute lecture croise au moins une copie à jour
QUORUM + QUORUM = 2 + 2 > 3   cohérent, une panne tolérée
ONE + ONE                      rapide, et périmé possible
```

| `CONSISTENCY` | Réussit si | Un nœud mort | Deux nœuds morts |
| --- | --- | --- | --- |
| `ONE` | 1 copie répond | passe | passe - et peut mentir |
| `QUORUM` | 2 sur 3 | passe | **refusé** (« Cannot achieve consistency level QUORUM ») |
| `ALL` | les 3 | **refusé** | refusé |

Se règle **par requête, en lecture ET en écriture** : le `w: "majority"` du
chapitre 1, enfin des deux côtés. `QUORUM` des deux côtés : on ne ment
jamais, on refuse parfois (C). `ONE` : on répond toujours, on ment parfois (A).

**Cohérence à terme** : si on arrête d'écrire, les copies finiront d'accord.
Dans l'anneau, « à terme » a un mécanisme : une lecture qui compare plusieurs
copies répare celle qui est en retard (*read repair*). Entre-temps, `ONE`
peut lire hier.

## La carte des quatre familles

| Famille | Contrat | Refuse | Chez Ondine |
| --- | --- | --- | --- |
| **Documents** (ch. 2) | l'objet entier, souple, interrogeable | les jointures riches | le catalogue, les avis |
| **Clé-valeur** (ch. 3) | la clé, en RAM, mille fois plus lu qu'écrit | toute requête | le Top, le cache, la session |
| **Graphe** | les liens, les sauts, les chemins | le volume plat, les filtres | « aussi écouté », le social |
| **Colonnes** | des écritures sans fin, des lectures prévues | les questions imprévues | l'historique |

Et les paiements : **aucune des quatre**. Une transaction, de l'intégrité, la
cohérence forte : c'est le relationnel. La base de Tom n'était pas mauvaise,
elle était mal employée.

## Dans le site - Cypher et CQL depuis Python

**Neo4j** (`app/stockage/neo4j_.py`) : `requete(cypher, **params)` exécute du
Cypher et renvoie une liste de dictionnaires. Les paramètres s'écrivent
`$nom` dans la requête et `nom=valeur` en Python. Les dates Python
correspondent à `localdatetime` côté Cypher.

```python
lignes = requete("MATCH (c:Contenu {id: $id})<-[e:A_ECOUTE]-(u) WHERE e.date >= $depuis "
                 "RETURN count(DISTINCT u) AS fans", id="p001", depuis=depuis)
lignes[0]["fans"]
```

**Cassandra** (`app/stockage/cassandra_.py`) : `executer(cql, params)` exécute
un ordre au niveau de cohérence de `.env` ; les valeurs s'écrivent `%s`.
Une ligne se lit comme un objet (`l.contenu_id`) ou un dictionnaire
(`l._asdict()`).

```python
lignes = executer("SELECT contenu_id, date FROM ecoutes_par_utilisateur "
                  "WHERE utilisateur_id = %s LIMIT %s", (uid, n))
[l._asdict() for l in lignes]
```

Deux réglages dans `.env` : `CASSANDRA_HOSTS` (un nœud, ou `cass1,cass2,cass3`)
et `CASSANDRA_CL` (`ONE`, `QUORUM`, `ALL`).
