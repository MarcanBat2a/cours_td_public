# La billetterie du chapitre 1

Neuf machines Docker pour observer, sur votre poste, ce que le cours
raisonne : une double réservation, un timeout, une copie en retard, une
partition réseau, une majorité.

```bash
docker compose up -d --build     # démarrer
docker compose ps                # neuf lignes « Up »
docker compose down -v           # tout arrêter et effacer
```

Les consignes sont dans `td-enonces.md`, à la racine de la branche.

| Dossier | Contenu |
| --- | --- |
| `postgres/` | le primaire `pg-a`, sa copie `pg-b` et le schéma de la billetterie |
| `billetterie/` | le guichet web et le catalogue répliqué (Python, bibliothèque standard) |
| `compose.yaml` | les neuf machines et leurs trois réseaux |

Vous n'avez rien à modifier dans ces fichiers. Vous pouvez les lire : le
guichet (`billetterie/guichet.py`) contient la requête d'attribution
conditionnelle et la gestion de la clé d'idempotence.
