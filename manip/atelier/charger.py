"""Recharge les données du TD.

    python charger.py            les deux bases, `cours` et `boutique`
    python charger.py cours      seulement le jeu du cours (instantané)
    python charger.py boutique   seulement la grande boutique (environ 30 s)

Chaque base est supprimée puis recréée : index, validateurs et modifications
faites pendant les TD disparaissent.
"""

import sys
import time

from pymongo import WriteConcern

from commun import client
from generer import generer
from jeu_cours import JEU

LOT = 2000


def charger_cours(mongo):
    mongo.drop_database("cours")
    base = mongo["cours"]
    for nom, docs in JEU.items():
        base[nom].insert_many(docs)
    print("cours     : " + ", ".join(f"{len(d)} {n}" for n, d in JEU.items()), flush=True)


def charger_boutique(mongo):
    debut = time.perf_counter()
    mongo.drop_database("boutique")
    # w=1 pendant le chargement : les copies rattrapent pendant qu'on insère.
    base = mongo.get_database("boutique", write_concern=WriteConcern(w=1))
    for nom, docs in generer().items():
        for i in range(0, len(docs), LOT):
            base[nom].insert_many(docs[i:i + LOT], ordered=True)
        print(f"boutique  : {len(docs):7d} {nom}", flush=True)
    # Dernière écriture à la majorité : les trois membres ont tout reçu, ou presque.
    mongo["boutique"].get_collection("chargement", write_concern=WriteConcern(w=3, wtimeout=120_000)) \
        .replace_one({"_id": "etat"}, {"_id": "etat", "pret": True}, upsert=True)
    print(f"boutique  : chargée en {time.perf_counter() - debut:.0f} s", flush=True)


def charger(mongo, quoi=("cours", "boutique")):
    if "cours" in quoi:
        charger_cours(mongo)
    if "boutique" in quoi:
        charger_boutique(mongo)


if __name__ == "__main__":
    demande = sys.argv[1:] or ["cours", "boutique"]
    inconnus = [d for d in demande if d not in ("cours", "boutique")]
    if inconnus:
        sys.exit(f"Base inconnue : {', '.join(inconnus)}. Choix : cours, boutique.")
    charger(client(), demande)
    print("Prêt.")
