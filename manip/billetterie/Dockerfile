# Guichet, catalogue et poste : la même image, lancée avec des commandes différentes.
FROM python:3.12-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir "psycopg[binary]==3.2.*" tzdata
ENV PYTHONUNBUFFERED=1 TZ=Europe/Paris
WORKDIR /app
COPY commun.py guichet.py catalogue.py ./
