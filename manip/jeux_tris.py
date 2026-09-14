"""Jeux reproductibles : une graine par série, tailles tirées dans l'ordre.

    from jeux_tris import jeux_selection, jeux_fusion
    listes = jeux_fusion()  # la même série à chaque appel

Comparer plusieurs tris sur les mêmes listes, sans modifier leurs entrées.
"""
import random


def jeux_selection():
    rng = random.Random(2026)
    return {n: rng.sample(range(100000), n) for n in (10, 100, 1000)}


def jeux_fusion():
    rng = random.Random(2026)
    return {n: rng.sample(range(10**6), n) for n in (10, 100, 1000, 10000)}
