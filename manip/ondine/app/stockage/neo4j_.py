"""Ondine et Neo4j - « les auditeurs ont aussi écouté » (chapitre 4).

Un seul rôle : RECO=neo4j. Le graphe contient les mêmes écoutes que les
autres bases - une arête A_ECOUTE par écoute, avec sa date. La
recommandation est un motif de deux sauts :

    (X)<-[:A_ECOUTE]-(quelqu'un)-[:A_ECOUTE]->(autre chose)

Squelette : la requête Cypher est à vous (mission 2). Vous l'avez déjà écrite
dans Neo4j Browser ; ici, elle est identique, avec des paramètres $id,
$depuis, $jusqua, $n.
"""
from __future__ import annotations

from datetime import datetime

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable

from app import config
from app.stockage import AFaire, BaseIndisponible

_pilote = None


def pilote():
    global _pilote
    if _pilote is None:
        _pilote = GraphDatabase.driver(config.NEO4J_URL, connection_timeout=3)
    return _pilote


def requete(cypher: str, **params) -> list[dict]:
    """Exécute du Cypher, renvoie une liste de dictionnaires (une par ligne)."""
    try:
        with pilote().session() as s:
            return [r.data() for r in s.run(cypher, **params)]
    except (ServiceUnavailable, Neo4jError, OSError) as e:
        raise BaseIndisponible(f"Neo4j ({config.NEO4J_URL}) : {e}") from e


# ==================================================================== reco

def aussi_ecoute(contenu_id: str, depuis: datetime, jusqua: datetime, n: int = 5) -> list[tuple[str, int]]:
    """Mission 2 - le double saut.

    Écrivez le MATCH : le contenu $id, les utilisateurs qui l'ont écouté
    (arête e1), et ce qu'ils ont écouté d'autre (arête e2). Excluez le contenu
    de départ (autre <> c), gardez les deux arêtes dans la fenêtre
    [$depuis, $jusqua[, comptez les personnes DISTINCTES par contenu, triez,
    limitez à $n. Renvoyez une liste de (id, fans).

        lignes = requete("MATCH ...", id=contenu_id, depuis=depuis, jusqua=jusqua, n=n)
    """
    raise AFaire("Mission 2 : aussi_ecoute() dans app/stockage/neo4j_.py")
