"""Remplit les tables Cassandra d'Ondine (chapitre 4, mission 4).

    docker compose exec web python -m donnees.charger cassandra

Squelette : la première table est écrite, les deux autres sont à vous. La
règle : la table naît de la question. Relisez la question, choisissez la
clé de partition (ce qu'on donne dans le WHERE), puis la colonne de tri.

    « qu'a écouté u17, du plus récent au plus ancien ? »   → écrite
    « combien d'écoutes a a001 ? »                          → à vous
    « que s'est-il passé aujourd'hui sur Ondine ? »         → mission 5

Le chargeur verse les 120 000 écoutes dans CHAQUE table qui existe. Comptez
une minute par table. Rejoué, il ne double rien : toute écriture est un upsert.
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

-- TODO mission 4 : CREATE TABLE ecoutes_par_contenu (...)

-- TODO mission 5 : CREATE TABLE ecoutes_par_jour (...)
"""

# Pour chaque table : son nom, ses colonnes, et comment en tirer une ligne
# depuis une écoute e = {utilisateur_id, contenu_id, date, plateforme, duree_ecoutee_s}.
# Ajoutez une entrée par table que vous créez.
CHARGEMENTS = [
    ("ecoutes_par_utilisateur", "(utilisateur_id, date, contenu_id, plateforme, duree_ecoutee_s)",
     lambda e: (e["utilisateur_id"], e["date"], e["contenu_id"], e["plateforme"], e["duree_ecoutee_s"])),
    # TODO mission 4 : ("ecoutes_par_contenu", "(...)", lambda e: (...)),
    # TODO mission 5 : ("ecoutes_par_jour", "(...)", lambda e: (e["date"].date(), ...)),
]


def charger(d: dict) -> None:
    rf = min(3, len(config.CASSANDRA_HOSTS))
    cluster = Cluster(config.CASSANDRA_HOSTS, connect_timeout=10)
    s = cluster.connect()
    s.execute(f"DROP KEYSPACE IF EXISTS {KEYSPACE}")
    s.execute(f"CREATE KEYSPACE {KEYSPACE} WITH replication = "
              f"{{'class': 'SimpleStrategy', 'replication_factor': {rf}}}")
    s.set_keyspace(KEYSPACE)
    for ordre in TABLES.strip().split(";"):
        ordre = "\n".join(l for l in ordre.splitlines() if not l.strip().startswith("--"))
        if ordre.strip():
            s.execute(ordre)
    print(f"  keyspace       {KEYSPACE} (réplication ×{rf}), {len(CHARGEMENTS)} table(s)")

    ecoutes = d["ecoutes"]
    for table, colonnes, valeurs in CHARGEMENTS:
        prep = s.prepare(f"INSERT INTO {table} {colonnes} VALUES ({', '.join('?' * colonnes.count(',') + '?')})")
        for i in range(0, len(ecoutes), 10000):
            execute_concurrent_with_args(s, prep, [valeurs(e) for e in ecoutes[i:i + 10000]], concurrency=100)
            print(f"\r  {table:24} {min(i + 10000, len(ecoutes)):>7} / {len(ecoutes)}", end="", flush=True)
        print()
    cluster.shutdown()
