# Missions - Aussi écouté

**UE 1 - Persistance & Systèmes Distribués (NoSQL) · Chapitre 4**
Marcu-Andria Battesti · Bachelor CLIC · 2026-2027

> **Où on en est.** Le catalogue est sur MongoDB, le Top et le cache sur Redis.
> Il reste le troisième point du mail de Léa : « aussi écouté fait peur » et
> « l'historique doit tenir ». Séance 1 : le graphe. Séance 2 : les colonnes.
> À la fin, plus rien ne tourne sur la base de Tom.
>
> **Le terrain.** `manip/ondine/` : l'appli complète jusqu'au chapitre 3, plus
> trois squelettes - `app/stockage/neo4j_.py`, `app/stockage/cassandra_.py`,
> `donnees/charger_cassandra.py`. La veille, **impérativement** :
> `docker compose --profile graphe --profile colonne pull` (un giga).
>
> **Six missions**, cinq au clavier. ★ marque la question qui prépare l'écrit.
>
> **Mémoire.** Neo4j et Cassandra sont gourmands. Séance 1 : MongoDB + Redis +
> Neo4j. Séance 2 : arrêtez Neo4j (`docker compose stop neo4j`) avant de
> démarrer Cassandra, et arrêtez le nœud Cassandra seul avant de lever
> l'anneau. Le déroulé le rappelle à chaque étape.

---

# Mission 1 - Poser le graphe

**35 minutes · en binôme · sur machine**

## Étape 0 - Une vérité, quatre bases *(8 min)*

```bash
docker compose --profile mongo --profile redis --profile graphe up -d
docker compose exec web python -m donnees.charger neo4j
```

Une minute : les 120 000 écoutes partent par paquets. Lisez l'en-tête de
`donnees/charger_neo4j.py` pendant ce temps : ce que le graphe contient, et
d'où ça vient. Une phrase dans le journal : qu'est-ce que le graphe **n'a
pas** que MongoDB a ?

## Étape 1 - Regarder *(12 min)*

Ouvrez <http://localhost:7474> (pas d'authentification : cliquez « Connect »).
Dans la barre du haut :

```cypher
MATCH (c:Contenu {id: "a001"})-[r]-(x) RETURN c, r, x
```

Le graphe se dessine. Dépliez un nœud (double-clic). Puis :

```cypher
MATCH (u:Utilisateur {id: "u17"})-[:SUIT]->(v) RETURN u, v
MATCH (u:Utilisateur {id: "u17"})-[:A_ECOUTE]->(c) RETURN u, c LIMIT 50
```

Notez ce que suit `u17`, et pourquoi la seconde requête a besoin d'un `LIMIT`.

## Étape 2 - Compter *(8 min)*

```cypher
MATCH (n) RETURN labels(n)[0] AS etiquette, count(*) AS n ORDER BY n DESC
MATCH ()-[r]->() RETURN type(r) AS relation, count(*) AS n ORDER BY n DESC
```

Les deux tableaux dans le journal. Retrouvez le 120 000 et le 400 : ce sont
les mêmes qu'en MongoDB. Le graphe n'invente rien, il **range autrement**.

## Étape 3 - Trois premiers motifs *(7 min)*

En Cypher, sans regarder le mémo si vous pouvez :

1. l'artiste et les genres de `a001` ;
2. combien d'écoutes a reçu `p001` **cette semaine** (du 14 décembre au 21
   décembre midi - `localdatetime("2026-12-14T00:00:00")`), et combien de
   personnes différentes ;
3. les trois artistes de jazz les plus écoutés cette semaine.

Les nombres dans le journal. Pour la 2 : comparez avec le Top du chapitre 2.

---

# Mission 2 - Aussi écouté

**40 minutes · en binôme · sur machine**

## Étape 1 - Le double saut ★ *(12 min)*

« Les auditeurs de p001 ont aussi écouté », cette semaine. Écrivez le motif :
`(p001)<-[e1:A_ECOUTE]-(quelqu'un)-[e2:A_ECOUTE]->(autre chose)`, avec les
deux dates dans la semaine, `autre <> c`, une personne comptée une fois par
contenu, les cinq premiers.

Le podium dans le journal. ★ Lisez votre requête à voix haute : elle doit se
dire en une phrase. Ouvrez `app/stockage/mongo.py`, fonction `aussi_ecoute` :
c'est la même question. Comptez les étages.

## Étape 2 - La recommandation sociale *(10 min)*

Deux sauts d'un autre genre : ce que **les personnes que suit u17** ont aimé
(`A_AIME`), et que u17 n'a pas encore aimé. Puis trois sauts : ce que **les
amis de ses amis** ont aimé.

Le premier de chaque liste. Une phrase : ce que coûterait le troisième saut
en MongoDB.

## Étape 3 - Brancher, et chronométrer ★ *(17 min)*

Dans `app/stockage/neo4j_.py`, `aussi_ecoute` : votre requête de l'étape 1,
avec les paramètres `$id`, `$depuis`, `$jusqua`, `$n` à la place des valeurs,
et une fenêtre de trente jours (c'est le site qui la passe).

`.env` : `RECO=neo4j`. Ouvrez la fiche `a001`, puis `p001`. Notez « aussi
écouté » en ms, deux fois chacune (la première charge). Puis `RECO=mongo`, et
les mêmes mesures.

★ Le graphe est-il plus rapide ? Sur laquelle des deux fiches perd-il, et
pourquoi (pensez au nombre de fans de p001, et à ce que chacun a écouté) ?
Alors pourquoi le garder ? Trois phrases.

Laissez `RECO=neo4j`.

---

# Mission 3 - La feuille et le graphe

**20 minutes · en binôme · papier**

## Contexte

> **De :** Léa · **Objet :** trois questions du produit
>
> 1. « Les playlists qui contiennent ce titre. »
> 2. « Les artistes que mes amis suivent, et que je ne suis pas. »
> 3. « Les contenus de jazz sortis en 2026, les plus récents d'abord. »

## Partie A - Graphe, ou pas graphe ★ *(12 min)*

Pour chaque question : combien de sauts ? Est-ce une question de graphe ?
Si oui, le motif Cypher (en français, puis en Cypher). Si non, où va-t-elle,
et pourquoi le graphe serait une mauvaise idée.

## Partie B - Le dessin *(8 min)*

La question 2 demande une relation qui n'existe pas encore dans le graphe.
Dessinez-la : nœuds, type, sens, propriétés. Puis la commande qui la crée
pour u17 et « Les Lucioles ».

---

# Mission 4 - Deux tables, une donnée

**45 minutes · en binôme · sur machine**

## Étape 0 - Démarrer le nœud *(6 min)*

```bash
docker compose stop neo4j
docker compose --profile colonne up -d
```

Cassandra met **une minute** à répondre : `docker compose exec cassandra cqlsh`
échoue tant qu'elle démarre, puis s'ouvre. Pendant ce temps, ouvrez
`donnees/charger_cassandra.py` : une table est écrite, deux `TODO` vous
attendent.

## Étape 1 - La table naît de la question ★ *(12 min)*

Lisez la table écrite : `ecoutes_par_utilisateur`, partition `utilisateur_id`,
tri `date DESC`. Elle répond à « qu'a écouté u17, du plus récent au plus
ancien ».

★ La seconde question : « combien d'écoutes a a001 ? ». Écrivez
`ecoutes_par_contenu` dans le `TODO mission 4` : quelle clé de partition,
quel tri, quelles colonnes. Ajoutez son entrée dans `CHARGEMENTS`. Puis :

```bash
docker compose exec web python -m donnees.charger cassandra
```

Deux tables, 120 000 lignes chacune. Une phrase : pourquoi la même écoute
est-elle écrite deux fois, et qu'est-ce que ça coûterait en SQL ?

## Étape 2 - La question interdite ★ *(9 min)*

```bash
docker compose exec cassandra cqlsh ondine
```

```sql
SELECT contenu_id, date FROM ecoutes_par_utilisateur WHERE utilisateur_id = 'u17' LIMIT 5;
SELECT count(*) FROM ecoutes_par_contenu WHERE contenu_id = 'a001';
SELECT count(*) FROM ecoutes_par_contenu WHERE date >= '2026-12-14';
SELECT * FROM ecoutes_par_utilisateur WHERE utilisateur_id = 'u17' ORDER BY contenu_id LIMIT 3;
```

Deux des quatre sont refusées. Recopiez le message de chacune. ★ Pour la
troisième : ajoutez `ALLOW FILTERING` à la fin. Elle passe. Alors pourquoi
Cassandra a-t-elle refusé la première fois - et qu'est-ce qu'elle a **lu**
pour répondre ?

## Étape 3 - Brancher *(18 min)*

Dans `app/stockage/cassandra_.py` : `enregistrer_ecoute` (deux `INSERT`),
`historique_utilisateur`, `nb_ecoutes_contenu`. `executer(cql, params)`
prend des `%s`. `.env` : `HISTORIQUE=cassandra`.

Vérifiez : connecté comme `u17`, écoutez `a001` ; page **Moi** ; compteur de
la fiche. Puis l'accueil : la colonne « En ce moment » dit **indisponible**.

Une phrase : pourquoi ce n'est **pas un bug**, et ce que Tom aurait fait.

---

# Mission 5 - En ce moment

**20 minutes · en binôme · sur machine**

## Étape 1 - Dessiner la table ★ *(6 min)*

« Que s'est-il passé aujourd'hui sur Ondine, les dernières écoutes d'abord ? »

★ Quelle clé de partition ? (Indice : ce qu'on met dans le `WHERE`. Ce n'est
ni un utilisateur, ni un contenu.) Quel tri ? Quel problème aurait une
partition unique `'tout'` ?

## Étape 2 - Créer, remplir, lire *(10 min)*

La table dans le `TODO mission 5` de `charger_cassandra.py`, son entrée dans
`CHARGEMENTS`, `charger cassandra`. Puis dans `cassandra_.py` : le troisième
`INSERT` dans `enregistrer_ecoute`, et `dernieres_ecoutes` (la partition
d'aujourd'hui - `horloge.maintenant().date()` - et celle d'hier).

L'accueil : « En ce moment » est revenu. Écoutez un titre : il y est.

## Étape 3 - Le prix *(4 min)*

Chaque écoute fait maintenant **trois** `INSERT`, sans transaction entre eux.
Une phrase : que se passe-t-il si le troisième échoue, et est-ce grave pour
cette table-là ?

---

# Mission 6 - Le curseur, en écriture

**35 minutes · en binôme · sur machine**

## Étape 0 - Lever l'anneau *(8 min)*

```bash
docker compose stop cassandra
bash cluster/anneau.sh
```

Trois minutes : les nœuds rejoignent l'anneau l'un après l'autre. Lisez
`nodetool status` à la fin : trois `UN`, et la colonne `Owns`.

## Étape 1 - Trois copies de tout *(8 min)*

Dans `.env` : `CASSANDRA_HOSTS=cass1,cass2,cass3`, `CASSANDRA_CL=QUORUM`,
`docker compose up -d web`, puis `charger cassandra` (le facteur de
réplication suit le nombre de nœuds : 3).

```bash
docker compose exec cass1 cqlsh ondine
```

```sql
CONSISTENCY;
SELECT count(*) FROM ecoutes_par_contenu WHERE contenu_id = 'a001';
CONSISTENCY ALL;
SELECT count(*) FROM ecoutes_par_contenu WHERE contenu_id = 'a001';
```

Même nombre. Trois copies. `nodetool getendpoints ondine ecoutes_par_contenu a001` :
qui a `a001` ?

## Étape 2 - Tuer, et compter ★ *(14 min)*

```bash
docker kill cass3
```

Huit secondes, puis `nodetool status` sur `cass1` : un `DN`. Dans `cqlsh`,
la même lecture en `ONE`, en `QUORUM`, en `ALL`. Puis une écriture
(`INSERT` d'une écoute de `u17` sur `a001`, date `2026-12-21 13:00:00`) en
`QUORUM`, puis en `ALL`.

★ Tableau dans le journal : niveau × (lecture, écriture) → passe ou refuse.
Puis `docker kill cass2`. Le même tableau. Que reste-t-il ? Ce qui reste
peut-il mentir ?

Le site pendant ce temps : `CASSANDRA_CL=QUORUM`, un nœud mort → ? Deux
nœuds morts → ? Ouvrez **Moi** à chaque étape.

## Étape 3 - Le retour, et le nettoyage *(5 min)*

`docker compose start cass2 cass3`, deux minutes. Le retour des deux nœuds
se regarde au vidéoprojecteur (la lecture `ONE` sur `cass3` qui n'a pas
l'écriture, la lecture `ALL` qui la lui apporte) : c'est la slide « La
cohérence à terme », en vrai.

Puis `.env` : `CASSANDRA_HOSTS=cassandra`, `CASSANDRA_CL=ONE`.
`docker compose stop cass1 cass2 cass3`. Le chapitre 5 repart sur MongoDB.

La carte des quatre familles - où va chaque donnée d'Ondine, et ce qu'on
perd en se trompant - est la dernière mission du module, au chapitre 5.

