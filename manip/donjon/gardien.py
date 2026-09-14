# Le gardien de la salle 6 a caché la clé dans une des 1 000 salles du
# donjon, numérotées de 1 à 1000. Il répond à chaque question, et il compte.
#
#   from gardien import question, questions_posees, nouvelle_partie
#   question(500)      → "plus haut", "plus bas" ou "trouvé"
#   questions_posees() → combien de questions depuis le début de la partie
#   nouvelle_partie()  → une autre salle secrète, compteur remis à zéro
#
# Le secret change à chaque partie mais reste le même pour tout le monde
# à la première partie : une graine fixe, pour comparer les compteurs.
import random

_rng = random.Random(2026)
_secret = _rng.randint(1, 1000)
_compteur = 0


def question(x):
    """Compare x à la salle secrète et compte la question."""
    global _compteur
    _compteur += 1
    if x < _secret:
        return "plus haut"
    if x > _secret:
        return "plus bas"
    return "trouvé"


def questions_posees():
    return _compteur


def nouvelle_partie():
    global _secret, _compteur
    _secret = _rng.randint(1, 1000)
    _compteur = 0
