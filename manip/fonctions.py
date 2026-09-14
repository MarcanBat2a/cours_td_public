# Huit fonctions à lire. Pour chacune : combien d'opérations en fonction de n,
# la taille de la liste (ou la valeur de n pour f4) ? On répond en lisant,
# puis on vérifie au chronomètre.


def f1(t):
    return t[0] + t[-1]


def f2(t):
    total = 0
    for x in t:
        total += x
    return total


def f3(t):
    paires = 0
    for x in t:
        for y in t:
            if x + y == 0:
                paires += 1
    return paires


def f4(n):
    etapes = 0
    while n > 1:
        n = n // 2
        etapes += 1
    return etapes


def f5(t):
    communs = 0
    autres = list(range(0, len(t), 2))
    for x in t:
        if x in autres:
            communs += 1
    return communs


def f6(t):
    return sorted(t)[0]


def f7(t):
    resultat = []
    for x in t:
        resultat.insert(0, x)
    return resultat


def f8(t):
    total = 0
    for i in range(len(t)):
        for j in range(i):
            total += t[i] * t[j]
    return total
