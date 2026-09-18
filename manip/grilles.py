# Des graphes de taille réglable pour chronométrer les parcours (chapitre 4).
#
#   from grilles import grille
#   g = grille(30)          → 900 sommets, ~1 740 routes, poids 1 à 9, toujours les mêmes
#
# Une grille k × k : chaque case est un sommet (i, j), reliée à sa voisine de
# droite et à sa voisine du dessous. Le graphe est un dictionnaire
# sommet → {voisin: poids}, la forme du chapitre. Graine fixe : deux étudiants
# mesurent la même grille, seule la machine change.
import random


def grille(k):
    random.seed(4000 + k)
    g = {(i, j): {} for i in range(k) for j in range(k)}
    for i in range(k):
        for j in range(k):
            if j + 1 < k:
                p = random.randint(1, 9)
                g[(i, j)][(i, j + 1)] = p
                g[(i, j + 1)][(i, j)] = p
            if i + 1 < k:
                p = random.randint(1, 9)
                g[(i, j)][(i + 1, j)] = p
                g[(i + 1, j)][(i, j)] = p
    return g


def nb_routes(g):
    return sum(len(v) for v in g.values()) // 2
