# Point de départ du TD 4, pour une séance qui commence directement à ce TD.
#
# Ce fichier contient déjà les trois fonctions écrites au TD 2 : le chargement
# des routes et les deux accès au graphe. Le TD 4 les utilise sans les réécrire.
#
#   cp depart-td4/graphes.py graphes.py      depuis algo3/chapitre4/
#
# Vous ajouterez ensuite vos propres fonctions à la suite, TD après TD.
# Les fonctions ci-dessous ne sont plus à modifier.
#
# La représentation du chapitre : un graphe est un dictionnaire
#   {commune: {commune voisine: distance en kilomètres}}
# Une route à double sens est enregistrée dans les deux sens, donc deux fois.
#
#   from graphes import charger_routes, voisins, km
#   g = charger_routes("routes.csv")  → 24 communes, 32 routes
#   voisins(g, "Isulacciu")           → ['Caldarella', 'Finosella']
#   km(g, "Isulacciu", "Caldarella")  → 6
import csv


def charger_routes(chemin):
    """Lit le CSV des routes et renvoie {commune: {voisine: distance}}."""
    g = {}
    with open(chemin, encoding="utf-8") as f:
        for ligne in csv.DictReader(f):
            a = ligne["depart"]
            b = ligne["arrivee"]
            distance = int(ligne["km"])
            g.setdefault(a, {})[b] = distance
            g.setdefault(b, {})[a] = distance
    return g


def voisins(g, s):
    """La liste des communes voisines de `s`, dans l'ordre alphabétique.

    Tous les parcours du chapitre visitent les voisins dans cet ordre : deux
    étudiants obtiennent donc le même ordre de visite.
    """
    return sorted(g[s])


def km(g, a, b):
    """La distance de la route entre `a` et `b`, deux communes reliées.

    Sans route entre les deux, Python signale une `KeyError` : les TD
    n'appellent cette fonction que sur des communes voisines.
    """
    return g[a][b]
