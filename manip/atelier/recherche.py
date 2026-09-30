"""Projection du catalogue MongoDB dans Elasticsearch pour l'atelier local.

MongoDB reste la source. Une synchronisation reconstruit l'index `catalogue`,
pour reproduire aussi les suppressions. Les changements MongoDB ne sont donc
visibles dans Elasticsearch qu'après cette action explicite.
"""

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

URL = os.environ.get("ELASTICSEARCH_URL", "http://elasticsearch:9200").rstrip("/")
INDEX = "catalogue"
CHAMPS = ("nom", "categorie", "marque", "tags", "prix", "stock")
MAPPING = {
    "settings": {"number_of_shards": 1, "number_of_replicas": 0},
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "nom": {"type": "text", "analyzer": "standard"},
            "categorie": {"type": "keyword"},
            "marque": {"type": "keyword"},
            "tags": {"type": "keyword"},
            "prix": {"type": "integer"},
            "stock": {"type": "integer"},
        },
    },
}


class ErreurRecherche(RuntimeError):
    """Erreur réseau ou réponse Elasticsearch invalide, avec statut HTTP éventuel."""

    def __init__(self, message, statut=None, details=None):
        super().__init__(message)
        self.statut = statut
        self.details = details


def requete(method, path, body=None):
    """Exécuter une requête Elasticsearch et renvoyer sa réponse JSON.

    `body` accepte un objet JSON, ou un texte NDJSON pour l'API `_bulk`.
    Une réponse vide (notamment HEAD) vaut None. Toute erreur lève
    ErreurRecherche, dont `statut` contient le code HTTP lorsque disponible.
    """
    if not isinstance(path, str) or not path.startswith("/") or path.startswith("//"):
        raise ValueError("Le chemin Elasticsearch doit commencer par un seul /.")
    if isinstance(body, str):
        donnees = body.encode("utf-8")
        contenu = "application/x-ndjson"
    elif body is None:
        donnees = None
        contenu = "application/json"
    else:
        donnees = json.dumps(body, ensure_ascii=False).encode("utf-8")
        contenu = "application/json"
    demande = Request(URL + path, data=donnees, method=method.upper(),
                      headers={"Content-Type": contenu, "Accept": "application/json"})
    try:
        with urlopen(demande, timeout=30) as reponse:
            texte = reponse.read().decode("utf-8")
            return json.loads(texte) if texte else None
    except HTTPError as erreur:
        texte = erreur.read().decode("utf-8", errors="replace")
        try:
            details = json.loads(texte) if texte else None
        except json.JSONDecodeError:
            details = texte
        raison = details.get("error") if isinstance(details, dict) else details
        raise ErreurRecherche(f"Elasticsearch HTTP {erreur.code} : {raison or erreur.reason}",
                             statut=erreur.code, details=details) from erreur
    except (URLError, TimeoutError, OSError) as erreur:
        raise ErreurRecherche(f"Elasticsearch inaccessible : {erreur}") from erreur
    except (json.JSONDecodeError, UnicodeDecodeError) as erreur:
        raise ErreurRecherche("Elasticsearch a renvoyé une réponse JSON illisible.") from erreur


def _existe():
    try:
        requete("HEAD", f"/{INDEX}")
        return True
    except ErreurRecherche as erreur:
        if erreur.statut == 404:
            return False
        raise


def synchroniser(mongo):
    """Reconstruire catalogue depuis cours.produits, sans toucher à MongoDB.

    Les identifiants MongoDB deviennent les identifiants Elasticsearch.
    Le stock absent reste absent, le stock null reste null.
    """
    projection = {champ: 1 for champ in CHAMPS}
    produits = list(mongo["cours"]["produits"].find({}, projection).sort("_id", 1))
    # Préparer toutes les données avant de supprimer l'ancienne projection.
    lignes = []
    for produit in produits:
        lignes.append(json.dumps({"index": {"_index": INDEX, "_id": str(produit["_id"])}}))
        lignes.append(json.dumps({champ: produit[champ] for champ in CHAMPS if champ in produit},
                                 ensure_ascii=False))

    if _existe():
        requete("DELETE", f"/{INDEX}")
    requete("PUT", f"/{INDEX}", MAPPING)
    if lignes:
        reponse = requete("POST", "/_bulk", "\n".join(lignes) + "\n")
        erreurs = [action for item in reponse.get("items", []) for action in item.values()
                   if action.get("status", 500) >= 300 or action.get("error")]
        if reponse.get("errors") or erreurs or len(reponse.get("items", [])) != len(produits):
            raise ErreurRecherche("La synchronisation du catalogue a échoué pour certains produits.",
                                 details=erreurs or reponse)
    requete("POST", f"/{INDEX}/_refresh")
    return {"index": INDEX, "documents": len(produits), "synchronise": True}


def initialiser(mongo):
    """Créer la projection au premier démarrage et préserver un index existant."""
    if not _existe():
        return synchroniser(mongo)
    nombre = requete("GET", f"/{INDEX}/_count")["count"]
    return {"index": INDEX, "documents": nombre, "synchronise": False}
