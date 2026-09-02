# Missions - Bienvenue chez Ondine

**UE 1 - Persistance & Systèmes Distribués (NoSQL) · Chapitre 1**
Marcu-Andria Battesti · Bachelor CLIC · 2026-2027

> **Le jeu.** Vous venez d'être embauché chez Ondine, un petit service de
> streaming. Tom, qui avait tout écrit, est parti. Le site rame le samedi soir.
> Pendant cinq chapitres, vous le démontez et vous le remontez sur les bonnes
> bases. Chaque chapitre finit par rejouer le samedi soir, et on compare.
>
> **Le terrain.** La branche du dépôt contient `manip/ondine/` : l'appli, ses
> données, ses bases. Il faut Docker Desktop, et rien d'autre. **Téléchargez les
> images la veille** (`docker compose pull` dans `manip/ondine/`) : sur le wifi
> de la salle, mongo:7 met dix minutes.
>
> **Les missions** se font en binôme, dans l'ordre. Le symbole ★ marque la
> question qui prépare l'écrit : sur machine, le temps manque toujours, faites
> celle-là d'abord.
>
> **Répondez en phrases courtes**, dans un fichier `journal.md` que vous gardez
> d'un chapitre à l'autre. On y note aussi les chiffres : le p95 d'aujourd'hui
> est celui qu'on battra au chapitre 2.
>
> **Sous Windows**, tout se fait dans Git Bash. Si un poste refuse de démarrer
> Docker après dix minutes, rejoignez un voisin : les missions se font à deux,
> elles se font aussi bien à trois.

---

# Mission 1 - Faire tomber Ondine

**45 minutes · en binôme · sur machine**

## Contexte

> **De :** Léa, CTO · **Objet :** on ne tient plus
>
> La table `contenus` est ingérable. L'accueil rame. « Aussi écouté » fait peur.
> Le samedi soir, on tombe. Tom est parti. C'est à vous.

Avant de réparer quoi que ce soit : le voir tomber, et comprendre pourquoi.

## Étape 0 - Démarrer *(10 min)*

Dans `manip/ondine/` :

```bash
docker compose up -d
docker compose exec web python -m donnees.charger sql
```

La première commande construit l'image du site (une minute) et démarre
PostgreSQL. La seconde charge les données de Tom : 400 contenus, 60
utilisateurs, 120 000 écoutes.

Ouvrez <http://localhost:8000>. Si le port est pris, changez `ONDINE_PORT`
dans `.env` et relancez `docker compose up -d`.

## Étape 1 - Visiter *(5 min)*

1. **Connectez-vous** comme `u17` (c'est tom13, de Nantes). Il n'y a pas de mot
   de passe : c'est un TD.
2. Écoutez quelque chose - le bouton ▶ sur n'importe quelle fiche. Retournez sur
   **Moi** : l'écoute est là.
3. Ouvrez la page **État**. C'est votre tableau de score. Notez le p95 de
   `GET /` et de `GET /contenu/{id}` dans votre journal : c'est le score « seul ».

## Étape 2 - Samedi soir *(8 min)*

```bash
docker compose exec web python -m outils.samedi_soir
```

Vingt clients pendant vingt secondes. Pendant que ça tourne, rechargez la page
d'accueil dans votre navigateur : vous êtes le vingt-et-unième.

Relevez dans le journal : le p95 de chaque page, le nombre de requêtes par
seconde, et le verdict. Puis rechargez **État** : quelles lignes sont rouges ?

## Étape 3 - Le coupable ★ *(14 min)*

Trois instruments, dans l'ordre.

**Les logs.** Une ligne par requête, avec son temps :

```bash
docker compose logs --tail 50 web
```

**Le code.** Ouvrez `app/stockage/sql.py`. Deux fonctions vous intéressent :
`top_semaine` (l'accueil) et `aussi_ecoute` (la fiche). Lisez le SQL.

**La base.** Un shell PostgreSQL, et la requête du Top 50 sous `EXPLAIN` :

```bash
docker compose exec pg psql -U ondine
```

```sql
EXPLAIN (ANALYZE, COSTS OFF)
SELECT contenu_id, count(*) FROM ecoutes
WHERE date >= '2026-12-14' AND date < '2026-12-21 12:00'
GROUP BY contenu_id ORDER BY 2 DESC LIMIT 50;
```

Cherchez trois choses dans le plan : le mot `Seq Scan`, la ligne
`Rows Removed by Filter`, et `Execution Time`.

★ **La question.** Seule, cette requête prend quelques millisecondes. À vingt
clients, l'accueil met une seconde. Expliquez l'écart en trois phrases, en
utilisant les mots *processeur*, *à chaque affichage* et *tout relire*.

Puis la même chose sur la requête de `aussi_ecoute` (copiez-la depuis le code,
avec `'a001'` et la fenêtre du 21 novembre au 21 décembre). Notez son temps.
C'est cette page-là qui coûte le plus cher : dites pourquoi en une phrase.

## Étape 4 - La table de Tom *(8 min)*

Toujours dans `psql` :

```sql
\d contenus
```

Comptez les colonnes. Puis comptez celles qui sont vides pour un podcast :

```sql
SELECT (SELECT count(*) FROM json_each_text(row_to_json(c)) WHERE value IS NULL)
FROM contenus c WHERE id = 'p001';
```

(la syntaxe est tordue, on vous la donne : ce n'est pas le sujet.)

Deux questions, une phrase chacune :

1. Un artiste sort un album de **treize** pistes. Que se passe-t-il ?
2. Léa veut ajouter un cinquième type de contenu, les **interviews vidéo**, avec
   cinq attributs propres. Qu'est-ce que ça coûte à la table, et au site ?

**Ne rien réparer.** C'est le chapitre 2. Aujourd'hui, on constate.

---

# Mission 2 - Mesurer la distance

**20 minutes · en binôme · partie B sur machine**

## Partie A - Quatre incidents *(8 min · papier)*

Ondine a un serveur à Paris, et bientôt un à Montréal. Pour chaque incident,
dites ce que voit le serveur de Paris et laquelle des quatre causes du cours
(mort, lent, message perdu, réponse perdue) est en jeu - ou plusieurs.

1. Montréal ne répond plus depuis 30 secondes.
2. Paris envoie une écriture, ne reçoit rien ; il la renvoie ; Montréal l'a maintenant **deux fois**.
3. Montréal répond « OK » à une écriture, puis redémarre : l'écriture n'y est plus.
4. Paris a déclaré Montréal mort après 200 ms d'attente. Montréal allait très bien.

★ Pour l'incident 4 : quel timeout auriez-vous mis, et pourquoi pas 200 ms ?
Pour l'incident 2 : qu'est-ce qui, dans la **requête**, aurait évité le doublon ?

## Partie B - Le chronomètre *(12 min · machine)*

Le temps d'un aller-retour, mesuré par `curl`. D'abord chez vous :

```bash
curl -s -o /dev/null -w "%{time_total}\n" http://localhost:8000/sante
```

Cinq fois (flèche haut, Entrée). Notez le plus petit et le plus grand.

Puis l'autre bout du monde - un site qui répond vite, par exemple :

```bash
curl -s -o /dev/null -w "%{time_connect}  %{time_total}\n" https://www.wikipedia.org/
curl -s -o /dev/null -w "%{time_connect}  %{time_total}\n" https://www.canada.ca/
```

`time_connect` est le temps d'ouvrir la connexion : à peu près un
aller-retour, sans le travail du serveur. Cinq fois chacun.

Trois lignes dans le journal :

1. l'aller-retour local, le plus petit ;
2. l'aller-retour le plus lointain, le plus petit ;
3. ★ le rapport entre les deux, et ce rapport comparé aux **6 ms** de la
   requête SQL de la mission 1. Que peut faire une base contre ça ? Que
   peut faire Ondine ?

---

# Mission 3 - Trois copies

**40 minutes · en binôme · sur machine**

## Étape 0 - Lever le cluster *(8 min)*

```bash
bash cluster/replica-set.sh
```

Trois MongoDB, un replica set nommé `rs-td`. Le script attend l'élection et
affiche l'état. Notez qui est `PRIMARY`.

## Étape 1 - Reconnaître le terrain *(7 min)*

Un shell sur le primaire (remplacez `mongo1` par le bon) :

```bash
docker compose exec mongo1 mongosh --quiet
```

```js
rs.status().members.map(m => [m.name, m.stateStr])
db.hello().primary
```

Écrivez quelque chose :

```js
use labo
db.essais.insertOne({ qui: "u17", quoi: "première écriture" })
db.essais.find()
```

Puis ouvrez un **second terminal**, un shell sur un secondaire, et lisez :

```js
use labo
db.essais.find()
```

Deux résultats possibles : le document, ou une erreur `NotPrimaryNoSecondaryOk`.
Si c'est l'erreur, dites au shell que vous acceptez de lire une copie :

```js
db.getMongo().setReadPref("secondary")
db.essais.find()
```

Une phrase dans le journal : pourquoi MongoDB refuse-t-il **par défaut** de
lire sur un secondaire ?

## Étape 2 - Le prix de la majorité *(10 min)*

Sur le primaire, deux cents écritures en `w: 1`, puis deux cents en
`w: "majority"`, chronométrées :

```js
function mesurer(w) {
  const debut = Date.now()
  for (let i = 0; i < 200; i++) db.chrono.insertOne({ i }, { writeConcern: { w } })
  return Date.now() - debut
}
mesurer(1)
mesurer("majority")
```

Chaque valeur trois fois. Notez la médiane de chacune. ★ Qu'achète-t-on avec
la différence ? (Relisez la slide « Quand le primaire dit c'est bon ».)

## Étape 3 - Tuer le primaire *(15 min)*

Dans un troisième terminal, chronomètre en main :

```bash
docker stop mongo1        # ou le nom du primaire
```

Dans le shell d'un secondaire, toutes les deux secondes :

```js
rs.status().members.map(m => [m.name, m.stateStr])
```

Notez combien de temps il faut pour qu'un nouveau `PRIMARY` apparaisse, et le
`term` (le mandat) avant et après :

```js
rs.status().term
```

Puis relancez le mort - `docker start mongo1` - et regardez ce qu'il devient.

Trois questions, une phrase chacune :

1. ★ Qui a décidé du nouveau primaire, et avec quoi ?
2. Pendant les secondes sans primaire, que pouvait faire Ondine : lire ? écrire ?
3. Et si vous aviez arrêté **deux** nœuds sur trois ?
   (Essayez. Puis redémarrez-les : `docker start mongo2 mongo3`.)

---

# Mission 4 - Perdre une écriture

**30 minutes · en binôme · sur machine**

## Étape 0 - Lire avant de lancer *(5 min)*

Ouvrez `cluster/perdre-une-ecriture.sh` et lisez l'en-tête. Le script :
écrit sur le primaire en `w: 1`, le coupe du réseau **pendant qu'il écrit**,
laisse les deux autres élire un remplaçant, écrit sur le remplaçant, puis
reconnecte l'ancien. Il compte ce qui reste.

Avant de le lancer, un pari dans le journal : sur les écritures confirmées
pendant la coupure, combien vont survivre ?

## Étape 1 - Lancer *(10 min)*

```bash
bash cluster/perdre-une-ecriture.sh
```

Soixante-dix secondes. Lisez ce qu'il affiche au fur et à mesure. À la fin,
recopiez le tableau dans le journal.

## Étape 2 - Où sont-elles ? *(8 min)*

Le script vous donne la commande : un dossier `rollback` sur l'ancien primaire,
avec un fichier `.bson` dedans. Regardez-le.

★ **La question du chapitre.** La base avait répondu « écriture confirmée » à
chacune de ces écritures. Que confirmait-elle, exactement ? Et qu'aurait-il
fallu demander pour qu'elle ne confirme que ce qui survivra ?

## Étape 3 - La réparation *(7 min)*

Vous avez la réponse. Vérifiez-la : relancez le script après avoir remplacé,
dans son code, `{ w: 1 }` par `{ w: "majority" }` (une seule ligne, dans le
bloc « écritures en w:1 »). Que devient le nombre de confirmées ? Le nombre
de refusées ? Notez le prix payé.

Remettez `w: 1` à la fin : le script doit rester tel quel pour le voisin.

---

# Mission 5 - Le procès, et le réglage

**30 minutes · en groupes de trois · débat, puis papier**

## Partie A - Six affirmations *(12 min)*

Pour chacune : **vrai**, **faux**, ou **ça dépend** - et de quoi. Deux phrases
au plus. Vous serez interrogés au tableau.

1. « MongoDB est CP, Cassandra est AP. »
2. « Avec CAP, on choisit deux propriétés sur trois. »
3. « Un système cohérent au sens de CAP est un système ACID. »
4. « Pendant une partition réseau, un système AP répond toujours - donc il ment parfois. »
5. « Quand le réseau va bien, un système CP est aussi disponible qu'un système AP. »
6. « Une base sur une seule machine est CA. »

## Partie B - Régler Ondine ★ *(15 min)*

En janvier, Ondine aura un serveur à Montréal. Un samedi soir, le câble
transatlantique tombe pendant quarante minutes. Les deux serveurs vivent, les
deux ont des clients, ils ne se voient plus.

Pour chaque opération d'Ondine, dites si vous voulez **C** (une réponse
exacte ou pas de réponse) ou **A** (une réponse, quitte à ce qu'elle soit un
peu vieille), et le réglage MongoDB qui va avec : `w: 1` ou `w: "majority"`
pour l'écriture, lecture sur le primaire ou sur n'importe quelle copie.

| Opération | C ou A | Écriture | Lecture | Pourquoi (une phrase) |
| --- | --- | --- | --- | --- |
| afficher le Top 50 | | - | | |
| afficher une fiche contenu | | - | | |
| enregistrer une écoute | | | - | |
| publier un avis | | | | |
| payer l'abonnement | | | | |
| supprimer son compte (RGPD) | | | | |

★ Une dernière ligne : laquelle de ces opérations Léa acceptera-t-elle de
voir refusée pendant la coupure ? Laquelle jamais ?

## Partie C - Le cas qui dérange *(3 min)*

Un Montréalais et un Parisien modifient **la même playlist partagée** pendant
la coupure. Quarante minutes plus tard, le câble revient. Les deux versions
arrivent. **Qui gagne ?** Proposez une règle, et dites ce qu'elle a de gênant.
