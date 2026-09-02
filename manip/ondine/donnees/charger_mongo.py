"""La migration : PostgreSQL → MongoDB. Le corrigé de la mission 3 du chapitre 2.

    docker compose exec web python -m donnees.charger mongo

Ce chargeur ne lit pas PostgreSQL : il part du même jeu de données que
charger_sql.py, déjà en forme de documents. La VRAIE migration - lire les
61 colonnes et les replier en documents - est celle que vous écrivez au
TD (donnees/migrer.py). Ce fichier sert ensuite de « nouvelle partie » :
il détruit la base `ondine` et la recrée, avec les index de la mission 9
du chapitre 2 déjà posés. (Au chapitre 2, la mission 8 les retire d'abord :
`db.ecoutes.dropIndexes()` - c'est vous qui les posez, pour les voir agir.)
"""
from __future__ import annotations

from datetime import date, datetime

from pymongo import MongoClient, ASCENDING, DESCENDING

from app import config


def _datetime(d) -> datetime | None:
    """MongoDB n'a pas de date sans heure."""
    if d is None or isinstance(d, datetime):
        return d
    return datetime(d.year, d.month, d.day)


def document_contenu(c: dict) -> dict:
    doc = {
        "_id": c["id"], "titre": c["titre"], "type": c["type"], "artiste": c["artiste"],
        "duree_s": c["duree_s"], "date_sortie": _datetime(c["date_sortie"]),
        "pays": c["pays"], "explicite": c["explicite"],
        "details": {k: (_datetime(v) if isinstance(v, date) else v) for k, v in c["details"].items()},
    }
    # Les 32 albums importés du CSV n'ont ni genres ni langue : le champ est
    # ABSENT, pas null. La mission 5 vous fera sentir la différence.
    if c["genres"] is not None:
        doc["genres"] = c["genres"]
        doc["langue"] = c["langue"]
    else:
        doc["import_source"] = "csv-2024"
    return doc


def charger(d: dict) -> None:
    client = MongoClient(config.MONGO_URL, serverSelectionTimeoutMS=5000)
    client.drop_database(config.MONGO_BASE)
    b = client[config.MONGO_BASE]

    b.contenus.insert_many([document_contenu(c) for c in d["contenus"]])
    print(f"  contenus       {len(d['contenus']):>7}")

    b.utilisateurs.insert_many([{
        "_id": u["id"], "pseudo": u["pseudo"], "email": u["email"], "ville": u["ville"],
        "inscrit_le": u["inscrit_le"], "abonnement": u["abonnement"],
        "playlists": [{"nom": p["nom"], "creee_le": p["creee_le"], "contenus": p["contenus"]}
                      for p in u["playlists"]],
    } for u in d["utilisateurs"]])
    print(f"  utilisateurs   {len(d['utilisateurs']):>7}  (playlists imbriquées)")

    b.avis.insert_many([{
        "_id": a["id"], "contenu_id": a["contenu_id"],
        "utilisateur": {"id": a["utilisateur_id"], "pseudo": a["pseudo"]},
        "note": a["note"], "texte": a["texte"], "date": a["date"],
    } for a in d["avis"]])
    print(f"  avis           {len(d['avis']):>7}  (collection référencée)")

    b.ecoutes.insert_many([{
        "utilisateur_id": e["utilisateur_id"], "contenu_id": e["contenu_id"], "date": e["date"],
        "plateforme": e["plateforme"], "duree_ecoutee_s": e["duree_ecoutee_s"],
    } for e in d["ecoutes"]], ordered=False)
    print(f"  ecoutes        {len(d['ecoutes']):>7}")

    # Les index de la mission 9 du chapitre 2 : ceux que vous avez posés à la main.
    b.ecoutes.create_index([("date", ASCENDING)])
    b.ecoutes.create_index([("contenu_id", ASCENDING), ("date", ASCENDING)])
    b.ecoutes.create_index([("utilisateur_id", ASCENDING), ("date", DESCENDING)])
    b.avis.create_index([("contenu_id", ASCENDING), ("date", DESCENDING)])
    print("  index          posés (mission 9 du chapitre 2)")
