#!/usr/bin/env bash
# Lève l'anneau Cassandra à trois nœuds, dans l'ordre (chapitre 4).
#
#   docker compose stop cassandra        # libérer la RAM du nœud seul
#   bash cluster/anneau.sh
#
# Un nœud Cassandra ne rejoint l'anneau que lorsque le précédent est debout :
# deux nœuds qui démarrent ensemble se disputent leurs jetons et l'un des deux
# abandonne. Comptez deux à trois minutes. Idempotent.
#
# Pour brancher le site dessus, dans .env :
#   CASSANDRA_HOSTS=cass1,cass2,cass3
#   CASSANDRA_CL=QUORUM
set -euo pipefail
cd "$(dirname "$0")/.."

attendre_cql() {
  for _ in $(seq 90); do
    docker compose exec -T "$1" cqlsh -e 'DESCRIBE CLUSTER' >/dev/null 2>&1 && { echo "  $1 répond en CQL"; return 0; }
    sleep 2
  done
  echo "ERREUR : $1 ne répond pas après 3 minutes - docker compose logs $1" >&2
  exit 1
}

for n in cass1 cass2 cass3; do
  echo "→ démarrage de $n…"
  docker compose --profile anneau up -d "$n"
  attendre_cql "$n"
done

echo "→ état de l'anneau (UN = Up/Normal, Owns = la part de l'anneau) :"
docker compose exec -T cass1 nodetool status
echo
echo "Prêt. Un shell :  docker compose exec cass1 cqlsh"
