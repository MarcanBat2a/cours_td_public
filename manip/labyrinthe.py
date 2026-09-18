"""Charger le labyrinthe du TD 9 sous la forme d'un graphe non orienté.

# : mur ; . : case libre ; D : départ. Les coordonnées (ligne, colonne)
commencent à 0. Chaque déplacement horizontal ou vertical a un poids de 1.
La fonction renvoie (graphe, depart). Elle est fournie aux étudiants.
"""

from pathlib import Path


def charger_labyrinthe(chemin="labyrinthe.txt"):
    lignes = Path(chemin).read_text(encoding="utf-8").splitlines()
    if not lignes or not lignes[0] or any(len(l) != len(lignes[0]) for l in lignes):
        raise ValueError("Le labyrinthe doit être une grille rectangulaire non vide.")
    if any(c not in "#.D" for ligne in lignes for c in ligne):
        raise ValueError("Les seuls caractères autorisés sont #, . et D.")

    departs = [(i, j) for i, ligne in enumerate(lignes) for j, c in enumerate(ligne) if c == "D"]
    if len(departs) != 1:
        raise ValueError("Le labyrinthe doit contenir exactement un départ D.")

    g = {(i, j): {} for i, ligne in enumerate(lignes) for j, c in enumerate(ligne) if c != "#"}
    for i, j in g:
        for voisin in ((i + 1, j), (i, j + 1)):
            if voisin in g:
                g[(i, j)][voisin] = 1
                g[voisin][(i, j)] = 1
    return g, departs[0]
