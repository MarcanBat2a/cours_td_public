"""Le catalogue du concert C17, recopié sur deux machines (cat-a et cat-b).

Chaque copie répond seule, avec ce qu'elle sait. Toutes les secondes, elle
demande à l'autre copie son état et fusionne les deux.

    GET  /description                  la description vue par CETTE copie
    PUT  /description                  {"valeur": "Ouverture à 20 h"}
    POST /admin/horloge                {"decalage": -300}   (secondes)
    POST /admin/fusion                 {"mode": "horodatage" | "conflits"}
    POST /admin/reset                  tout remettre à zéro, sur les deux copies

Fusion « horodatage » : en cas d'écritures concurrentes, la version au plus
grand horodatage gagne. Fusion « conflits » : les deux versions sont gardées,
un opérateur tranche par un nouveau PUT.
"""
import json
import os
import threading
import time
import urllib.request

from commun import heure, servir

NOEUD = os.environ.get("NOEUD", "A")
PAIR = os.environ.get("PAIR", "cat-b")
INITIALE = "Ouverture des portes : horaire à confirmer"

verrou = threading.Lock()
etat: dict = {}
contact = {"dernier": None}


def remettre_a_zero(generation: float) -> None:
    etat.clear()
    etat.update(
        generation=generation,
        mode="horodatage",
        decalage=0,
        versions=[{"valeur": INITIALE, "ts": 0.0, "noeud": "-", "vv": {}}],
    )


remettre_a_zero(0.0)


def horloge() -> float:
    """L'heure de CETTE machine, décalage compris."""
    return time.time() + etat["decalage"]


def domine(v: dict, w: dict) -> bool:
    """w a vu tout ce que v a vu, et plus : v est une version périmée."""
    cles = set(v["vv"]) | set(w["vv"])
    return v["vv"] != w["vv"] and all(v["vv"].get(k, 0) <= w["vv"].get(k, 0) for k in cles)


def fusionner(versions: list[dict], mode: str) -> list[dict]:
    uniques = {json.dumps(v["vv"], sort_keys=True): v for v in versions}
    restantes = [v for v in uniques.values() if not any(domine(v, w) for w in uniques.values())]
    if mode == "horodatage" and len(restantes) > 1:
        gagnante = max(restantes, key=lambda v: (v["ts"], v["noeud"]))
        cles = {k for v in restantes for k in v["vv"]}
        vv = {k: max(v["vv"].get(k, 0) for v in restantes) for k in cles}
        restantes = [{**gagnante, "vv": vv}]
    return sorted(restantes, key=lambda v: (v["ts"], v["noeud"]))


def synchroniser() -> None:
    while True:
        time.sleep(1)
        try:
            with urllib.request.urlopen(f"http://{PAIR}:8000/interne/etat", timeout=1) as r:
                autre = json.load(r)
        except Exception:
            continue
        with verrou:
            contact["dernier"] = time.time()
            if autre["generation"] > etat["generation"]:
                etat.update(generation=autre["generation"], mode=autre["mode"],
                            versions=autre["versions"], decalage=0)
            elif autre["generation"] == etat["generation"]:
                etat["versions"] = fusionner(etat["versions"] + autre["versions"], etat["mode"])


def vue() -> dict:
    dernier = contact["dernier"]
    joignable = dernier is not None and time.time() - dernier < 3
    return {
        "copie": NOEUD,
        "horloge_de_la_copie": heure(horloge()),
        "copie_voisine": "joignable" if joignable else (
            f"injoignable depuis {heure(dernier)}" if dernier else "jamais jointe"),
        "fusion": etat["mode"],
        "versions": [
            {"valeur": v["valeur"],
             "horodatage": heure(v["ts"]) if v["ts"] else "-",
             "ecrite_sur": v["noeud"]}
            for v in etat["versions"]
        ],
    }


def lire(h, _reste):
    with verrou:
        h.repondre(200, vue())


def ecrire(h, _reste):
    valeur = h.corps.get("valeur")
    if not valeur:
        return h.repondre(400, {"erreur": 'corps attendu : {"valeur": "Ouverture à 20 h"}'})
    with verrou:
        cles = {k for v in etat["versions"] for k in v["vv"]}
        vv = {k: max(v["vv"].get(k, 0) for v in etat["versions"]) for k in cles}
        vv[NOEUD] = vv.get(NOEUD, 0) + 1
        etat["versions"] = [{"valeur": valeur, "ts": horloge(), "noeud": NOEUD, "vv": vv}]
        h.repondre(200, vue())


def regler_horloge(h, _reste):
    decalage = h.corps.get("decalage")
    if not isinstance(decalage, (int, float)):
        return h.repondre(400, {"erreur": 'corps attendu : {"decalage": -300}'})
    with verrou:
        etat["decalage"] = decalage
        h.repondre(200, {"copie": NOEUD, "decalage_s": decalage,
                         "horloge_de_la_copie": heure(horloge()), "heure_reelle": heure(time.time())})


def prevenir_pair(chemin: str, corps: dict) -> str:
    requete = urllib.request.Request(
        f"http://{PAIR}:8000{chemin}", data=json.dumps(corps).encode(), method="POST",
        headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(requete, timeout=1).read()
        return "appliqué aussi sur la copie voisine"
    except Exception:
        return "copie voisine injoignable : réglage appliqué ICI seulement"


def regler_fusion(h, _reste):
    mode = h.corps.get("mode")
    if mode not in ("horodatage", "conflits"):
        return h.repondre(400, {"erreur": "modes possibles : horodatage, conflits"})
    with verrou:
        etat["mode"] = mode
    voisin = prevenir_pair("/interne/fusion", {"mode": mode}) if not h.path.startswith("/interne") else ""
    h.repondre(200, {"copie": NOEUD, "fusion": mode, "voisine": voisin})


def reset(h, _reste):
    generation = time.time()
    with verrou:
        remettre_a_zero(generation)
    voisin = prevenir_pair("/interne/reset", {"generation": generation}) \
        if not h.path.startswith("/interne") else ""
    h.repondre(200, {"copie": NOEUD, "statut": "catalogue remis à zéro", "voisine": voisin})


def reset_interne(h, _reste):
    with verrou:
        remettre_a_zero(h.corps.get("generation", time.time()))
    h.repondre(200, {"copie": NOEUD})


def etat_interne(h, _reste):
    with verrou:
        h.repondre(200, {k: etat[k] for k in ("generation", "mode", "versions")})


if __name__ == "__main__":
    threading.Thread(target=synchroniser, daemon=True).start()
    servir({
        ("GET", "/description"): lire,
        ("PUT", "/description"): ecrire,
        ("POST", "/admin/horloge"): regler_horloge,
        ("POST", "/admin/fusion"): regler_fusion,
        ("POST", "/admin/reset"): reset,
        ("POST", "/interne/fusion"): regler_fusion,
        ("POST", "/interne/reset"): reset_interne,
        ("GET", "/interne/etat"): etat_interne,
    })
