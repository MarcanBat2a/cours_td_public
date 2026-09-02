# L'image du site Ondine. Le code n'est PAS copié dedans : il est monté en
# volume par docker-compose, et uvicorn se recharge à chaque fichier
# enregistré. Vous éditez sur votre poste, le conteneur exécute.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 CASS_DRIVER_NO_CYTHON=1
WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
