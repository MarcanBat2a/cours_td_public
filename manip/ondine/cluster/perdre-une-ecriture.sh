#!/usr/bin/env bash
# Fait disparaître des écritures que la base a pourtant confirmées (chapitre 1).
#
#   bash cluster/perdre-une-ecriture.sh
#
# La manip se joue dans une fenêtre d'une dizaine de secondes : entre l'instant
# où le primaire perd le contact avec la majorité et celui où il se démet. À la
# main, on la rate une fois sur deux. Le script la joue, vous regardez.
#
#   1. il repère le primaire ;
#   2. il lance dessus une série d'écritures en w:1, une toutes les 200 ms ;
#   3. il coupe ce nœud du réseau pendant que les écritures continuent ;
#   4. le nœud isolé confirme encore des écritures, jusqu'à ce qu'il se démette ;
#   5. les deux autres élisent un primaire, sur lequel le script écrit en
#      w:"majority" - c'est cette écriture qui rend les deux histoires
#      incompatibles, et le retour en arrière inévitable ;
#   6. il reconnecte l'ancien primaire, attend, et compte ce qui reste.
#
# Le script travaille dans sa propre base (`labo`) : Ondine n'est pas touchée.
set -uo pipefail
cd "$(dirname "$0")/.."

RESEAU=ondine-net
BASE=labo
COLL=condamnees

primaire() {
  local n
  for n in mongo1 mongo2 mongo3; do
    docker compose exec -T "$n" mongosh --quiet --eval 'quit(db.hello().isWritablePrimary ? 0 : 1)' >/dev/null 2>&1 && echo "$n"
  done
}

nettoyer() {
  if [ -n "${P:-}" ] && ! docker network inspect "$RESEAU" 2>/dev/null | grep -q "\"$P\""; then
    echo "→ reconnexion de secours de $P"
    docker network connect "$RESEAU" "$P" 2>/dev/null || true
  fi
}
trap nettoyer EXIT

echo "→ repérage du primaire…"
P=$(primaire | head -1)
if [ -z "${P:-}" ]; then
  echo "ERREUR : aucun primaire. Le cluster tourne-t-il ?  bash cluster/replica-set.sh" >&2
  exit 1
fi
echo "   primaire : $P"
docker compose exec -T "$P" mongosh --quiet --eval "db.getSiblingDB('$BASE').$COLL.drop()" >/dev/null 2>&1

echo "→ écritures en w:1 sur $P, une toutes les 200 ms, pendant 20 secondes…"
JOURNAL=$(mktemp)
docker compose exec -T "$P" mongosh --quiet --eval "
  const c = db.getSiblingDB('$BASE').$COLL
  const fin = Date.now() + 20000
  let confirmees = 0, refusees = 0
  while (Date.now() < fin) {
    try { c.insertOne({ n: confirmees, t: new Date() }, { writeConcern: { w: 1 } }); confirmees++ }
    catch (e) { refusees++ }
    sleep(200)
  }
  print('CONFIRMEES=' + confirmees); print('REFUSEES=' + refusees)
" > "$JOURNAL" 2>&1 &
ECRIVAIN=$!

sleep 6
echo "→ coupure du réseau pour $P - il est encore primaire, il ne le sait pas encore"
docker network disconnect "$RESEAU" "$P"

wait $ECRIVAIN
CONFIRMEES=$(grep -o 'CONFIRMEES=[0-9]*' "$JOURNAL" | cut -d= -f2); CONFIRMEES=${CONFIRMEES:-0}
REFUSEES=$(grep -o 'REFUSEES=[0-9]*' "$JOURNAL" | cut -d= -f2); REFUSEES=${REFUSEES:-0}
rm -f "$JOURNAL"
echo "   $CONFIRMEES écritures confirmées par $P, puis $REFUSEES refusées une fois démis"

echo "→ attente de l'élection d'un nouveau primaire parmi les deux autres…"
NOUVEAU=""
for _ in $(seq 40); do
  for n in mongo1 mongo2 mongo3; do
    [ "$n" = "$P" ] && continue
    docker compose exec -T "$n" mongosh --quiet --eval 'quit(db.hello().isWritablePrimary ? 0 : 1)' >/dev/null 2>&1 && { NOUVEAU="$n"; break; }
  done
  [ -n "$NOUVEAU" ] && break
  sleep 1
done
[ -z "$NOUVEAU" ] && { echo "ERREUR : aucune élection en 40 s." >&2; exit 1; }
echo "   nouveau primaire : $NOUVEAU"

echo "→ écriture en w:majority sur $NOUVEAU - les deux histoires deviennent incompatibles"
docker compose exec -T "$NOUVEAU" mongosh --quiet --eval "
  db.getSiblingDB('$BASE').evenements.insertOne({ note: 'après bascule' }, { writeConcern: { w: 'majority' } })" >/dev/null 2>&1

echo "→ reconnexion de $P"
docker network connect "$RESEAU" "$P"
echo "→ attente du retour à la normale (25 s)…"
sleep 25

RESTANTES=$(docker compose exec -T "$NOUVEAU" mongosh --quiet --eval "print(db.getSiblingDB('$BASE').$COLL.countDocuments())" 2>/dev/null | tr -d '\r' | tail -1)
ANNULEES=$(docker compose logs "$P" 2>/dev/null | grep -o '"totalEntriesRolledBackIncludingNoops":[0-9]*' | tail -1 | cut -d: -f2)

echo
echo "──────────────────────────────────────────────────────"
echo "  Écritures confirmées par la base : $CONFIRMEES"
echo "  Écritures encore présentes       : ${RESTANTES:-?}"
[ -n "${ANNULEES:-}" ] && echo "  Annulées, d'après MongoDB        : $ANNULEES"
echo "──────────────────────────────────────────────────────"
echo
echo "Où sont passées les écritures manquantes ?"
echo "  docker compose exec $P ls -R /data/db/rollback"
echo
echo "La base avait répondu « écriture confirmée ». Que confirmait-elle, exactement ?"
