"""Rejoue la semaine en cours dans le sorted set du Top 50 (chapitre 3).

    docker compose exec web python -m donnees.charger redis

Émet un ZINCRBY par écoute du 14 au 21 décembre, dans l'ordre chronologique :
exactement ce que fait le site à chaque clic sur « Écouter », condensé en une
seconde. La clé est d'abord supprimée : relancé deux fois, le Top ne double
pas. (Sans ce DEL, il doublerait - ZINCRBY n'est pas idempotent, et c'est
une leçon du TD.)

Le cache des fiches (ondine:fiche:*) est vidé aussi : nouvelle partie.
"""
from __future__ import annotations

from datetime import datetime

import redis

from app import config
from app.stockage.redis_ import CLE_TOP, CLE_STATS

SEMAINE = (datetime(2026, 12, 14), datetime(2026, 12, 21, 12))


def charger(d: dict) -> None:
    r = redis.Redis.from_url(config.REDIS_URL, decode_responses=True)
    r.delete(CLE_TOP, CLE_STATS)
    for cle in r.scan_iter("ondine:fiche:*"):
        r.delete(cle)
    semaine = [e for e in d["ecoutes"] if SEMAINE[0] <= e["date"] < SEMAINE[1]]
    with r.pipeline(transaction=False) as p:
        for e in semaine:
            p.zincrby(CLE_TOP, 1, e["contenu_id"])
        p.execute()
    print(f"  {CLE_TOP:24} {len(semaine):>7} écoutes rejouées, {r.zcard(CLE_TOP)} contenus classés")
    print(f"  cache des fiches         vidé")
