"""La configuration d'Ondine : qui stocke quoi.

Tout se règle dans le fichier `.env` à la racine du projet - c'est LE fichier
que vous modifiez au fil des chapitres. Chaque rôle de l'application peut
être confié à une base différente :

    CATALOGUE   sql | mongo              contenus, avis, utilisateurs, playlists
    TOP         sql | mongo | redis      le Top 50 de la semaine
    HISTORIQUE  sql | mongo | cassandra  les écoutes : enregistrer, relire, compter
    RECO        sql | mongo | neo4j      « les auditeurs de X ont aussi écouté »
    CACHE       aucun | redis            le cache des fiches contenu

Au chapitre 1, tout est en `sql`. Au chapitre 5, plus rien.

Après un changement de `.env` : `docker compose up -d web` (le conteneur est
recréé avec les nouvelles variables). La page /etat affiche ce qui est en
vigueur.
"""
from __future__ import annotations

import os

# ------------------------------------------------------------------ rôles
ROLES = {
    "CATALOGUE": os.environ.get("CATALOGUE", "sql"),
    "TOP": os.environ.get("TOP", "sql"),
    "HISTORIQUE": os.environ.get("HISTORIQUE", "sql"),
    "RECO": os.environ.get("RECO", "sql"),
    "CACHE": os.environ.get("CACHE", "aucun"),
}

# Quel module Python derrière quel nom de base.
MODULES = {
    "sql": "app.stockage.sql",
    "mongo": "app.stockage.mongo",
    "redis": "app.stockage.redis_",
    "neo4j": "app.stockage.neo4j_",
    "cassandra": "app.stockage.cassandra_",
    "aucun": "app.stockage.aucun",
}

# ---------------------------------------------------------------- accès
PG_DSN = os.environ.get("PG_DSN", "postgresql://ondine:ondine@pg:5432/ondine")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://mongo:27017")
MONGO_BASE = os.environ.get("MONGO_BASE", "ondine")
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379")
NEO4J_URL = os.environ.get("NEO4J_URL", "bolt://neo4j:7687")
CASSANDRA_HOSTS = [h.strip() for h in os.environ.get("CASSANDRA_HOSTS", "cassandra").split(",")]
CASSANDRA_CL = os.environ.get("CASSANDRA_CL", "ONE")

# ------------------------------------------------------------- réglages
# Durée de vie d'une fiche dans le cache (chapitre 3).
CACHE_TTL_S = int(os.environ.get("CACHE_TTL_S", "60"))
# Fenêtre de la recommandation « aussi écouté », en jours (chapitre 4).
RECO_FENETRE_JOURS = int(os.environ.get("RECO_FENETRE_JOURS", "30"))
