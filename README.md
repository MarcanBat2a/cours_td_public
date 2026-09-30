# Panique au Pop-up

**UE 1 · Chapitre 2 · Bases orientées documents**

Un TD/TP de 3 heures pour sauver l'ouverture d'une boutique : répondre à
un client, débusquer des stocks trompeurs, réparer le catalogue, calculer
les ventes et comprendre pourquoi un résultat de recherche peut mentir.
Vous écrivez vos requêtes sur de vrais serveurs MongoDB et Elasticsearch.

Travail en binômes : une personne pilote, l'autre prévoit et vérifie les
résultats. Échangez les rôles à chaque mission. Les 180 minutes annoncées
ne comprennent pas l'installation ; les bonus prolongent la séance.

Branche du chapitre : `tp/ue1-02-orientees-documents-popup`.

## Récupérer l'atelier

```bash
git clone https://github.com/MarcanBat2a/cours_td_public.git
cd cours_td_public
git switch tp/ue1-02-orientees-documents-popup
cd manip
docker compose up -d --build
docker compose logs -f atelier
```

Si vous avez déjà le dépôt, faites `git fetch origin` puis
`git switch tp/ue1-02-orientees-documents-popup` avant le démarrage.

Si un autre TD du chapitre tourne déjà, exportez vos réponses et lancez
`docker compose down` depuis son dossier `manip/` **avant de changer de
branche**. Les deux environnements utilisent les mêmes noms Docker et
doivent fonctionner l'un après l'autre.

Attendez la ligne `Atelier prêt : http://localhost:8000`, quittez les
journaux avec Ctrl+C et ouvrez [Panique au Pop-up](http://localhost:8000).
Docker Desktop doit être lancé. Les images et les données peuvent prendre
quelques minutes à se préparer la première fois.

## Choisir son poste de travail

Le site réunit les missions, des indices, les éditeurs de requêtes et un
journal. Il envoie vos requêtes aux bases Docker. Vous pouvez aussi
utiliser Compass et Elasticvue pour inspecter et interroger les mêmes
données.

| Outil | Connexion |
| --- | --- |
| Atelier dans le navigateur | [http://localhost:8000](http://localhost:8000) |
| MongoDB Compass | `mongodb://localhost:27018/?directConnection=true` |
| Elasticvue Desktop | cluster `http://localhost:9200`, sans authentification |
| Elasticvue en conteneur, facultatif | [http://localhost:8080](http://localhost:8080), après `docker compose --profile outils up -d elasticvue` dans `manip/` |

Les consignes de connexion et le dépannage sont dans
[manip/README.md](manip/README.md).

## Deux bases, une copie de recherche

| Ensemble | Contenu | Usage |
| --- | --- | --- |
| MongoDB `cours` | 7 produits, 4 commandes, 4 avis au départ | raisonner sur des résultats lisibles |
| MongoDB `boutique` | 20 000 produits, 20 000 clients, 50 000 commandes, plus de 100 000 avis | diagnostiquer des anomalies et mesurer les lectures |
| Elasticsearch `catalogue` | copie initiale des 7 produits de `cours` | analyser les mots et construire une recherche |

La synchronisation vers Elasticsearch est **manuelle** dans cet atelier.
Rafraîchir Elasticsearch et synchroniser le catalogue sont deux actions
distinctes. La dernière mission vous fera constater la différence.

## Les documents de la séance

| Document | À quoi sert-il ? |
| --- | --- |
| [td-enonces.md](td-enonces.md) | les 8 missions, les preuves à conserver et les bonus |
| [memo-a4.md](memo-a4.md) | la syntaxe MongoDB et Elasticsearch à garder sous la main |
| [manip/README.md](manip/README.md) | démarrer, connecter les outils, remettre les données à zéro |
| [TD MongoDB complet](https://github.com/MarcanBat2a/cours_td_public/tree/tp/ue1-02-orientees-documents) | l'autre parcours, avec mongosh, les scripts de vente et les expériences de réplication |

Le TD MongoDB possède son propre énoncé et son environnement sur l'autre
branche. Il prolonge le chapitre avec les transactions et la réplication.

## Rendre son travail

Dans le journal du site, gardez les requêtes, les résultats utiles et vos
explications. Cliquez sur **Exporter mon carnet**, puis sur
**Télécharger reponses.md** en fin de séance. Le navigateur
enregistre les notes et la progression localement ; exportez aussi à la
pause pour conserver une copie.

Cocher une mission signifie que vous pensez l'avoir terminée. Le site
n'est pas un correcteur automatique : une requête exécutée sans erreur
peut répondre à la mauvaise question. Les preuves demandées dans
l'énoncé permettent à votre binôme puis à l'enseignant de vérifier le
raisonnement.

Travaillez sur votre copie et rendez les réponses par le canal annoncé
en séance. Les corrigés ne sont pas dans ce dépôt public.

Pour arrêter l'atelier en conservant les données, dans `manip/` :

```bash
docker compose down
```

Pour effacer les données Docker et repartir de zéro au prochain
démarrage : `docker compose down -v`. Cette commande n'efface pas les
notes enregistrées dans votre navigateur.
