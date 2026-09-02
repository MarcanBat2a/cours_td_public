"""CACHE=aucun : pas de cache. Chaque fiche est relue dans le catalogue."""


def lire(cle: str):
    return None


def ecrire(cle: str, valeur, ttl_s: int) -> None:
    pass


def supprimer(cle: str) -> None:
    pass


def statistiques() -> dict:
    return {"actif": False}
