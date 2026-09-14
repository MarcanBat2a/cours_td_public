# Le donjon : lance-le après chaque TD pour voir les salles s'ouvrir.
#
#   python donjon.py
#
# Chaque salle appelle une fonction que vous avez écrite dans un de vos
# fichiers (entree.py, compagnie.py, guildes.py, scores.py, tris.py,
# recherche.py, recursif.py, labyrinthe.py). Une fonction absente ou
# fausse laisse la porte fermée ; le message dit laquelle. Rien ici n'est
# à modifier.
import importlib
import random

from aventuriers import AVENTURIERS

OUVERTE, FERMEE = "ouverte", "fermée"


def charger(module, nom):
    """La fonction `nom` du fichier `module`.py, ou None."""
    try:
        return getattr(importlib.import_module(module), nom)
    except (ImportError, AttributeError):
        return None


def salle(numero, titre, module, nom, verification):
    f = charger(module, nom)
    if f is None:
        print(f"  Salle {numero} - {titre:<22} porte {FERMEE:<8} il manque {nom}() dans {module}.py")
        return False
    try:
        ok, detail = verification(f)
    except Exception as e:  # une fonction qui plante ne ferme pas le donjon
        ok, detail = False, f"{type(e).__name__}: {e}"
    etat = OUVERTE if ok else FERMEE
    print(f"  Salle {numero} - {titre:<22} porte {etat:<8} {detail}")
    return ok


# --- les vérifications : (vrai/faux, ce qu'on affiche) --------------------

def v_etapes(f):
    return f(27) == 111, f"etapes(27) = {f(27)}"

def v_maximum(f):
    for valeurs, attendu in (
        ([12, 47, 3, 91, 25, 68, 91, 7], (91, 3)),
        ([-8, -3, -5], (-3, 1)),
        ([7], (7, 0)),
        ([4, 4, 4], (4, 0)),
    ):
        valeur, position = f(list(valeurs))
        if type(position) is not int or (valeur, position) != attendu:
            return False, f"sur {valeurs} : attendu {attendu}, reçu {(valeur, position)}"
    return True, "maximum et première position vérifiés, y compris négatifs et ex æquo"

def v_plus_riche(f):
    a = f(AVENTURIERS)
    return a["nom"] == "Maëlle", f"{a['nom']} avec {a['or']} pièces"

def v_par_guilde(f):
    d = f(AVENTURIERS)
    return d.get("Ombre") == 7190, ", ".join(f"{g} {v}" for g, v in sorted(d.items()))

def v_charger(f):
    return f("aventuriers.csv") == AVENTURIERS, "le CSV redonne exactement AVENTURIERS"

def v_classement(f):
    noms = [a["nom"] for a in f(AVENTURIERS)][:3]
    return noms == ["Maëlle", "Ysolde", "Fenna"], "podium : " + ", ".join(noms)

def v_tri(nom):
    def v(f):
        rng = random.Random(2026)
        cas = ([], [7], [2, 2, 1], [-3, 0, -8], [1, 2, 3], [3, 2, 1],
               rng.sample(range(100000), 200))
        for t in cas:
            avant = list(t)
            triee, comparaisons = f(t)
            if triee != sorted(avant):
                return False, f"{nom} : résultat incorrect sur {avant}"
            if t != avant:
                return False, f"{nom} : l'entrée doit rester inchangée"
            if type(comparaisons) is not int or comparaisons < 0:
                return False, f"{nom} : le compteur doit être un entier positif ou nul"
            if (len(avant) < 2 and comparaisons != 0) or (len(avant) >= 2 and comparaisons == 0):
                return False, f"{nom} : compteur incohérent pour {len(avant)} valeurs"
        return True, f"cas limites et entrée inchangée vérifiés ; 200 cartes, {comparaisons} comparaisons"
    return v

def v_dichotomie(f):
    t = sorted(a["niveau"] for a in AVENTURIERS)
    i, n = f(t, 9)
    return t[i] == 9, f"niveau 9 trouvé en {n} regards"

def v_deviner(f):
    import gardien
    gardien.nouvelle_partie()
    salle_secrete = f(gardien.question)
    n = gardien.questions_posees()
    return gardien.question(salle_secrete) == "trouvé" and n <= 10, f"la clé en salle {salle_secrete}, en {n} questions"

def v_fib(f):
    resultat = f(5)
    return resultat == 5, f"fib(5) = {resultat}"


def v_tri_fusion(f):
    rng = random.Random(2026)
    for t in ([], [7], [2, 2, 1], [-3, 0, -8], rng.sample(range(100000), 200)):
        avant = list(t)
        resultat = f(t)
        if resultat != sorted(avant) or t != avant:
            return False, "résultat incorrect ou entrée modifiée"
    return True, "fusion vérifiée : liste vide, doublons et 200 cartes"

def v_compter_cases(f):
    grille = [list(l) for l in open("labyrinthe.txt").read().splitlines()]
    i, j = next((i, l.index("D")) for i, l in enumerate(grille) if "D" in l)
    n = f(grille, i, j)
    return n == 43, f"{n} salles atteignables depuis D"


SALLES = [
    (1, "Le sort du magicien", "entree", "etapes", v_etapes),
    (1, "Le meilleur score", "entree", "maximum", v_maximum),
    (2, "La compagnie", "compagnie", "plus_riche", v_plus_riche),
    (3, "Les guildes", "guildes", "par_guilde", v_par_guilde),
    (3, "Le registre", "guildes", "charger", v_charger),
    (4, "Le tableau des scores", "scores", "classement", v_classement),
    (5, "La main de cartes", "tris", "tri_selection", v_tri("tri_selection")),
    (5, "La main de cartes", "tris", "tri_insertion", v_tri("tri_insertion")),
    (6, "Le gardien", "recherche", "recherche_dichotomique", v_dichotomie),
    (6, "Le gardien", "recherche", "deviner", v_deviner),
    (7, "L'escalier", "recursif", "fib", v_fib),
    (8, "Le tournoi", "tris", "tri_fusion", v_tri_fusion),
    (9, "Le labyrinthe", "labyrinthe", "compter_cases", v_compter_cases),
]

if __name__ == "__main__":
    print("Le donjon\n")
    ouvertes = sum(salle(*s) for s in SALLES)
    print(f"\n{ouvertes} porte(s) ouverte(s) sur {len(SALLES)}.")
    if ouvertes == len(SALLES):
        print("Le trésor est à vous.")
