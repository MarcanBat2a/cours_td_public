"""Au lancement de l'atelier : former le replica set, puis charger les données.

Relancé sur un ensemble déjà prêt, il ne recharge rien : les données et les
index créés pendant les TD sont conservés d'un `docker compose up` à l'autre.
"""

import time

from pymongo.errors import PyMongoError

from charger import charger
from commun import MEMBRES, client, direct

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
        except PyMongoError:
            pass
        time.sleep(1)
    raise SystemExit(f"Délai dépassé : {message}")


def repond(membre):
    return direct(membre).admin.command("ping")["ok"] == 1


attendre(lambda: all(repond(m) for m in MEMBRES), "Attente des trois machines MongoDB...")

try:
    direct("mongo-a").admin.command("replSetGetStatus")
    print("Replica set rs0 déjà formé.", flush=True)
except PyMongoError:
    direct("mongo-a").admin.command("replSetInitiate", CONFIG)
    print("Replica set rs0 : configuration envoyée.", flush=True)

mongo = client()
attendre(lambda: mongo.admin.command("hello").get("primary") == "mongo-a:27017",
         "Attente de l'élection de mongo-a comme primaire...")

if mongo["boutique"]["chargement"].find_one({"_id": "etat", "pret": True}):
    print("Données déjà chargées : rien à refaire.", flush=True)
else:
    charger(mongo)

print("Boutique prête.", flush=True)
while True:
    time.sleep(3600)
