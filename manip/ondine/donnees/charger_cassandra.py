"""Remplit les tables Cassandra d'Ondine (chapitre 4).

    docker compose exec web python -m donnees.charger cassandra

Crée le keyspace `ondine` (facteur de réplication = nombre de nœuds déclarés
dans CASSANDRA_HOSTS, 3 au plus), les trois tables, puis y verse les
120 000 écoutes - TROIS FOIS, une par table. Ce n'est pas une maladresse,
c'est le modèle : la donnée se duplique, la requête ne se tord pas.

Comptez une à deux minutes. Rejoué, le chargeur ne double rien : en
Cassandra toute écriture est un upsert, et la clé primaire rend chaque
ligne unique.
"""
from __future__ import annotations

from cassandra.cluster import Cluster
from cassandra.concurrent import execute_concurrent_with_args

from app import config

KEYSPACE = "ondine"

TABLES = """
CREATE TABLE IF NOT EXISTS ecoutes_par_utilisateur (
  utilisateur_id text, date timestamp, contenu_id text, plateforme text, duree_ecoutee_s int,
  PRIMARY KEY (utilisateur_id, date)
) WITH CLUSTERING ORDER BY (date DESC);

CREATE TABLE IF NOT EXISTS ecoutes_par_contenu (
  contenu_id text, date timestamp, utilisateur_id text, plateforme text,
  PRIMARY KEY (contenu_id, date)
) WITH CLUSTERING ORDER BY (date DESC);

CREATE TABLE IF NOT EXISTS ecoutes_par_jour (
  jour date, date timestamp, utilisateur_id text, contenu_id text,
  PRIMARY KEY (jour, date)
) WITH CLUSTERING ORDER BY (date DESC);
"""


def charger(d: dict) -> None:
    rf = min(3, len(config.CASSANDRA_HOSTS))
    cluster = Cluster(config.CASSANDRA_HOSTS, connect_timeout=10)
    s = cluster.connect()
    s.execute(f"DROP KEYSPACE IF EXISTS {KEYSPACE}")
    s.execute(f"CREATE KEYSPACE {KEYSPACE} WITH replication = "
              f"{{'class': 'SimpleStrategy', 'replication_factor': {rf}}}")
    s.set_keyspace(KEYSPACE)
    for ordre in TABLES.strip().split(";"):
        if ordre.strip():
            s.execute(ordre)
    print(f"  keyspace       {KEYSPACE} (réplication ×{rf}), 3 tables")

    ecoutes = d["ecoutes"]
    for table, colonnes, valeurs in (
        ("ecoutes_par_utilisateur", "(utilisateur_id, date, contenu_id, plateforme, duree_ecoutee_s)",
         lambda e: (e["utilisateur_id"], e["date"], e["contenu_id"], e["plateforme"], e["duree_ecoutee_s"])),
        ("ecoutes_par_contenu", "(contenu_id, date, utilisateur_id, plateforme)",
         lambda e: (e["contenu_id"], e["date"], e["utilisateur_id"], e["plateforme"])),
        ("ecoutes_par_jour", "(jour, date, utilisateur_id, contenu_id)",
         lambda e: (e["date"].date(), e["date"], e["utilisateur_id"], e["contenu_id"])),
    ):
        prep = s.prepare(f"INSERT INTO {table} {colonnes} VALUES ({', '.join('?' * colonnes.count(',') + '?')})")
        for i in range(0, len(ecoutes), 10000):
            execute_concurrent_with_args(s, prep, [valeurs(e) for e in ecoutes[i:i + 10000]], concurrency=100)
            print(f"\r  {table:24} {min(i + 10000, len(ecoutes)):>7} / {len(ecoutes)}", end="", flush=True)
        print()
    cluster.shutdown()
