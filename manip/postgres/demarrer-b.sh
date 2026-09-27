#!/bin/bash
# Démarrage de pg-b : au premier lancement, B copie intégralement A
# (pg_basebackup), puis suit en continu le journal des écritures de A.
set -e
export PGPASSWORD=replicateur

# B est « loin » de A : chaque paquet sortant de B attend 20 ms.
/usr/local/bin/eloigner.sh 20ms || true

if [ ! -s "$PGDATA/PG_VERSION" ]; then
  echo "pg-b : copie initiale depuis pg-a..."
  until pg_isready -q -h pg-a; do sleep 1; done
  mkdir -p "$PGDATA"
  chown postgres:postgres "$PGDATA"
  chmod 700 "$PGDATA"
  gosu postgres pg_basebackup -h pg-a -U replicateur -D "$PGDATA" -X stream -R
  # Le nom sous lequel A voit B : pg_b (utile pour la réplication synchrone).
  echo "primary_conninfo = 'host=pg-a user=replicateur password=replicateur application_name=pg_b'" \
    >> "$PGDATA/postgresql.auto.conf"
fi

exec docker-entrypoint.sh postgres -c hot_standby=on
