"""Construit le graphe d'Ondine dans Neo4j (chapitre 4).

    docker compose exec web python -m donnees.charger neo4j

Ce que le graphe contient, et d'où ça vient :

    (:Utilisateur)    60     id, pseudo, ville
    (:Contenu)        400    id, titre, type
    (:Artiste)        ~50    nom
    (:Genre)          ~30    nom
    [:PAR]            contenu → artiste
    [:DANS_GENRE]     contenu → genre (les 32 albums du CSV n'en ont pas)
    [:A_ECOUTE]       utilisateur → contenu, UNE arête PAR écoute, avec sa
                      date et sa plateforme : 120 000 arêtes, les mêmes
                      écoutes que partout ailleurs
    [:A_AIME]         utilisateur → contenu, depuis les avis notés 4 ou 5
    [:SUIT]           utilisateur → utilisateur, le réseau social d'Ondine

Le premier ordre DÉTRUIT le graphe existant. Comptez une minute : les
120 000 arêtes partent par paquets de 5 000.
"""
from __future__ import annotations

from neo4j import GraphDatabase

from app import config


def charger(d: dict) -> None:
    pilote = GraphDatabase.driver(config.NEO4J_URL)
    with pilote.session() as s:
        def run(cypher, **p):
            return s.run(cypher, **p).consume()

        # Terrain rasé, par paquets (un DELETE de 120 000 arêtes d'un coup
        # peut dépasser la mémoire bornée du conteneur).
        while True:
            r = s.run("MATCH (n) WITH n LIMIT 20000 DETACH DELETE n RETURN count(*) AS n").single()
            if r["n"] == 0:
                break
        for etiquette, prop in (("Utilisateur", "id"), ("Contenu", "id"), ("Artiste", "nom"), ("Genre", "nom")):
            run(f"CREATE CONSTRAINT {etiquette.lower()}_{prop} IF NOT EXISTS "
                f"FOR (x:{etiquette}) REQUIRE x.{prop} IS UNIQUE")

        run("UNWIND $l AS r CREATE (:Utilisateur {id: r.id, pseudo: r.pseudo, ville: r.ville})",
            l=[{"id": u["id"], "pseudo": u["pseudo"], "ville": u["ville"]} for u in d["utilisateurs"]])
        run("UNWIND $l AS r CREATE (:Contenu {id: r.id, titre: r.titre, type: r.type})",
            l=[{"id": c["id"], "titre": c["titre"], "type": c["type"]} for c in d["contenus"]])
        artistes = sorted({c["artiste"] for c in d["contenus"]})
        run("UNWIND $l AS nom CREATE (:Artiste {nom: nom})", l=artistes)
        genres = sorted({g for c in d["contenus"] for g in (c["genres"] or [])})
        run("UNWIND $l AS nom CREATE (:Genre {nom: nom})", l=genres)
        print(f"  nœuds          {len(d['utilisateurs'])} utilisateurs, {len(d['contenus'])} contenus, "
              f"{len(artistes)} artistes, {len(genres)} genres")

        run("UNWIND $l AS r MATCH (c:Contenu {id: r.c}), (a:Artiste {nom: r.a}) CREATE (c)-[:PAR]->(a)",
            l=[{"c": c["id"], "a": c["artiste"]} for c in d["contenus"]])
        run("UNWIND $l AS r MATCH (c:Contenu {id: r.c}), (g:Genre {nom: r.g}) CREATE (c)-[:DANS_GENRE]->(g)",
            l=[{"c": c["id"], "g": g} for c in d["contenus"] for g in (c["genres"] or [])])

        aime = {}
        for a in d["avis"]:
            if a["note"] >= 4:
                cle = (a["utilisateur_id"], a["contenu_id"])
                aime[cle] = max(aime.get(cle, 0), a["note"])
        run("UNWIND $l AS r MATCH (u:Utilisateur {id: r.u}), (c:Contenu {id: r.c}) CREATE (u)-[:A_AIME {note: r.note}]->(c)",
            l=[{"u": u, "c": c, "note": n} for (u, c), n in sorted(aime.items())])
        run("UNWIND $l AS r MATCH (u:Utilisateur {id: r.u}), (v:Utilisateur {id: r.v}) CREATE (u)-[:SUIT]->(v)",
            l=[{"u": u, "v": v} for u, v in d["suit"]])
        print(f"  arêtes         PAR, DANS_GENRE, {len(aime)} A_AIME, {len(d['suit'])} SUIT")

        ecoutes = d["ecoutes"]
        for i in range(0, len(ecoutes), 5000):
            paquet = [{"u": e["utilisateur_id"], "c": e["contenu_id"], "date": e["date"], "p": e["plateforme"]}
                      for e in ecoutes[i:i + 5000]]
            run("UNWIND $l AS r MATCH (u:Utilisateur {id: r.u}), (c:Contenu {id: r.c}) "
                "CREATE (u)-[:A_ECOUTE {date: r.date, plateforme: r.p}]->(c)", l=paquet)
            print(f"\r  A_ECOUTE       {min(i + 5000, len(ecoutes)):>7} / {len(ecoutes)}", end="", flush=True)
        print()
        run("CREATE INDEX a_ecoute_date IF NOT EXISTS FOR ()-[e:A_ECOUTE]-() ON (e.date)")
    pilote.close()
