# PostgreSQL 17, plus « tc » pour simuler la distance entre A et B.
FROM postgres:17
RUN apt-get update \
 && apt-get install -y --no-install-recommends iproute2 \
 && rm -rf /var/lib/apt/lists/*
COPY demarrer-b.sh eloigner.sh /usr/local/bin/
COPY initialiser-a.sh /docker-entrypoint-initdb.d/10-initialiser-a.sh
COPY billetterie.sql /docker-entrypoint-initdb.d/20-billetterie.sql
# Les fins de ligne Windows (CRLF) cassent bash : on les retire.
RUN sed -i 's/\r$//' /usr/local/bin/*.sh /docker-entrypoint-initdb.d/* \
 && chmod +x /usr/local/bin/demarrer-b.sh /usr/local/bin/eloigner.sh /docker-entrypoint-initdb.d/10-initialiser-a.sh
