# Démarrer Panique au Pop-up

Cet atelier fait tourner trois MongoDB 7.0 en replica set, Elasticsearch
8.19.22 et le site des missions. Les requêtes du site et celles de Compass
ou Elasticvue utilisent les mêmes bases.

Toutes les commandes Docker de cette page se tapent dans un terminal
sur votre poste, **depuis le dossier `manip/`**. Sous Windows, utilisez
PowerShell. Lancez Docker Desktop avant de commencer.

Pour passer depuis l'autre TD du chapitre, exportez vos réponses et
arrêtez d'abord ses conteneurs avec `docker compose down`, depuis son
dossier `manip/`, puis changez de branche. Les deux environnements
utilisent les mêmes noms Docker et se lancent l'un après l'autre.

## Le premier démarrage

Depuis la racine du dépôt :

```bash
git switch tp/ue1-02-orientees-documents-popup
cd manip
docker compose up -d --build
docker compose logs -f atelier
```

Attendez cette ligne :

```text
Atelier prêt : http://localhost:8000
```

Ctrl+C quitte l'affichage des journaux ; il laisse les serveurs en marche.
Ouvrez ensuite [http://localhost:8000](http://localhost:8000).
La première préparation télécharge les images, forme le replica set et
charge les données. Les démarrages suivants utilisent les volumes existants.

Pour vérifier les services :

```bash
docker compose ps
```

## Les données de départ

| Ensemble | Contenu | Utilisation |
| --- | --- | --- |
| MongoDB `cours` | 7 produits, 4 commandes, 4 avis | missions lisibles et comparaison avec le cours |
| MongoDB `boutique` | 20 000 produits, 20 000 clients, 50 000 commandes, plus de 100 000 avis | diagnostic d'import et indexation |
| Elasticsearch `catalogue` | copie initiale de `cours.produits` | recherche et analyse du texte |

Le grand catalogue utilise une graine fixe : chaque poste retrouve les
mêmes documents. Ses défauts font partie des exercices. La copie
Elasticsearch reçoit les changements par **synchronisation manuelle**
depuis le site. Le bouton de rafraîchissement Elasticsearch ne copie
aucune donnée depuis MongoDB.

## Se connecter avec Compass

Ajoutez une connexion MongoDB avec cette URI :

```text
mongodb://localhost:27018/?directConnection=true
```

Les bases `cours` et `boutique` deviennent accessibles après le chargement.
Le port publié par défaut est **27018**, pour laisser le port habituel
27017 disponible à un autre MongoDB déjà présent sur le poste.

Pour une lecture, ouvrez la collection puis renseignez les champs
Filter, Project et Sort. Pour les pipelines, utilisez l'onglet
Aggregations. Dans ces champs, ne collez pas l'enveloppe `{ "filter": ... }`
du site : collez seulement la valeur du champ correspondant.

Pour une commande comme `updateMany` avec un pipeline, ouvrez le shell
intégré via le bouton `>_`, puis choisissez la base avec `use boutique`
ou `use cours`. Il reçoit des commandes JavaScript comme
`db.produits.updateMany(...)`. La disposition du bouton dépend de la
version de Compass.
[Documentation officielle : shell intégré](https://www.mongodb.com/docs/compass/embedded-shell/).

La connexion directe vise `mongo-a`, primaire initial et favorisé lors
des élections. Les expériences de panne font partie de l'autre TD,
sur la branche MongoDB d'approfondissement.

## Se connecter avec Elasticvue

Dans Elasticvue Desktop, ajoutez un cluster :

| Champ | Valeur |
| --- | --- |
| Nom | `Pop-up local` |
| URL | `http://localhost:9200` |
| Authentification | aucune |

Utilisez la vue REST pour indiquer la méthode, le chemin et le corps JSON.
Par exemple, `GET /catalogue/_mapping` lit le mapping ; son corps peut
rester vide. La vue des indices permet d'inspecter `catalogue`.
La version Desktop est disponible sur le
[site officiel d'Elasticvue](https://elasticvue.com/installation/).

Si vous préférez Elasticvue dans le navigateur, l'atelier propose un
conteneur facultatif :

```bash
docker compose --profile outils up -d elasticvue
```

Ouvrez [http://localhost:8080](http://localhost:8080), puis ajoutez le même
cluster `http://localhost:9200`. La configuration de l'atelier autorise
l'accès depuis cette interface locale.

## Réinitialiser une expérience

Depuis `manip/`, vous pouvez recharger seulement le petit jeu :

```bash
docker compose exec atelier python charger.py cours
```

Cela efface les modifications, les index ajoutés et les validateurs de
la base `cours`. **Synchronisez ensuite le catalogue dans le site** pour
remettre aussi la copie Elasticsearch au même état.

Pour retrouver les prix en texte et supprimer les index créés sur le
grand catalogue :

```bash
docker compose exec atelier python charger.py boutique
```

Pour recharger les deux bases MongoDB :

```bash
docker compose exec atelier python charger.py
```

Les notes du journal restent dans votre navigateur : une remise à zéro
des bases ne constitue pas un export des réponses et ne remet pas
nécessairement votre progression à zéro.

## Si le lancement bloque

| Symptôme | Vérification |
| --- | --- |
| le site ne s'ouvre pas encore | attendre la ligne de disponibilité dans `docker compose logs -f atelier` |
| un conteneur s'arrête | consulter `docker compose ps`, puis `docker compose logs atelier` ou `docker compose logs elasticsearch` |
| Compass ne se connecte pas | vérifier le port 27018, `directConnection=true` et le chargement terminé |
| Elasticsearch ne répond pas | vérifier `http://localhost:9200` et les journaux du service `elasticsearch` |
| un port est occupé | consulter le nom du port dans l'erreur ; ne pas arrêter un autre service pour le libérer |
| les résultats ne ressemblent plus au départ | recharger la base concernée, puis synchroniser si `cours` a changé |

Pour changer le port MongoDB publié, créez dans `manip/` un fichier `.env`
contenant, par exemple, `MONGO_PORT=27019`, puis relancez
`docker compose up -d --build`. Adaptez ensuite le port dans l'URI
Compass. Le réseau Docker interne garde son propre port MongoDB 27017.

## Les outils supplémentaires

Des shells et des scripts MongoDB sont aussi disponibles dans cet
atelier. Le [TD d'approfondissement](https://github.com/MarcanBat2a/cours_td_public/tree/tp/ue1-02-orientees-documents)
utilise ces outils dans son propre environnement, sur l'autre branche.

| Terminal | Commande pour l'ouvrir depuis `manip/` |
| --- | --- |
| mongosh sur le primaire initial | `docker compose exec mongo-a mongosh boutique` |
| scripts Python de l'atelier | `docker compose exec atelier bash` |
| mongosh sur un secondaire | `docker compose exec mongo-b mongosh boutique` ou la même commande avec `mongo-c` |

Dans mongosh, `use cours` et `use boutique` changent de base. Pour quitter
un shell, tapez `exit`.

| Fichier | Rôle |
| --- | --- |
| `compose.yaml` | serveurs, ports et réseaux de l'atelier |
| `atelier/generer.py` | grand catalogue déterministe et anomalies |
| `atelier/jeu_cours.py` | documents du petit jeu |
| `atelier/charger.py` | rechargement des bases MongoDB |
| `atelier/vente_flash.py` | concurrence entre cinquante acheteurs |
| `atelier/ecrire_en_continu.py` | caisse pendant une panne |
| `atelier/verifier_ecritures.py` | comparaison du carnet de la caisse avec la base |

## Arrêter et reprendre

Cliquez sur **Exporter mon carnet**, puis sur **Télécharger reponses.md**
avant de quitter. Pour arrêter les serveurs et
conserver leurs données :

```bash
docker compose down
```

Pour effacer les données Docker, puis repartir de l'état initial au
prochain démarrage :

```bash
docker compose down -v
```

Les notes du site sont enregistrées dans le stockage local du navigateur.
Les volumes Docker et ces notes sont deux stockages séparés.
