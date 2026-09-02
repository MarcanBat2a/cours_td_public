"""Ondine et Cassandra - l'historique des écoutes (chapitre 4).

Un seul rôle : HISTORIQUE=cassandra. Et une règle qui change tout : ici, on
crée UNE TABLE PAR QUESTION. La même écoute est écrite deux fois :

    ecoutes_par_utilisateur   « qu'a écouté u17 ? »        partition = utilisateur
    ecoutes_par_contenu       « combien d'écoutes a a001 ? » partition = contenu

Et « que se passe-t-il en ce moment sur Ondine ? » n'a pas de table : il n'y
a donc pas de réponse. Ce n'est pas un bug, c'est le modèle - c'est la
mission 5 du TD qui vous fait créer la troisième table.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster, NoHostAvailable, Session
from cassandra.query import SimpleStatement

from app import config, horloge
from app.stockage import BaseIndisponible

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
    # Deux tables, deux écritures. Pas de transaction entre elles : si la
    # seconde échoue, la première reste. C'est le prix - et il est connu.
    executer("INSERT INTO ecoutes_par_utilisateur (utilisateur_id, date, contenu_id, plateforme, duree_ecoutee_s) "
             "VALUES (%s, %s, %s, %s, %s)", (utilisateur_id, date, contenu_id, plateforme, duree_ecoutee_s))
    executer("INSERT INTO ecoutes_par_contenu (contenu_id, date, utilisateur_id, plateforme) "
             "VALUES (%s, %s, %s, %s)", (contenu_id, date, utilisateur_id, plateforme))
    executer("INSERT INTO ecoutes_par_jour (jour, date, utilisateur_id, contenu_id) "
             "VALUES (%s, %s, %s, %s)", (date.date(), date, utilisateur_id, contenu_id))


def historique_utilisateur(utilisateur_id: str, n: int = 20) -> list[dict]:
    lignes = executer("SELECT contenu_id, date, plateforme, duree_ecoutee_s FROM ecoutes_par_utilisateur "
                      "WHERE utilisateur_id = %s LIMIT %s", (utilisateur_id, n))
    return [l._asdict() for l in lignes]


def nb_ecoutes_contenu(contenu_id: str) -> int:
    return executer("SELECT count(*) AS nb FROM ecoutes_par_contenu WHERE contenu_id = %s", (contenu_id,))[0].nb


def dernieres_ecoutes(n: int = 10) -> list[dict]:
    """La table de la mission 5 : une partition par jour, les plus récentes
    en tête. Sans elle, cette question n'a pas de réponse en Cassandra."""
    jour = horloge.maintenant().date()
    lignes = executer("SELECT utilisateur_id, contenu_id, date FROM ecoutes_par_jour "
                      "WHERE jour IN (%s, %s) LIMIT %s", (jour, jour - timedelta(days=1), n))
    return sorted((l._asdict() for l in lignes), key=lambda e: e["date"], reverse=True)[:n]
