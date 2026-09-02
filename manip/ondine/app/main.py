"""Ondine - le site. Cinq pages, et un tableau de bord.

    /                    l'accueil : le Top 50 de la semaine, les dernières écoutes
    /catalogue           chercher, filtrer
    /contenu/{id}        la fiche, les avis, « écouter », « aussi écouté »
    /moi                 mes playlists, mon historique
    /connexion           qui êtes-vous aujourd'hui ?
    /etat                le tableau de bord : qui stocke quoi, et en combien de temps

Le code des pages ne parle à aucune base directement : il passe par
`stockage.catalogue()`, `stockage.top()`, ... et c'est `.env` qui décide.
"""
from __future__ import annotations

import logging
import time
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import config, horloge, mesure, stockage
from app.stockage import AFaire, BaseIndisponible

ICI = Path(__file__).parent
app = FastAPI(title="Ondine")
app.mount("/static", StaticFiles(directory=ICI / "static"), name="static")
gabarits = Jinja2Templates(directory=ICI / "templates")
journal = logging.getLogger("ondine")
logging.basicConfig(level=logging.INFO, format="%(message)s")


def duree_lisible(s) -> str:
    if s is None:
        return "-"
    h, reste = divmod(int(s), 3600)
    m, sec = divmod(reste, 60)
    return f"{h} h {m:02d}" if h else f"{m} min {sec:02d}"


gabarits.env.filters["duree"] = duree_lisible


# --------------------------------------------------------------- chrono
@app.middleware("http")
async def chronometre(request: Request, appel):
    debut = time.perf_counter()
    reponse = await appel(request)
    ms = (time.perf_counter() - debut) * 1000
    route = request.scope.get("route")
    nom = getattr(route, "path", request.url.path)
    if not nom.startswith("/static"):
        mesure.enregistrer(f"{request.method} {nom}", ms)
        journal.info("%s %s  %6.1f ms", request.method, request.url.path, ms)
    reponse.headers["X-Temps-ms"] = f"{ms:.1f}"
    return reponse


# --------------------------------------------------------------- erreurs
@app.exception_handler(AFaire)
async def mission(request: Request, e: AFaire):
    return gabarits.TemplateResponse(request, "erreur.html", {
        "titre": "C'est à vous", "message": str(e), "type": "mission"}, status_code=501)


@app.exception_handler(BaseIndisponible)
async def base_absente(request: Request, e: BaseIndisponible):
    return gabarits.TemplateResponse(request, "erreur.html", {
        "titre": "Une base ne répond pas", "message": str(e), "type": "base"}, status_code=503)


@app.exception_handler(Exception)
async def autre_erreur(request: Request, e: Exception):
    journal.exception("erreur sur %s", request.url.path)
    return gabarits.TemplateResponse(request, "erreur.html", {
        "titre": "Ça a cassé", "message": f"{type(e).__name__} : {e}", "type": "bug"}, status_code=500)


# ----------------------------------------------------------- utilitaires
def _moi(request: Request) -> dict | None:
    uid = request.cookies.get("ondine_u")
    return stockage.catalogue().utilisateur(uid) if uid else None


def _page(request: Request, gabarit: str, **contexte) -> HTMLResponse:
    contexte.setdefault("moi", _moi(request))
    contexte["roles"] = config.ROLES
    contexte["horloge"] = horloge.maintenant()
    return gabarits.TemplateResponse(request, gabarit, contexte)


def _page_contenu(id: str) -> dict | None:
    """Tout ce que la fiche affiche : le contenu, ses avis, son compteur, la
    recommandation. C'est ce bloc entier qui est mis en cache (chapitre 3) :
    la partie chère, c'est la recommandation, pas la fiche."""
    fiche = stockage.catalogue().fiche_contenu(id)
    if fiche is None:
        return None
    avis = stockage.catalogue().avis_du_contenu(id)
    for a in avis:
        a["date_txt"] = a["date"].strftime("%d/%m/%Y") if a.get("date") else ""
    depuis, jusqua = horloge.fenetre(config.RECO_FENETRE_JOURS)
    with mesure.Chrono() as c_reco:
        reco = stockage.reco().aussi_ecoute(id, depuis, jusqua, 5)
    return {"fiche": fiche, "avis": avis, "nb_ecoutes": stockage.historique().nb_ecoutes_contenu(id),
            "reco": reco, "reco_ms": c_reco.ms}


def _page_contenu_avec_cache(id: str) -> tuple[dict | None, bool]:
    """Cache-aside : on regarde dans le cache ; sinon on calcule, et on range
    le résultat pour CACHE_TTL_S secondes. Renvoie (page, servie_du_cache)."""
    cache = stockage.cache()
    cle = f"ondine:fiche:{id}"
    page = cache.lire(cle)
    if page is not None:
        return page, True
    page = _page_contenu(id)
    if page is not None:
        cache.ecrire(cle, page, config.CACHE_TTL_S)
    return page, False


def _invalider(id: str) -> None:
    """Après une écriture qui change la fiche : on retire la copie du cache.
    Sans ça, la fiche ment pendant CACHE_TTL_S secondes (chapitre 3, mission 4)."""
    stockage.cache().supprimer(f"ondine:fiche:{id}")


# ----------------------------------------------------------------- pages
@app.get("/", response_class=HTMLResponse)
def accueil(request: Request):
    depuis, jusqua = horloge.semaine()
    with mesure.Chrono() as c_top:
        top = stockage.top().top_semaine(depuis, jusqua, 50)
    titres = stockage.catalogue().fiches_contenus([cid for cid, _ in top])
    with mesure.Chrono() as c_dern:
        dernieres = stockage.historique().dernieres_ecoutes(10)
    titres.update(stockage.catalogue().fiches_contenus(
        [e["contenu_id"] for e in dernieres if e["contenu_id"] not in titres]))
    return _page(request, "accueil.html", top=top, titres=titres, dernieres=dernieres,
                 chrono={"top": c_top.ms, "dernieres": c_dern.ms}, depuis=depuis)


@app.get("/catalogue", response_class=HTMLResponse)
def catalogue(request: Request, type: str = "", genre: str = "", q: str = ""):
    cat = stockage.catalogue()
    types, genres = cat.types_et_genres()
    contenus = cat.lister_contenus(type or None, genre or None, q or None)
    return _page(request, "catalogue.html", contenus=contenus, types=types, genres=genres,
                 filtre={"type": type, "genre": genre, "q": q})


@app.get("/contenu/{id}", response_class=HTMLResponse)
def contenu(request: Request, id: str):
    with mesure.Chrono() as c_page:
        page, du_cache = _page_contenu_avec_cache(id)
    if page is None:
        return _page(request, "erreur.html", titre="Introuvable",
                     message=f"Aucun contenu {id}.", type="404")
    titres = stockage.catalogue().fiches_contenus([cid for cid, _ in page["reco"]])
    return _page(request, "contenu.html", c=page["fiche"], avis=page["avis"],
                 nb_ecoutes=page["nb_ecoutes"], reco=page["reco"], titres=titres,
                 chrono={"page": c_page.ms, "reco": page["reco_ms"], "du_cache": du_cache},
                 cache=stockage.cache().statistiques())


@app.post("/contenu/{id}/ecouter")
def ecouter(request: Request, id: str, plateforme: str = Form("web")):
    moi = _moi(request)
    if moi is None:
        return RedirectResponse("/connexion", status_code=303)
    quand = horloge.maintenant()
    stockage.historique().enregistrer_ecoute(moi["id"], id, quand, plateforme, 180)
    stockage.top().noter_ecoute(moi["id"], id, quand)
    _invalider(id)
    return RedirectResponse(f"/contenu/{id}", status_code=303)


@app.post("/contenu/{id}/avis")
def donner_avis(request: Request, id: str, note: int = Form(...), texte: str = Form("")):
    moi = _moi(request)
    if moi is None:
        return RedirectResponse("/connexion", status_code=303)
    stockage.catalogue().ajouter_avis(id, moi["id"], moi["pseudo"], note, texte.strip(),
                                      horloge.maintenant())
    _invalider(id)
    return RedirectResponse(f"/contenu/{id}", status_code=303)


@app.get("/moi", response_class=HTMLResponse)
def moi(request: Request):
    u = _moi(request)
    if u is None:
        return RedirectResponse("/connexion", status_code=303)
    historique = stockage.historique().historique_utilisateur(u["id"], 20)
    ids = {e["contenu_id"] for e in historique}
    for pl in u["playlists"]:
        ids.update(pl["contenus"])
    titres = stockage.catalogue().fiches_contenus(list(ids))
    return _page(request, "moi.html", moi=u, historique=historique, titres=titres)


@app.get("/connexion", response_class=HTMLResponse)
def connexion(request: Request):
    return _page(request, "connexion.html", utilisateurs=stockage.catalogue().utilisateurs())


@app.post("/connexion")
def se_connecter(utilisateur_id: str = Form(...)):
    reponse = RedirectResponse("/moi", status_code=303)
    reponse.set_cookie("ondine_u", utilisateur_id, httponly=True)
    return reponse


@app.post("/deconnexion")
def se_deconnecter():
    reponse = RedirectResponse("/", status_code=303)
    reponse.delete_cookie("ondine_u")
    return reponse


# ----------------------------------------------------------------- état
@app.get("/etat", response_class=HTMLResponse)
def etat(request: Request):
    return _page(request, "etat.html", bilan=mesure.bilan(), acces={
        "PG_DSN": config.PG_DSN, "MONGO_URL": config.MONGO_URL, "REDIS_URL": config.REDIS_URL,
        "NEO4J_URL": config.NEO4J_URL, "CASSANDRA_HOSTS": ",".join(config.CASSANDRA_HOSTS),
        "CASSANDRA_CL": config.CASSANDRA_CL, "CACHE_TTL_S": config.CACHE_TTL_S,
        "RECO_FENETRE_JOURS": config.RECO_FENETRE_JOURS})


@app.post("/etat/zero")
def etat_zero():
    mesure.remettre_a_zero()
    return RedirectResponse("/etat", status_code=303)


@app.get("/sante")
def sante():
    return {"ok": True, "horloge": horloge.maintenant().isoformat()}
