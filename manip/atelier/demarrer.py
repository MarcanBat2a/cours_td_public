"""Au lancement de l'atelier : former le replica set, puis charger les données.

Relancé sur un ensemble déjà prêt, il ne recharge rien : les données et les
index créés pendant les TD sont conservés d'un `docker compose up` à l'autre.
"""

import time

from pymongo.errors import PyMongoError

from charger import charger
from commun import MEMBRES, client, direct
from recherche import ErreurRecherche, initialiser, requete
from serveur import servir

CONFIG = {
    "_id": "rs0",
    "members": [
        {"_id": 0, "host": "mongo-a:27017", "priority": 2},  # mongo-a : primaire au départ
        {"_id": 1, "host": "mongo-b:27017", "priority": 1},
        {"_id": 2, "host": "mongo-c:27017", "priority": 1},
    ],
}


def attendre(condition, message, delai=120):
    print(message, flush=True)
    fin = time.monotonic() + delai
    while time.monotonic() < fin:
        try:
            if condition():
                return
        except (PyMongoError, ErreurRecherche):
            pass
        time.sleep(1)
    raise SystemExit(f"Délai dépassé : {message}")


def repond(membre):
    with direct(membre) as noeud:
        return noeud.admin.command("ping")["ok"] == 1


def demarrer():
    attendre(lambda: all(repond(m) for m in MEMBRES), "Attente des trois machines MongoDB...")

    with direct("mongo-a") as noeud:
        try:
            noeud.admin.command("replSetGetStatus")
            print("Replica set rs0 déjà formé.", flush=True)
        except PyMongoError as erreur:
            if getattr(erreur, "code", None) != 94:  # NotYetInitialized
                raise
            noeud.admin.command("replSetInitiate", CONFIG)
            print("Replica set rs0 : configuration envoyée.", flush=True)

    with client(serverSelectionTimeoutMS=2000) as mongo:
        attendre(lambda: bool(mongo.admin.command("hello").get("isWritablePrimary")),
                 "Attente de l'élection d'un primaire MongoDB...")

        if mongo["boutique"]["chargement"].find_one({"_id": "etat", "pret": True}):
            print("Données déjà chargées : rien à refaire.", flush=True)
        else:
            # Un chargement boutique interrompu ne doit pas effacer le travail du cours.
            bases = ("boutique",) if mongo["cours"].list_collection_names() else ("cours", "boutique")
            charger(mongo, bases)

        attendre(lambda: requete("GET", "/").get("cluster_name"),
                 "Attente d'Elasticsearch...", delai=180)
        etat = initialiser(mongo)
        if etat["synchronise"]:
            print(f"Recherche : {etat['documents']} produits du cours indexés.", flush=True)
        else:
            print("Recherche : index catalogue existant conservé.", flush=True)

    print("Boutique prête. Atelier : http://localhost:8000", flush=True)
    servir()


if __name__ == "__main__":
    demarrer()
