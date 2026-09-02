# Missions - Le catalogue déménage

**UE 1 - Persistance & Systèmes Distribués (NoSQL) · Chapitre 2**
Marcu-Andria Battesti · Bachelor CLIC · 2026-2027

> **Où on en est.** Au chapitre 1, vous avez fait tomber Ondine : p95 à une
> seconde le samedi soir, une table à 61 colonnes, un Top 50 recalculé à chaque
> affichage. Aujourd'hui, le catalogue déménage dans MongoDB. Vous écrivez la
> migration, vous branchez le site, vous rejouez le samedi soir.
>
> **Le terrain.** `manip/ondine/` contient l'appli du chapitre 1, plus deux
> squelettes : `donnees/migrer.py` et `app/stockage/mongo.py`. Les fonctions
> marquées « à vous » lèvent `AFaire` ; le site vous dit laquelle. La veille :
> `docker compose --profile mongo pull`.
>
> **Dix missions**, huit au clavier, sur quatre séances. Le symbole ★ marque
> la question qui prépare l'écrit. Le **mémo A4** (`memo-a4.md`) porte toute la
> syntaxe : gardez-le ouvert, vous n'apprenez rien par cœur.
>
> **Le journal** continue : `journal.md`, avec les chiffres. Le p95 de fin de
> séance 3 est celui qu'on affiche à côté de celui du chapitre 1.
>
> **Trois gestes qui font gagner du temps** dans `mongosh` : flèche haut
> rappelle la commande ; `.editor` ouvre une saisie multiligne (on colle un
> pipeline, on valide par Ctrl-D) ; `docker compose --profile mongo-ui up -d`
> publie une interface web sur <http://localhost:8081> pour **voir** un document
> se déplier.

---

# Mission 1 - Dessiner

**25 minutes · en binôme · papier**

## Contexte

> **De :** Léa · **Objet :** on migre le catalogue
>
> Avant d'écrire une ligne, je veux voir la forme. Trois documents, sur papier,
> pour un album, un podcast et un concert. Et dites-moi où vont les playlists
> et les avis.

## Partie A - Trois documents *(12 min)*

À partir de la table de Tom (`\d contenus` au chapitre 1 - ou `donnees/charger_sql.py`,
le schéma y est), écrivez les documents JSON de trois contenus de la même
collection `contenus` :

- un **album** : label, et deux ou trois pistes avec numéro, titre, durée ;
- un **podcast** : saison, épisode, invité ;
- un **concert filmé** : lieu, ville, captation 4K ou non.

Contraintes :

- les champs communs (titre, type, artiste, durée, date de sortie, genres)
  apparaissent dans les trois, **au même endroit** ;
- les attributs propres au type sont rangés de façon à ce qu'un **cinquième
  type n'impose aucune modification** aux quatre autres ;
- `genres` n'est plus une chaîne.

Deux phrases : le choix qui vous permet de tenir la deuxième contrainte.

## Partie B - Dedans, ou à côté ★ *(13 min)*

Deux données tournent autour du catalogue. Pour chacune, décidez : imbriquée
dans un document, ou dans sa propre collection - et justifiez en une phrase
avec les mots *bornée*, *lue avec*, *modifiée seule*.

1. les **playlists** d'un utilisateur (2 à 12 titres, quelques-unes par personne) ;
2. les **avis** sur un contenu (un podcast populaire en reçoit des centaines).

Puis : dans un avis, met-on le pseudo de l'auteur, ou seulement son
identifiant ? Qu'est-ce que ça coûte, dans les deux cas ?

---

# Mission 2 - Poser les mains

**30 minutes · en binôme · sur machine**

## Étape 0 - Démarrer *(6 min)*

```bash
docker compose --profile mongo up -d
docker compose exec mongo mongosh --quiet ondine
```

Le shell s'ouvre sur la base `ondine`, vide. `show collections` ne montre rien.

## Étape 1 - Vos trois documents *(12 min)*

Insérez vos trois documents de la mission 1, un par un, avec `insertOne` -
en donnant vous-même le `_id` (`"a900"`, `"p900"`, `"c900"`).

Puis :

```js
db.contenus.find()
db.contenus.find({ type: "album" })
db.contenus.findOne({ _id: "p900" })
db.contenus.countDocuments()
db.contenus.find({ "details.saison": 1 })
```

Ajoutez un genre à l'album avec `updateOne` et `$push`. Relisez-le.

Deux essais qui doivent vous surprendre :

```js
db.contenus.find({ type: "Album" })
db.contenus.find({ genres: "jazz" })      // si votre album a "jazz" dans ses genres
```

Une phrase sur chacun dans le journal.

## Étape 2 - Le site sur une base vide *(6 min)*

Dans `.env`, mettez `CATALOGUE=mongo` puis `docker compose up -d web`. Ouvrez
le catalogue. Lisez la page. Elle vous dit le nom du fichier et de la fonction
qui manque : c'est la mission 6.

Remettez `CATALOGUE=sql`, `docker compose up -d web`. Le site revit.

## Étape 3 - Nettoyer *(6 min)*

```js
db.contenus.deleteMany({})
```

La mission 3 remplit la base pour de bon. Vérifiez : `countDocuments()` → 0.

---

# Mission 3 - La migration

**60 minutes · en binôme · sur machine**

## Contexte

Ondine ne va pas ressaisir 400 contenus. Un script lit PostgreSQL, replie les
61 colonnes, écrit dans MongoDB. C'est le script de la nuit de bascule, et il
est presque écrit : `donnees/migrer.py`.

## Étape 0 - Lire *(8 min)*

Ouvrez `donnees/migrer.py`. Lisez l'en-tête et la fonction `migrer()` : d'où
viennent les lignes, où vont les documents, ce qui est déjà fait (avis,
écoutes). Repérez les deux `TODO`.

Ouvrez aussi `app/stockage/sql.py`, fonction `_en_document` : c'est le
même repliement, écrit par Tom pour l'affichage. Vous pouvez vous en inspirer -
mais pas le recopier : il produit des `null` là où vous ne voulez **pas de
champ**.

## Étape 1 - `document_contenu` *(25 min)*

Écrivez la fonction. Testez-la souvent :

```bash
docker compose exec web python -m donnees.migrer
```

Chaque exécution **repart de zéro** (la base est supprimée et recréée). Après
chaque essai, dans `mongosh` :

```js
db.contenus.findOne({ _id: "a001" })
db.contenus.findOne({ _id: "p001" })
db.contenus.findOne({ _id: "a003" })       // un album du CSV de Tom
```

Ce qu'on attend :

- `a001` : `genres` est un tableau de deux chaînes, `details.pistes` un tableau
  de 10 éléments, pas de clé `podcast_*` ;
- `p001` : `details.invite` vaut `null` (Tom l'avait mis à NULL : c'est une
  information, « pas d'invité »), pas de `pistes` ;
- `a003` : **pas de champ** `genres`, pas de champ `langue`, un champ
  `import_source`.

## Étape 2 - Les playlists *(12 min)*

Second `TODO` : les playlists imbriquées dans l'utilisateur. Vérifiez :

```js
db.utilisateurs.findOne({ _id: "u01" })
db.utilisateurs.findOne({ _id: "u01" }).playlists.length     // 3
db.utilisateurs.findOne({ _id: "u01" }).playlists[0].contenus.length   // 5
```

## Étape 3 - Les comptes ★ *(15 min)*

```js
db.contenus.countDocuments()                                // 400
db.utilisateurs.countDocuments()                            // 60
db.avis.countDocuments()                                    // 1500
db.ecoutes.countDocuments()                                 // 120000
db.contenus.countDocuments({ genres: { $exists: false } })  // 32
```

★ Les 32 albums sans `genres` : pourquoi n'avez-vous pas mis `genres: null`,
ou `genres: []` ? Donnez un cas où chacune des trois formes donne un résultat
différent à la même requête. (Vous vérifierez à la mission 5.)

**Repli à T+40.** Si votre migration ne donne pas encore des contenus
corrects, `docker compose exec web python -m donnees.charger mongo` charge une
base conforme depuis le jeu de données, sans passer par SQL. Les missions
suivantes en ont besoin ; vous finissez `migrer.py` chez vous.

---

# Mission 4 - Huit demandes de Léa

**40 minutes · en binôme · sur machine**

## Contexte

> **De :** Léa · **Objet :** huit questions, réponse ce soir
>
> Le marketing veut des chiffres. Répondez en `find`, et donnez le nombre.

## Étape 0 - État des lieux *(3 min)*

`db.contenus.countDocuments()` doit dire 400. Sinon : `charger mongo`.

## Étape 1 - Huit demandes *(25 min)*

Pour chacune : la requête, et le nombre. Le mémo A4 est là pour ça.

1. Les albums de jazz.
2. Les podcasts de la saison 3.
3. Les contenus sortis en 2026.
4. Les contenus dont le titre contient « refuge ».
5. Les contenus de plus d'une heure.
6. Les cinq derniers contenus sortis : titre et artiste seulement, sans `_id`.
7. Les contenus explicites.
8. Les livres audio lus par « Voix : Sara Nadal ».

## Étape 2 - Deux zéros ★ *(12 min)*

Deux de ces demandes renvoient **zéro** si on les écrit comme on parle.
Trouvez lesquelles, expliquez pourquoi la base ne s'est pas trompée, et
réécrivez-les.

★ Pourquoi ces deux zéros sont-ils **plus graves** qu'une erreur de syntaxe ?
Deux phrases, avec le mot *personne*.

---

# Mission 5 - La chasse

**25 minutes · en binôme · sur machine**

## Étape 1 - Les tableaux *(8 min)*

1. Les contenus qui ont **à la fois** « jazz » et « folk » dans leurs genres.
2. Les contenus qui ont **exactement trois** genres.
3. Les albums dont **au moins une piste** dure plus de six minutes.

Notez les trois nombres.

## Étape 2 - Le même élément ★ *(10 min)*

Léa veut « les albums dont la **piste 1** dure plus de six minutes ». Écrivez
la requête comme elle vient :

```js
db.contenus.countDocuments({ "details.pistes.no": 1, "details.pistes.duree_s": { $gt: 360 } })
```

Comparez au nombre de la question 3 de l'étape 1. ★ Expliquez ce que cette
requête demande **vraiment**. Puis écrivez celle qui répond à Léa, et donnez
le bon nombre.

## Étape 3 - L'absent et le null ★ *(8 min)*

```js
db.contenus.countDocuments({ genres: null })
db.contenus.countDocuments({ genres: { $exists: false } })
db.contenus.countDocuments({ genres: { $type: "null" } })
db.contenus.countDocuments({ "details.invite": null })
```

Le dernier nombre est très supérieur au nombre de podcasts sans invité (29).
★ Que matche exactement `{ "details.invite": null }` ? Écrivez la requête qui
répond à « les podcasts sans invité », et seulement eux.

Reprenez votre réponse ★ de la mission 3 : elle tient ?

---

# Mission 6 - Brancher le site

**45 minutes · en binôme · sur machine**

## Contexte

Le catalogue est dans Mongo. Le site lit encore PostgreSQL. `app/stockage/mongo.py`
attend six fonctions.

## Étape 0 - Le contrat *(5 min)*

Ouvrez `app/stockage/mongo.py`. Lisez `base()`, `_protege`, et la docstring
de chaque fonction « à vous » : elle dit ce que le site attend en retour.
Ouvrez `sql.py` en face : la même fonction, en SQL. C'est la traduction.

Dans `.env` : `CATALOGUE=mongo`, puis `docker compose up -d web`. Le site
vous dit ce qui manque, dans l'ordre où vous le rencontrez.

## Étape 1 - La fiche *(8 min)*

`fiche_contenu`. Ouvrez <http://localhost:8000/contenu/a001>. Quand elle
s'affiche : dix pistes, et **plus une colonne à NULL**. Regardez la ligne
« fiche lue en ». Comparez avec le chapitre 1.

## Étape 2 - Le catalogue *(12 min)*

`lister_contenus`, avec ses trois filtres. Testez chaque filtre sur le site :
type, genre, recherche « refuge ». Le nombre de résultats pour « albums de
jazz » doit être celui de la mission 4.

## Étape 3 - L'historique *(12 min)*

`HISTORIQUE=mongo` dans `.env`, `docker compose up -d web`. Trois fonctions :
`enregistrer_ecoute`, `historique_utilisateur`, `nb_ecoutes_contenu`.

Vérifiez : connectez-vous comme `u17`, écoutez `a001`, allez sur **Moi**.
L'écoute est en tête. Le compteur de la fiche a augmenté de un. Dans
`mongosh`, retrouvez le document que le site vient d'écrire.

## Étape 4 - État *(8 min)*

La page **État** : CATALOGUE et HISTORIQUE disent `mongo`, TOP et RECO disent
encore `sql`. **Deux bases côte à côte, c'est normal** : le Top est la
mission 8.

La reco, elle, est déjà écrite dans `mongo.py` : lisez `aussi_ecoute`, comptez
les étages du pipeline (vous en reparlerez au chapitre 4), puis `RECO=mongo`,
`docker compose up -d web`. Une fiche : « aussi écouté » s'affiche toujours ;
en combien de temps ?

Relevez les temps « seul » de l'accueil et de la fiche dans le journal.
Pourquoi l'accueil n'a-t-il pas changé ?

---

# Mission 7 - Écrire sans écraser

**35 minutes · en binôme · sur machine**

## Étape 1 - Retoucher *(8 min)*

Dans `mongosh` :

1. Le label de `a001` devient « Vieux Port » (`$set`).
2. `a001` gagne le genre « live » (`$push`). Puis encore une fois. Combien de
   fois « live » apparaît-il ? Quelle variante de `$push` l'aurait évité ?
3. La piste 3 de `a001` change de titre : « Route immobile (version longue) ».
   Indice : l'opérateur positionnel `$` après `pistes`.

## Étape 2 - Le geste qui détruit *(6 min)*

```js
db.contenus.replaceOne({ _id: "a002" }, { titre: "Archipel électrique" })
db.contenus.findOne({ _id: "a002" })
```

Ouvrez la fiche `a002` sur le site. Une phrase : qu'est-ce qui s'est passé, et
pourquoi MongoDB n'a rien dit. Réparez avec `charger mongo` (tout revient).

## Étape 3 - L'upsert *(6 min)*

```js
db.compteurs.updateOne({ _id: "a001" }, { $inc: { vues: 1 } }, { upsert: true })
```

Trois fois. Lisez le document. ★ Deux navigateurs font ça au même instant :
combien vaut `vues` ? Pourquoi aucun incrément n'est perdu ?

## Étape 4 - Les avis dans le site *(15 min)*

Deux fonctions dans `mongo.py` : `avis_du_contenu` et `ajouter_avis`. Puis,
connecté comme `u17`, publiez un avis sur `a001`. Il apparaît en tête, avec
votre pseudo. Retrouvez-le dans `mongosh` : quel est son `_id` ? Pourquoi pas
`"v1501"` ?

---

# Mission 8 - Le Top 50 d'Ondine

**40 minutes · en binôme · sur machine**

## Étape 0 - Base fraîche, sans index *(3 min)*

`charger mongo`, pour que tout le monde ait les mêmes chiffres. Puis, dans
`mongosh` :

```js
db.ecoutes.dropIndexes()
```

Le chargeur pose les index dont les chapitres suivants ont besoin. Aujourd'hui
on les retire : c'est vous qui les poserez, à la mission 9, pour les voir
agir.

## Étape 1 - Compter la semaine *(6 min)*

La « semaine en cours » d'Ondine : du 14 décembre 2026 au 21 décembre midi.

```js
db.ecoutes.countDocuments({ date: { $gte: ISODate("2026-12-14"), $lt: ISODate("2026-12-21T12:00:00Z") } })
```

Notez le nombre. C'est celui que chaque étape du pipeline doit voir entrer.

## Étape 2 - Le podium *(8 min)*

Le pipeline de la slide, avec `$limit: 5`. Les trois premiers : identifiants
et nombres dans le journal.

## Étape 3 - Les titres *(6 min)*

Ajoutez un `$lookup` vers `contenus` et un `$project` pour avoir le titre à
côté du nombre. Le premier est un podcast : lequel ?

## Étape 4 - Lire avant d'exécuter ★ *(10 min)*

Un collègue propose ce pipeline « plus rapide » :

```js
db.ecoutes.aggregate([
  { $group: { _id: "$contenu_id", nb: { $sum: 1 } } },
  { $match: { date: { $gte: ISODate("2026-12-14") } } },
  { $sort: { nb: -1 } }, { $limit: 5 }
])
```

**Avant de l'exécuter**, écrivez ce qu'il va renvoyer, et pourquoi. Puis
exécutez. ★ Le premier nombre a changé : expliquez avec la phrase « les
documents qui entrent dans le `$match` n'ont plus de champ… ».

## Étape 5 - Dans le site *(7 min)*

`top_semaine` dans `mongo.py`, `TOP=mongo` dans `.env`, `docker compose up -d web`.
L'accueil affiche le même podium. Notez son temps « seul ».

Puis le samedi soir :

```bash
docker compose exec web python -m outils.samedi_soir
```

Notez le p95. Mieux qu'au chapitre 1 ? De combien ? Et **pourquoi pas
plus** ? Gardez la question pour la mission 9.

---

# Mission 9 - Voir ce que voit la base

**35 minutes · en binôme · sur machine**

## Étape 1 - La requête nue *(8 min)*

```js
db.ecoutes.find({ date: { $gte: ISODate("2026-12-14"), $lt: ISODate("2026-12-21T12:00:00Z") } })
  .explain("executionStats").executionStats
```

Trois nombres dans le journal : `totalDocsExamined`, `nReturned`,
`executionTimeMillis`. Et le mot `COLLSCAN`, quelque part dans
`executionStages`. ★ En une phrase : ce que la base a lu pour rien.

## Étape 2 - Le premier index *(7 min)*

```js
db.ecoutes.createIndex({ date: 1 })
```

Le même `explain`. Les trois nombres. Le mot `IXSCAN`.

Rechargez l'accueil du site : le temps « seul » ?

## Étape 3 - L'historique *(10 min)*

La requête de `historique_utilisateur` pour `u17`, sous `explain` :

```js
db.ecoutes.find({ utilisateur_id: "u17" }).sort({ date: -1 }).limit(20)
  .explain("executionStats").executionStats
```

`totalDocsExamined` avec l'index `{ date: 1 }` seul. Puis :

```js
db.ecoutes.createIndex({ utilisateur_id: 1, date: -1 })
```

Et encore. ★ Pourquoi l'index sur `date` seul examine-t-il 1 095 documents
pour en rendre 20, et le composé 20 ?

## Étape 4 - Le compteur, et la facture *(5 min)*

`nb_ecoutes_contenu` compte par `contenu_id`. Quel index lui faut-il ? Posez-le.

Puis : `db.ecoutes.getIndexes()`. Trois index. Chaque écriture dans `ecoutes`
les met à jour tous les trois. Une phrase : pourquoi on n'en pose pas un
quatrième « au cas où ».

## Étape 5 - Le samedi soir *(5 min)*

```bash
docker compose exec web python -m outils.samedi_soir
```

Le p95, à côté de celui du chapitre 1 et de celui de la mission 8. Trois
chiffres, une ligne : ce qui a fait la différence à chaque étape.

---

# Mission 10 - Imbriquer ou référencer

**30 minutes · en binôme · papier**

## Contexte

> **De :** Léa · **Objet :** trois nouveautés pour janvier
>
> 1. Les utilisateurs pourront **commenter chaque piste** d'un album.
> 2. Chaque fiche affichera un **compteur de vues** (pas d'écoutes : de vues).
> 3. Une playlist pourra être **partagée** avec d'autres utilisateurs, qui la
>    modifient aussi.

## Partie A - Placer chaque donnée ★ *(15 min)*

Pour chacune des trois : **dedans** (quel document), **à côté** (quelle
collection, référencée comment), ou **copié** - et la justification par les
trois questions : lue avec ? bornée ? modifiée seule ?

Pour la 3, dites aussi ce que devient la playlist imbriquée de la mission 1
partie B. Faut-il la sortir ? Pourquoi ?

## Partie B - Le document fautif *(10 min)*

Un développeur a choisi, pour la nouveauté 1 :

```json
{ "_id": "a001", "titre": "...", "details": { "pistes": [
    { "no": 1, "titre": "...", "commentaires": [ { "auteur": "u17", "texte": "..." }, ... ] } ] } }
```

Trois problèmes concrets, un par phrase. Puis : à partir de quel moment ça
casse pour de bon (le chiffre est dans le cours).

## Partie C - Le compteur *(5 min)*

Pour la nouveauté 2, deux développeurs proposent : `$inc` sur le document
`contenus`, ou une collection `compteurs` à part. Quel est l'argument de chacun ?
Lequel gagne si Ondine reçoit mille vues par seconde sur `p001` ?

---

# Démo - Le garde-fou

**10 minutes · au vidéoprojecteur**

Le validateur de la slide, posé sur `contenus`. Puis trois insertions :

```js
db.contenus.insertOne({ _id: "t001", titre: "Test", type: "interview", artiste: "X", details: {} })
db.contenus.insertOne({ _id: "t002", titre: "Test", type: "album", artiste: "X", details: {}, genres: "jazz" })
db.contenus.insertOne({ _id: "t003", titre: "Test", type: "album", artiste: "X", details: {} })
```

Lesquelles passent ? Puis `genres` ajouté à `required`, et un `$set` du label
sur `a003` (un des 32 albums du CSV).

★ Deux stratégies : réparer les 32 (avec quoi ?) ou les tolérer
(`validationLevel: "moderate"`). Laquelle, en une phrase, en pensant à
`mongo.py` qui fait `c.setdefault("genres", None)` ?

---

# Mission 11 - Le mémo à la main

**30 minutes · seul · papier**

## Étape 1 - Recopier *(20 min)*

Le mémo A4 du chapitre (`memo-a4.md`), recopié à la main sur une feuille que
vous garderez jusqu'à l'épreuve. Pas de photocopie : une antisèche écrite se
retrouve sous stress, une antisèche photocopiée non.

## Étape 2 - Sans regarder *(10 min)*

Votre voisin tire trois questions ★ du chapitre (missions 1 à 10). Vous
répondez de mémoire, en une phrase chacune. Puis vous échangez. Ce qui a
manqué va dans le journal : c'est votre liste de révision.
