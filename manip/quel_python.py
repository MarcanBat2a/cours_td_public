import sys

print("version      :", sys.version.split()[0])
print("exécutable   :", sys.executable)
print("préfixe      :", sys.prefix)
print("dans un venv :", sys.prefix != sys.base_prefix)
