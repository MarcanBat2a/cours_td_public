"""Ondine et Cassandra - l'historique des écoutes (chapitre 4).

Un seul rôle : HISTORIQUE=cassandra. Et une règle qui change tout : ici, on
crée UNE TABLE PAR QUESTION. La même écoute est écrite plusieurs fois :

    ecoutes_par_utilisateur   « qu'a écouté u17 ? »          partition = utilisateur
    ecoutes_par_contenu       « combien d'écoutes a a001 ? »  partition = contenu

Et « que se passe-t-il en ce moment sur Ondine ? » n'a pas de table : il n'y
a donc pas de réponse. Ce n'est pas un bug, c'est le modèle - la mission 5
vous fait créer la troisième table.

Squelette : les fonctions marquées « à vous » sont les missions 4 et 5. Ce que
vous tapez dans cqlsh se passe tel quel à executer(cql, params), avec %s à la
place des valeurs.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster, NoHostAvailable, Session
from cassandra.query import SimpleStatement

from app import config, horloge
from app.stockage import AFaire, BaseIndisponible

KEYSPACE = "ondine"
_session: Session | None = None


def session() -> Session:
    global _session
    if _session is None:
        try:
            _session = Cluster(config.CASSANDRA_HOSTS, connect_timeout=5).connect(KEYSPACE)
        except NoHostAvailable as e:
            raise BaseIndisponible(f"Cassandra ({','.join(config.CASSANDRA_HOSTS)}) : {e}") from e
    return _session


def executer(cql: str, params=()) -> list:
    """Exécute un ordre CQL au niveau de cohérence de .env (CASSANDRA_CL)."""
    ordre = SimpleStatement(cql, consistency_level=getattr(ConsistencyLevel, config.CASSANDRA_CL))
    try:
        return list(session().execute(ordre, params))
    except NoHostAvailable as e:
        raise BaseIndisponible(f"Cassandra : plus assez de nœuds pour {config.CASSANDRA_CL} - {e}") from e
    except Exception as e:  # Unavailable, ReadTimeout, InvalidRequest...
        raise BaseIndisponible(f"Cassandra ({config.CASSANDRA_CL}) : {type(e).__name__} - {e}") from e


# ============================================================== historique

def enregistrer_ecoute(utilisateur_id: str, contenu_id: str, date: datetime,
                       plateforme: str, duree_ecoutee_s: int) -> None:
    """Mission 4 - une écoute, DEUX INSERT : un par table. Pas de transaction
    entre les deux : si le second échoue, le premier reste. C'est le prix."""
    raise AFaire("Mission 4 : enregistrer_ecoute() dans app/stockage/cassandra_.py")


def historique_utilisateur(utilisateur_id: str, n: int = 20) -> list[dict]:
    """Mission 4 - SELECT sur ecoutes_par_utilisateur, une seule partition,
    LIMIT n. Les lignes sont déjà dans l'ordre (CLUSTERING ORDER BY date DESC).
    Renvoyez [l._asdict() for l in lignes]."""
    raise AFaire("Mission 4 : historique_utilisateur() dans app/stockage/cassandra_.py")


def nb_ecoutes_contenu(contenu_id: str) -> int:
    """Mission 4 - count(*) sur UNE partition de ecoutes_par_contenu."""
    raise AFaire("Mission 4 : nb_ecoutes_contenu() dans app/stockage/cassandra_.py")


def dernieres_ecoutes(n: int = 10) -> list[dict]:
    """Mission 5 - « en ce moment ». Il n'y a pas de table pour cette question,
    donc pas de réponse : on renvoie une liste vide, et l'accueil affiche
    « indisponible avec cette base ». Ce n'est pas un bug, c'est le modèle.

    Mission 5 : créez la table (une partition par jour, les plus récentes en
    tête), écrivez-y aussi dans enregistrer_ecoute, puis lisez ici la partition
    d'aujourd'hui (horloge.maintenant().date()) et celle d'hier."""
    return []  # TODO mission 5
