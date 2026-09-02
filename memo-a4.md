# Mémo - la matière de votre A4

**UE 1 - Persistance & Systèmes Distribués (NoSQL) · Chapitre 3**
Distribué en fin de séance 1 · à garder sous la main pendant toutes les missions

> Ce mémo récapitule toute la syntaxe du chapitre : pendant les séances, il
> vous évite de fouiller le deck. En fin de chapitre, il rejoint la matière de
> votre **feuille A4 manuscrite** autorisée à l'épreuve, à côté du tableau
> C ou A du chapitre 1 et des trois questions de modélisation du chapitre 2.
>
> **Recopiez-le à la main.** Une antisèche photocopiée ne se retrouve pas
> sous stress - une antisèche écrite, si.

## Les clés

```text
ondine:session:u17        convention application:objet:id, séparateur :
```

| | |
| --- | --- |
| `SET cle val` | écrit - **remplace sans prévenir** |
| `SET cle val NX` | seulement si la clé est absente - refus = `(nil)` |
| `GET` · `DEL` · `EXISTS` | lire · supprimer · tester |
| `GET` d'une clé absente | `(nil)` - **pas une erreur** : le zéro-résultat du chapitre 2 |
| `DBSIZE` | le nombre de clés |
| `SCAN 0 MATCH motif` | parcourir les clés par paquets |
| `KEYS *` | jamais en production : bloque le serveur (mono-thread) |

**La clé est le seul chemin** : aucune requête sur les valeurs. Filtrer,
chercher « ce qui contient » = le métier de MongoDB, pas de Redis.

## Les cinq structures

| Le besoin dit... | Structure | Commandes |
| --- | --- | --- |
| compter, à plusieurs | **String** | `INCR` · `INCRBY` - atomique : mono-thread, une commande entière |
| objet plat, retouché champ par champ | **Hash** | `HSET h champ val` · `HGET` · `HGETALL` · `HINCRBY` |
| les N derniers, dans l'ordre | **List** | `LPUSH` (en tête) · `LTRIM 0 9` (la borne) · `LRANGE 0 -1` · `LLEN` |
| déjà vu ? (sans doublon, sans ordre) | **Set** | `SADD` · `SISMEMBER` · `SCARD` |
| classement à score mouvant | **Sorted set** | `ZINCRBY cle 1 membre` · `ZREVRANGE 0 49 WITHSCORES` · `ZSCORE` · `ZREVRANK` · `ZCARD` |

À gauche du tableau du cours, on **calcule** à la lecture ; ici, on
**maintient** à l'écriture, et la lecture est immédiate. Quand on lit mille
fois plus qu'on écrit, on paie à l'écriture.

- `LPUSH` + `LTRIM` : l'anti-patron du tableau qui grossit (chapitre 2),
  résolu par la structure.
- `ZINCRBY` n'est **pas idempotent** : rejouer un journal double les scores.
  D'où le `DEL` avant un rejeu (`charger redis`).
- Une session en chaîne JSON : à éviter - retouche = réécriture intégrale, et
  deux écrivains s'écrasent (le `replaceOne` du chapitre 2). `HSET` retouche
  un champ, atomiquement.

## L'expiration

| | |
| --- | --- |
| `SET cle val EX 60` | naît avec 60 s à vivre |
| `EXPIRE cle 1800` | poser une échéance |
| `TTL cle` | secondes restantes · `-1` = sans échéance · `-2` = la clé n'existe pas (ou plus) |

## Le cache

```text
page = cache.lire(cle)                     GET
si None : page = composer (la base)        ← 120 ms
          cache.ecrire(cle, page, 60)      SET ... EX 60
répondre page                              ← 0,4 ms
```

**Cache-aside** : l'application fait tout ; la base reste la source de
vérité ; Redis n'a qu'une copie, avec une date de péremption.

- **Taux de succès** : succès / (succès + échecs). Il monte quand tout le
  monde lit les mêmes fiches - le samedi soir.
- **Le TTL est une fenêtre de mensonge** : la copie reste fausse jusqu'à
  l'expiration. Toujours **borner** : « jusqu'à 60 s », jamais « pour
  toujours ».
- Même symptôme que la copie en retard du chapitre 1 (« je ne vois pas mon
  avis »), cause différente : un retard rattrape tout seul ; une copie en
  cache, jamais avant son TTL.

| Stratégie | Coût | Reste faux pendant |
| --- | --- | --- |
| **attendre** le TTL | rien | jusqu'à 60 s |
| **invalider** à l'écriture (`DEL`) | une ligne dans le code de l'écriture ; un chemin oublié = bug silencieux | 0 s |
| **réécrire** à l'écriture | recalculer à chaque écriture, même si personne ne lit | 0 s |

## La panne

| Réglage | Ce qui survit | Prix |
| --- | --- | --- |
| rien (`save ""`) | rien | aucun |
| snapshot (RDB) | l'état d'il y a N minutes | un fichier de temps en temps |
| journal (AOF, `appendonly yes`) | tout, à la seconde près | une écriture disque par commande |

La règle : **une donnée dont Redis est la seule copie doit avoir été voulue
comme telle.** Un cache, un Top rejouable depuis MongoDB : Redis peut
mourir. Un compteur que personne ne sait recalculer : AOF, ou pas dans Redis.

## La grille du chapitre

1. **Qui est la source de vérité ?** Jamais Redis, par défaut.
2. **Que coûte une perte ?** rien (rejouable) · un agacement · irréparable.
3. **Que coûte le périmé, et combien de temps ?** c'est le choix du TTL.
4. **Quelle structure fait le travail toute seule ?** si l'application
   refait le tri ou le compte, c'est la mauvaise.

## Dans le site - redis-cli → redis-py

`client()` est le client Redis de `app/stockage/redis_.py`. Les commandes
gardent leur nom, en minuscules.

| redis-cli | redis-py |
| --- | --- |
| `SET cle valeur EX 60` | `client().set(cle, valeur, ex=60)` |
| `SET cle valeur NX` | `client().set(cle, valeur, nx=True)` → `True` ou `None` |
| `GET cle` | `client().get(cle)` → `None` si absent |
| `DEL cle` | `client().delete(cle)` |
| `INCR cle` · `INCRBY cle 10` | `client().incr(cle)` · `client().incr(cle, 10)` |
| `HSET cle champ valeur` · `HGETALL cle` | `client().hset(cle, champ, valeur)` · `client().hgetall(cle)` |
| `HINCRBY cle champ 1` | `client().hincrby(cle, champ, 1)` |
| `LPUSH cle v` · `LTRIM cle 0 9` · `LRANGE cle 0 -1` | `lpush` · `ltrim(cle, 0, 9)` · `lrange(cle, 0, -1)` |
| `ZINCRBY cle 1 membre` | `client().zincrby(cle, 1, membre)` |
| `ZREVRANGE cle 0 49 WITHSCORES` | `client().zrevrange(cle, 0, 49, withscores=True)` → liste de `(membre, score)` |
| `EXPIRE cle 1800` · `TTL cle` | `client().expire(cle, 1800)` · `client().ttl(cle)` |

Une fiche en cache est du **JSON** : `json.dumps(page, default=_json)` pour
écrire (les dates deviennent des chaînes), `json.loads(brut)` pour lire.
