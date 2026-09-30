"""Compare les tickets confirmés (le carnet) à ceux que contient la base (TD 8)."""

from commun import client

CARNET = "/tmp/confirmees.txt"


def intervalles(numeros):
    """[85, 86, 87, 90] -> '85 à 87, 90'."""
    morceaux, debut, precedent = [], None, None
    for n in numeros:
        if debut is None:
            debut = precedent = n
        elif n == precedent + 1:
            precedent = n
        else:
            morceaux.append((debut, precedent))
            debut = precedent = n
    if debut is not None:
        morceaux.append((debut, precedent))
    return ", ".join(str(a) if a == b else f"{a} à {b}" for a, b in morceaux)


with open(CARNET) as carnet:
    confirmes = [int(ligne) for ligne in carnet if ligne.strip()]
presents = {t["_id"] for t in client()["boutique"]["tickets"].find({}, {"_id": 1})}
perdus = [n for n in confirmes if n not in presents]
inattendus = sorted(presents - set(confirmes))

print(f"Tickets confirmés au client : {len(confirmes)}")
print(f"Retrouvés dans la base      : {len(confirmes) - len(perdus)}")
print(f"Confirmés puis perdus       : {len(perdus)}" + (f"  (n° {intervalles(perdus)})" if perdus else ""))
print(f"Présents sans confirmation  : {len(inattendus)}" + (f"  (n° {intervalles(inattendus)})" if inattendus else ""))
