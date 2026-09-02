"""Ondine et Neo4j - « les auditeurs ont aussi écouté » (chapitre 4).

Un seul rôle : RECO=neo4j. Le graphe contient les mêmes écoutes que les
autres bases - une arête A_ECOUTE par écoute, avec sa date - et la
recommandation est un motif de deux sauts :

    (X)<-[:A_ECOUTE]-(quelqu'un)-[:A_ECOUTE]->(autre chose)

Comparez avec l'auto-jointure SQL et le pipeline MongoDB : même question,
même fenêtre, trois textes.
"""
from __future__ import annotations

from datetime import datetime

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable

from app import config
from app.stockage import BaseIndisponible

_pilote = None


def pilote():
    global _pilote
    if _pilote is None:
        _pilote = GraphDatabase.driver(config.NEO4J_URL, connection_timeout=3)
    return _pilote


def requete(cypher: str, **params) -> list[dict]:
    try:
        with pilote().session() as s:
            return [r.data() for r in s.run(cypher, **params)]
    except (ServiceUnavailable, Neo4jError, OSError) as e:
        raise BaseIndisponible(f"Neo4j ({config.NEO4J_URL}) : {e}") from e


# ==================================================================== reco

def aussi_ecoute(contenu_id: str, depuis: datetime, jusqua: datetime, n: int = 5) -> list[tuple[str, int]]:
    lignes = requete("""
        MATCH (c:Contenu {id: $id})<-[e1:A_ECOUTE]-(u:Utilisateur)-[e2:A_ECOUTE]->(autre:Contenu)
        WHERE autre <> c
          AND e1.date >= $depuis AND e1.date < $jusqua
          AND e2.date >= $depuis AND e2.date < $jusqua
        RETURN autre.id AS id, count(DISTINCT u) AS fans
        ORDER BY fans DESC, id
        LIMIT $n
    """, id=contenu_id, depuis=depuis, jusqua=jusqua, n=n)
    return [(l["id"], l["fans"]) for l in lignes]
