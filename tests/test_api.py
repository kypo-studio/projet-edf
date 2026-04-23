"""
Smoke tests de l'API de prédiction EDF.
Nécessite : pytest, httpx, et les artefacts models/ + data/ présents.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    """Client de test avec démarrage/arrêt du lifespan (chargement modèle)."""
    with TestClient(app) as c:
        yield c


# ─────────────────────────────────────────────────────────────────────────────
# Health & Info
# ─────────────────────────────────────────────────────────────────────────────
def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["features_count"] == 15


def test_info(client):
    r = client.get("/info")
    assert r.status_code == 200
    data = r.json()
    assert "features" in data
    assert len(data["features"]) == 15


# ─────────────────────────────────────────────────────────────────────────────
# Prédiction — cas nominaux
# ─────────────────────────────────────────────────────────────────────────────
def test_predict_post(client):
    r = client.post("/predict", json={"date": "2024-01-15"})
    assert r.status_code == 200
    data = r.json()
    assert data["date"] == "2024-01-15"
    assert 20_000 < data["predicted_consumption_mw"] < 110_000


def test_predict_get(client):
    r = client.get("/predict/2024-07-14")
    assert r.status_code == 200
    data = r.json()
    assert data["is_holiday"] is True
    assert data["season"] == "Été"


def test_predict_weekend(client):
    r = client.get("/predict/2024-03-09")  # samedi
    assert r.status_code == 200
    assert r.json()["is_weekend"] is True


def test_predict_noel(client):
    r = client.get("/predict/2024-12-25")
    assert r.status_code == 200
    data = r.json()
    assert data["is_holiday"] is True
    assert data["season"] == "Hiver"


# ─────────────────────────────────────────────────────────────────────────────
# Prédiction — plage de dates
# ─────────────────────────────────────────────────────────────────────────────
def test_predict_range(client):
    r = client.get("/predict/range/2024-01-01/2024-01-07")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 7
    assert len(data["predictions"]) == 7


def test_predict_range_too_large(client):
    r = client.get("/predict/range/2023-01-01/2025-01-01")
    assert r.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# Prédiction — cas d'erreur
# ─────────────────────────────────────────────────────────────────────────────
def test_predict_invalid_date_format(client):
    r = client.post("/predict", json={"date": "25/12/2024"})
    assert r.status_code == 422


def test_predict_date_too_early(client):
    r = client.post("/predict", json={"date": "2010-01-01"})
    assert r.status_code == 422
