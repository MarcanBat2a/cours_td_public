"""Le chronomètre d'Ondine : chaque requête est mesurée, la page /etat fait
les comptes. C'est votre tableau de score - avant / après chaque mission.

Les temps sont gardés en mémoire du serveur : redémarrer `web` remet tout à
zéro, et le bouton de /etat aussi.
"""
from __future__ import annotations

import time
from collections import defaultdict

_temps: dict[str, list[float]] = defaultdict(list)
_MAX = 5000  # par route : au-delà, on oublie le plus ancien


def enregistrer(route: str, duree_ms: float) -> None:
    liste = _temps[route]
    liste.append(duree_ms)
    if len(liste) > _MAX:
        del liste[: len(liste) - _MAX]


def remettre_a_zero() -> None:
    _temps.clear()


def _percentile(valeurs: list[float], p: float) -> float:
    if not valeurs:
        return 0.0
    tri = sorted(valeurs)
    k = min(len(tri) - 1, int(round(p * (len(tri) - 1))))
    return tri[k]


def bilan() -> list[dict]:
    lignes = []
    for route, valeurs in sorted(_temps.items()):
        lignes.append({
            "route": route, "nb": len(valeurs),
            "moyenne": sum(valeurs) / len(valeurs),
            "p50": _percentile(valeurs, 0.5),
            "p95": _percentile(valeurs, 0.95),
            "max": max(valeurs),
        })
    return lignes


class Chrono:
    """with Chrono() as c: ...  ; c.ms"""

    def __enter__(self):
        self._debut = time.perf_counter()
        return self

    def __exit__(self, *_):
        self.ms = (time.perf_counter() - self._debut) * 1000
