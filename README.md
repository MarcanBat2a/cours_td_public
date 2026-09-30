# TD MongoDB : bases orientées documents

**UE 1 · Chapitre 2 · TD d'approfondissement**

Un parcours complet sur le catalogue d'une boutique : modéliser, lire,
modifier, agréger, indexer, puis observer les transactions et la
réplication. Les requêtes se font dans mongosh et les scripts s'exécutent
dans Docker.

Branche : `tp/ue1-02-orientees-documents`.

## Récupérer le TD

```bash
git clone https://github.com/MarcanBat2a/cours_td_public.git
cd cours_td_public
git switch tp/ue1-02-orientees-documents
cd manip
docker compose up -d --build
docker compose logs -f atelier
```

Attendez `Boutique prête.`, puis quittez les journaux avec Ctrl+C.
Si vous avez déjà le dépôt, utilisez `git fetch origin` avant de changer
de branche. Docker Desktop doit être lancé.

## Le matériel

- [td-enonces.md](td-enonces.md) : les exercices et les résultats à présenter.
- [memo-a4.md](memo-a4.md) : la syntaxe à garder sous la main.
- [manip/README.md](manip/README.md) : les quatre services et les scripts de la boutique.

Le jeu `cours` contient 7 produits, 4 commandes et 4 avis. Le jeu
`boutique` contient 20 000 produits et permet de mesurer les index et de
diagnostiquer les anomalies.

## L'autre TD du chapitre

[Panique au Pop-up](https://github.com/MarcanBat2a/cours_td_public/tree/tp/ue1-02-orientees-documents-popup)
propose un atelier ludique de 3 heures, avec un site local, MongoDB et
Elasticsearch. Il se trouve sur la branche
`tp/ue1-02-orientees-documents-popup`.

Depuis `manip/`, arrêtez l'environnement courant avec `docker compose down`
avant de changer de branche et de lancer l'autre atelier.

## Rendre son travail

Gardez vos requêtes, vos observations et vos explications dans
`reponses.md`. Rendez ce fichier par le canal annoncé en séance.
Les corrigés restent sur le site du cours, ils ne sont pas dans ce dépôt
public.
