#!/bin/bash
# Exécuté une seule fois, à la création de pg-a : autorise la copie B à se
# brancher sur le journal des écritures (WAL) de A.
set -e
psql -v ON_ERROR_STOP=1 <<-SQL
	CREATE ROLE replicateur WITH REPLICATION LOGIN PASSWORD 'replicateur';
SQL
echo "host replication replicateur all scram-sha-256" >> "$PGDATA/pg_hba.conf"
