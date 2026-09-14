# Un programme qui marche, et qui est lent. Trois causes, trois remèdes du
# chapitre. Lancez-le, chronométrez chaque partie, puis réparez.
#
#   python lent.py
import random
import time

random.seed(2026)
N = 10000
IDENTIFIANTS = random.sample(range(1, 200000), N)
IDENTIFIANTS.append(IDENTIFIANTS[N // 2])       # un doublon, un seul
REQUETES = [random.choice(IDENTIFIANTS) if i % 2 else random.randrange(1, 200000)
            for i in range(N)]
CANTONS = ["Littoral", "Montagne", "Vallée", "Plateau"]
HABITANTS = [(random.choice(CANTONS), random.randrange(1, 500)) for _ in range(N)]
DEMANDES = [random.choice(CANTONS) for _ in range(N)]


def part1_connus(requetes, identifiants):
    """Combien de requêtes portent sur un identifiant connu ?"""
    connus = 0
    for r in requetes:
        if r in identifiants:
            connus += 1
    return connus


def part2_doublons(identifiants):
    """Y a-t-il des identifiants en double ?"""
    doublons = []
    for i in range(len(identifiants)):
        for j in range(i + 1, len(identifiants)):
            if identifiants[i] == identifiants[j]:
                doublons.append(identifiants[i])
    return doublons


def part3_populations(demandes, habitants):
    """Pour chaque demande, la population totale du canton demandé."""
    reponses = []
    for canton in demandes:
        total = 0
        for c, pop in habitants:
            if c == canton:
                total += pop
        reponses.append(total)
    return reponses


if __name__ == "__main__":
    for nom, f, args in [
        ("part1_connus", part1_connus, (REQUETES, IDENTIFIANTS)),
        ("part2_doublons", part2_doublons, (IDENTIFIANTS,)),
        ("part3_populations", part3_populations, (DEMANDES, HABITANTS)),
    ]:
        debut = time.perf_counter()
        resultat = f(*args)
        duree = time.perf_counter() - debut
        apercu = resultat if not isinstance(resultat, list) else f"{len(resultat)} valeurs, somme {sum(resultat)}"
        print(f"{nom:20} {duree:8.3f} s   {apercu}")
