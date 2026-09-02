"""Le jeu de données d'Ondine - toujours le même, sur toutes les machines.

Le générateur pseudo-aléatoire est initialisé avec une graine fixe : chaque
poste de la salle produit exactement les mêmes contenus, les mêmes
utilisateurs, les mêmes écoutes. C'est ce qui permet aux corrigés d'annoncer
des chiffres exacts - si vous trouvez autre chose, ce n'est pas une variante,
c'est une erreur, et elle s'explique.

Ondine vit un jour fixe : le **21 décembre 2026 à midi**. Toutes les dates
sont absolues, la « semaine en cours » est toujours celle du 14 au 21
décembre, et les résultats ne dépendent pas du jour où vous travaillez.

Ce module ne touche à aucune base : il fabrique des objets Python, les
chargeurs (charger_sql.py, charger_mongo.py, ...) les écrivent où il faut.

    from donnees.generer import jeu
    d = jeu()
    len(d["contenus"])   # 400
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta

GRAINE = 20262
AUJOURDHUI = datetime(2026, 12, 21, 12, 0, 0)
DEBUT_ECOUTES = datetime(2026, 6, 1)
NB_ECOUTES = 120_000

ARTISTES = [
    "Lise Andrieu", "Les Marées", "Kotone", "Bruno Vasseur", "Clair-Obscur",
    "La Fanfare du Vieux Port", "Mireille Santi", "Écume", "Trio Bergame",
    "Nadir Boulif", "Palissade", "Suzanne Weyl", "Les Grands Fonds",
    "Orphée Circuit", "Maya Quintane", "Ferraille Douce", "Le Cartel des Ondes",
    "Hortense Valade", "Baume", "Ilona Marek", "Grive", "Pavel Dune",
    "Ceinture de Feu", "Anouk Lespérance", "Minuit Chrome", "Sacha Reinart",
    "Les Lucioles", "Delta Charnière", "Rosa Vermeil", "Kaino",
    "Brume Capitale", "Théo Malartre", "Velours Gris", "Iris Fontaine",
    "Chorale Armorique", "Nino Bellagamba", "Onde Porteuse", "Judith Casta",
    "Marbre", "Elias Renard",
]
GENRES = ["pop", "rock", "jazz", "electro", "hip-hop", "classique", "folk",
          "soul", "ambient", "chanson", "metal", "world", "live"]
NOMS_ALBUM = ["Voyage", "Hiver", "Rivage", "Silence", "Orage", "Jardin",
              "Refuge", "Vertige", "Sillage", "Mirage", "Théâtre", "Empire",
              "Fleuve", "Signal", "Royaume", "Archipel", "Comptoir", "Cratère"]
ADJECTIFS = ["lointain", "bleu", "ordinaire", "sauvage", "immobile", "doux",
             "électrique", "dernier", "premier", "invisible", "clair", "sombre"]
MOTS_PISTE = ["Aube", "Départ", "Ligne", "Marée", "Nuit", "Fenêtre", "Route",
              "Pluie", "Cendre", "Écho", "Boussole", "Vitrail", "Rumeur",
              "Lampe", "Sable", "Falaise", "Comète", "Passerelle"]
THEMES_PODCAST = ["histoire", "sciences", "cuisine", "voyage", "cinéma",
                  "économie", "sport", "littérature", "musique", "tech"]
PODCASTS = ["Les Voix du Port", "Cartes sur table", "Sous la surface",
            "Le Comptoir des idées", "Terrain vague", "Après l'orage"]
INVITES = ["Camille Roux", "Pierre Vallon", "Anaïs Berger", "Youssef Kadri",
           "Marion Tessier", "Lucas Ferri", "Inès Colonna", "Rémi Ghazal"]
AUTEURS = ["Jeanne Aubrac", "Marc Solenne", "Aurélie Dast", "Pascal Rimbert",
           "Léonie Marchal", "Hugo Baptiste"]
NARRATEURS = ["Voix : Claire Dumont", "Voix : Antoine Léger", "Voix : Sara Nadal"]
LIEUX = [("Le Silo", "Marseille"), ("La Cigale", "Paris"), ("Le Trianon", "Paris"),
         ("Stereolux", "Nantes"), ("Le Bikini", "Toulouse"), ("L'Aéronef", "Lille"),
         ("Théâtre de Bastia", "Bastia"), ("La Sirène", "La Rochelle")]
VILLES = ["Bastia", "Ajaccio", "Marseille", "Lyon", "Paris", "Nantes",
          "Toulouse", "Lille", "Bordeaux", "Corte", "Nice", "Montréal"]
PRENOMS = ["nina", "tom", "lea", "youssef", "maya", "hugo", "ines", "sacha",
           "lou", "emma", "noa", "elio", "zoe", "adam", "jade", "liam", "rose",
           "milo", "anna", "paul"]
PLATEFORMES = ["web", "ios", "android"]
AVIS_TEXTES = [
    "Un disque qu'on remet en boucle.", "Pas convaincu par la deuxième moitié.",
    "Découvert par hasard, adopté.", "La voix porte tout.",
    "Trop long, mais de beaux moments.", "Parfait pour un dimanche pluvieux.",
    "L'épisode le plus clair de la saison.", "Je n'ai rien compris, j'ai adoré.",
    "Le son du live est superbe.", "Un peu daté, mais attachant.",
]


def _pad(prefixe: str, n: int, largeur: int) -> str:
    return f"{prefixe}{n:0{largeur}d}"


def jeu() -> dict:
    """Fabrique tout le jeu de données. Toujours le même : graine fixe."""
    r = random.Random(GRAINE)
    entier = r.randint
    choix = r.choice

    def date_entre(d1: datetime, d2: datetime) -> datetime:
        secondes = int((d2 - d1).total_seconds())
        return d1 + timedelta(seconds=entier(0, secondes))

    # ------------------------------------------------------------ contenus
    contenus: list[dict] = []
    for i in range(1, 221):
        nb_pistes = entier(3, 12)
        pistes = [{"no": k, "titre": f"{choix(MOTS_PISTE)} {choix(ADJECTIFS)}",
                   "duree_s": entier(120, 420)} for k in range(1, nb_pistes + 1)]
        # 32 albums importés d'un vieux CSV par Tom : ni genres, ni langue.
        import_csv = i % 7 == 3
        contenus.append({
            "id": _pad("a", i, 3), "type": "album",
            "titre": f"{choix(NOMS_ALBUM)} {choix(ADJECTIFS)}",
            "artiste": choix(ARTISTES),
            "genres": None if import_csv else sorted(r.sample(GENRES, entier(1, 3))),
            "langue": None if import_csv else choix(["fr", "en", "co", "it"]),
            "duree_s": sum(p["duree_s"] for p in pistes),
            "date_sortie": date_entre(datetime(2005, 1, 1), datetime(2026, 12, 1)).date(),
            "pays": choix(["FR", "FR", "FR", "IT", "BE", "CA"]),
            "explicite": r.random() < 0.1,
            "details": {"label": choix(["Ondine Records", "Vieux Port", "Nuit Blanche",
                                        "Arpège", "Indépendant"]),
                        "nb_pistes": nb_pistes,
                        "annee_pressage": entier(2005, 2026),
                        "pochette_url": f"/static/pochettes/{_pad('a', i, 3)}.jpg",
                        "pistes": pistes},
        })
    for i in range(1, 91):
        contenus.append({
            "id": _pad("p", i, 3), "type": "podcast",
            "titre": f"{choix(PODCASTS)} - {choix(THEMES_PODCAST).capitalize()} #{entier(1, 60)}",
            "artiste": choix(PODCASTS),
            "genres": [choix(THEMES_PODCAST)],
            "langue": "fr", "duree_s": entier(900, 5400),
            "date_sortie": date_entre(datetime(2022, 1, 1), datetime(2026, 12, 15)).date(),
            "pays": "FR", "explicite": False,
            "details": {"saison": entier(1, 6), "episode": entier(1, 40),
                        "invite": choix(INVITES) if r.random() < 0.7 else None,
                        "theme": choix(THEMES_PODCAST),
                        "flux_rss": f"https://ondine.example/rss/{_pad('p', i, 3)}"},
        })
    for i in range(1, 51):
        contenus.append({
            "id": _pad("l", i, 3), "type": "livre_audio",
            "titre": f"{choix(NOMS_ALBUM)} {choix(ADJECTIFS)}",
            "artiste": choix(AUTEURS),
            "genres": [choix(["roman", "policier", "jeunesse", "essai"])],
            "langue": "fr", "duree_s": entier(10800, 54000),
            "date_sortie": date_entre(datetime(2015, 1, 1), datetime(2026, 12, 1)).date(),
            "pays": "FR", "explicite": False,
            "details": {"auteur": choix(AUTEURS), "narrateur": choix(NARRATEURS),
                        "isbn": f"978-2-{entier(10000, 99999)}-{entier(100, 999)}-{entier(0, 9)}",
                        "editeur": choix(["Écoute Éditions", "Sonore", "Plume & Voix"]),
                        "nb_chapitres": entier(8, 40), "langue_vo": choix(["fr", "en", "es"])},
        })
    for i in range(1, 41):
        lieu, ville = choix(LIEUX)
        contenus.append({
            "id": _pad("c", i, 3), "type": "concert",
            "titre": f"{choix(ARTISTES)} au {lieu}",
            "artiste": choix(ARTISTES),
            "genres": sorted(r.sample(GENRES, entier(1, 2))) + ["live"],
            "langue": choix(["fr", "en"]), "duree_s": entier(3600, 7200),
            "date_sortie": date_entre(datetime(2018, 1, 1), datetime(2026, 12, 1)).date(),
            "pays": "FR", "explicite": r.random() < 0.05,
            "details": {"lieu": lieu, "ville": ville,
                        "date_concert": date_entre(datetime(2017, 1, 1), datetime(2026, 11, 1)).date(),
                        "captation_4k": r.random() < 0.5, "nb_cameras": entier(3, 9),
                        "tournee": f"Tournée {entier(2017, 2026)}",
                        "setlist": [f"{choix(MOTS_PISTE)} {choix(ADJECTIFS)}"
                                    for _ in range(entier(8, 16))]},
        })

    # -------------------------------------------------------- utilisateurs
    ids_contenus = [c["id"] for c in contenus]
    utilisateurs: list[dict] = []
    for i in range(1, 61):
        uid = _pad("u", i, 2)
        playlists = []
        for k in range(entier(0, 3)):
            playlists.append({
                "nom": choix(["Réveil", "Route", "Soir", "Sport", "Concentration",
                              "Dimanche", "Fête", "Nuit"]) + (f" {k + 1}" if k else ""),
                "creee_le": date_entre(datetime(2025, 1, 1), AUJOURDHUI),
                "contenus": r.sample(ids_contenus, entier(2, 12)),
            })
        utilisateurs.append({
            "id": uid,
            "pseudo": f"{choix(PRENOMS)}{entier(1, 99)}",
            "email": f"{uid}@ondine.example",
            "ville": choix(VILLES),
            "inscrit_le": date_entre(datetime(2023, 1, 1), datetime(2026, 11, 30)),
            "abonnement": choix(["gratuit", "gratuit", "premium", "famille"]),
            "playlists": playlists,
        })
    ids_utilisateurs = [u["id"] for u in utilisateurs]

    # ---------------------------------------------------------------- avis
    avis: list[dict] = []
    for i in range(1, 1501):
        u = choix(utilisateurs)
        avis.append({
            "id": _pad("v", i, 4),
            "contenu_id": choix(ids_contenus),
            "utilisateur_id": u["id"], "pseudo": u["pseudo"],
            "note": entier(1, 5), "texte": choix(AVIS_TEXTES),
            "date": date_entre(datetime(2025, 6, 1), AUJOURDHUI),
        })

    # ------------------------------------------------------------- écoutes
    # Une popularité par contenu, très inégale : quelques titres concentrent
    # les écoutes, c'est ce qui donne un Top 50 qui veut dire quelque chose.
    poids = [1.0 / (k + 1) ** 0.8 for k in range(len(ids_contenus))]
    ordre = ids_contenus[:]
    r.shuffle(ordre)
    ecoutes: list[dict] = []
    for i in range(1, NB_ECOUTES + 1):
        c = r.choices(ordre, weights=poids, k=1)[0]
        ecoutes.append({
            "id": i,
            "utilisateur_id": choix(ids_utilisateurs),
            "contenu_id": c,
            "date": date_entre(DEBUT_ECOUTES, AUJOURDHUI),
            "plateforme": choix(PLATEFORMES),
            "duree_ecoutee_s": entier(30, 1800),
        })
    ecoutes.sort(key=lambda e: e["date"])
    for i, e in enumerate(ecoutes, start=1):
        e["id"] = i

    # ---------------------------------------------------------------- suit
    # Le réseau social d'Ondine : chacun suit 4 à 8 autres personnes. Ne sert
    # qu'au graphe du chapitre 4, mais vit ici pour rester déterministe.
    suit: list[tuple[str, str]] = []
    for u in ids_utilisateurs:
        cibles: set[str] = set()
        while len(cibles) < entier(4, 8):
            v = choix(ids_utilisateurs)
            if v != u:
                cibles.add(v)
        suit.extend((u, v) for v in sorted(cibles))

    return {"contenus": contenus, "utilisateurs": utilisateurs, "avis": avis,
            "ecoutes": ecoutes, "suit": suit}


if __name__ == "__main__":
    d = jeu()
    for nom, liste in d.items():
        print(f"{nom:14} {len(liste):>7}")
    semaine = [e for e in d["ecoutes"] if datetime(2026, 12, 14) <= e["date"] < AUJOURDHUI]
    print(f"{'écoutes semaine':14} {len(semaine):>7}")
