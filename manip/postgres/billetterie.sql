-- Concert C17 : 5 000 places numérotées, aucune attribuée.
CREATE TABLE places (
  concert    text NOT NULL,
  place      int  NOT NULL,
  titulaire  text,
  PRIMARY KEY (concert, place)
);
INSERT INTO places (concert, place)
SELECT 'C17', n FROM generate_series(1, 5000) AS n;

-- Les réservations confirmées par le guichet : R314, R315...
CREATE SEQUENCE numero_reservation START 314;
CREATE TABLE reservations (
  id        text PRIMARY KEY DEFAULT 'R' || nextval('numero_reservation'),
  client    text NOT NULL,
  concert   text NOT NULL,
  place     int  NOT NULL,
  creee_a   timestamptz NOT NULL DEFAULT now()
);

-- Clé d'idempotence -> réservation déjà créée pour cette demande.
CREATE TABLE idempotence (
  cle             text PRIMARY KEY,
  reservation_id  text NOT NULL REFERENCES reservations(id)
);

-- Un petit journal pour mesurer la réplication (TD 3).
CREATE TABLE journal (
  id      serial PRIMARY KEY,
  message text NOT NULL,
  ecrit_a timestamptz NOT NULL DEFAULT now()
);
