# Chronométrer une fonction, et voir comment son temps grandit avec n.
#
#   from chrono import chrono, tableau
#   chrono(tri_insertion, liste)              → durée en secondes, meilleur de 3 essais
#   tableau(tri_insertion, [100, 1000, 10000]) → n, temps, et le rapport d'une ligne à l'autre
#
# Le générateur par défaut fabrique une liste d'entiers aléatoires de taille n,
# toujours la même pour un n donné (graine fixe) : deux binômes mesurent la
# même liste, seule la machine change.
import random
import time


def chrono(f, *args, repetitions=3):
    """Le meilleur temps de `repetitions` exécutions de f(*args), en secondes."""
    meilleur = None
    for _ in range(repetitions):
        debut = time.perf_counter()
        f(*args)
        duree = time.perf_counter() - debut
        if meilleur is None or duree < meilleur:
            meilleur = duree
    return meilleur


def liste_aleatoire(n):
    """n entiers distincts, toujours les mêmes pour un même n."""
    random.seed(2026 + n)
    return random.sample(range(10 * n + 10), n)


def tableau(f, tailles, generateur=liste_aleatoire, repetitions=3):
    """Affiche n, le temps de f sur une entrée de taille n, et le rapport entre lignes."""
    precedent = None
    print(f"{'n':>10} {'temps (s)':>12} {'rapport':>9}")
    for n in tailles:
        entree = generateur(n)
        duree = chrono(f, entree, repetitions=repetitions)
        rapport = "" if precedent is None else f"x {duree / precedent:.1f}"
        print(f"{n:>10} {duree:>12.6f} {rapport:>9}")
        precedent = duree
