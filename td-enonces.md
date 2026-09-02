# Missions - Trois millisecondes

**UE 1 - Persistance & Systèmes Distribués (NoSQL) · Chapitre 3**
Marcu-Andria Battesti · Bachelor CLIC · 2026-2027

> **Où on en est.** Le catalogue et l'historique d'Ondine sont sur MongoDB,
> indexés ; le samedi soir est passé de 1 060 à 25 ms. Mais l'accueil recalcule
> encore le même Top 50 pour tout le monde, et chaque fiche refait la même
> recommandation. Aujourd'hui, Redis : un classement qui se maintient tout
> seul, et un cache - qui ment, parfois.
>
> **Le terrain.** `manip/ondine/` contient l'appli du chapitre 2 complète
> (`mongo.py` et `migrer.py` corrigés), plus `app/stockage/redis_.py` en
> squelette. La veille : `docker compose --profile redis pull`.
>
> **Six missions**, cinq au clavier, sur deux séances. ★ marque la question
> qui prépare l'écrit. Le mémo A4 porte les commandes.
>
> **Deux bases côte à côte** tout le chapitre : MongoDB reste démarré
> (`--profile mongo`), Redis s'ajoute (`--profile redis`). La page **État**
> dit qui fait quoi. Au début de chaque séance : `charger mongo` (vingt
> secondes, base propre, index posés).

---

# Mission 1 - Poser les clés

**30 minutes · en binôme · sur machine**

## Étape 0 - Démarrer les deux bases *(6 min)*

```bash
docker compose --profile mongo --profile redis up -d
docker compose exec web python -m donnees.charger mongo
docker compose exec redis redis-cli
```

Dans `.env`, `CATALOGUE`, `TOP`, `HISTORIQUE` et `RECO` sont sur `mongo` :
c'est l'état où le chapitre 2 a laissé le site. `CACHE` est encore à `aucun`.
`docker compose up -d web`, page État : vérifiez.

Redis démarre **vide**. `DBSIZE` → 0. C'est déjà une leçon : notez-la.

## Étape 1 - Le contrat minimal *(12 min)*

```
SET ondine:essai bonjour
GET ondine:essai
GET ondine:inconnu
SET ondine:essai autre_chose
GET ondine:essai
SET ondine:essai encore NX
GET ondine:essai
DEL ondine:essai
EXISTS ondine:essai
```

Trois questions, une phrase chacune :

1. `GET ondine:inconnu` : qu'a répondu Redis ? Est-ce une erreur ? Comparez
   avec les « deux zéros » du chapitre 2.
2. Le second `SET` : a-t-il prévenu qu'il écrasait ? Quel `SET` refuse
   d'écraser ?
3. Que vaut la valeur après le `SET ... NX` ?

## Étape 2 - Ce que la clé sait dire *(6 min)*

```
SET ondine:fiche:a001 "{...}" EX 30
TTL ondine:fiche:a001
TTL ondine:fiche:a001
```

Attendez trente secondes. `GET`. Puis :

```
SET ondine:fiche:a002 x
SET ondine:top:semaine x
SET ondine:session:u17 x
SCAN 0 MATCH ondine:fiche:*
KEYS ondine:*
```

Une phrase : pourquoi `KEYS` est-il interdit en production, et `SCAN` pas ?

## Étape 3 - La question interdite ★ *(6 min)*

Léa demande : « les contenus dont le titre contient *Refuge* ». Vous avez
la fiche `a001` dans `ondine:fiche:a001`, et 399 autres.

★ Écrivez la commande Redis qui répond. Si vous n'en trouvez pas, dites
pourquoi en une phrase avec les mots *clé* et *chemin* - et où cette question
doit aller.

---

# Mission 2 - Trois besoins, trois structures

**40 minutes · en binôme · sur machine**

La session en hash (`HSET`, `HGET`, `HINCRBY`, `HGETALL`) se montre au
vidéoprojecteur avant la mission ; le mémo en garde la trace.

## Étape 1 - La course ★ *(12 min)*

Le compteur d'écoutes de `a001`, dans une chaîne :

```
SET ondine:ecoutes:a001 207
INCR ondine:ecoutes:a001
GET ondine:ecoutes:a001
```

Maintenant, la course. Deux terminaux `redis-cli`, et dans chacun, collez :

```
EVAL "for i=1,10000 do redis.call('INCR','ondine:ecoutes:a001') end return 1" 0
```

Lancez les deux le plus vite possible l'un après l'autre. `GET`. Vingt mille
de plus, exactement ? ★ Pourquoi aucun incrément n'a été perdu - et qu'est-ce
qui, dans un « lire, +1, écrire » fait par Python, en aurait perdu ?

## Étape 2 - L'historique *(10 min)*

« Vos dix dernières écoutes » :

```
LPUSH ondine:recents:u17 a124
LPUSH ondine:recents:u17 a001 p003 c010
LRANGE ondine:recents:u17 0 -1
```

Poussez-en quinze de plus (n'importe quels identifiants). `LLEN`. Puis :

```
LTRIM ondine:recents:u17 0 9
LLEN ondine:recents:u17
LRANGE ondine:recents:u17 0 -1
```

★ Quel anti-patron du chapitre 2 ce couple `LPUSH` + `LTRIM` résout-il, et
comment ?

## Étape 3 - Le classement ★ *(15 min)*

Rejouez la semaine d'Ondine dans un sorted set - un `ZINCRBY` par écoute
du 14 au 21 décembre, ce que fera le site à chaque clic :

```bash
docker compose exec web python -m donnees.charger redis
```

Puis :

```
ZCARD ondine:top:semaine
ZREVRANGE ondine:top:semaine 0 4 WITHSCORES
ZSCORE ondine:top:semaine a001
ZREVRANK ondine:top:semaine a001
ZINCRBY ondine:top:semaine 1 a001
ZREVRANK ondine:top:semaine a001
```

Comparez le podium avec celui de la mission 8 du chapitre 2. Puis
**relancez `charger redis`** et regardez `ZSCORE a001`. Ouvrez le script :
qu'est-ce qui l'empêche de doubler ? Commentez la ligne `r.delete(...)`,
relancez, et regardez encore.

★ `ZINCRBY` n'est pas idempotent ; l'`INSERT` de Cassandra (chapitre 4) le
sera. En une phrase : ce que ça change quand on **rejoue** un journal
d'écoutes après une panne.

---

# Mission 3 - Trois millisecondes

**40 minutes · en binôme · sur machine**

## Étape 0 - Le point de départ *(5 min)*

`charger redis` (un Top propre). Le site est sur `TOP=mongo`. Rechargez
l'accueil trois fois, notez le temps « calculé en ». Puis :

```bash
docker compose exec web python -m outils.samedi_soir --clients 60
```

Soixante clients : le vrai samedi soir. Notez le p95 et les requêtes par
seconde. C'est la référence à battre.

## Étape 1 - Deux fonctions *(12 min)*

Dans `app/stockage/redis_.py` : `noter_ecoute` (un `ZINCRBY`) et
`top_semaine` (un `ZREVRANGE ... WITHSCORES`, converti en liste de tuples,
scores en entiers). La docstring dit tout.

`.env` : `TOP=redis`. `docker compose up -d web`. L'accueil affiche le même
podium. Le temps « calculé en » ?

## Étape 2 - Le Top bouge *(8 min)*

Connecté comme `u17`, écoutez `a201` (le cinquième) trois fois. Rechargez
l'accueil : il a bougé ? Dans `redis-cli`, `ZSCORE ondine:top:semaine a201`.

Puis regardez `docker compose logs --tail 20 web` : combien de temps prend
un `POST /contenu/{id}/ecouter` ? Il fait maintenant **deux** écritures
(Mongo et Redis). Une phrase : et si la seconde échoue ?

## Étape 3 - Soixante clients *(10 min)*

Le samedi soir à 60 clients, `TOP=redis`. Les deux p95 côte à côte, les deux
débits. Puis, dans `redis-cli` : `INFO stats` et la ligne
`total_commands_processed` - avant et après un second samedi soir.

★ Le p95 a peu bougé. Qu'a-t-on gagné, alors ? Deux phrases, avec les mots
*MongoDB* et *pour rien*.

## Étape 4 - Lundi matin ★ *(5 min)*

Le sorted set s'appelle `ondine:top:semaine`. Lundi 4 h du matin, la semaine
change. ★ Que doit-il se passer, et qui le fait ? Proposez une solution avec
une clé par jour et `ZUNIONSTORE` - trois lignes, pas de code.

---

# Mission 4 - Le cache ment

**45 minutes · en binôme · sur machine**

## Étape 0 - Le prix de la fiche *(4 min)*

`CACHE=aucun`. Ouvrez la fiche `a001` trois fois. La ligne « page composée
en » : notez le temps, et celui de « aussi écouté ». C'est la recommandation
MongoDB (le pipeline à `$lookup`) qui coûte - à chaque visite, pour tout le
monde, alors qu'elle ne change pas d'une minute à l'autre.

## Étape 1 - Trois fonctions *(12 min)*

Dans `redis_.py` : `lire` (GET, `json.loads`, et le compteur de succès ou
d'échec dans le hash `CLE_STATS`), `ecrire` (`json.dumps` avec `default=_json`,
SET avec `ex=`), et `supprimer` - **laissez-la vide** pour l'instant.

`.env` : `CACHE=redis`. Ouvrez `a001` trois fois. Le temps « page composée
en » et la mention « servie du cache ». Le compteur « succès / échecs ».

## Étape 2 - Vous êtes l'application *(8 min)*

Dans `redis-cli` : `GET ondine:fiche:a001`, `TTL ondine:fiche:a001`. Lisez le
JSON : tout y est, avis compris.

Ouvrez vingt fiches différentes au hasard (le catalogue), puis `DBSIZE` et le
compteur succès / échecs. ★ Calculez le taux de succès. Un samedi soir,
qu'est-ce qui le fait monter ?

## Étape 3 - Le cache ment ★ *(9 min)*

Connecté comme `u17`, publiez un avis sur `a001` : « le cache ment ». La page
se recharge. **Votre avis n'y est pas.** Rechargez. Toujours pas. Dans
`redis-cli`, `TTL ondine:fiche:a001` : voilà combien de temps il n'y sera pas.

★ Écrivez le ticket du support (deux lignes), puis l'explication technique
en trois phrases avec les mots *copie*, *TTL* et *écriture*. Comparez avec
« je ne vois pas ma propre écriture » du chapitre 1 - la lecture sur une copie
en retard : même symptôme, cause différente - laquelle ?

## Étape 4 - Invalider *(8 min)*

Ouvrez `app/main.py`, fonction `_invalider` : le site **appelle déjà**
`supprimer` après chaque avis et chaque écoute. Écrivez `supprimer` (une
ligne). Publiez un nouvel avis : il est là.

★ Deux stratégies restaient possibles (attendre, réécrire). Une phrase sur
ce que chacune aurait coûté, et pourquoi `DEL` gagne ici.

## Étape 5 - Le samedi soir *(4 min)*

Soixante clients, `TOP=redis`, `CACHE=redis`. Le p95, le débit, et dans
`redis-cli` le taux de succès du cache après la charge.

---

# Mission 5 - La mémoire courte

**35 minutes · en binôme · sur machine**

## Étape 0 - L'inventaire *(4 min)*

`DBSIZE`, `ZCARD ondine:top:semaine`, `HGETALL ondine:cache:stats`. Notez.
Puis, connecté, écoutez trois titres : ils sont dans le Top.

## Étape 1 - Arracher la prise ★ *(8 min)*

```bash
docker compose exec redis rm -f /data/dump.rdb    # aucune sauvegarde de secours
docker kill ondine-redis                          # pas un arrêt : une panne
docker compose start redis
docker compose exec redis redis-cli DBSIZE
```

Ouvrez l'accueil. Ouvrez une fiche. Ouvrez **Moi**.

★ Pour chaque page : ce qu'elle affiche, si c'est une erreur ou un mensonge,
et d'où vient ce qu'elle affiche. Laquelle vous inquiète le plus ?

## Étape 2 - Rejouer *(6 min)*

```bash
docker compose exec web python -m donnees.charger redis
```

Le Top est de retour, en une seconde - **mais pas vos trois écoutes de
l'étape 0**. Où sont-elles ? Retrouvez-les dans MongoDB (`db.ecoutes`, triées
par date). Une phrase : pourquoi le Top rejoué ne les compte pas, alors que
la source de vérité les a.

## Étape 3 - Le journal *(12 min)*

Dans `.env` : `REDIS_AOF=yes`. Puis `docker compose up -d redis` (le conteneur
est recréé avec le journal), `charger redis`, trois écoutes, et :

```bash
docker kill ondine-redis
docker compose start redis
docker compose exec redis redis-cli ZCARD ondine:top:semaine
docker compose exec redis ls -la /data/appendonlydir
```

Tout est là. ★ Qu'a coûté chaque `ZINCRBY` depuis que le journal est allumé ?
Pour le Top 50 - rejouable depuis MongoDB en une seconde - le journal
vaut-il son prix ? Et pour un compteur de vues que personne ne sait
recalculer ?

## Étape 4 - Nettoyage *(5 min)*

Remettez `REDIS_AOF=no`, `docker compose up -d redis`, `charger redis`. Une
ligne dans le journal : la règle du chapitre, dans vos mots.

---

# Mission 6 - Où Redis gagne

**15 minutes · en binôme · papier**

## Contexte

> **De :** Léa · **Objet :** quatre demandes, une réponse chacune
>
> Pour chaque besoin : Redis ou pas ? Si oui : quelle structure, quelle clé,
> et ce qui se passe si Redis tombe un samedi soir. Si non : où, alors ?

1. Le nombre de personnes **en train d'écouter** en ce moment (affiché sur
   l'accueil, rafraîchi toutes les dix secondes).
2. La liste des **contenus de jazz sortis en 2026**.
3. « **Reprendre l'écoute** » : la position, en secondes, dans le dernier
   titre écouté par chaque utilisateur.
4. Un **verrou** : une seule instance du script « Top de la semaine » doit
   tourner à la fois, même si on le lance deux fois.

★ Pour la 3 et la 4 : que se passe-t-il exactement si Redis tombe, et
est-ce acceptable ? Une phrase chacune.
