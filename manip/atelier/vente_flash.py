"""Vente flash : beaucoup d'acheteurs, peu de casques (TD 4).

    python vente_flash.py naif           lire le stock, puis écrire le stock calculé
    python vente_flash.py inc            lire le stock, puis le décrémenter avec $inc
    python vente_flash.py conditionnel   tester et décrémenter dans le même updateOne

Options : --acheteurs 50 --stock 10

Chaque acheteur est un fil d'exécution avec sa propre demande. Tous partent
en même temps. Entre la lecture et l'écriture, les modes `naif` et `inc`
laissent passer 50 ms : le temps de vérifier un paiement.
"""

import argparse
import threading
import time

from commun import client

PRODUIT = "A-FLASH"
REFLEXION = 0.05


def acheter_naif(produits):
    """Lire, décider dans l'application, puis écrire la nouvelle valeur."""
    fiche = produits.find_one({"_id": PRODUIT})
    if fiche["stock"] < 1:
        return False
    time.sleep(REFLEXION)
    produits.update_one({"_id": PRODUIT}, {"$set": {"stock": fiche["stock"] - 1}})
    return True


def acheter_inc(produits):
    """Lire, décider dans l'application, puis laisser la base décrémenter."""
    fiche = produits.find_one({"_id": PRODUIT})
    if fiche["stock"] < 1:
        return False
    time.sleep(REFLEXION)
    produits.update_one({"_id": PRODUIT}, {"$inc": {"stock": -1}})
    return True


def acheter_conditionnel(produits):
    """Tester et décrémenter en une seule opération, sur le serveur."""
    resultat = produits.update_one({"_id": PRODUIT, "stock": {"$gte": 1}}, {"$inc": {"stock": -1}})
    return resultat.modified_count == 1


MODES = {"naif": acheter_naif, "inc": acheter_inc, "conditionnel": acheter_conditionnel}


def main():
    parser = argparse.ArgumentParser(description="Vente flash du TD 4")
    parser.add_argument("mode", choices=MODES)
    parser.add_argument("--acheteurs", type=int, default=50)
    parser.add_argument("--stock", type=int, default=10)
    args = parser.parse_args()

    base = client(maxPoolSize=args.acheteurs + 5)["flash"]
    base.produits.replace_one(
        {"_id": PRODUIT},
        {"_id": PRODUIT, "nom": "Casque Nomade, édition limitée", "prix": 99, "stock": args.stock},
        upsert=True,
    )
    base.commandes.delete_many({})

    depart = threading.Barrier(args.acheteurs)
    acheter = MODES[args.mode]

    def acheteur(numero):
        depart.wait()
        if acheter(base.produits):
            # La confirmation envoyée au client : une commande enregistrée.
            base.commandes.insert_one({"client": f"acheteur-{numero:02d}", "produit": PRODUIT, "prix": 99})

    fils = [threading.Thread(target=acheteur, args=(n,)) for n in range(1, args.acheteurs + 1)]
    for f in fils:
        f.start()
    for f in fils:
        f.join()

    print(f"Vente flash : {args.acheteurs} acheteurs, {args.stock} casques en stock, mode {args.mode}")
    print(f"  commandes confirmées : {base.commandes.count_documents({})}")
    print(f"  stock final          : {base.produits.find_one({'_id': PRODUIT})['stock']}")


if __name__ == "__main__":
    main()
