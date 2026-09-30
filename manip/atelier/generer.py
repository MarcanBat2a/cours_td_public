"""Catalogue, clients, commandes et avis de la boutique du TD.

Tout est tiré d'un générateur pseudo-aléatoire à graine fixe : chaque poste
obtient exactement les mêmes documents, donc les mêmes comptes et les mêmes
plans d'exécution. Quelques défauts sont plantés volontairement, comme dans
une vraie base qui a vécu : des prix saisis en texte par un import, une faute
de frappe dans un nom de champ, des avis en double ou invalides.
"""

import bisect
import itertools
import random
from datetime import datetime, timedelta, timezone

GRAINE = 20262

NB_PRODUITS = 20_000
NB_CLIENTS = 20_000
NB_COMMANDES = 50_000
NB_AVIS = 100_000

# Défauts plantés (voir le corrigé).
NB_PRIX_TEXTE = 40
NB_FAUTE_CATEGORIE = 15
NB_AVIS_DOUBLES = 23

UTC = timezone.utc
DEBUT_VENTES = datetime(2026, 1, 1, tzinfo=UTC)
FIN_VENTES = datetime(2026, 9, 27, 20, 0, tzinfo=UTC)

CATEGORIES = [  # (valeur, préfixe, part du catalogue)
    ("vetement", "V", 0.30),
    ("livre", "L", 0.25),
    ("audio", "A", 0.15),
    ("epicerie", "E", 0.15),
    ("maison", "M", 0.15),
]

PRENOMS = ["Alice", "Karim", "Lina", "Hugo", "Inès", "Paul", "Chloé", "Yanis", "Léa", "Tom",
           "Sarah", "Nabil", "Emma", "Lucas", "Jade", "Mehdi", "Zoé", "Louis", "Nora", "Adam",
           "Manon", "Théo", "Camille", "Rayan", "Julie", "Sacha", "Anaïs", "Malik", "Eva", "Noé"]
NOMS = ["Martin", "Benali", "Costa", "Garnier", "Roux", "Petit", "Durand", "Moreau", "Leroy",
        "Fournier", "Girard", "Bonnet", "Dupont", "Lambert", "Fontaine", "Rousseau", "Vincent",
        "Muller", "Faure", "Mercier", "Blanc", "Guerin", "Boyer", "Chevalier", "Robin", "Gauthier"]
VILLES = [  # (ville, code postal, poids)
    ("Paris", "75011", 22), ("Lyon", "69003", 9), ("Marseille", "13001", 8),
    ("Toulouse", "31000", 7), ("Nice", "06000", 4), ("Nantes", "44000", 5),
    ("Montpellier", "34000", 4), ("Strasbourg", "67000", 4), ("Bordeaux", "33000", 5),
    ("Lille", "59000", 5), ("Rennes", "35000", 4), ("Reims", "51100", 2),
    ("Toulon", "83000", 2), ("Grenoble", "38000", 3), ("Dijon", "21000", 2),
    ("Angers", "49000", 2), ("Brest", "29200", 2), ("Tours", "37000", 2),
    ("Ajaccio", "20000", 1), ("Bastia", "20200", 1),
]

VETEMENTS = ["T-shirt", "Sweat", "Chemise", "Pull", "Veste", "Pantalon", "Robe", "Short", "Polo", "Gilet"]
MATIERES = ["Coton Bio", "Lin", "Laine", "Capuche", "Rayé", "Uni", "Oversize", "Brodé", "Recyclé", "Velours"]
MARQUES_VETEMENT = ["Maille", "Fil d'Or", "Coton & Co", "Atelier Nord", "Lin Vert", "Basique"]
TAILLES = ["XS", "S", "M", "L", "XL"]
COULEURS = ["blanc", "noir", "gris", "bleu", "vert", "rouge", "beige"]

LIVRES_DEBUT = ["Petit traité", "Introduction", "Manuel", "Guide pratique", "Histoire", "Précis", "Carnet", "Atlas"]
LIVRES_SUJET = ["des données", "de la cuisine", "du jardin", "des réseaux", "de la mer", "du vélo",
                "des étoiles", "de la photographie", "du café", "des montagnes", "du code", "des oiseaux"]
EDITEURS = ["Éditions du Port", "La Presse Claire", "Sillage", "Le Pas de Côté"]

AUDIO = ["Casque", "Écouteurs", "Enceinte", "Barre de son", "Radio"]
MARQUES_AUDIO = ["Sonar", "Écho", "Onde", "Basse Fréquence"]
MODELES = ["Nomade", "Galet", "Aurore", "Brise", "Studio", "Corail", "Horizon", "Pixel", "Vague", "Zénith",
           "Lagune", "Cime", "Éclat", "Orbite", "Rivage"]

EPICERIE = ["Café", "Thé", "Chocolat", "Miel", "Huile d'olive", "Pâtes", "Riz", "Confiture"]
ORIGINES = ["Éthiopie", "Colombie", "Pérou", "Inde", "Italie", "Corse", "Espagne", "Vietnam"]
MARQUES_EPICERIE = ["Moka", "Terroir", "Grain d'Or", "Maquis"]

MAISON = ["Lampe", "Coussin", "Plaid", "Vase", "Bougie", "Tasse", "Plateau", "Miroir"]
MARQUES_MAISON = ["Maison Claire", "Nid", "Terre & Feu"]

ETIQUETTES = {
    "vetement": ["coton", "bio", "lin", "laine", "recyclé", "fabriqué en France"],
    "livre": ["informatique", "broché", "poche", "illustré", "cuisine", "voyage"],
    "audio": ["sans fil", "réduction de bruit", "étanche", "bluetooth", "sport"],
    "epicerie": ["bio", "équitable", "sans gluten", "vegan", "local"],
    "maison": ["fait main", "céramique", "bois", "recyclé", "coton"],
}
COMMUNES = ["promo", "nouveauté", "cadeau"]

TEXTES_AVIS = [
    "Conforme à la description.", "Très bon produit, je recommande.", "Livraison rapide, bien emballé.",
    "Un peu déçu par la qualité.", "Rapport qualité-prix correct.", "Taille bien, tissu agréable.",
    "Ne correspond pas aux photos.", "Parfait pour offrir.", "Je rachèterai sans hésiter.",
    "Moyen, sans plus.", "Excellent, au-delà de mes attentes.", "Arrivé abîmé, service client réactif.",
    "Bonne autonomie, son équilibré.", "Un peu amer à mon goût.", "Se lit d'une traite.",
]


def _cumul(poids):
    return list(itertools.accumulate(poids))


def _tirer(rng, cumul, k):
    """k indices tirés selon les poids cumulés (avec remise)."""
    total = cumul[-1]
    return [bisect.bisect_left(cumul, rng.random() * total) for _ in range(k)]


def _popularites(rng, n, s):
    """Poids de Zipf d'exposant s, attribués dans un ordre mélangé."""
    rangs = list(range(1, n + 1))
    rng.shuffle(rangs)
    return [1 / r ** s for r in rangs]


def _date(rng, debut, fin):
    return debut + timedelta(seconds=rng.randrange(int((fin - debut).total_seconds())))


def _nom_personne(rng):
    return f"{rng.choice(PRENOMS)} {rng.choice(NOMS)}"


def _etiquettes(rng, categorie):
    tags = rng.sample(ETIQUETTES[categorie], rng.randint(1, 3))
    if rng.random() < 0.15:
        tags.append(rng.choice(COMMUNES))
    return tags


def _produit(rng, categorie, prefixe, numero):
    p = {"_id": f"{prefixe}-{numero}"}
    if categorie == "vetement":
        p["nom"] = f"{rng.choice(VETEMENTS)} {rng.choice(MATIERES)} {rng.choice(MODELES)}"
        p["categorie"] = categorie
        p["prix"] = rng.randint(15, 120)
        p["marque"] = rng.choice(MARQUES_VETEMENT)
        variantes = []
        for taille in sorted(rng.sample(TAILLES, rng.randint(2, 5)), key=TAILLES.index):
            stock = 0 if rng.random() < 0.3 else rng.randint(1, 20)
            variantes.append({"taille": taille, "couleur": rng.choice(COULEURS), "stock": stock})
        p["variantes"] = variantes
        p["stock"] = sum(v["stock"] for v in variantes)
    elif categorie == "livre":
        p["nom"] = f"{rng.choice(LIVRES_DEBUT)} {rng.choice(LIVRES_SUJET)}"
        p["categorie"] = categorie
        numerique = rng.random() < 0.3
        p["prix"] = rng.randint(6, 25) if numerique else rng.randint(9, 60)
        p["auteurs"] = [_nom_personne(rng) for _ in range(rng.choice([1, 1, 1, 2, 2, 3]))]
        p["editeur"] = rng.choice(EDITEURS)
        p["pages"] = rng.randint(90, 800)
        if numerique:
            p["format"] = "epub"  # un livre numérique n'a pas de stock : le champ est absent
        else:
            p["format"] = "broché"
            p["stock"] = 0 if rng.random() < 0.1 else rng.randint(1, 80)
    elif categorie == "audio":
        p["nom"] = f"{rng.choice(AUDIO)} {rng.choice(MODELES)}"
        p["categorie"] = categorie
        p["prix"] = rng.randint(20, 400)
        p["marque"] = rng.choice(MARQUES_AUDIO)
        if rng.random() < 0.9:
            p["caracteristiques"] = {
                "autonomieHeures": rng.choice([8, 12, 20, 24, 30, 40, 60]),
                "bluetooth": rng.choice(["5.0", "5.2", "5.3", "5.4"]),
                "poidsGrammes": rng.randint(5, 900),
            }
        if rng.random() < 0.04:  # précommande : stock inconnu, valeur null
            p["disponibleLe"] = _date(rng, datetime(2026, 10, 15, tzinfo=UTC), datetime(2027, 2, 1, tzinfo=UTC))
            p["stock"] = None
        else:
            p["stock"] = 0 if rng.random() < 0.15 else rng.randint(1, 60)
    elif categorie == "epicerie":
        produit = rng.choice(EPICERIE)
        poids = rng.choice([100, 250, 500, 1000])
        p["nom"] = f"{produit} {rng.choice(MODELES)} {poids} g"
        p["categorie"] = categorie
        p["prix"] = rng.randint(3, 40)
        p["marque"] = rng.choice(MARQUES_EPICERIE)
        p["origine"] = rng.choice(ORIGINES)
        p["poidsGrammes"] = poids
        p["stock"] = 0 if rng.random() < 0.1 else rng.randint(1, 150)
    else:
        p["nom"] = f"{rng.choice(MAISON)} {rng.choice(MODELES)}"
        p["categorie"] = categorie
        p["prix"] = rng.randint(10, 150)
        p["marque"] = rng.choice(MARQUES_MAISON)
        p["stock"] = 0 if rng.random() < 0.15 else rng.randint(1, 40)
    p["tags"] = _etiquettes(rng, categorie)
    p["ajouteLe"] = _date(rng, datetime(2023, 1, 1, tzinfo=UTC), datetime(2026, 9, 1, tzinfo=UTC))
    return p


def generer():
    rng = random.Random(GRAINE)

    # --- Produits ------------------------------------------------------------
    produits = []
    for categorie, prefixe, part in CATEGORIES:
        for numero in range(10_000, 10_000 + round(NB_PRODUITS * part)):
            produits.append(_produit(rng, categorie, prefixe, numero))

    # Défauts d'import : un prix en texte, une faute dans le nom d'un champ.
    abimes = rng.sample(range(len(produits)), NB_PRIX_TEXTE + NB_FAUTE_CATEGORIE)
    for i in abimes[:NB_PRIX_TEXTE]:
        produits[i]["prix"] = str(produits[i]["prix"])
    for i in abimes[NB_PRIX_TEXTE:]:
        ancien = produits[i]
        produits[i] = {("categori" if k == "categorie" else k): v for k, v in ancien.items()}

    # --- Clients -------------------------------------------------------------
    clients = []
    for n in range(1, NB_CLIENTS + 1):
        ville, cp, _ = rng.choices(VILLES, weights=[v[2] for v in VILLES])[0]
        clients.append({
            "_id": f"U-{n:05d}",
            "nom": _nom_personne(rng),
            "ville": ville,
            "cp": cp,
            "inscritLe": _date(rng, datetime(2020, 1, 1, tzinfo=UTC), datetime(2026, 9, 1, tzinfo=UTC)),
        })
    # La meilleure cliente est Alice Martin, comme dans le cours.
    clients[16].update(nom="Alice Martin", ville="Lyon", cp="69003")

    # --- Commandes -----------------------------------------------------------
    pop_ventes = _cumul(_popularites(rng, len(produits), 0.8))
    poids_clients = _popularites(rng, NB_CLIENTS, 0.6)
    top = max(range(NB_CLIENTS), key=poids_clients.__getitem__)
    poids_clients[16], poids_clients[top] = poids_clients[top], poids_clients[16]
    pop_clients = _cumul(poids_clients)

    commandes = []
    for n, c in zip(range(NB_COMMANDES), _tirer(rng, pop_clients, NB_COMMANDES)):
        client = clients[c]
        date = _date(rng, DEBUT_VENTES, FIN_VENTES)
        if date > datetime(2026, 9, 24, tzinfo=UTC):
            statut = rng.choice(["preparation", "expediee"])
        elif date > datetime(2026, 9, 17, tzinfo=UTC):
            statut = "expediee" if rng.random() < 0.3 else "livree"
        else:
            statut = "annulee" if rng.random() < 0.05 else "livree"
        nb_lignes = rng.choices([1, 2, 3, 4, 5], weights=[45, 30, 15, 7, 3])[0]
        choisis = []
        while len(choisis) < nb_lignes:
            i = _tirer(rng, pop_ventes, 1)[0]
            if i not in choisis:
                choisis.append(i)
        lignes = []
        for i in choisis:
            p = produits[i]
            prix = float(p["prix"]) if isinstance(p["prix"], str) else p["prix"]
            if isinstance(prix, float) and prix.is_integer():
                prix = int(prix)
            if rng.random() < 0.1:  # le prix a changé depuis l'achat
                prix = max(1, prix + rng.choice([-5, -3, -2, 2, 3, 5]))
            ligne = {"produit": p["_id"], "nom": p["nom"]}
            if "variantes" in p:
                ligne["taille"] = rng.choice(p["variantes"])["taille"]
            quantites = [50, 30, 20] if p.get("categorie") == "epicerie" else [80, 15, 5]
            ligne["prix"] = prix
            ligne["quantite"] = rng.choices([1, 2, 3], weights=quantites)[0]
            lignes.append(ligne)
        commandes.append({
            "_id": f"CMD-{100_001 + n}",
            "client": {"id": client["_id"], "nom": client["nom"]},
            "date": date,
            "statut": statut,
            "adresse": {"ville": client["ville"], "cp": client["cp"]},
            "lignes": lignes,
            "total": sum(l["prix"] * l["quantite"] for l in lignes),
        })
    commandes.sort(key=lambda c: c["date"])
    for n, c in enumerate(commandes):
        c["_id"] = f"CMD-{100_001 + n}"

    # --- Avis ----------------------------------------------------------------
    pop_avis = _cumul(_popularites(rng, len(produits), 1.0))
    rang = {p["_id"]: i for i, p in enumerate(produits)}
    par_produit = [0] * len(produits)
    for i in _tirer(rng, pop_avis, NB_AVIS):
        par_produit[i] += 1
    avis = []
    for i, k in enumerate(par_produit):
        if not k:
            continue
        for c in rng.sample(range(NB_CLIENTS), k):  # un avis par client et par produit
            note = rng.choices([1, 2, 3, 4, 5], weights=[5, 7, 15, 35, 38])[0]
            avis.append({
                "produit": produits[i]["_id"],
                "client": clients[c]["_id"],
                "note": note,
                "texte": rng.choice(TEXTES_AVIS),
                "date": _date(rng, datetime(2025, 6, 1, tzinfo=UTC), FIN_VENTES),
            })
    rng.shuffle(avis)
    avis = avis[:NB_AVIS]

    # Avis invalides : note hors bornes, en texte, décimale ; texte manquant.
    # Pris parmi les produits très commentés, pour que leur moyenne reste calculable.
    commentes = [a for a in avis if par_produit[rang[a["produit"]]] >= 20]
    for a, defaut in zip(rng.sample(commentes, 14), [6, 6, 6, 6, "5", "5", "4", 4.5, 3.5] + [None] * 5):
        if defaut is None:
            del a["texte"]
        else:
            a["note"] = defaut
    # Doublons : le même client note deux fois le même produit (double clic).
    valides = [a for a in avis if isinstance(a["note"], int) and 1 <= a["note"] <= 5 and "texte" in a]
    for a in rng.sample(valides, NB_AVIS_DOUBLES):
        avis.append({**a, "date": a["date"] + timedelta(seconds=rng.randint(1, 5))})
    avis.sort(key=lambda a: a["date"])
    avis = [{"_id": f"AV-{n:06d}", **a} for n, a in enumerate(avis, 1)]

    # Note moyenne et nombre d'avis, tenus à jour dans chaque produit.
    notes = {}
    for a in avis:
        n = notes.setdefault(a["produit"], [0, 0, 0])
        n[0] += 1
        if isinstance(a["note"], int) and 1 <= a["note"] <= 5:
            n[1] += a["note"]
            n[2] += 1
    for p in produits:
        if p["_id"] in notes:
            nb, somme, valides = notes[p["_id"]]
            p["note"] = {"moyenne": round(somme / valides, 1), "nb": nb}

    return {"produits": produits, "clients": clients, "commandes": commandes, "avis": avis}


if __name__ == "__main__":
    import time

    t = time.perf_counter()
    donnees = generer()
    for nom, docs in donnees.items():
        print(f"{nom:10} {len(docs):7d}")
    print(f"{time.perf_counter() - t:.1f} s")
