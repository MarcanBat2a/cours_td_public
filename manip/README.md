# La boutique du chapitre 2

Quatre machines Docker pour manipuler MongoDB sur votre poste : un
replica set de trois membres, une boutique de 20 000 produits, et un
atelier qui charge les données et porte les scripts des TD.

```bash
docker compose up -d --build      # démarrer
docker compose logs -f atelier    # attendre « Boutique prête. »
docker compose down -v            # tout arrêter et effacer
```

Les consignes sont dans `td-enonces.md`, à la racine de la branche.

| Fichier | Contenu |
| --- | --- |
| `compose.yaml` | les trois machines MongoDB, l'atelier et leurs réseaux |
| `atelier/generer.py` | le catalogue, les clients, les commandes et les avis, tirés d'une graine fixe |
| `atelier/jeu_cours.py` | les sept produits du cours, chargés dans la base `cours` |
| `atelier/charger.py` | recharge `cours`, `boutique` ou les deux |
| `atelier/vente_flash.py` | cinquante acheteurs pour dix casques (TD 4) |
| `atelier/ecrire_en_continu.py`, `verifier_ecritures.py` | une caisse qui encaisse pendant une panne (TD 8) |

Vous n'avez rien à modifier dans ces fichiers. Vous pouvez les lire : les
trois fonctions `acheter_...` de `vente_flash.py` tiennent en quelques
lignes et utilisent le pilote Python vu en cours.

Les machines n'ouvrent aucun port sur votre poste : tout se fait par
`docker compose exec`. L'ensemble occupe environ 700 Mo de mémoire.
