"""Charge le jeu de données dans PostgreSQL - l'état d'Ondine au chapitre 1.

    docker compose exec web python -m donnees.charger sql

Le script DÉTRUIT et recrée les tables. Il est déterministe : relancez-le
sans crainte, vous retrouvez toujours le même état de départ.

Le schéma est celui que Tom a laissé : une table `contenus` de 61 colonnes
pour loger albums, podcasts, livres audio et concerts filmés. Un podcast en
remplit 12 sur 61, le reste à NULL. Les pistes d'un album sont des colonnes
(piste_1_titre, piste_1_duree_s, ... piste_12_titre) : au-delà de douze
pistes, on ne sait plus. Et la table `ecoutes` n'a aucun index - « on verra
plus tard », disait Tom.

Ce n'est pas une caricature : c'est ce qu'on trouve.
"""
from __future__ import annotations

import psycopg

from app import config

SCHEMA = """
DROP TABLE IF EXISTS ecoutes, avis, playlist_contenus, playlists, utilisateurs, contenus;
DROP SEQUENCE IF EXISTS avis_seq;

CREATE TABLE contenus (
  id                   text PRIMARY KEY,
  titre                text NOT NULL,
  type                 text NOT NULL,          -- album | podcast | livre_audio | concert
  artiste              text,
  duree_s              integer,
  date_sortie          date,
  genres               text,                   -- « jazz,folk » : une liste dans une chaîne
  langue               text,
  pays                 text,
  explicite            boolean,
  cache_nb_ecoutes     integer,                -- jamais mis à jour depuis 2025
  cache_note_moyenne   numeric(3,2),
  -- albums
  album_label          text,
  album_nb_pistes      integer,
  album_annee_pressage integer,
  album_pochette_url   text,
  album_piste_1_titre  text, album_piste_1_duree_s  integer,
  album_piste_2_titre  text, album_piste_2_duree_s  integer,
  album_piste_3_titre  text, album_piste_3_duree_s  integer,
  album_piste_4_titre  text, album_piste_4_duree_s  integer,
  album_piste_5_titre  text, album_piste_5_duree_s  integer,
  album_piste_6_titre  text, album_piste_6_duree_s  integer,
  album_piste_7_titre  text, album_piste_7_duree_s  integer,
  album_piste_8_titre  text, album_piste_8_duree_s  integer,
  album_piste_9_titre  text, album_piste_9_duree_s  integer,
  album_piste_10_titre text, album_piste_10_duree_s integer,
  album_piste_11_titre text, album_piste_11_duree_s integer,
  album_piste_12_titre text, album_piste_12_duree_s integer,
  -- podcasts
  podcast_saison       integer,
  podcast_episode      integer,
  podcast_invite       text,
  podcast_theme        text,
  podcast_flux_rss     text,
  -- livres audio
  livre_auteur         text,
  livre_narrateur      text,
  livre_isbn           text,
  livre_editeur        text,
  livre_nb_chapitres   integer,
  livre_langue_vo      text,
  -- concerts filmés
  concert_lieu         text,
  concert_ville        text,
  concert_date         date,
  concert_captation_4k boolean,
  concert_nb_cameras   integer,
  concert_tournee      text,
  concert_setlist      text,                   -- « Aube bleue;Route sombre;... »
  -- technique
  cree_le              timestamp,
  modifie_le           timestamp,
  import_source        text                    -- « csv-2024 » pour les 32 albums de Tom
);

CREATE TABLE utilisateurs (
  id          text PRIMARY KEY,
  pseudo      text NOT NULL,
  email       text NOT NULL,
  ville       text,
  inscrit_le  timestamp,
  abonnement  text
);

CREATE TABLE playlists (
  id              serial PRIMARY KEY,
  utilisateur_id  text REFERENCES utilisateurs(id),
  nom             text NOT NULL,
  creee_le        timestamp
);

CREATE TABLE playlist_contenus (
  playlist_id  integer REFERENCES playlists(id),
  position     integer,
  contenu_id   text REFERENCES contenus(id),
  PRIMARY KEY (playlist_id, position)
);

CREATE SEQUENCE avis_seq START 100000;

CREATE TABLE avis (
  id              text PRIMARY KEY,
  contenu_id      text REFERENCES contenus(id),
  utilisateur_id  text REFERENCES utilisateurs(id),
  note            integer,
  texte           text,
  date            timestamp
);

-- Aucun index, aucune clé étrangère : « ça ralentit les insertions » (Tom).
CREATE TABLE ecoutes (
  id               integer,
  utilisateur_id   text,
  contenu_id       text,
  date             timestamp,
  plateforme       text,
  duree_ecoutee_s  integer
);
"""

COLONNES_CONTENU = [
    "id", "titre", "type", "artiste", "duree_s", "date_sortie", "genres", "langue",
    "pays", "explicite", "cache_nb_ecoutes", "cache_note_moyenne",
    "album_label", "album_nb_pistes", "album_annee_pressage", "album_pochette_url",
    *[f"album_piste_{k}_{champ}" for k in range(1, 13) for champ in ("titre", "duree_s")],
    "podcast_saison", "podcast_episode", "podcast_invite", "podcast_theme", "podcast_flux_rss",
    "livre_auteur", "livre_narrateur", "livre_isbn", "livre_editeur", "livre_nb_chapitres",
    "livre_langue_vo",
    "concert_lieu", "concert_ville", "concert_date", "concert_captation_4k",
    "concert_nb_cameras", "concert_tournee", "concert_setlist",
    "cree_le", "modifie_le", "import_source",
]
assert len(COLONNES_CONTENU) == 61


def ligne_contenu(c: dict) -> dict:
    """Aplatit un contenu (forme document) en une ligne de 61 colonnes."""
    d = c["details"]
    ligne = {col: None for col in COLONNES_CONTENU}
    ligne.update({
        "id": c["id"], "titre": c["titre"], "type": c["type"], "artiste": c["artiste"],
        "duree_s": c["duree_s"], "date_sortie": c["date_sortie"],
        "genres": ",".join(c["genres"]) if c["genres"] else None,
        "langue": c["langue"], "pays": c["pays"], "explicite": c["explicite"],
        "cree_le": c["date_sortie"], "modifie_le": None,
        "import_source": "csv-2024" if c["genres"] is None else None,
    })
    if c["type"] == "album":
        ligne.update({"album_label": d["label"], "album_nb_pistes": d["nb_pistes"],
                      "album_annee_pressage": d["annee_pressage"],
                      "album_pochette_url": d["pochette_url"]})
        for p in d["pistes"][:12]:
            ligne[f"album_piste_{p['no']}_titre"] = p["titre"]
            ligne[f"album_piste_{p['no']}_duree_s"] = p["duree_s"]
    elif c["type"] == "podcast":
        ligne.update({"podcast_saison": d["saison"], "podcast_episode": d["episode"],
                      "podcast_invite": d["invite"], "podcast_theme": d["theme"],
                      "podcast_flux_rss": d["flux_rss"]})
    elif c["type"] == "livre_audio":
        ligne.update({"livre_auteur": d["auteur"], "livre_narrateur": d["narrateur"],
                      "livre_isbn": d["isbn"], "livre_editeur": d["editeur"],
                      "livre_nb_chapitres": d["nb_chapitres"], "livre_langue_vo": d["langue_vo"]})
    elif c["type"] == "concert":
        ligne.update({"concert_lieu": d["lieu"], "concert_ville": d["ville"],
                      "concert_date": d["date_concert"], "concert_captation_4k": d["captation_4k"],
                      "concert_nb_cameras": d["nb_cameras"], "concert_tournee": d["tournee"],
                      "concert_setlist": ";".join(d["setlist"])})
    return ligne


def charger(d: dict) -> None:
    with psycopg.connect(config.PG_DSN, autocommit=False) as cx, cx.cursor() as cur:
        cur.execute(SCHEMA)

        lignes = [ligne_contenu(c) for c in d["contenus"]]
        with cur.copy(f"COPY contenus ({', '.join(COLONNES_CONTENU)}) FROM STDIN") as copie:
            for l in lignes:
                copie.write_row([l[col] for col in COLONNES_CONTENU])
        print(f"  contenus       {len(lignes):>7}  (61 colonnes)")

        cur.executemany(
            "INSERT INTO utilisateurs VALUES (%s, %s, %s, %s, %s, %s)",
            [(u["id"], u["pseudo"], u["email"], u["ville"], u["inscrit_le"], u["abonnement"])
             for u in d["utilisateurs"]])
        nb_pl = nb_pc = 0
        for u in d["utilisateurs"]:
            for pl in u["playlists"]:
                cur.execute("INSERT INTO playlists (utilisateur_id, nom, creee_le) VALUES (%s, %s, %s) RETURNING id",
                            (u["id"], pl["nom"], pl["creee_le"]))
                pid = cur.fetchone()[0]
                cur.executemany("INSERT INTO playlist_contenus VALUES (%s, %s, %s)",
                                [(pid, pos, cid) for pos, cid in enumerate(pl["contenus"], 1)])
                nb_pl += 1
                nb_pc += len(pl["contenus"])
        print(f"  utilisateurs   {len(d['utilisateurs']):>7}")
        print(f"  playlists      {nb_pl:>7}  ({nb_pc} lignes de contenus)")

        cur.executemany("INSERT INTO avis VALUES (%s, %s, %s, %s, %s, %s)",
                        [(a["id"], a["contenu_id"], a["utilisateur_id"], a["note"], a["texte"], a["date"])
                         for a in d["avis"]])
        print(f"  avis           {len(d['avis']):>7}")

        with cur.copy("COPY ecoutes FROM STDIN") as copie:
            for e in d["ecoutes"]:
                copie.write_row([e["id"], e["utilisateur_id"], e["contenu_id"], e["date"],
                                 e["plateforme"], e["duree_ecoutee_s"]])
        print(f"  ecoutes        {len(d['ecoutes']):>7}  (sans index)")
        cx.commit()
