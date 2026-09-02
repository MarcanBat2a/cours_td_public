#!/usr/bin/env bash
# Assemble le cluster MongoDB shardé (chapitre 5) : un serveur de configuration,
# deux fragments, un routeur.
#
#   bash cluster/shards.sh
#
# Le shell s'ouvre sur le ROUTEUR :  docker compose exec mongos mongosh --quiet
# Les fragments s'interrogent aussi en direct (docker compose exec shard1
# mongosh) : c'est l'instrument de mesure du TD, jamais un geste de production.
#
# La taille de morceau (chunk) est abaissée à 1 Mo : avec les 120 000 écoutes
# du TD (~15 Mo), la taille par défaut (128 Mo) ne découperait jamais rien.
# Ne pas l'« optimiser ».
#
# Pour brancher le site dessus, dans .env :  MONGO_URL=mongodb://mongos:27017
set -euo pipefail
cd "$(dirname "$0")/.."

docker compose --profile shards up -d cfg shard1 shard2 mongos

echo "→ attente des processus…"
for n in cfg shard1 shard2; do
  for _ in $(seq 30); do
    docker compose exec -T "$n" mongosh --quiet --eval 'db.adminCommand({ping:1})' >/dev/null 2>&1 && { echo "  $n répond"; break; }
    sleep 1
  done
done

init_rs() {
  docker compose exec -T "$1" mongosh --quiet --eval "
    try { rs.status(); print('  $2 : déjà initialisé') }
    catch (e) { rs.initiate({ _id: '$2', $3 members: [{ _id: 0, host: '$1:27017' }] }); print('  $2 : initialisé') }"
}
echo "→ replica sets (un nœud chacun : c'est un TD)…"
init_rs cfg cfg-td "configsvr: true,"
init_rs shard1 sh1-td ""
init_rs shard2 sh2-td ""

echo "→ attente du routeur…"
for _ in $(seq 60); do
  docker compose exec -T mongos mongosh --quiet --eval 'db.adminCommand({ping:1})' >/dev/null 2>&1 && break
  sleep 1
done

echo "→ déclaration des fragments, taille de morceau à 1 Mo…"
docker compose exec -T mongos mongosh --quiet --eval "
  sh.addShard('sh1-td/shard1:27017'); sh.addShard('sh2-td/shard2:27017')
  db.getSiblingDB('config').settings.updateOne({ _id: 'chunksize' }, { \$set: { value: 1 } }, { upsert: true })
  db.adminCommand({ listShards: 1 }).shards.forEach(s => print('  ' + s._id.padEnd(8) + s.host))"
echo
echo "Prêt. Un shell sur le routeur :  docker compose exec mongos mongosh --quiet"
