# Demande à PyPI la fiche d'un paquet : dernière version publiée, nombre de
# versions, résumé. Utilise la bibliothèque requests - qui doit donc être
# installée dans le Python qui lance ce script.
#
#   python version_pypi.py requests
#   python version_pypi.py networkx
import sys

import requests

nom = sys.argv[1] if len(sys.argv) > 1 else "requests"
reponse = requests.get(f"https://pypi.org/pypi/{nom}/json", timeout=10)
if reponse.status_code != 200:
    print(f"PyPI ne connaît pas « {nom} » (réponse {reponse.status_code})")
    sys.exit(1)

infos = reponse.json()
print("paquet            :", infos["info"]["name"])
print("dernière version  :", infos["info"]["version"])
print("versions publiées :", len(infos["releases"]))
print("résumé            :", infos["info"]["summary"])
print("requests utilisé  :", requests.__version__)
