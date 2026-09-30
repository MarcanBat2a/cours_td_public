"""Une caisse qui encaisse sans arrêt : quatre écritures par seconde (TD 8).

    python ecrire_en_continu.py             confirmation par la majorité
    python ecrire_en_continu.py --w 1       confirmation par le seul primaire

Chaque écriture confirmée est notée dans /tmp/confirmees.txt. Arrêtez avec
Ctrl+C, puis lancez `python verifier_ecritures.py` : il compare ce carnet à
ce que contient réellement la base.
"""

import argparse
import time
from datetime import datetime, timezone

from pymongo import WriteConcern
from pymongo.errors import PyMongoError

from commun import client

CARNET = "/tmp/confirmees.txt"
PERIODE = 0.25


def heure():
    return datetime.now().strftime("%H:%M:%S")


def main():
    parser = argparse.ArgumentParser(description="Écritures continues du TD 8")
    parser.add_argument("--w", default="majority", help="1 ou majority (défaut : majority)")
    args = parser.parse_args()
    w = int(args.w) if args.w.isdigit() else args.w

    mongo = client(serverSelectionTimeoutMS=1000, socketTimeoutMS=2000, connectTimeoutMS=1000)
    tickets = mongo["boutique"].get_collection("tickets", write_concern=WriteConcern(w=w, wtimeout=1500))
    mongo["boutique"].drop_collection("tickets")
    open(CARNET, "w").close()

    confirmees = erreurs = numero = 0
    dernier_succes = time.monotonic()
    plus_longue = 0.0
    en_panne = False
    print(f"Écritures continues, w = {w!r}. Ctrl+C pour arrêter.", flush=True)
    try:
        while True:
            numero += 1
            debut = time.monotonic()
            try:
                tickets.insert_one({"_id": numero, "date": datetime.now(timezone.utc)})
            except PyMongoError as erreur:
                erreurs += 1
                en_panne = True
                message = str(erreur).split(",")[0][:70]
                print(f"{heure()}  ticket {numero:4d}  ERREUR  {type(erreur).__name__} : {message}", flush=True)
            else:
                maintenant = time.monotonic()
                if en_panne:
                    print(f"{heure()}  ticket {numero:4d}  reprise après {maintenant - dernier_succes:.1f} s sans écriture confirmée",
                          flush=True)
                plus_longue = max(plus_longue, maintenant - dernier_succes)
                dernier_succes = maintenant
                en_panne = False
                confirmees += 1
                with open(CARNET, "a") as carnet:
                    carnet.write(f"{numero}\n")
                primaire = mongo.primary[0] if mongo.primary else "?"
                if numero % 4 == 0:
                    print(f"{heure()}  ticket {numero:4d}  confirmé par {primaire}", flush=True)
            time.sleep(max(0.0, PERIODE - (time.monotonic() - debut)))
    except KeyboardInterrupt:
        print()
        print(f"Tickets confirmés : {confirmees}   erreurs : {erreurs}")
        print(f"Plus longue interruption : {plus_longue:.1f} s")


if __name__ == "__main__":
    main()
