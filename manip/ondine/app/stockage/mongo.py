"""Ondine sur MongoDB - le catalogue déménagé (chapitre 2).

Un contenu est un document : les champs communs à la racine, les attributs
propres au type dans le sous-objet `details`, les pistes d'un album dans un
tableau. Plus de 61 colonnes, plus de `if` par type.

Ce fichier est un squelette : les fonctions marquées « à vous » lèvent
`AFaire`, et la page correspondante du site vous le dit. Écrivez-les au fil
des missions - le serveur se recharge à chaque enregistrement. Le mémo A4
porte toute la syntaxe ; ce que vous avez tapé dans mongosh se traduit presque
mot pour mot en pymongo :

    db.contenus.find({type: "album"}).sort({date_sortie: -1}).limit(60)
    base().contenus.find({"type": "album"}).sort("date_sortie", -1).limit(60)
"""
from __future__ import annotations

from datetime import datetime

from pymongo import MongoClient, DESCENDING
from pymongo.errors import PyMongoError

from app import config
from app.stockage import AFaire, BaseIndisponible

_client: MongoClient | None = None


def base():
    """La base `ondine`. base().contenus est la collection contenus."""
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
def fiche_contenu(id: str) -> dict | None:
    """Mission 6 - la fiche. Un find_one, et c'est tout.

    Le site attend le document tel quel, avec deux retouches :
      - la clé `_id` renommée en `id` (c["id"] = c.pop("_id")) ;
      - `genres` et `details` présents même s'ils manquent (c.setdefault).
    Renvoyez None si le contenu n'existe pas. Passez le résultat par _date_seule.
    """
    raise AFaire("Mission 6 : fiche_contenu() dans app/stockage/mongo.py")


@_protege
def lister_contenus(type=None, genre=None, q=None, limite=60) -> list[dict]:
    """Mission 6 - le catalogue, avec ses filtres.

    Construisez un filtre dictionnaire :
      - type   → {"type": type}
      - genre  → un genre DANS le tableau genres : {"genres": genre} suffit ;
      - q      → titre OU artiste contenant q, sans tenir compte de la casse :
                 {"$or": [{"titre": {"$regex": q, "$options": "i"}}, {...}]}
    Projetez titre, type, artiste, duree_s, genres, date_sortie ; triez par
    date_sortie décroissante puis _id ; limitez. Chaque résultat doit porter
    une clé "id" en plus de "_id", et passer par _date_seule.
    """
    raise AFaire("Mission 6 : lister_contenus() dans app/stockage/mongo.py")


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
    """Mission 7 - les avis d'un contenu, du plus récent au plus ancien.

    Un avis est stocké ainsi :
      {"contenu_id": "a001", "utilisateur": {"id": "u17", "pseudo": "tom13"},
       "note": 4, "texte": "...", "date": ISODate(...)}
    Le site attend une liste de {id, note, texte, date, pseudo, utilisateur_id}.
    """
    raise AFaire("Mission 7 : avis_du_contenu() dans app/stockage/mongo.py")


@_protege
def ajouter_avis(contenu_id: str, utilisateur_id: str, pseudo: str, note: int,
                 texte: str, date: datetime) -> None:
    """Mission 7 - publier un avis : un insert_one, avec l'utilisateur en
    sous-document {id, pseudo}. Pas de _id : MongoDB en fabrique un."""
    raise AFaire("Mission 7 : ajouter_avis() dans app/stockage/mongo.py")


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
    """Mission 8 - le Top 50 en pipeline : filtrer la semaine ($match sur
    date entre depuis et jusqua), grouper par contenu_id en comptant ($group,
    $sum: 1), trier par nb décroissant puis _id, couper à n ($limit).
    Renvoyez une liste de (contenu_id, nb)."""
    raise AFaire("Mission 8 : top_semaine() dans app/stockage/mongo.py")


def noter_ecoute(utilisateur_id: str, contenu_id: str, date: datetime) -> None:
    pass  # rien à faire : le Top lit la collection ecoutes


# ============================================================== historique

@_protege
def enregistrer_ecoute(utilisateur_id: str, contenu_id: str, date: datetime,
                       plateforme: str, duree_ecoutee_s: int) -> None:
    """Mission 6 - une écoute = un document dans ecoutes, avec ces cinq champs."""
    raise AFaire("Mission 6 : enregistrer_ecoute() dans app/stockage/mongo.py")


@_protege
def historique_utilisateur(utilisateur_id: str, n: int = 20) -> list[dict]:
    """Mission 6 - les n dernières écoutes d'un utilisateur, sans le _id
    (projection {"_id": 0}), les plus récentes d'abord."""
    raise AFaire("Mission 6 : historique_utilisateur() dans app/stockage/mongo.py")


@_protege
def nb_ecoutes_contenu(contenu_id: str) -> int:
    """Mission 6 - count_documents."""
    raise AFaire("Mission 6 : nb_ecoutes_contenu() dans app/stockage/mongo.py")


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
    """« Les auditeurs de X ont aussi écouté », en pipeline. À LIRE, pas à
    écrire : chaque « saut » coûte un étage - et une auto-jointure ($lookup)
    de la collection ecoutes sur elle-même. Vous le comparerez au chapitre 4
    avec deux lignes de Cypher."""
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
