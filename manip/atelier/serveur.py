"""Atelier HTTP local : les requêtes sont exécutées sur les vraies bases."""

import json
import mimetypes
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from bson import json_util
from pymongo.errors import PyMongoError

from charger import charger_cours
from commun import client
from recherche import ErreurRecherche, requete, synchroniser

WEB = Path(__file__).with_name("web").resolve()
BASES = {"cours", "boutique"}
COLLECTIONS = {"produits", "commandes", "avis", "clients"}
MAX_RESULTATS = 50


def objet(valeur, nom):
    if not isinstance(valeur, dict):
        raise ValueError(f"{nom} doit être un objet JSON, entouré de {{ }}.")
    return valeur


def sans_sortie(pipeline):
    if not isinstance(pipeline, list):
        raise ValueError("pipeline doit être un tableau JSON, entouré de [ ].")
    # Une agrégation du carnet ne doit pas remplacer une collection par accident.
    def inspecter(valeur):
        if isinstance(valeur, dict):
            if any(k in valeur for k in ("$out", "$merge", "$function", "$accumulator")):
                raise ValueError("Cette étape n'est pas proposée dans l'atelier. Utilisez Compass pour les bonus avancés.")
            for v in valeur.values():
                inspecter(v)
        elif isinstance(valeur, list):
            for v in valeur:
                inspecter(v)
    inspecter(pipeline)


def executer_mongo(mongo, demande):
    base, nom = demande.get("base", "cours"), demande.get("collection", "produits")
    if base not in BASES or nom not in COLLECTIONS:
        raise ValueError("Choisissez une base et une collection de l'atelier.")
    collection = mongo[base][nom]
    p = objet(demande.get("payload", {}), "Le corps")
    operation = demande.get("operation", "find")
    filtre = objet(p.get("filter", {}), "filter")
    if "$where" in json.dumps(filtre):
        raise ValueError("Utilisez les opérateurs de filtre du cours, sans JavaScript serveur.")
    debut = time.perf_counter()
    if operation in ("find", "explain"):
        projection = p.get("projection")
        if projection is not None:
            objet(projection, "projection")
        tri = objet(p.get("sort", {}), "sort")
        limite = p.get("limit", MAX_RESULTATS if operation == "find" else None)
        if operation == "find" and limite is None:
            raise ValueError("limit doit être un entier entre 1 et 50.")
        if limite is not None and (isinstance(limite, bool) or not isinstance(limite, int) or not 1 <= limite <= MAX_RESULTATS):
            raise ValueError("limit doit être un entier entre 1 et 50.")
        curseur = collection.find(filtre, projection).max_time_ms(5000)
        if tri:
            curseur = curseur.sort(list(tri.items()))
        if limite is not None:
            curseur = curseur.limit(limite)
        if operation == "explain":
            commande = {"find": nom, "filter": filtre}
            if limite is not None:
                commande["limit"] = limite
            if projection is not None:
                commande["projection"] = projection
            if tri:
                commande["sort"] = tri
            resultat = mongo[base].command("explain", commande, verbosity="executionStats", maxTimeMS=5000)
        else:
            resultat = {"documents": list(curseur), "total": collection.count_documents(filtre, maxTimeMS=5000), "limite": limite}
    elif operation == "aggregate":
        pipeline = p.get("pipeline", [])
        sans_sortie(pipeline)
        docs = list(collection.aggregate(pipeline + [{"$limit": MAX_RESULTATS + 1}], maxTimeMS=5000))
        resultat = {"documents": docs[:MAX_RESULTATS], "tronque": len(docs) > MAX_RESULTATS}
    elif operation in ("updateOne", "updateMany"):
        modification = p.get("update")
        if isinstance(modification, list):
            sans_sortie(modification)
            if not modification:
                raise ValueError("Le pipeline de mise à jour est vide.")
        elif not isinstance(modification, dict) or not modification or not all(k.startswith("$") for k in modification):
            raise ValueError('update doit contenir des opérateurs, par exemple {"$set": {"prix": 27}}.')
        if not filtre:
            raise ValueError("Précisez un filtre avant une mise à jour.")
        methode = collection.update_one if operation == "updateOne" else collection.update_many
        r = methode(filtre, modification)
        resultat = {"matchedCount": r.matched_count, "modifiedCount": r.modified_count}
    elif operation == "insertOne":
        r = collection.insert_one(objet(p.get("document"), "document"))
        resultat = {"insertedId": r.inserted_id}
    elif operation == "createIndex":
        cles = objet(p.get("keys"), "keys")
        if not cles or any(v not in (1, -1, "text") for v in cles.values()):
            raise ValueError('keys associe chaque champ à 1, -1 ou "text".')
        options = {"name": p["name"]} if p.get("name") else {}
        resultat = {"index": collection.create_index(list(cles.items()), **options)}
    else:
        raise ValueError("Cette opération n'est pas proposée dans l'atelier.")
    return {"resultat": resultat, "duree_ms": round((time.perf_counter() - debut) * 1000, 1), "source": f"MongoDB / {base}.{nom}"}


def executer_elastic(demande):
    methode = demande.get("method", "POST")
    if not isinstance(methode, str):
        raise ValueError("method doit être une chaîne de caractères.")
    methode = methode.upper()
    chemin = demande.get("path", "/catalogue/_search")
    if methode not in {"GET", "POST", "PUT", "DELETE"}:
        raise ValueError("Méthode HTTP non proposée.")
    # La console peut explorer le catalogue, pas les autres réglages du cluster.
    if not isinstance(chemin, str) or not (chemin == "/catalogue" or chemin.startswith("/catalogue/") or chemin.startswith("/catalogue?")):
        raise ValueError("Le chemin doit cibler /catalogue.")
    if any(c in chemin for c in ("..", "#", ":", "\\")):
        raise ValueError("Chemin Elasticsearch invalide.")
    endpoint = chemin.split("?")[0]
    if endpoint not in {"/catalogue", "/catalogue/_search", "/catalogue/_analyze", "/catalogue/_mapping", "/catalogue/_count", "/catalogue/_refresh"} and not endpoint.startswith("/catalogue/_doc/"):
        raise ValueError("Utilisez _search, _analyze, _mapping, _count, _refresh ou _doc dans cette console.")
    debut = time.perf_counter()
    resultat = requete(methode, chemin, demande.get("payload"))
    return {"resultat": resultat, "duree_ms": round((time.perf_counter() - debut) * 1000, 1), "source": "Elasticsearch / catalogue"}


def action(mongo, demande):
    nom = demande.get("action")
    if nom == "acheter":
        r = mongo.cours.produits.update_one({"_id": "A-400", "stock": {"$gte": 1}}, {"$inc": {"stock": -1}})
        return {"accepte": r.matched_count == 1, "matchedCount": r.matched_count,
                "stock": mongo.cours.produits.find_one({"_id": "A-400"})["stock"],
                "message": "Casque attribué : décrément confirmé." if r.matched_count else "Rupture de stock : aucun casque attribué.",
                "precision": "Cette démonstration ne crée pas de commande. Stock et commande ensemble demanderaient une transaction."}
    if nom == "preparer":
        mongo.cours.produits.update_one({"_id": "A-400"}, {"$set": {"stock": 1}})
        return {"message": "Scène préparée : un casque dans MongoDB et dans sa copie.", **synchroniser(mongo)}
    if nom == "synchroniser":
        return synchroniser(mongo)
    if nom == "rafraichir":
        return requete("POST", "/catalogue/_refresh")
    if nom == "restaurer_cours":
        charger_cours(mongo)
        return {"message": "Les 7 produits, 4 commandes et 4 avis du cours sont restaurés.", **synchroniser(mongo)}
    raise ValueError("Action inconnue.")


def etat(mongo):
    resultat = {"mongo": False, "elastic": False}
    try:
        mongo.admin.command("ping")
        resultat.update(mongo=True, produits_cours=mongo.cours.produits.count_documents({}),
                        produits_boutique=mongo.boutique.produits.count_documents({}))
        casque = mongo.cours.produits.find_one({"_id": "A-400"})
        resultat["stock_mongo"] = casque.get("stock") if casque else None
    except PyMongoError as e:
        resultat["erreur_mongo"] = str(e)
    try:
        compte = requete("GET", "/catalogue/_count")
        casque = requete("POST", "/catalogue/_search", {"query": {"ids": {"values": ["A-400"]}}})
        docs = casque["hits"]["hits"]
        resultat.update(elastic=True, produits_elastic=compte["count"],
                        stock_elastic=docs[0]["_source"].get("stock") if docs else None)
    except ErreurRecherche as e:
        resultat["erreur_elastic"] = str(e)
    return resultat


def servir():
    mongo = client(serverSelectionTimeoutMS=3000, socketTimeoutMS=10000)
    carnets = {}

    class Serveur(BaseHTTPRequestHandler):
        def envoyer(self, code, valeur):
            donnees = json_util.dumps(valeur, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(donnees)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(donnees)

        def do_GET(self):
            if self.path == "/api/status":
                self.envoyer(200, etat(mongo))
                return
            if self.path.startswith("/carnets/"):
                carnet = carnets.get(self.path)
                if carnet is None or time.monotonic() - carnet[0] > 3600:
                    self.envoyer(404, {"erreur": "Cet export a expiré. Exportez à nouveau votre carnet depuis le site."})
                    return
                donnees = carnet[1]
                self.send_response(200)
                self.send_header("Content-Type", "text/markdown; charset=utf-8")
                self.send_header("Content-Disposition", 'attachment; filename="reponses.md"')
                self.send_header("Content-Length", str(len(donnees)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(donnees)
                return
            chemin = WEB / ("index.html" if self.path.split("?")[0] == "/" else self.path.split("?")[0].lstrip("/"))
            if not chemin.resolve().is_relative_to(WEB) or not chemin.is_file():
                self.envoyer(404, {"erreur": "Page inconnue."})
                return
            donnees = chemin.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", (mimetypes.guess_type(chemin)[0] or "application/octet-stream") + "; charset=utf-8")
            self.send_header("Content-Length", str(len(donnees)))
            self.end_headers()
            self.wfile.write(donnees)

        def do_POST(self):
            try:
                if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                    raise ValueError("Envoyez un corps JSON.")
                taille = int(self.headers.get("Content-Length", "0"))
                if not 0 < taille <= (4194304 if self.path == "/api/export" else 262144):
                    raise ValueError("Le corps de la requête est vide ou trop grand.")
                demande = objet(json_util.loads(self.rfile.read(taille).decode("utf-8")), "La demande")
                if self.path == "/api/export":
                    texte = demande.get("markdown")
                    if not isinstance(texte, str):
                        raise ValueError("Le carnet doit être du texte Markdown.")
                    if len(carnets) >= 10:
                        carnets.pop(next(iter(carnets)), None)
                    chemin = f"/carnets/{uuid.uuid4().hex}/reponses.md"
                    carnets[chemin] = (time.monotonic(), texte.encode("utf-8"))
                    self.envoyer(200, {"url": chemin})
                    return
                elif self.path == "/api/mongo":
                    resultat = executer_mongo(mongo, demande)
                elif self.path == "/api/elastic":
                    resultat = executer_elastic(demande)
                elif self.path == "/api/action":
                    resultat = {"resultat": action(mongo, demande), "source": "Scène du dernier casque"}
                else:
                    self.envoyer(404, {"erreur": "Action inconnue."})
                    return
                self.envoyer(200, resultat)
            except (ValueError, TypeError, KeyError, PyMongoError, ErreurRecherche) as e:
                self.envoyer(400, {"erreur": str(e)})

    serveur = ThreadingHTTPServer(("0.0.0.0", 8000), Serveur)
    print("Atelier prêt : http://localhost:8000", flush=True)
    try:
        serveur.serve_forever()
    finally:
        serveur.server_close()
        mongo.close()


if __name__ == "__main__":
    servir()
