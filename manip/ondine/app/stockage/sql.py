"""Tout Ondine dans PostgreSQL - l'état de départ, celui que Tom a laissé.

Ce module sait tout faire : catalogue, Top 50, historique, recommandation.
C'est lui que vous démontez chapitre après chapitre. Lisez-le, il vaut le
détour : la fonction `fiche_contenu` reconstruit un album à partir de ses
61 colonnes, et `aussi_ecoute` est la requête que « personne n'ose toucher ».
"""
from __future__ import annotations

import threading
from datetime import datetime

import psycopg
from psycopg.rows import dict_row

from app import config
from app.stockage import BaseIndisponible

# Une connexion par thread : uvicorn sert les pages depuis plusieurs threads,
# et une connexion psycopg ne se partage pas.
_local = threading.local()


def _connexion() -> psycopg.Connection:
    cx = getattr(_local, "cx", None)
    if cx is None or cx.closed:
        try:
            cx = psycopg.connect(config.PG_DSN, autocommit=True, row_factory=dict_row)
        except psycopg.OperationalError as e:
            raise BaseIndisponible(f"PostgreSQL ({config.PG_DSN}) : {e}") from e
        _local.cx = cx
    return cx


def _requete(sql: str, params=()) -> list[dict]:
    with _connexion().cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall() if cur.description else []


# =============================================================== catalogue

def _en_document(ligne: dict) -> dict:
    """Remonte la pente : 61 colonnes → un contenu avec ses détails.

    C'est le code que l'application exécute à CHAQUE affichage de fiche.
    Regardez le nombre de `if` : chaque nouveau type de contenu en ajoute.
    """
    c = {k: ligne[k] for k in ("id", "titre", "type", "artiste", "duree_s",
                                "date_sortie", "langue", "pays", "explicite")}
    c["genres"] = ligne["genres"].split(",") if ligne["genres"] else None
    c["import_source"] = ligne["import_source"]
    t = ligne["type"]
    if t == "album":
        pistes = []
        for k in range(1, 13):
            if ligne[f"album_piste_{k}_titre"] is not None:
                pistes.append({"no": k, "titre": ligne[f"album_piste_{k}_titre"],
                               "duree_s": ligne[f"album_piste_{k}_duree_s"]})
        c["details"] = {"label": ligne["album_label"], "nb_pistes": ligne["album_nb_pistes"],
                        "annee_pressage": ligne["album_annee_pressage"], "pistes": pistes}
    elif t == "podcast":
        c["details"] = {"saison": ligne["podcast_saison"], "episode": ligne["podcast_episode"],
                        "invite": ligne["podcast_invite"], "theme": ligne["podcast_theme"]}
    elif t == "livre_audio":
        c["details"] = {"auteur": ligne["livre_auteur"], "narrateur": ligne["livre_narrateur"],
                        "isbn": ligne["livre_isbn"], "editeur": ligne["livre_editeur"],
                        "nb_chapitres": ligne["livre_nb_chapitres"]}
    elif t == "concert":
        c["details"] = {"lieu": ligne["concert_lieu"], "ville": ligne["concert_ville"],
                        "date_concert": ligne["concert_date"],
                        "captation_4k": ligne["concert_captation_4k"],
                        "nb_cameras": ligne["concert_nb_cameras"], "tournee": ligne["concert_tournee"],
                        "setlist": ligne["concert_setlist"].split(";") if ligne["concert_setlist"] else []}
    else:
        c["details"] = {}
    # Le nombre de colonnes à NULL : affiché sur la fiche, pour mémoire.
    c["colonnes_vides"] = sum(1 for v in ligne.values() if v is None)
    return c


def lister_contenus(type=None, genre=None, q=None, limite=60) -> list[dict]:
    conditions, params = [], []
    if type:
        conditions.append("type = %s")
        params.append(type)
    if genre:
        # Chercher un genre dans une liste rangée dans une chaîne : LIKE, et prier.
        conditions.append("(',' || genres || ',') LIKE %s")
        params.append(f"%,{genre},%")
    if q:
        conditions.append("(titre ILIKE %s OR artiste ILIKE %s)")
        params += [f"%{q}%", f"%{q}%"]
    ou = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    lignes = _requete(f"""
        SELECT id, titre, type, artiste, duree_s, genres, date_sortie
        FROM contenus {ou} ORDER BY date_sortie DESC, id LIMIT %s""", (*params, limite))
    for l in lignes:
        l["genres"] = l["genres"].split(",") if l["genres"] else None
    return lignes


def fiche_contenu(id: str) -> dict | None:
    lignes = _requete("SELECT * FROM contenus WHERE id = %s", (id,))
    return _en_document(lignes[0]) if lignes else None


def fiches_contenus(ids: list[str]) -> dict[str, dict]:
    if not ids:
        return {}
    lignes = _requete("SELECT id, titre, type, artiste FROM contenus WHERE id = ANY(%s)", (list(ids),))
    return {l["id"]: l for l in lignes}


def types_et_genres() -> tuple[list[str], list[str]]:
    types = [l["type"] for l in _requete("SELECT DISTINCT type FROM contenus ORDER BY type")]
    genres = sorted({g for l in _requete("SELECT genres FROM contenus WHERE genres IS NOT NULL")
                     for g in l["genres"].split(",")})
    return types, genres


def avis_du_contenu(contenu_id: str) -> list[dict]:
    return _requete("""
        SELECT a.id, a.note, a.texte, a.date, u.pseudo, a.utilisateur_id
        FROM avis a JOIN utilisateurs u ON u.id = a.utilisateur_id
        WHERE a.contenu_id = %s ORDER BY a.date DESC""", (contenu_id,))


def ajouter_avis(contenu_id: str, utilisateur_id: str, pseudo: str, note: int,
                 texte: str, date: datetime) -> None:
    _requete("""
        INSERT INTO avis (id, contenu_id, utilisateur_id, note, texte, date)
        VALUES ('v' || nextval('avis_seq')::text, %s, %s, %s, %s, %s)""",
             (contenu_id, utilisateur_id, note, texte, date))


def utilisateurs() -> list[dict]:
    return _requete("SELECT id, pseudo, ville, abonnement FROM utilisateurs ORDER BY id")


def utilisateur(id: str) -> dict | None:
    lignes = _requete("SELECT * FROM utilisateurs WHERE id = %s", (id,))
    if not lignes:
        return None
    u = lignes[0]
    u["playlists"] = []
    for pl in _requete("SELECT id, nom, creee_le FROM playlists WHERE utilisateur_id = %s ORDER BY id", (id,)):
        pl["contenus"] = [l["contenu_id"] for l in _requete(
            "SELECT contenu_id FROM playlist_contenus WHERE playlist_id = %s ORDER BY position", (pl["id"],))]
        u["playlists"].append(pl)
    return u


# ===================================================================== top

def top_semaine(depuis: datetime, jusqua: datetime, n: int = 50) -> list[tuple[str, int]]:
    """Recalculé À CHAQUE affichage de l'accueil, sur toute la table ecoutes."""
    lignes = _requete("""
        SELECT contenu_id, count(*) AS nb
        FROM ecoutes WHERE date >= %s AND date < %s
        GROUP BY contenu_id ORDER BY nb DESC, contenu_id LIMIT %s""", (depuis, jusqua, n))
    return [(l["contenu_id"], l["nb"]) for l in lignes]


def noter_ecoute(utilisateur_id: str, contenu_id: str, date: datetime) -> None:
    pass  # rien à faire : le Top lit la table ecoutes


# ============================================================== historique

def enregistrer_ecoute(utilisateur_id: str, contenu_id: str, date: datetime,
                       plateforme: str, duree_ecoutee_s: int) -> None:
    _requete("""
        INSERT INTO ecoutes (id, utilisateur_id, contenu_id, date, plateforme, duree_ecoutee_s)
        VALUES ((SELECT coalesce(max(id), 0) + 1 FROM ecoutes), %s, %s, %s, %s, %s)""",
             (utilisateur_id, contenu_id, date, plateforme, duree_ecoutee_s))


def historique_utilisateur(utilisateur_id: str, n: int = 20) -> list[dict]:
    return _requete("""
        SELECT contenu_id, date, plateforme, duree_ecoutee_s
        FROM ecoutes WHERE utilisateur_id = %s ORDER BY date DESC LIMIT %s""", (utilisateur_id, n))


def nb_ecoutes_contenu(contenu_id: str) -> int:
    return _requete("SELECT count(*) AS nb FROM ecoutes WHERE contenu_id = %s", (contenu_id,))[0]["nb"]


def dernieres_ecoutes(n: int = 10) -> list[dict]:
    return _requete("""
        SELECT e.contenu_id, e.utilisateur_id, e.date, u.pseudo
        FROM ecoutes e JOIN utilisateurs u ON u.id = e.utilisateur_id
        ORDER BY e.date DESC LIMIT %s""", (n,))


# ==================================================================== reco

def aussi_ecoute(contenu_id: str, depuis: datetime, jusqua: datetime, n: int = 5) -> list[tuple[str, int]]:
    """« Les auditeurs de X ont aussi écouté » : la table ecoutes jointe à
    elle-même. Personne n'ose y toucher."""
    lignes = _requete("""
        SELECT e2.contenu_id, count(DISTINCT e2.utilisateur_id) AS fans
        FROM ecoutes e1
        JOIN ecoutes e2 ON e2.utilisateur_id = e1.utilisateur_id
        WHERE e1.contenu_id = %s AND e2.contenu_id <> %s
          AND e1.date >= %s AND e1.date < %s
          AND e2.date >= %s AND e2.date < %s
        GROUP BY e2.contenu_id ORDER BY fans DESC, e2.contenu_id LIMIT %s""",
                      (contenu_id, contenu_id, depuis, jusqua, depuis, jusqua, n))
    return [(l["contenu_id"], l["fans"]) for l in lignes]
