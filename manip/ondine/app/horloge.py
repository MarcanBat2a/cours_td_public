"""Ondine vit le 21 décembre 2026, à midi. Éternellement.

Le jeu de données est figé à cette date pour que les corrigés annoncent des
chiffres exacts. Mais une écoute que vous enregistrez aujourd'hui doit tomber
dans « la semaine en cours » : l'horloge de l'application part donc du
21 décembre 2026 et avance au rythme réel depuis le démarrage du serveur.

    maintenant()     → 2026-12-21 12:00:00 + (temps écoulé depuis le démarrage)
    semaine()        → (2026-12-14, maintenant)  la fenêtre du Top 50
"""
from __future__ import annotations

import time
from datetime import datetime, timedelta

ORIGINE = datetime(2026, 12, 21, 12, 0, 0)
_DEMARRAGE = time.time()


def maintenant() -> datetime:
    return ORIGINE + timedelta(seconds=time.time() - _DEMARRAGE)


def semaine() -> tuple[datetime, datetime]:
    fin = maintenant()
    return datetime(2026, 12, 14), fin


def fenetre(jours: int) -> tuple[datetime, datetime]:
    fin = maintenant()
    return fin - timedelta(days=jours), fin
