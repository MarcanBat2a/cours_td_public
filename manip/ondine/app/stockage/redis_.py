"""Ondine et Redis - le Top 50 à trois millisecondes, et le cache (chapitre 3).

Deux rôles :

    TOP=redis      le Top 50 vit dans un sorted set, mis à jour à CHAQUE écoute
                   et lu d'un coup. Plus rien n'est recalculé à l'affichage.
    CACHE=redis    les fiches contenu, en JSON, avec une durée de vie (TTL).

Squelette : les fonctions marquées « à vous » sont celles des missions 3 et 4.
Ce que vous avez tapé dans redis-cli se traduit mot pour mot :

    ZINCRBY ondine:top:semaine 1 a001      client().zincrby(CLE_TOP, 1, "a001")
    ZREVRANGE ondine:top:semaine 0 49 WITHSCORES
                                            client().zrevrange(CLE_TOP, 0, 49, withscores=True)
    SET cle valeur EX 60                    client().set(cle, valeur, ex=60)
"""
from __future__ import annotations

import json
from datetime import date, datetime

import redis
from redis.exceptions import RedisError

from app import config
from app.stockage import AFaire, BaseIndisponible

CLE_TOP = "ondine:top:semaine"
CLE_STATS = "ondine:cache:stats"

_r: redis.Redis | None = None


def client() -> redis.Redis:
    global _r
    if _r is None:
        _r = redis.Redis.from_url(config.REDIS_URL, decode_responses=True,
                                  socket_connect_timeout=2, socket_timeout=2)
    return _r


def _protege(f):
    def enveloppe(*a, **k):
        try:
            return f(*a, **k)
        except RedisError as e:
            raise BaseIndisponible(f"Redis ({config.REDIS_URL}) : {e}") from e
    enveloppe.__name__ = f.__name__
    return enveloppe


# ===================================================================== top

@_protege
def top_semaine(depuis: datetime, jusqua: datetime, n: int = 50) -> list[tuple[str, int]]:
    """Mission 3 - lire le Top : les n premiers du sorted set, scores compris.
    Les bornes de dates sont ignorées : le sorted set EST la semaine en cours.
    Renvoyez une liste de (contenu_id, nb) avec nb entier."""
    raise AFaire("Mission 3 : top_semaine() dans app/stockage/redis_.py")


@_protege
def noter_ecoute(utilisateur_id: str, contenu_id: str, date: datetime) -> None:
    """Mission 3 - une écoute de plus pour ce contenu : ZINCRBY de 1."""
    raise AFaire("Mission 3 : noter_ecoute() dans app/stockage/redis_.py")


# =================================================================== cache

def _json(o):
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    return str(o)


@_protege
def lire(cle: str):
    """Mission 4 - lire une fiche dans le cache. GET, puis json.loads ; None
    si la clé n'existe pas. Comptez le succès ou l'échec dans le hash
    CLE_STATS (HINCRBY "succes" / "echecs") : la fiche affiche ces chiffres."""
    raise AFaire("Mission 4 : lire() dans app/stockage/redis_.py")


@_protege
def ecrire(cle: str, valeur, ttl_s: int) -> None:
    """Mission 4 - ranger une fiche : json.dumps(valeur, default=_json), puis
    SET avec une durée de vie (ex=ttl_s)."""
    raise AFaire("Mission 4 : ecrire() dans app/stockage/redis_.py")


@_protege
def supprimer(cle: str) -> None:
    """Mission 4, étape 4 - invalider : DEL.

    Volontairement vide au départ : le site l'appelle après chaque écriture,
    et tant qu'elle ne fait rien, la fiche MENT pendant CACHE_TTL_S secondes.
    Regardez-la mentir avant de l'écrire."""
    pass  # TODO mission 4 : client().delete(cle)


@_protege
def statistiques() -> dict:
    s = client().hgetall(CLE_STATS)
    return {"actif": True, "succes": int(s.get("succes", 0)), "echecs": int(s.get("echecs", 0))}
