"""Ondine et Redis - le Top 50 à trois millisecondes, et le cache (chapitre 3).

Deux rôles ici :

    TOP=redis      le Top 50 vit dans un sorted set, mis à jour à CHAQUE écoute
                   (ZINCRBY) et lu d'un coup (ZREVRANGE). Plus rien n'est
                   recalculé à l'affichage.
    CACHE=redis    les fiches contenu, en JSON, avec une durée de vie (TTL).
                   La page lit d'abord ici ; si la clé n'existe pas, elle lit
                   la vraie base et range le résultat.

Les clés suivent la convention  ondine:objet:id  - c'est le seul schéma que
Redis connaîtra jamais.
"""
from __future__ import annotations

import json
from datetime import date, datetime

import redis
from redis.exceptions import RedisError

from app import config
from app.stockage import BaseIndisponible

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
    """Les bornes sont ignorées : le sorted set EST la semaine en cours.
    (Le lundi matin, quelqu'un doit faire DEL - ou tenir un set par jour et
    les additionner : ZUNIONSTORE. C'est une question du TD.)"""
    return [(cid, int(score)) for cid, score in client().zrevrange(CLE_TOP, 0, n - 1, withscores=True)]


@_protege
def noter_ecoute(utilisateur_id: str, contenu_id: str, date: datetime) -> None:
    client().zincrby(CLE_TOP, 1, contenu_id)


# =================================================================== cache

def _json(o):
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    return str(o)


@_protege
def lire(cle: str):
    brut = client().get(cle)
    client().hincrby(CLE_STATS, "succes" if brut is not None else "echecs", 1)
    return json.loads(brut) if brut is not None else None


@_protege
def ecrire(cle: str, valeur, ttl_s: int) -> None:
    client().set(cle, json.dumps(valeur, default=_json), ex=ttl_s)


@_protege
def supprimer(cle: str) -> None:
    client().delete(cle)


@_protege
def statistiques() -> dict:
    s = client().hgetall(CLE_STATS)
    return {"actif": True, "succes": int(s.get("succes", 0)), "echecs": int(s.get("echecs", 0))}
