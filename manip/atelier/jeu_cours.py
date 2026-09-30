"""Le jeu d'exemple du cours : sept produits, quatre commandes, quatre avis.

Chargé dans la base `cours`. Chaque requête projetée en cours y donne le
résultat affiché sur la diapositive.
"""

from datetime import datetime, timezone


def _date(texte):
    return datetime.fromisoformat(texte).replace(tzinfo=timezone.utc)


PRODUITS = [
    {
        "_id": "T-100", "nom": "T-shirt Coton Bio", "categorie": "vetement", "prix": 25, "marque": "Maille",
        "variantes": [
            {"taille": "S", "couleur": "blanc", "stock": 12},
            {"taille": "M", "couleur": "blanc", "stock": 0},
            {"taille": "L", "couleur": "noir", "stock": 5},
        ],
        "stock": 17, "tags": ["coton", "bio"], "note": {"moyenne": 4.2, "nb": 57},
    },
    {
        "_id": "T-200", "nom": "Sweat Capuche", "categorie": "vetement", "prix": 49, "marque": "Maille",
        "variantes": [
            {"taille": "M", "couleur": "gris", "stock": 3},
            {"taille": "L", "couleur": "gris", "stock": 0},
        ],
        "stock": 3, "tags": ["coton"], "note": {"moyenne": 4.6, "nb": 21},
    },
    {
        "_id": "L-300", "nom": "Petit traité des données", "categorie": "livre", "prix": 32,
        "auteurs": ["Inès Garnier", "Paul Roux"], "isbn": "978-2-0000-0300-7", "pages": 412,
        "stock": 14, "tags": ["informatique", "broché"], "note": {"moyenne": 4.8, "nb": 12},
    },
    {
        "_id": "L-301", "nom": "Petit traité des données (epub)", "categorie": "livre", "prix": 18,
        "auteurs": ["Inès Garnier", "Paul Roux"], "format": "epub",
        "tags": ["informatique", "numérique"], "note": {"moyenne": 4.8, "nb": 5},
    },
    {
        "_id": "A-400", "nom": "Casque Nomade", "categorie": "audio", "prix": 129, "marque": "Sonar",
        "caracteristiques": {"autonomieHeures": 30, "bluetooth": "5.3", "poidsGrammes": 250},
        "stock": 1, "tags": ["sans fil", "réduction de bruit"], "note": {"moyenne": 4.1, "nb": 203},
    },
    {
        "_id": "A-500", "nom": "Enceinte Galet", "categorie": "audio", "prix": 79, "marque": "Sonar",
        "disponibleLe": _date("2026-11-20T00:00:00"), "stock": None, "tags": ["sans fil"],
    },
    {
        "_id": "C-600", "nom": "Café Moka 250 g", "categorie": "epicerie", "prix": 9,
        "origine": "Éthiopie", "poidsGrammes": 250, "stock": 0, "tags": ["bio"],
        "note": {"moyenne": 4.4, "nb": 88},
    },
]

COMMANDES = [
    {
        "_id": "CMD-1042", "client": {"id": "U-17", "nom": "Alice Martin"},
        "date": _date("2026-10-03T09:12:00"), "statut": "livree",
        "adresse": {"ville": "Lyon", "cp": "69003"},
        "lignes": [
            {"produit": "T-100", "nom": "T-shirt Coton Bio", "taille": "M", "prix": 25, "quantite": 2},
            {"produit": "L-300", "nom": "Petit traité des données", "prix": 32, "quantite": 1},
        ],
        "total": 82,
    },
    {
        "_id": "CMD-1043", "client": {"id": "U-21", "nom": "Karim Benali"},
        "date": _date("2026-10-05T18:40:00"), "statut": "livree",
        "adresse": {"ville": "Nantes", "cp": "44000"},
        "lignes": [{"produit": "A-400", "nom": "Casque Nomade", "prix": 129, "quantite": 1}],
        "total": 129,
    },
    {
        "_id": "CMD-1044", "client": {"id": "U-17", "nom": "Alice Martin"},
        "date": _date("2026-10-12T07:55:00"), "statut": "expediee",
        "adresse": {"ville": "Lyon", "cp": "69003"},
        "lignes": [
            {"produit": "C-600", "nom": "Café Moka 250 g", "prix": 9, "quantite": 3},
            {"produit": "L-301", "nom": "Petit traité des données (epub)", "prix": 18, "quantite": 1},
        ],
        "total": 45,
    },
    {
        "_id": "CMD-1045", "client": {"id": "U-30", "nom": "Lina Costa"},
        "date": _date("2026-10-20T12:03:00"), "statut": "preparation",
        "adresse": {"ville": "Lille", "cp": "59000"},
        "lignes": [
            {"produit": "T-100", "nom": "T-shirt Coton Bio", "taille": "L", "prix": 25, "quantite": 1},
            {"produit": "T-200", "nom": "Sweat Capuche", "taille": "M", "prix": 49, "quantite": 1},
            {"produit": "C-600", "nom": "Café Moka 250 g", "prix": 9, "quantite": 2},
        ],
        "total": 92,
    },
]

AVIS = [
    {"_id": "AV-1", "produit": "A-400", "client": "U-21", "note": 5, "texte": "Très confortable"},
    {"_id": "AV-2", "produit": "A-400", "client": "U-17", "note": 2, "texte": "Bluetooth instable"},
    {"_id": "AV-3", "produit": "T-100", "client": "U-17", "note": 4, "texte": "Taille bien"},
    {"_id": "AV-4", "produit": "C-600", "client": "U-30", "note": 3, "texte": "Un peu amer"},
]

JEU = {"produits": PRODUITS, "commandes": COMMANDES, "avis": AVIS}
