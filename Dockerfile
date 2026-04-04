# ─────────────────────────────────────────────────────────────────────────────
# Image de base légère Python 3.11
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="EDF R&D IA"
LABEL description="API de prédiction de consommation électrique"
LABEL version="1.0.0"

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# ─────────────────────────────────────────────────────────────────────────────
# Dépendances système minimales
# ─────────────────────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

# ─────────────────────────────────────────────────────────────────────────────
# Dépendances Python (uniquement ce dont l'API a besoin)
# ─────────────────────────────────────────────────────────────────────────────
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# ─────────────────────────────────────────────────────────────────────────────
# Code applicatif + artefacts du modèle
# ─────────────────────────────────────────────────────────────────────────────
COPY main.py .
COPY static/ static/
COPY models/xgb_best.json  models/xgb_best.json
COPY models/features.json  models/features.json
COPY data/daily_consumption.csv data/daily_consumption.csv

# ─────────────────────────────────────────────────────────────────────────────
# Exposition du port et healthcheck
# ─────────────────────────────────────────────────────────────────────────────
EXPOSE ${PORT}

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# ─────────────────────────────────────────────────────────────────────────────
# Démarrage
# ─────────────────────────────────────────────────────────────────────────────
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
