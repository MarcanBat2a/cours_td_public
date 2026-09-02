"""La migration : PostgreSQL → MongoDB, pour de vrai (chapitre 2, mission 3).

    docker compose exec web python -m donnees.migrer

Lit les tables de Tom, replie les 61 colonnes en documents, et écrit dans
MongoDB. C'est le script qu'Ondine exécutera une fois, la nuit de la bascule.

Choix de modèle (ceux de la mission 1) :

    contenus       un document par contenu, les champs communs à la racine,
                   les attributs du type dans `details`, les pistes en tableau.
                   Un champ vide (genres NULL) est ABSENT du document, pas null.
    utilisateurs   les playlists IMBRIQUÉES : petites, bornées, toujours lues
                   avec leur propriétaire.
    avis           collection à part, RÉFÉRENCÉE par contenu_id : ils
                   s'accumulent sans borne.
    ecoutes        collection à part, une écoute par document.
"""
from __future__ import annotations

from datetime import date, datetime

import psycopg
from psycopg.rows import dict_row
from pymongo import MongoClient

from app import config


def _dt(d):
    """MongoDB n'a pas de date sans heure : une date devient un datetime à minuit."""
    if isinstance(d, datetime) or d is None:
        return d
    return datetime(d.year, d.month, d.day)


def document_contenu(ligne: dict) -> dict:
    """Une ligne de 61 colonnes → un document."""
    doc = {
        "_id": ligne["id"], "titre": ligne["titre"], "type": ligne["type"],
        "artiste": ligne["artiste"], "duree_s": ligne["duree_s"],
        "date_sortie": _dt(ligne["date_sortie"]), "pays": ligne["pays"],
        "explicite": ligne["explicite"],
    }
    # Une liste rangée dans une chaîne redevient une liste. Et si Tom n'en
    # avait pas, le champ n'existe pas - on n'invente pas de null.
    if ligne["genres"]:
        doc["genres"] = ligne["genres"].split(",")
    if ligne["langue"]:
        doc["langue"] = ligne["langue"]
    if ligne["import_source"]:
        doc["import_source"] = ligne["import_source"]

    t = ligne["type"]
    if t == "album":
        pistes = [{"no": k, "titre": ligne[f"album_piste_{k}_titre"], "duree_s": ligne[f"album_piste_{k}_duree_s"]}
                  for k in range(1, 13) if ligne[f"album_piste_{k}_titre"] is not None]
        doc["details"] = {"label": ligne["album_label"], "nb_pistes": ligne["album_nb_pistes"],
                          "annee_pressage": ligne["album_annee_pressage"],
                          "pochette_url": ligne["album_pochette_url"], "pistes": pistes}
    elif t == "podcast":
        doc["details"] = {"saison": ligne["podcast_saison"], "episode": ligne["podcast_episode"],
                          "invite": ligne["podcast_invite"], "theme": ligne["podcast_theme"],
                          "flux_rss": ligne["podcast_flux_rss"]}
    elif t == "livre_audio":
        doc["details"] = {"auteur": ligne["livre_auteur"], "narrateur": ligne["livre_narrateur"],
                          "isbn": ligne["livre_isbn"], "editeur": ligne["livre_editeur"],
                          "nb_chapitres": ligne["livre_nb_chapitres"], "langue_vo": ligne["livre_langue_vo"]}
    elif t == "concert":
        doc["details"] = {"lieu": ligne["concert_lieu"], "ville": ligne["concert_ville"],
                          "date_concert": _dt(ligne["concert_date"]),
                          "captation_4k": ligne["concert_captation_4k"],
                          "nb_cameras": ligne["concert_nb_cameras"], "tournee": ligne["concert_tournee"],
                          "setlist": ligne["concert_setlist"].split(";") if ligne["concert_setlist"] else []}
    return doc


def document_utilisateur(u: dict, playlists: list[dict]) -> dict:
    return {"_id": u["id"], "pseudo": u["pseudo"], "email": u["email"], "ville": u["ville"],
            "inscrit_le": u["inscrit_le"], "abonnement": u["abonnement"],
            "playlists": [{"nom": p["nom"], "creee_le": p["creee_le"], "contenus": p["contenus"]}
                          for p in playlists]}


def migrer() -> None:
    pg = psycopg.connect(config.PG_DSN, row_factory=dict_row)
    mongo = MongoClient(config.MONGO_URL, serverSelectionTimeoutMS=5000)
    mongo.drop_database(config.MONGO_BASE)
    b = mongo[config.MONGO_BASE]

    with pg.cursor() as cur:
        cur.execute("SELECT * FROM contenus ORDER BY id")
        b.contenus.insert_many([document_contenu(l) for l in cur])
        print(f"  contenus       {b.contenus.count_documents({}):>7}")

        cur.execute("SELECT * FROM utilisateurs ORDER BY id")
        utilisateurs = cur.fetchall()
        docs = []
        for u in utilisateurs:
            cur.execute("SELECT id, nom, creee_le FROM playlists WHERE utilisateur_id = %s ORDER BY id", (u["id"],))
            playlists = cur.fetchall()
            for p in playlists:
                cur.execute("SELECT contenu_id FROM playlist_contenus WHERE playlist_id = %s ORDER BY position", (p["id"],))
                p["contenus"] = [l["contenu_id"] for l in cur]
            docs.append(document_utilisateur(u, playlists))
        b.utilisateurs.insert_many(docs)
        print(f"  utilisateurs   {len(docs):>7}  (playlists imbriquées)")

        cur.execute("SELECT a.*, u.pseudo FROM avis a JOIN utilisateurs u ON u.id = a.utilisateur_id ORDER BY a.id")
        b.avis.insert_many([{"_id": a["id"], "contenu_id": a["contenu_id"],
                             "utilisateur": {"id": a["utilisateur_id"], "pseudo": a["pseudo"]},
                             "note": a["note"], "texte": a["texte"], "date": a["date"]} for a in cur])
        print(f"  avis           {b.avis.count_documents({}):>7}  (collection référencée)")

        cur.execute("SELECT utilisateur_id, contenu_id, date, plateforme, duree_ecoutee_s FROM ecoutes ORDER BY id")
        paquet = []
        n = 0
        for e in cur:
            paquet.append(dict(e))
            if len(paquet) == 10000:
                b.ecoutes.insert_many(paquet, ordered=False)
                n += len(paquet)
                paquet = []
        if paquet:
            b.ecoutes.insert_many(paquet, ordered=False)
            n += len(paquet)
        print(f"  ecoutes        {n:>7}")
    print("Migration terminée. Dans .env : CATALOGUE=mongo, puis docker compose up -d web")


if __name__ == "__main__":
    migrer()
