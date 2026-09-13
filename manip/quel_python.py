# Quel Python exécute ce fichier ? Quatre lignes de réponse.
# La dernière compare le préfixe du Python courant à celui du Python
# d'origine : dans un environnement virtuel, les deux diffèrent.
import sys

print("version      :", sys.version.split()[0])
print("exécutable   :", sys.executable)
print("préfixe      :", sys.prefix)
print("dans un venv :", sys.prefix != sys.base_prefix)
