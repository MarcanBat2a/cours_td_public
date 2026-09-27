# TD - Systèmes distribués et théorème CAP

**UE 1 - Persistance et systèmes distribués · Chapitre 1**
Marcu-Andria Battesti · Bachelor CLIC · 2026-2027

Six TD en une séance de 3 h 30, pause comprise. Le travail est **individuel**.
Vous n'écrivez pas de programme : vous lancez des machines, vous provoquez
des pannes et vous notez ce que vous observez.

Chaque étape se termine par un paragraphe **Résultat attendu** : c'est ce
que vous présentez à la correction. Notez vos réponses dans un fichier
`reponses.md` ou sur papier, avec le numéro du TD et de l'étape. Les bonus
sont regroupés en fin de fiche. Ils sont facultatifs, et la suite n'en
dépend pas.

Le [cours Google Slides](https://docs.google.com/presentation/d/19GHYcCHuAYXxYBGtbKccdqwM1XIar3k4wFp_FDY-bEA/edit)
pose les questions. Ici, vous allez y répondre en observant de vrais
systèmes : PostgreSQL pour les réservations, etcd pour la majorité, et une
petite billetterie web.

## Avant la séance : préparer Docker

Installez [Docker Desktop](https://www.docker.com/products/docker-desktop/)
et lancez-le. Puis, **chez vous**, parce que le premier téléchargement pèse
environ 400 Mo :

```bash
cd manip
docker compose build
docker compose pull
```

Aucune de ces deux commandes ne doit afficher d'erreur. Sinon, venez
avec le message d'erreur : on le règle en début de séance.

## Le décor : neuf machines

| Machine | Rôle |
| --- | --- |
| `pg-a` | PostgreSQL, primaire : il reçoit les réservations. |
| `pg-b` | PostgreSQL, copie de `pg-a`, située « loin » : 20 ms de trajet. |
| `guichet` | Le site de réservation. Il écrit dans `pg-a`. |
| `cat-a`, `cat-b` | Deux copies du catalogue du concert. |
| `etcd-a`, `etcd-b`, `etcd-c` | Trois nœuds etcd, qui décident à la majorité. |
| `poste` | Votre poste de travail dans le décor : `curl` y est installé. |

Les machines communiquent par un réseau nommé `ue1-interne`. **Débrancher
une machine de ce réseau provoque une partition réseau** : la machine
continue de tourner, mais elle ne parle plus aux autres.

```bash
docker network disconnect ue1-interne pg-b    # couper
docker network connect ue1-interne pg-b       # rebrancher
```

## Vos terminaux

Vous ouvrirez plusieurs terminaux, **tous placés dans le dossier `manip/`**.
La fiche les désigne par leur nom :

| Nom | Ce qui s'y tape | Pour l'ouvrir |
| --- | --- | --- |
| **hôte** | les commandes `docker` | un terminal de votre machine, dans `manip/` |
| **poste** | les commandes `curl` | `docker compose exec poste bash` |
| **Alice**, **Karim** | du SQL sur `pg-a` | `docker compose exec pg-a psql` |
| **B** | du SQL sur la copie `pg-b` | `docker compose exec pg-b psql` |

Sous Windows, utilisez PowerShell pour le terminal **hôte**. Les commandes
`curl` se tapent toujours dans **poste**, jamais directement dans
PowerShell : les guillemets n'y sont pas interprétés de la même façon.

Pour quitter `psql`, tapez `\q`. Pour quitter **poste**, tapez `exit`.

---

# TD 0 - Démarrer la billetterie

**Objectif : lancer les neuf machines et repérer qui parle à qui.**

## Étape 1 - Lancer *(5 min)*

Dans **hôte** :

```bash
docker compose up -d --build
docker compose ps
```

Attendez que `pg-a` et `pg-b` affichent `(healthy)`. Si ce n'est pas le
cas après une minute, relancez `docker compose ps`.

**Résultat attendu :** neuf lignes, toutes à l'état `Up`.

## Étape 2 - Une première réservation *(5 min)*

Ouvrez **poste**, puis :

```bash
curl -s guichet:8000/places/7
curl -s -X POST guichet:8000/reservations -d '{"client": "alice", "place": 7}'
curl -s guichet:8000/places/7
```

**Résultat attendu :** le numéro de réservation obtenu et le titulaire de la
place 7 avant et après la réservation.

## Étape 3 - Le plan du réseau *(5 min)*

Dans **hôte**, listez les machines branchées sur chaque réseau :

```bash
docker network inspect ue1-interne --format '{{range .Containers}}{{.Name}} {{end}}'
docker network inspect ue1-acces-a --format '{{range .Containers}}{{.Name}} {{end}}'
docker network inspect ue1-acces-b --format '{{range .Containers}}{{.Name}} {{end}}'
```

Dessinez les neuf machines et un trait par réseau.

**Résultat attendu :** le dessin, et la réponse à cette question : si l'on
débranche `cat-b` du réseau `ue1-interne`, **poste** peut-il encore
interroger `cat-b` ? Et `cat-a` peut-il encore joindre `cat-b` ?

---

# TD 1 - Deux clients, une place

**Objectif : obtenir une double réservation sur une seule machine, sans
panne ni copie, puis l'empêcher.** Diapositives « Une double réservation,
même sur une seule base ».

## Étape 1 - Préparer la scène *(3 min)*

Ouvrez deux terminaux **Alice** et **Karim** côte à côte. Dans **poste**,
remettez la billetterie à zéro :

```bash
curl -s -X POST guichet:8000/admin/reset
```

## Étape 2 - Lire, puis écrire *(8 min)*

Tapez les quatre commandes **dans cet ordre**, en changeant de terminal à
chaque ligne :

| Ordre | Terminal | Commande |
| --- | --- | --- |
| 1 | Alice | `SELECT titulaire FROM places WHERE concert = 'C17' AND place = 42;` |
| 2 | Karim | `SELECT titulaire FROM places WHERE concert = 'C17' AND place = 42;` |
| 3 | Alice | `UPDATE places SET titulaire = 'alice' WHERE concert = 'C17' AND place = 42;` |
| 4 | Karim | `UPDATE places SET titulaire = 'karim' WHERE concert = 'C17' AND place = 42;` |

Chacun a lu « libre » avant d'écrire : pour le site, une réponse
`UPDATE 1` vaut confirmation.

**Résultat attendu :** ce qu'affiche chaque commande, le nombre de
confirmations envoyées, et le titulaire final de la place 42.

## Étape 3 - Avec une transaction *(8 min)*

Remettez la place à zéro, dans **Alice** :

```sql
UPDATE places SET titulaire = NULL WHERE concert = 'C17' AND place = 42;
```

Recommencez la même séquence, mais chacun ouvre une transaction :

| Ordre | Terminal | Commande |
| --- | --- | --- |
| 1 | Alice | `BEGIN;` puis le `SELECT` |
| 2 | Karim | `BEGIN;` puis le `SELECT` |
| 3 | Alice | l'`UPDATE` pour `'alice'` |
| 4 | Karim | l'`UPDATE` pour `'karim'` : **observez** |
| 5 | Alice | `COMMIT;` : **regardez le terminal Karim** |
| 6 | Karim | `COMMIT;` |

**Résultat attendu :** ce qui se passe à l'ordre 4, puis à l'ordre 5, et
votre réponse : le mot `BEGIN` a-t-il empêché la double confirmation ?

## Étape 4 - Tester et attribuer en une seule opération ★ *(11 min)*

Remettez la place à zéro, puis tapez, dans cet ordre :

| Ordre | Terminal | Commande |
| --- | --- | --- |
| 1 | Alice | `UPDATE places SET titulaire = 'alice' WHERE concert = 'C17' AND place = 42 AND titulaire IS NULL;` |
| 2 | Karim | `UPDATE places SET titulaire = 'karim' WHERE concert = 'C17' AND place = 42 AND titulaire IS NULL;` |

Refaites ensuite l'essai avec la transaction de l'étape 3 (`BEGIN`, cet
`UPDATE` conditionnel des deux côtés, puis `COMMIT` d'Alice avant celui
de Karim).

Le guichet fonctionne ainsi. Vérifiez-le dans **poste** :

```bash
curl -s -X POST guichet:8000/admin/reset
curl -s -X POST guichet:8000/reservations -d '{"client": "alice", "place": 42}'
curl -s -X POST guichet:8000/reservations -d '{"client": "karim", "place": 42}'
```

**Résultat attendu :** les réponses `UPDATE` obtenues, puis celles du
guichet, et deux phrases :
- `UPDATE 0` est-il une panne, ou une réponse métier valide ?
- pourquoi la condition `titulaire IS NULL` doit-elle figurer **dans**
  l'`UPDATE`, et non dans un `SELECT` fait juste avant ?

---

# TD 2 - Le timeout d'Alice

**Objectif : constater qu'un même message d'erreur peut cacher des
réalités différentes, puis rendre un nouvel essai sans danger.**
Diapositives « Un timeout : que sait vraiment Alice ? » et « Recommencer
la même demande ».

Le guichet peut simuler une panne. Elle ne touche que **la prochaine**
demande de réservation, puis disparaît :

| Mode | Ce qui se passe réellement |
| --- | --- |
| `perd-demande` | la demande se perd avant d'arriver |
| `lent` | la demande attend 10 s avant d'être traitée |
| `perd-reponse` | la réservation est enregistrée, la réponse se perd |

L'option `-m 5` de `curl` fait abandonner l'attente au bout de 5 secondes :
c'est le timeout du navigateur d'Alice.

## Étape 1 - Trois pannes, un seul écran *(12 min)*

Pour **chacun** des trois modes, tapez dans **poste** :

```bash
curl -s -X POST guichet:8000/admin/reset
curl -s -X POST guichet:8000/admin/panne -d '{"mode": "perd-demande"}'
curl -sS -m 5 -X POST guichet:8000/reservations -d '{"client": "alice", "place": 42}'
curl -s "guichet:8000/reservations?client=alice"
```

Remplacez `perd-demande` par `lent`, puis par `perd-reponse`. Pour le mode
`lent`, relancez la dernière commande **15 secondes plus tard**.

Complétez :

| Mode | Message affiché à Alice | Réservation enregistrée, tout de suite ? | 15 s plus tard ? |
| --- | --- | --- | --- |
| `perd-demande` | | | |
| `lent` | | | |
| `perd-reponse` | | | |

Dans **hôte**, `docker compose logs guichet` montre le journal du serveur :
ce que le serveur sait, et qu'Alice ne voit pas.

**Résultat attendu :** le tableau complété, et une phrase : que peut
conclure Alice à partir du seul message affiché ?

## Étape 2 - Recommencer sans précaution *(8 min)*

```bash
curl -s -X POST guichet:8000/admin/reset
curl -s -X POST guichet:8000/admin/panne -d '{"mode": "perd-reponse"}'
curl -sS -m 5 -X POST guichet:8000/reservations -d '{"client": "alice", "place": 42}'
curl -s -X POST guichet:8000/reservations -d '{"client": "alice", "place": 42}'
```

La dernière commande est le clic d'Alice sur « Réessayer ».

**Résultat attendu :** la réponse du deuxième essai, ce qu'Alice en déduit
probablement, et ce qui est vrai en réalité.

## Étape 3 - Recommencer avec une clé d'idempotence ★ *(10 min)*

Le navigateur joint désormais à la demande une clé qui identifie
**l'intention** d'Alice : `reservation-A7`.

```bash
curl -s -X POST guichet:8000/admin/reset
curl -s -X POST guichet:8000/admin/panne -d '{"mode": "perd-reponse"}'
curl -sS -m 5 -X POST guichet:8000/reservations -H 'Idempotency-Key: reservation-A7' -d '{"client": "alice", "place": 42}'
curl -s -X POST guichet:8000/reservations -H 'Idempotency-Key: reservation-A7' -d '{"client": "alice", "place": 42}'
```

Envoyez ensuite la même clé avec la place 43 à la place de 42. Enfin, dans
un terminal **Alice**, affichez ce que le serveur conserve :

```sql
TABLE idempotence;
TABLE reservations;
```

**Résultat attendu :** les deux réponses obtenues avec la clé, la réponse
pour la place 43, et deux phrases :
- pourquoi la clé doit-elle être enregistrée **dans la même transaction**
  que la réservation ?
- que se passerait-il si le serveur oubliait les clés au bout d'une
  minute ?

## Étape 4 - Réessayer pendant que la première demande attend *(5 min)*

```bash
curl -s -X POST guichet:8000/admin/reset
curl -s -X POST guichet:8000/admin/panne -d '{"mode": "lent"}'
curl -sS -m 5 -X POST guichet:8000/reservations -H 'Idempotency-Key: reservation-A7' -d '{"client": "alice", "place": 42}'
curl -s -X POST guichet:8000/reservations -H 'Idempotency-Key: reservation-A7' -d '{"client": "alice", "place": 42}'
```

Attendez 10 secondes, puis consultez `docker compose logs guichet` dans
**hôte**.

**Résultat attendu :** l'ordre dans lequel le serveur a traité les deux
demandes, et le nombre de réservations créées.

---

# TD 3 - Deux copies de la place 42

**Objectif : observer une copie en retard, puis mesurer ce que coûte
l'attente de la copie avant de confirmer.** Diapositives « La copie B
prend du retard », « Attendre la copie avant de confirmer » et
« Sans partition, la copie peut rester en retard ».

## Étape 1 - Reconnaître A et B *(6 min)*

Ouvrez un terminal **B**. Tapez dans **Alice** puis dans **B** :

```sql
SELECT pg_is_in_recovery();
```

Essayez d'écrire sur B :

```sql
UPDATE places SET titulaire = 'karim' WHERE concert = 'C17' AND place = 1;
```

Dans **Alice**, demandez à A qui le suit :

```sql
SELECT application_name, state, sync_state FROM pg_stat_replication;
```

**Résultat attendu :** le rôle de chaque machine, le message obtenu sur B,
et le mode de réplication indiqué par `sync_state`.

## Étape 2 - La copie B prend du retard *(10 min)*

Pour voir le retard à l'œil nu, on met B en pause : il continue de recevoir
les modifications de A, mais ne les applique plus. Dans **B** :

```sql
SELECT pg_wal_replay_pause();
```

Dans **poste** :

```bash
curl -s -X POST guichet:8000/admin/reset
curl -s -X POST guichet:8000/reservations -d '{"client": "alice", "place": 42}'
```

Alice a reçu sa confirmation. Karim consulte la place sur B, et Alice sur A :

```sql
SELECT titulaire FROM places WHERE concert = 'C17' AND place = 42;
```

Dans **Alice**, comparez ce que A a envoyé et ce que B a appliqué :

```sql
SELECT application_name, sent_lsn, replay_lsn FROM pg_stat_replication;
```

Relâchez B, puis relisez la place sur B :

```sql
SELECT pg_wal_replay_resume();
```

**Résultat attendu :** les lectures sur A et sur B pendant la pause, puis
après, et la correspondance avec les instants t1, t2 et t3 de la
diapositive « La copie B prend du retard ».

## Étape 3 - Attendre la copie avant de confirmer ★ *(12 min)*

Dans **Alice**, activez le chronomètre de `psql` et écrivez trois lignes
dans le journal :

```sql
\timing on
INSERT INTO journal (message) VALUES ('essai 1');
INSERT INTO journal (message) VALUES ('essai 2');
INSERT INTO journal (message) VALUES ('essai 3');
```

Demandez maintenant à A de ne plus confirmer une écriture avant que B l'ait
appliquée :

```sql
ALTER SYSTEM SET synchronous_standby_names = 'pg_b';
SELECT pg_reload_conf();
SET synchronous_commit = remote_apply;
SELECT application_name, sync_state FROM pg_stat_replication;
```

Recommencez les trois `INSERT`.

**Résultat attendu :** les six durées, le nouveau `sync_state`, et une
explication de l'écart à partir du tableau « Le décor ». Faites le lien
avec la ligne « E : sinon, L ou C » de la diapositive PACELC.

## Étape 4 - Et si B ne suit plus ? *(8 min)*

Laissez **Alice** en mode synchrone. Dans **B** :

```sql
SELECT pg_wal_replay_pause();
```

Dans **Alice** :

```sql
INSERT INTO journal (message) VALUES ('pendant la pause');
```

Observez **Alice** pendant 20 secondes, puis relâchez B dans **B** avec
`SELECT pg_wal_replay_resume();`, et regardez de nouveau **Alice**.

**Résultat attendu :** ce qui est arrivé à l'`INSERT`, et votre réponse à
la question de la diapositive « Ce que signifie “confirmé” » : si B ne
répond plus, quelle politique permet encore de confirmer ?

## Étape 5 - Une suppression se réplique aussi *(4 min)*

Dans **Alice** : `DELETE FROM journal;`. Dans **B** :
`SELECT count(*) FROM journal;`.

**Résultat attendu :** le nombre affiché sur B, et une phrase sur la
différence entre une copie et une sauvegarde.

Laissez le mode synchrone en place : le TD 4 s'en sert.

---

# TD 4 - La liaison A-B est coupée

**Objectif : provoquer une vraie partition, puis comparer deux systèmes
qui font des choix opposés.** Diapositives « Une écriture confirmée,
puis une lecture », « Après discussion : les choix de B », « Continuer à
répondre de chaque côté » et « Quand la communication revient ».

## Partie A - Les réservations : PostgreSQL

### Étape 1 - Couper *(6 min)*

Dans **hôte**, coupez B et notez l'heure :

```bash
docker network disconnect ue1-interne pg-b
```

Dans **B**, lisez la place 99. Dans **Alice**, relancez la requête sur
`pg_stat_replication` tout de suite, puis toutes les 15 secondes, jusqu'à
ce que la ligne de `pg_b` disparaisse.

**Résultat attendu :** ce que répond B, et le temps mis par A pour
constater que B ne répond plus. Pendant ce temps, A pouvait-il savoir si B
était arrêté, lent ou isolé ?

### Étape 2 - Réserver pendant la coupure *(7 min)*

Dans **Alice**, vérifiez que vous êtes toujours en mode synchrone
(`SHOW synchronous_commit;` doit afficher `remote_apply`, sinon refaites
le `SET` du TD 3), puis :

```sql
UPDATE places SET titulaire = 'alice' WHERE concert = 'C17' AND place = 99 AND titulaire IS NULL;
```

Attendez 30 secondes. Puis appuyez sur **Ctrl+C** : Alice abandonne.
Recopiez **intégralement** le message affiché. Lisez ensuite la place 99
dans **Alice**, puis dans **B**.

**Résultat attendu :** le message, les deux lectures, et votre réponse :
la réservation d'Alice est-elle faite ? Est-elle confirmée ? Rapprochez
cette situation du TD 2.

### Étape 3 - Le choix de B *(4 min)*

Reprenez le tableau de la diapositive « Après discussion : les choix de
B » : lire sa valeur locale, attendre A, refuser la lecture.

**Résultat attendu :** l'option qu'a prise PostgreSQL sur B à l'étape 1,
celle qu'a prise A à l'étape 2, et, pour chacune, la limite annoncée
par la diapositive que vous avez observée.

### Étape 4 - Rebrancher et revenir en asynchrone *(3 min)*

```bash
docker network connect ue1-interne pg-b
```

Au bout de quelques secondes, relisez la place 99 sur **B**. Puis, dans
**Alice**, remettez la réplication asynchrone :

```sql
ALTER SYSTEM RESET synchronous_standby_names;
SELECT pg_reload_conf();
```

**Résultat attendu :** la valeur lue sur B après la reconnexion.

## Partie B - Le catalogue : deux copies qui répondent toujours

### Étape 5 - Deux écritures pendant la coupure *(10 min)*

Dans **poste**, remettez le catalogue à zéro, lisez les deux copies,
puis décalez l'horloge de `cat-b` de cinq minutes en arrière :

```bash
curl -s -X POST cat-a:8000/admin/reset
curl -s cat-a:8000/description
curl -s cat-b:8000/description
curl -s -X POST cat-b:8000/admin/horloge -d '{"decalage": -300}'
```

Dans **hôte**, coupez `cat-b` :

```bash
docker network disconnect ue1-interne cat-b
```

Dans **poste**, écrivez l'horaire sur A. **Attendez 10 secondes**, puis
écrivez la correction de l'organisateur sur B :

```bash
curl -s -X PUT cat-a:8000/description -d '{"valeur": "Ouverture à 19 h"}'
curl -s -X PUT cat-b:8000/description -d '{"valeur": "Ouverture à 20 h"}'
```

Lisez les deux copies, puis rebranchez `cat-b` (`docker network connect
ue1-interne cat-b` dans **hôte**). Attendez 3 secondes et relisez les deux
copies.

**Résultat attendu :** les valeurs lues pendant la coupure et après, la
valeur écrite en dernier dans le temps réel, et l'explication de l'écart
à partir des horodatages affichés.

### Étape 6 - Garder le conflit et laisser trancher ★ *(10 min)*

```bash
curl -s -X POST cat-a:8000/admin/reset
curl -s -X POST cat-a:8000/admin/fusion -d '{"mode": "conflits"}'
curl -s -X POST cat-b:8000/admin/horloge -d '{"decalage": -300}'
```

Refaites la coupure et les deux écritures de l'étape 5, puis rebranchez
et relisez. Enfin, jouez l'opérateur qui valide « 20 h » :

```bash
curl -s -X PUT cat-a:8000/description -d '{"valeur": "Ouverture à 20 h"}'
```

Relisez les deux copies.

**Résultat attendu :** ce que montrent les copies après la reconnexion,
puis après la décision de l'opérateur, et les trois conditions de la
diapositive « La cohérence à terme » que vous avez vues à l'œuvre.

---

# TD 5 - Trois nœuds et une majorité

**Objectif : observer un système qui préserve la cohérence en exigeant
une majorité.** Diapositive « Et si A tombe ? Trois nœuds et une
majorité ».

etcd est une base clé-valeur utilisée, entre autres, par Kubernetes. Ses
trois nœuds s'accordent avec l'algorithme Raft : un **leader** reçoit les
écritures et ne les confirme qu'une fois copiées sur une majorité.

## Étape 1 - Qui dirige ? *(5 min)*

Dans **hôte** :

```bash
docker compose exec etcd-a etcdctl endpoint status --cluster -w table
docker compose exec etcd-a etcdctl put /concert/C17/place/42 alice
docker compose exec etcd-b etcdctl get /concert/C17/place/42
```

Dans la suite, **X** désigne le nœud dont la colonne `IS LEADER` vaut
`true`, et **Y** l'un des deux autres. Remplacez `etcd-X` par son nom réel,
par exemple `etcd-c`.

**Résultat attendu :** le nom du leader et la valeur de `RAFT TERM`.

## Étape 2 - Isoler le leader *(12 min)*

```bash
docker network disconnect ue1-interne etcd-X
docker compose exec etcd-X etcdctl put /concert/C17/place/42 karim
docker compose exec etcd-X etcdctl get /concert/C17/place/42
docker compose exec etcd-X etcdctl get /concert/C17/place/42 --consistency=s
```

La dernière commande demande une lecture **locale** (`s` pour
*serializable*) : le nœud répond avec ce qu'il a, sans consulter les
autres. Côté majorité :

```bash
docker compose exec etcd-Y etcdctl endpoint status --cluster -w table
docker compose exec etcd-Y etcdctl put /concert/C17/place/42 karim
docker compose exec etcd-X etcdctl get /concert/C17/place/42 --consistency=s
```

La commande `status` affiche une erreur pour le nœud isolé : c'est
normal.

**Résultat attendu :** la réponse de chacune des sept commandes, le
nouveau leader et le nouveau `RAFT TERM`, et votre réponse : laquelle de
ces lectures n'est **pas** linéarisable, et pourquoi ?

## Étape 3 - Rebrancher *(5 min)*

```bash
docker network connect ue1-interne etcd-X
docker compose exec etcd-X etcdctl get /concert/C17/place/42
docker compose exec etcd-X etcdctl endpoint status --cluster -w table
```

**Résultat attendu :** la valeur lue sur X et son nouveau rôle. L'écriture
tentée sur X à l'étape 2 a-t-elle laissé une trace ?

## Étape 4 - Plus de majorité nulle part *(7 min)*

Débranchez **les trois** nœuds, puis tentez une écriture sur deux d'entre
eux :

```bash
docker network disconnect ue1-interne etcd-a
docker network disconnect ue1-interne etcd-b
docker network disconnect ue1-interne etcd-c
docker compose exec etcd-b etcdctl put /concert/C17/place/43 alice
docker compose exec etcd-c etcdctl put /concert/C17/place/43 karim
```

Rebranchez les trois (`docker network connect ue1-interne etcd-a`, puis
`b`, puis `c`), attendez une dizaine de secondes, puis lisez la place 43.

**Résultat attendu :** les réponses aux deux écritures, la valeur lue après
reconnexion, et une phrase : pourquoi aucun nœud ne confirme alors que
les trois sont en marche ?

## Étape 5 - Le compteur indicatif ★ *(6 min)*

La diapositive « Deux profils pour la billetterie » demande : quel profil
choisir pour un compteur indicatif de places restantes ?

**Résultat attendu :** votre réponse, justifiée par **deux mesures** de la
séance (une durée du TD 3, une lecture du TD 4 ou du TD 5), et le profil que
vous gardez pour la confirmation d'une place.

## Ranger

Dans **hôte** :

```bash
docker compose down -v
```

Cette commande arrête les machines et efface leurs données. La prochaine
fois, `docker compose up -d` repartira d'une billetterie vide.

---

# Bonus

Les bonus sont facultatifs et indépendants.

## Bonus 1 - Le niveau d'isolation REPEATABLE READ

Refaites l'étape 3 du TD 1 en ouvrant les deux transactions par
`BEGIN ISOLATION LEVEL REPEATABLE READ;` au lieu de `BEGIN;`. Que répond
PostgreSQL à Karim ? Que doit faire le site dans ce cas ?

## Bonus 2 - Réserver si libre, avec etcd

etcd propose aussi une opération conditionnelle. Dans **hôte** :

```bash
docker compose exec etcd-a etcdctl txn -i
```

Répondez aux trois invites : `create("/concert/C17/place/7") = "0"` pour
la condition (la clé n'existe pas encore), puis `put /concert/C17/place/7 alice`
en cas de succès, puis `get /concert/C17/place/7` en cas d'échec. Validez
chaque invite par une ligne vide. Recommencez depuis `etcd-b` pour `karim`.
Comparez avec l'étape 4 du TD 1.

## Bonus 3 - Éloigner davantage B

Dans **hôte**, `docker compose exec pg-b eloigner.sh 100ms`, puis refaites
les mesures de l'étape 3 du TD 3. La durée d'une écriture synchrone suit-elle
la distance ? Remettez `20ms` à la fin.

## Bonus 4 - Arrêter au lieu de débrancher

Refaites l'étape 2 du TD 5 avec `docker stop etcd-X` au lieu de
`docker network disconnect`, puis `docker start etcd-X`. Qu'est-ce qui
change pour le client qui interroge X ? Pour les deux autres nœuds, la
différence est-elle visible ?
