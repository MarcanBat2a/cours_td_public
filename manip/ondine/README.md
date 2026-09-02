# Ondine

Ondine est un petit service de streaming : albums, podcasts, livres audio,
concerts filmés. Quatre cents contenus, soixante utilisateurs, cent vingt mille
écoutes. Le site tourne sur PostgreSQL, et il rame le samedi soir.

Vous venez d'être embauché. Tom, qui avait tout écrit, est parti. Ce dépôt est
ce qu'il a laissé - et c'est ce que vous allez transformer, chapitre après
chapitre, jusqu'à ce que le samedi soir passe.

## Démarrer

Il faut [Docker Desktop](https://www.docker.com/products/docker-desktop/), et
rien d'autre : Python tourne dans un conteneur.

```bash
docker compose up -d                                  # le site + PostgreSQL
docker compose exec web python -m donnees.charger sql # les données de Tom
```

Le site : <http://localhost:8000>. Connectez-vous (n'importe quel compte, il n'y
a pas de mot de passe), écoutez quelque chose, regardez la page **État**.

Si le port 8000 est pris sur votre machine, changez `ONDINE_PORT` dans `.env`.

## Ce qu'il y a dedans

```
.env                    QUI STOCKE QUOI - le fichier que vous modifiez à chaque chapitre
docker-compose.yml      le site et toutes les bases, chacune derrière un profil
app/main.py             les pages du site (elles ne parlent à aucune base directement)
app/stockage/           un module par base : sql.py, mongo.py, redis_.py, neo4j_.py, cassandra_.py
donnees/generer.py      le jeu de données - toujours le même, sur toutes les machines
donnees/charger.py      « nouvelle partie » : remplit une base depuis zéro
outils/samedi_soir.py   le boss de fin de niveau : 20 clients, 20 secondes, un verdict
cluster/                les scripts qui lèvent les clusters de TD (replica set, anneau, shards)
```

Le code est monté dans le conteneur : vous éditez sur votre machine, le serveur
se recharge tout seul.

## Les gestes du quotidien

```bash
docker compose ps                                     # qui tourne
docker compose logs -f web                            # une ligne par requête, avec son temps
docker compose exec web python -m outils.samedi_soir  # le verdict
docker compose exec pg psql -U ondine                 # un shell SQL
docker compose exec mongo mongosh --quiet ondine      # un shell MongoDB
docker compose exec redis redis-cli                   # un shell Redis
docker compose exec cassandra cqlsh ondine            # un shell CQL
docker compose --profile '*' down                     # tout arrêter (les données restent)
docker compose --profile '*' down -v                  # tout arrêter ET tout effacer
```

Chaque base a son profil dans `docker-compose.yml` : `--profile mongo`,
`--profile redis`, `--profile graphe`, `--profile colonne`. Les profils
s'additionnent. Neo4j dessine son graphe sur <http://localhost:7474>.

## Changer de base

Tout se passe dans `.env` :

```
CATALOGUE=sql      # contenus, avis, utilisateurs, playlists   sql | mongo
TOP=sql            # le Top 50 de la semaine                   sql | mongo | redis
HISTORIQUE=sql     # les écoutes                                sql | mongo | cassandra
RECO=sql           # « aussi écouté »                           sql | mongo | neo4j
CACHE=aucun        # le cache des fiches                        aucun | redis
```

Puis `docker compose up -d web`. La page État confirme.

Une fonction pas encore écrite affiche « C'est à vous » avec le nom du fichier
et de la mission : c'est normal, c'est le TD.

## L'horloge

Ondine vit le **21 décembre 2026 à midi**, et avance à partir de là au rythme
réel depuis le démarrage du serveur. Le jeu de données est figé à cette date
pour que les corrigés annoncent des chiffres exacts ; vos écoutes tombent
quand même dans « la semaine en cours ». Ne cherchez pas la date du jour
dans les données.
