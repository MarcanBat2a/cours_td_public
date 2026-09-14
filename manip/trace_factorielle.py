"""Exemple du cours : voir les appels et les retours de factorielle(3).

Lancer : python trace_factorielle.py
Ce programme sert à observer une trace, sans modifier recursif.py.
"""


def factorielle_trace(n, profondeur=0):
    """n est un entier >= 0 ; affiche sa trace et renvoie n!."""
    retrait = "  " * profondeur
    if n <= 1:
        print(f"{retrait}factorielle({n}) renvoie 1 (cas de base)")
        return 1
    print(f"{retrait}factorielle({n}) attend {n} * factorielle({n - 1})")
    precedent = factorielle_trace(n - 1, profondeur + 1)
    resultat = n * precedent
    print(f"{retrait}factorielle({n}) reprend : {n} * {precedent} = {resultat}")
    return resultat


if __name__ == "__main__":
    resultat = factorielle_trace(3)
    print(f"Résultat final : {resultat}")
