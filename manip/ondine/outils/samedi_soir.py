"""Samedi soir : tout le monde ouvre Ondine en même temps.

    docker compose exec web python -m outils.samedi_soir
    docker compose exec web python -m outils.samedi_soir --clients 40 --duree 30

Lance N clients qui, pendant D secondes, font ce que font les gens un samedi
soir : l'accueil, une fiche, une recherche, une écoute. À la fin, le verdict :
requêtes par seconde, temps de réponse médian et p95, par page.

C'est le boss de fin de niveau. Chaque chapitre, vous le rejouez, et vous
comparez. Le chiffre qui compte est le p95 : « 95 % des visiteurs ont attendu
moins que ça ». La moyenne ment, elle cache les gens qui sont partis.
"""
from __future__ import annotations

import argparse
import asyncio
import random
import time
from collections import defaultdict

import httpx

BASE = "http://localhost:8000"
CONTENUS = ([f"a{i:03d}" for i in range(1, 221)] + [f"p{i:03d}" for i in range(1, 91)]
            + [f"l{i:03d}" for i in range(1, 51)] + [f"c{i:03d}" for i in range(1, 41)])
MOTS = ["refuge", "hiver", "orage", "lise", "port", "nuit", "jazz", "voix"]


async def client(no: int, fin: float, temps: dict, erreurs: list, seed: int) -> None:
    r = random.Random(seed + no)
    uid = f"u{r.randint(1, 60):02d}"
    async with httpx.AsyncClient(base_url=BASE, cookies={"ondine_u": uid}, timeout=60) as http:
        while time.perf_counter() < fin:
            tirage = r.random()
            if tirage < 0.40:
                page, requete = "GET /", http.get("/")
            elif tirage < 0.75:
                cid = r.choice(CONTENUS)
                page, requete = "GET /contenu/{id}", http.get(f"/contenu/{cid}")
            elif tirage < 0.90:
                page, requete = "GET /catalogue", http.get("/catalogue", params={"q": r.choice(MOTS)})
            else:
                cid = r.choice(CONTENUS)
                page, requete = "POST /contenu/{id}/ecouter", http.post(
                    f"/contenu/{cid}/ecouter", data={"plateforme": "web"}, follow_redirects=False)
            debut = time.perf_counter()
            try:
                reponse = await requete
                ms = (time.perf_counter() - debut) * 1000
                if reponse.status_code >= 500:
                    erreurs.append((page, reponse.status_code))
                else:
                    temps[page].append(ms)
            except Exception as e:  # timeout, connexion refusée
                erreurs.append((page, type(e).__name__))
            await asyncio.sleep(r.uniform(0.05, 0.3))  # le temps de lire


def percentile(v: list[float], p: float) -> float:
    if not v:
        return 0.0
    t = sorted(v)
    return t[min(len(t) - 1, int(round(p * (len(t) - 1))))]


async def principal(clients: int, duree: int, seed: int) -> None:
    temps: dict[str, list[float]] = defaultdict(list)
    erreurs: list = []
    print(f"→ samedi soir : {clients} clients pendant {duree} s…")
    debut = time.perf_counter()
    fin = debut + duree
    await asyncio.gather(*(client(i, fin, temps, erreurs, seed) for i in range(clients)))
    ecoule = time.perf_counter() - debut
    total = sum(len(v) for v in temps.values())

    print()
    print(f"  {'page':28} {'req':>6} {'p50':>9} {'p95':>9} {'max':>9}")
    for page in sorted(temps, key=lambda p: -percentile(temps[p], 0.95)):
        v = temps[page]
        print(f"  {page:28} {len(v):>6} {percentile(v, .5):>7.0f} ms {percentile(v, .95):>7.0f} ms {max(v):>7.0f} ms")
    tout = [ms for v in temps.values() for ms in v]
    print("  " + "-" * 66)
    print(f"  {'toutes pages':28} {total:>6} {percentile(tout, .5):>7.0f} ms {percentile(tout, .95):>7.0f} ms {max(tout) if tout else 0:>7.0f} ms")
    print()
    print(f"  {total / ecoule:.1f} requêtes par seconde, {len(erreurs)} erreurs")
    if erreurs:
        par_type = defaultdict(int)
        for page, quoi in erreurs:
            par_type[(page, quoi)] += 1
        for (page, quoi), n in sorted(par_type.items(), key=lambda x: -x[1])[:5]:
            print(f"    {n:>5} × {page} : {quoi}")
    p95 = percentile(tout, .95)
    verdict = ("les gens sont partis" if p95 > 2000 else
               "ça rame, on le sent" if p95 > 500 else
               "correct, sans plus" if p95 > 100 else "fluide")
    print(f"\n  Verdict : p95 = {p95:.0f} ms - {verdict}.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--clients", type=int, default=20)
    p.add_argument("--duree", type=int, default=20, help="secondes")
    p.add_argument("--seed", type=int, default=1)
    a = p.parse_args()
    asyncio.run(principal(a.clients, a.duree, a.seed))
