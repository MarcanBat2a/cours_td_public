"""Connexion au replica set, partagée par les scripts de l'atelier."""

import os

from pymongo import MongoClient

MEMBRES = ["mongo-a", "mongo-b", "mongo-c"]
URI = os.environ.get("MONGO_URI", "mongodb://mongo-a,mongo-b,mongo-c/?replicaSet=rs0")


def client(**options):
    return MongoClient(URI, **options)


def direct(membre, **options):
    """Connexion à un seul membre, sans découverte du replica set."""
    options.setdefault("serverSelectionTimeoutMS", 2000)
    return MongoClient(f"mongodb://{membre}:27017/?directConnection=true", **options)
