"""Le standard téléphonique d'Ondine : à chaque rôle, sa base.

    from app import stockage
    stockage.catalogue().fiche_contenu("a001")

`stockage.catalogue()` renvoie le module Python choisi par CATALOGUE dans
`.env` (app/stockage/sql.py, mongo.py, ...). Tous les modules exposent les
mêmes fonctions pour un rôle donné - c'est ce qui permet de changer de base
sans toucher aux pages.

Une fonction pas encore écrite lève `AFaire` : la page affiche alors quelle
mission vous attend, au lieu d'une pile d'erreurs.
"""
from __future__ import annotations

import importlib
from types import ModuleType

from app import config


class AFaire(NotImplementedError):
    """« Cette fonction est à vous. » Levée par les squelettes de mission."""


class BaseIndisponible(RuntimeError):
    """La base demandée ne répond pas - est-elle démarrée ?"""


def _module(role: str) -> ModuleType:
    nom = config.ROLES[role]
    chemin = config.MODULES.get(nom)
    if chemin is None:
        raise BaseIndisponible(f"{role}={nom} : valeur inconnue dans .env")
    try:
        return importlib.import_module(chemin)
    except ModuleNotFoundError as e:
        raise BaseIndisponible(
            f"{role}={nom} : le module {chemin} n'existe pas encore - "
            "c'est une mission d'un prochain chapitre.") from e


def catalogue() -> ModuleType:
    return _module("CATALOGUE")


def top() -> ModuleType:
    return _module("TOP")


def historique() -> ModuleType:
    return _module("HISTORIQUE")


def reco() -> ModuleType:
    return _module("RECO")


def cache() -> ModuleType:
    return _module("CACHE")
