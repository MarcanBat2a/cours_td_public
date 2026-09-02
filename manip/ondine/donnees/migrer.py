"""La migration : PostgreSQL → MongoDB, pour de vrai (chapitre 2, mission 3).

    docker compose exec web python -m donnees.migrer

Lit les tables de Tom, replie les 61 colonnes en documents, et écrit dans
MongoDB. C'est le script qu'Ondine exécutera une fois, la nuit de la bascule.

Ce qui est à vous : `document_contenu` (la partie qui compte) et l'imbrication
des playlists dans `document_utilisateur`. Le reste est écrit : la copie des
avis et des écoutes n'a rien à vous apprendre.

Les choix de modèle sont ceux de la mission 1 - vos trois documents sur
papier. Si vous hésitez, relisez-les avant d'écrire une ligne.
"""
from __future__ import annotations

from datetime import date, datetime

import psycopg
from psycopg.rows import dict_row
from pymongo import MongoClient

from app import config


def _dt(d):
    """MongoDB n'a pas de date sans heure : une date devient un datetime à minuit."""
    if isinstance(d, datetime) or d is None:
        return d
    return datetime(d.year, d.month, d.day)


def document_contenu(ligne: dict) -> dict:
    """Une ligne de 61 colonnes → un document.

    `ligne` est un dictionnaire : ligne["titre"], ligne["album_piste_3_titre"]...
    Les 61 clés sont celles de la table (docker compose exec pg psql -U ondine
    -c '\\d contenus' pour les voir).

    À faire :
      1. les champs communs à la racine ;
      2. `genres` : une chaîne « jazz,folk » → une liste. Si elle est NULL,
         PAS de champ (n'inventez pas de null - la mission 6 vous dira pourquoi) ;
      3. `details` : les attributs du type, et seulement eux ;
      4. pour un album, les pistes en TABLEAU de {no, titre, duree_s} - seules
         les colonnes non NULL sont des pistes.
    """
    doc = {
        "_id": ligne["id"], "titre": ligne["titre"], "type": ligne["type"],
        # ... à compléter
    }
    # TODO mission 3 : genres, langue, import_source (absents si NULL)

    # TODO mission 3 : details, selon ligne["type"]
    doc["details"] = {}
    return doc


def document_utilisateur(u: dict, playlists: list[dict]) -> dict:
    """`playlists` est une liste de {id, nom, creee_le, contenus: [ids]}.
    À faire : les imbriquer dans le document utilisateur (mission 1, partie B)."""
    return {"_id": u["id"], "pseudo": u["pseudo"], "email": u["email"], "ville": u["ville"],
            "inscrit_le": u["inscrit_le"], "abonnement": u["abonnement"],
            # TODO mission 3 : "playlists": [...]
            }


def migrer() -> None:
    pg = psycopg.connect(config.PG_DSN, row_factory=dict_row)
    mongo = MongoClient(config.MONGO_URL, serverSelectionTimeoutMS=5000)
    mongo.drop_database(config.MONGO_BASE)
    b = mongo[config.MONGO_BASE]

    with pg.cursor() as cur:
        cur.execute("SELECT * FROM contenus ORDER BY id")
        b.contenus.insert_many([document_contenu(l) for l in cur])
        print(f"  contenus       {b.contenus.count_documents({}):>7}")

        cur.execute("SELECT * FROM utilisateurs ORDER BY id")
        utilisateurs = cur.fetchall()
        docs = []
        for u in utilisateurs:
            cur.execute("SELECT id, nom, creee_le FROM playlists WHERE utilisateur_id = %s ORDER BY id", (u["id"],))
            playlists = cur.fetchall()
            for p in playlists:
                cur.execute("SELECT contenu_id FROM playlist_contenus WHERE playlist_id = %s ORDER BY position", (p["id"],))
                p["contenus"] = [l["contenu_id"] for l in cur]
            docs.append(document_utilisateur(u, playlists))
        b.utilisateurs.insert_many(docs)
        print(f"  utilisateurs   {len(docs):>7}")

        cur.execute("SELECT a.*, u.pseudo FROM avis a JOIN utilisateurs u ON u.id = a.utilisateur_id ORDER BY a.id")
        b.avis.insert_many([{"_id": a["id"], "contenu_id": a["contenu_id"],
                             "utilisateur": {"id": a["utilisateur_id"], "pseudo": a["pseudo"]},
                             "note": a["note"], "texte": a["texte"], "date": a["date"]} for a in cur])
        print(f"  avis           {b.avis.count_documents({}):>7}  (collection référencée)")

        cur.execute("SELECT utilisateur_id, contenu_id, date, plateforme, duree_ecoutee_s FROM ecoutes ORDER BY id")
        paquet, n = [], 0
        for e in cur:
            paquet.append(dict(e))
            if len(paquet) == 10000:
                b.ecoutes.insert_many(paquet, ordered=False)
                n += len(paquet)
                paquet = []
        if paquet:
            b.ecoutes.insert_many(paquet, ordered=False)
            n += len(paquet)
        print(f"  ecoutes        {n:>7}")
    print("Migration terminée. Dans .env : CATALOGUE=mongo, puis docker compose up -d web")


if __name__ == "__main__":
    migrer()
