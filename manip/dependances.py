# Ce qu'uv installe quand on demande requests et rich (chapitre 1, TD 2 et 3) :
# un graphe ORIENTÉ - une flèche de A vers B veut dire « A a besoin de B ».
#
#   from dependances import DEPEND_DE
#
# Les noms sont ceux de `uv tree`. Le graphe sert au TD 9 : dans quel ordre
# installer, pour qu'un paquet arrive toujours après ce dont il a besoin ?

DEPEND_DE = {
    "requests": ["charset-normalizer", "idna", "urllib3", "certifi"],
    "rich": ["markdown-it-py", "pygments"],
    "markdown-it-py": ["mdurl"],
    "charset-normalizer": [],
    "idna": [],
    "urllib3": [],
    "certifi": [],
    "pygments": [],
    "mdurl": [],
}
