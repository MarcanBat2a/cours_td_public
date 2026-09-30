# L'atelier : il forme le replica set, charge les données, et porte les
# scripts Python des TD 4 et 8. Aucun script ne se lance depuis votre machine.
FROM python:3.12-slim
RUN pip install --no-cache-dir "pymongo==4.10.*"
ENV PYTHONUNBUFFERED=1 TZ=Europe/Paris
WORKDIR /atelier
COPY commun.py generer.py jeu_cours.py charger.py demarrer.py \
     vente_flash.py ecrire_en_continu.py verifier_ecritures.py \
     recherche.py serveur.py ./
COPY web/ ./web/
CMD ["python", "demarrer.py"]
