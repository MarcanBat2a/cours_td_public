"""Point d'entrée des chargeurs : remplit une base avec le jeu de données.

    docker compose exec web python -m donnees.charger sql
    docker compose exec web python -m donnees.charger mongo
    docker compose exec web python -m donnees.charger redis
    docker compose exec web python -m donnees.charger neo4j
    docker compose exec web python -m donnees.charger cassandra

Chaque chargeur DÉTRUIT ce qu'il trouve et repart du même état : c'est le
bouton « nouvelle partie ». Le jeu de données est toujours le même, quelle que
soit la base - et c'est ce qui rend les comparaisons honnêtes.
"""
from __future__ import annotations

import importlib
import sys
import time

from donnees.generer import jeu

CIBLES = ["sql", "mongo", "redis", "neo4j", "cassandra"]


def main(argv: list[str]) -> int:
    if len(argv) != 1 or argv[0] not in CIBLES:
        print(f"usage : python -m donnees.charger {' | '.join(CIBLES)}")
        return 2
    cible = argv[0]
    try:
        module = importlib.import_module(f"donnees.charger_{cible}")
    except ModuleNotFoundError:
        print(f"Pas encore de chargeur pour « {cible} » : c'est une mission d'un prochain chapitre.")
        return 1
    debut = time.perf_counter()
    print("→ génération du jeu de données…")
    d = jeu()
    print(f"→ chargement dans {cible}…")
    module.charger(d)
    print(f"Terminé en {time.perf_counter() - debut:.1f} s.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
