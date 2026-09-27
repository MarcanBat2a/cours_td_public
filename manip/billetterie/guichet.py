"""Le guichet de la billetterie : réserve des places du concert C17 sur pg-a.

    GET  /places/42                      titulaire de la place 42
    GET  /reservations?client=alice      réservations enregistrées (la trace)
    POST /reservations                   {"client": "alice", "place": 42}
         en-tête facultatif              Idempotency-Key: reservation-A7
    POST /admin/panne                    {"mode": "perd-demande" | "lent" | "perd-reponse"}
    POST /admin/reset                    tout remettre à zéro

Une panne ne touche que la PROCHAINE demande de réservation, puis disparaît.
"""
import threading
import time

import psycopg

from commun import heure, servir

PANNES = {
    "aucune": "aucune panne",
    "perd-demande": "la demande se perd avant d'arriver : rien n'est enregistré",
    "lent": "la demande attend 10 s avant d'être traitée",
    "perd-reponse": "la réservation est enregistrée, la réponse se perd",
}
etat = {"panne": "aucune"}
verrou = threading.Lock()


def connexion():
    return psycopg.connect(autocommit=False)


def prendre_panne() -> str:
    with verrou:
        mode, etat["panne"] = etat["panne"], "aucune"
        return mode


def place(h, reste):
    if not reste.isdigit():
        return h.repondre(400, {"erreur": "numéro de place attendu, par exemple /places/42"})
    with connexion() as c:
        ligne = c.execute(
            "SELECT titulaire FROM places WHERE concert = 'C17' AND place = %s", (int(reste),)
        ).fetchone()
    if ligne is None:
        return h.repondre(404, {"erreur": f"la place {reste} n'existe pas (1 à 5000)"})
    h.repondre(200, {"concert": "C17", "place": int(reste), "titulaire": ligne[0]})


def reservations(h, _reste):
    client = (h.requete.get("client") or [None])[0]
    sql = "SELECT id, client, place, to_char(creee_a AT TIME ZONE 'Europe/Paris', 'HH24:MI:SS') FROM reservations"
    params = ()
    if client:
        sql += " WHERE client = %s"
        params = (client,)
    with connexion() as c:
        lignes = c.execute(sql + " ORDER BY creee_a", params).fetchall()
    h.repondre(200, [
        {"reservation": r, "client": cl, "place": p, "enregistree_a": t} for r, cl, p, t in lignes
    ])


def enregistrer(client: str, numero: int, cle: str | None):
    """Une seule transaction : clé déjà vue ? sinon attribution conditionnelle."""
    with connexion() as c:
        if cle:
            deja = c.execute(
                "SELECT r.id, r.client, r.place FROM idempotence i JOIN reservations r ON r.id = i.reservation_id"
                " WHERE i.cle = %s", (cle,)
            ).fetchone()
            if deja:
                return 200, {"reservation": deja[0], "client": deja[1], "place": deja[2],
                             "statut": "déjà confirmée pour cette clé"}
        attribuee = c.execute(
            "UPDATE places SET titulaire = %s WHERE concert = 'C17' AND place = %s AND titulaire IS NULL",
            (client, numero),
        ).rowcount
        if attribuee == 0:
            return 409, {"erreur": f"place {numero} déjà attribuée", "client": client}
        rid = c.execute(
            "INSERT INTO reservations (client, concert, place) VALUES (%s, 'C17', %s) RETURNING id",
            (client, numero),
        ).fetchone()[0]
        if cle:
            c.execute("INSERT INTO idempotence (cle, reservation_id) VALUES (%s, %s)", (cle, rid))
    return 201, {"reservation": rid, "client": client, "place": numero, "statut": "confirmée"}


def reserver(h, _reste):
    client, numero = h.corps.get("client"), h.corps.get("place")
    if not client or not isinstance(numero, int):
        return h.repondre(400, {"erreur": 'corps attendu : {"client": "alice", "place": 42}'})
    cle = h.headers.get("Idempotency-Key")
    panne = prendre_panne()
    print(f"  réservation {client}/{numero} clé={cle} panne={panne}")
    if panne == "perd-demande":
        time.sleep(30)
        return h.abandonner()
    if panne == "lent":
        time.sleep(10)
    code, reponse = enregistrer(client, numero, cle)
    print(f"  -> {code} {reponse}")
    if panne == "perd-reponse":
        time.sleep(30)
        return h.abandonner()
    h.repondre(code, reponse)


def panne(h, _reste):
    mode = h.corps.get("mode", "aucune")
    if mode not in PANNES:
        return h.repondre(400, {"erreur": f"modes possibles : {', '.join(PANNES)}"})
    with verrou:
        etat["panne"] = mode
    h.repondre(200, {"prochaine_reservation": PANNES[mode], "armee_a": heure(time.time())})


def reset(h, _reste):
    with connexion() as c:
        c.execute("TRUNCATE idempotence, reservations")
        c.execute("ALTER SEQUENCE numero_reservation RESTART 314")
        c.execute("UPDATE places SET titulaire = NULL WHERE titulaire IS NOT NULL")
    with verrou:
        etat["panne"] = "aucune"
    h.repondre(200, {"statut": "billetterie remise à zéro : aucune place attribuée"})


def aide(h, _reste):
    h.repondre(200, {"guichet": [l.strip() for l in __doc__.splitlines()[2:10] if l.strip()]})


if __name__ == "__main__":
    servir({
        ("GET", "/places"): place,
        ("GET", "/reservations"): reservations,
        ("POST", "/reservations"): reserver,
        ("POST", "/admin/panne"): panne,
        ("POST", "/admin/reset"): reset,
        ("GET", "/"): aide,
    })
