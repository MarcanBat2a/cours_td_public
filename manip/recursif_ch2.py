# Les fonctions récursives du chapitre 2, fournies : le chapitre 3 se fait
# sans avoir écrit les vôtres. `fib` et `puissance` ajoutent 1 à la globale
# `appels` à chaque entrée dans la fonction.
#
#   import recursif_ch2
#   recursif_ch2.appels = 0            # avant chaque mesure
#   recursif_ch2.fib(20)
#   print(recursif_ch2.appels)
#
# Lire et remettre à zéro le compteur par `recursif_ch2.appels` :
# `from recursif_ch2 import appels` n'en copierait que la valeur du moment.

appels = 0


def fib(n):
    """n >= 0 ; le n-ième nombre de Fibonacci, sans mémoire."""
    global appels
    appels += 1
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def puissance(x, n):
    """n >= 0 ; x puissance n, l'exposant diminue de 1 à chaque appel."""
    global appels
    appels += 1
    if n == 0:
        return 1
    return x * puissance(x, n - 1)


def somme(t):
    """Le premier élément plus la somme du reste."""
    if not t:
        return 0
    return t[0] + somme(t[1:])


def etapes(n):
    """n >= 1 ; nombre de transformations de Collatz jusqu'à 1."""
    compteur = 0
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        compteur += 1
    return compteur
