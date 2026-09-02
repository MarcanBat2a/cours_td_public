"""Ondine sur MongoDB - le catalogue déménagé (chapitre 2).

Un contenu est un document : les champs communs à la racine, les attributs
propres au type dans le sous-objet `details`, les pistes d'un album dans un
tableau. Plus de 61 colonnes, plus de `if` par type : la fiche est lue telle
qu'elle est stockée.

Ce module sait tout faire aussi (catalogue, top, historique, reco) - mais
regardez `aussi_ecoute` : c'est la requête qui poussera vers le graphe au
chapitre 4.
"""
from __future__ import annotations

from datetime import datetime

from pymongo import MongoClient, DESCENDING
from pymongo.errors import PyMongoError

from app import config
from app.stockage import BaseIndisponible

_client: MongoClient | None = None


def base():
    global _client
    if _client is None:
        _client = MongoClient(config.MONGO_URL, serverSelectionTimeoutMS=3000)
    return _client[config.MONGO_BASE]


def _protege(f):
    """Transforme une base injoignable en message clair, pas en pile d'erreurs."""
    def enveloppe(*a, **k):
        try:
            return f(*a, **k)
        except PyMongoError as e:
            raise BaseIndisponible(f"MongoDB ({config.MONGO_URL}) : {e}") from e
    enveloppe.__name__ = f.__name__
    return enveloppe


def _date_seule(c: dict) -> dict:
    """MongoDB n'a pas de type « date sans heure » : on la range en datetime."""
    if isinstance(c.get("date_sortie"), datetime):
        c["date_sortie"] = c["date_sortie"].date()
    return c


# =============================================================== catalogue

@_protege
def lister_contenus(type=None, genre=None, q=None, limite=60) -> list[dict]:
    filtre: dict = {}
    if type:
        filtre["type"] = type
    if genre:
        filtre["genres"] = genre            # « genre dans le tableau » : c'est tout
    if q:
        filtre["$or"] = [{"titre": {"$regex": q, "$options": "i"}},
                         {"artiste": {"$regex": q, "$options": "i"}}]
    curseur = (base().contenus
               .find(filtre, {"titre": 1, "type": 1, "artiste": 1, "duree_s": 1, "genres": 1, "date_sortie": 1})
               .sort([("date_sortie", DESCENDING), ("_id", 1)]).limit(limite))
    return [_date_seule({**c, "id": c["_id"]}) for c in curseur]


@_protege
def fiche_contenu(id: str) -> dict | None:
    c = base().contenus.find_one({"_id": id})
    if c is None:
        return None
    c["id"] = c.pop("_id")
    c.setdefault("genres", None)
    c.setdefault("details", {})
    return _date_seule(c)


@_protege
def fiches_contenus(ids: list[str]) -> dict[str, dict]:
    if not ids:
        return {}
    curseur = base().contenus.find({"_id": {"$in": list(ids)}}, {"titre": 1, "type": 1, "artiste": 1})
    return {c["_id"]: {**c, "id": c["_id"]} for c in curseur}


@_protege
def types_et_genres() -> tuple[list[str], list[str]]:
    return sorted(base().contenus.distinct("type")), sorted(base().contenus.distinct("genres"))


@_protege
def avis_du_contenu(contenu_id: str) -> list[dict]:
    curseur = base().avis.find({"contenu_id": contenu_id}).sort("date", DESCENDING)
    return [{"id": a["_id"], "note": a["note"], "texte": a["texte"], "date": a["date"],
             "pseudo": a["utilisateur"]["pseudo"], "utilisateur_id": a["utilisateur"]["id"]}
            for a in curseur]


@_protege
def ajouter_avis(contenu_id: str, utilisateur_id: str, pseudo: str, note: int,
                 texte: str, date: datetime) -> None:
    base().avis.insert_one({"contenu_id": contenu_id,
                            "utilisateur": {"id": utilisateur_id, "pseudo": pseudo},
                            "note": note, "texte": texte, "date": date})


@_protege
def utilisateurs() -> list[dict]:
    curseur = base().utilisateurs.find({}, {"pseudo": 1, "ville": 1, "abonnement": 1}).sort("_id", 1)
    return [{**u, "id": u["_id"]} for u in curseur]


@_protege
def utilisateur(id: str) -> dict | None:
    u = base().utilisateurs.find_one({"_id": id})
    if u is None:
        return None
    u["id"] = u.pop("_id")
    u.setdefault("playlists", [])
    return u


# ===================================================================== top

@_protege
def top_semaine(depuis: datetime, jusqua: datetime, n: int = 50) -> list[tuple[str, int]]:
    """Le pipeline du Top 50 : filtrer la semaine, grouper, trier, couper."""
    curseur = base().ecoutes.aggregate([
        {"$match": {"date": {"$gte": depuis, "$lt": jusqua}}},
        {"$group": {"_id": "$contenu_id", "nb": {"$sum": 1}}},
        {"$sort": {"nb": -1, "_id": 1}},
        {"$limit": n},
    ])
    return [(d["_id"], d["nb"]) for d in curseur]


def noter_ecoute(utilisateur_id: str, contenu_id: str, date: datetime) -> None:
    pass  # rien à faire : le Top lit la collection ecoutes


# ============================================================== historique

@_protege
def enregistrer_ecoute(utilisateur_id: str, contenu_id: str, date: datetime,
                       plateforme: str, duree_ecoutee_s: int) -> None:
    base().ecoutes.insert_one({"utilisateur_id": utilisateur_id, "contenu_id": contenu_id,
                               "date": date, "plateforme": plateforme,
                               "duree_ecoutee_s": duree_ecoutee_s})


@_protege
def historique_utilisateur(utilisateur_id: str, n: int = 20) -> list[dict]:
    return list(base().ecoutes.find({"utilisateur_id": utilisateur_id}, {"_id": 0})
                .sort("date", DESCENDING).limit(n))


@_protege
def nb_ecoutes_contenu(contenu_id: str) -> int:
    return base().ecoutes.count_documents({"contenu_id": contenu_id})


@_protege
def dernieres_ecoutes(n: int = 10) -> list[dict]:
    ecoutes = list(base().ecoutes.find({}, {"_id": 0}).sort("date", DESCENDING).limit(n))
    pseudos = {u["_id"]: u["pseudo"] for u in base().utilisateurs.find(
        {"_id": {"$in": [e["utilisateur_id"] for e in ecoutes]}}, {"pseudo": 1})}
    for e in ecoutes:
        e["pseudo"] = pseudos.get(e["utilisateur_id"])
    return ecoutes


# ==================================================================== reco

@_protege
def aussi_ecoute(contenu_id: str, depuis: datetime, jusqua: datetime, n: int = 5) -> list[tuple[str, int]]:
    """« Les auditeurs de X ont aussi écouté », en pipeline. Chaque « saut »
    coûte un étage - et une auto-jointure ($lookup) de la collection ecoutes
    sur elle-même. Comparez avec les deux lignes de Cypher du chapitre 4."""
    fenetre = {"$gte": depuis, "$lt": jusqua}
    curseur = base().ecoutes.aggregate([
        {"$match": {"contenu_id": contenu_id, "date": fenetre}},
        {"$group": {"_id": "$utilisateur_id"}},
        {"$lookup": {"from": "ecoutes", "localField": "_id",
                     "foreignField": "utilisateur_id", "as": "leurs"}},
        {"$unwind": "$leurs"},
        {"$match": {"leurs.date": fenetre, "leurs.contenu_id": {"$ne": contenu_id}}},
        {"$group": {"_id": {"fan": "$_id", "contenu": "$leurs.contenu_id"}}},
        {"$group": {"_id": "$_id.contenu", "fans": {"$sum": 1}}},
        {"$sort": {"fans": -1, "_id": 1}},
        {"$limit": n},
    ])
    return [(d["_id"], d["fans"]) for d in curseur]
