#!/usr/bin/env bash
# Lève le replica set MongoDB « rs-td » à trois nœuds et attend l'élection
# d'un primaire (chapitre 1).
#
#   bash cluster/replica-set.sh          (depuis la racine du projet)
#
# Idempotent : relancé sur un cluster déjà initialisé, il affiche l'état.
# Pour brancher le site dessus, dans .env :
#   MONGO_URL=mongodb://mongo1,mongo2,mongo3/?replicaSet=rs-td
set -euo pipefail
cd "$(dirname "$0")/.."

docker compose --profile rs up -d mongo1 mongo2 mongo3

echo "→ attente des trois nœuds…"
for n in mongo1 mongo2 mongo3; do
  for _ in $(seq 30); do
    docker compose exec -T "$n" mongosh --quiet --eval 'db.adminCommand({ping:1})' >/dev/null 2>&1 && { echo "  $n répond"; break; }
    sleep 1
  done
done

echo "→ initialisation…"
docker compose exec -T mongo1 mongosh --quiet --eval "
  try { rs.status(); print('  déjà initialisé') }
  catch (e) {
    rs.initiate({ _id: 'rs-td', members: [
      { _id: 0, host: 'mongo1:27017' }, { _id: 1, host: 'mongo2:27017' }, { _id: 2, host: 'mongo3:27017' } ] })
    print('  rs.initiate() envoyé')
  }"

echo "→ attente de l'élection du primaire…"
for _ in $(seq 60); do
  docker compose exec -T mongo1 mongosh --quiet --eval 'quit(db.hello().primary ? 0 : 1)' >/dev/null 2>&1 && break
  sleep 1
done
docker compose exec -T mongo1 mongosh --quiet --eval "
  const s = rs.status()
  print('replica set : ' + s.set + ' - mandat ' + s.term)
  s.members.forEach(m => print('  ' + m.name.padEnd(16) + m.stateStr))"
echo
echo "Prêt. Un shell sur le primaire :  docker compose exec mongo1 mongosh --quiet"
