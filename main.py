import json
import logging
import math
import time
from contextlib import asynccontextmanager
from datetime import date, timedelta
from typing import Optional

import numpy as np
import pandas as pd
import xgboost as xgb
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, field_validator

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("edf-api")

# ---------------------------------------------------------------------------
# State global chargé au démarrage
# ---------------------------------------------------------------------------
state: dict = {}


def _french_holidays(years: range) -> set:
    """Jours fériés français (algorithme de Butcher pour Pâques)."""
    def easter(year: int) -> date:
        a = year % 19
        b, c = divmod(year, 100)
        d, e = divmod(b, 4)
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i, k = divmod(c, 4)
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        month, day = divmod(114 + h + l - 7 * m, 31)
        return date(year, month, day + 1)

    holidays: set = set()
    for y in years:
        e = easter(y)
        holidays |= {
            date(y, 1, 1),
            e + timedelta(1),
            date(y, 5, 1),
            date(y, 5, 8),
            e + timedelta(39),
            e + timedelta(50),
            date(y, 7, 14),
            date(y, 8, 15),
            date(y, 11, 1),
            date(y, 11, 11),
            date(y, 12, 25),
        }
    return holidays


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Chargement du modèle et des données historiques...")
    t0 = time.time()

    model = xgb.XGBRegressor()
    model.load_model("models/xgb_best.json")

    with open("models/features.json") as f:
        features = json.load(f)

    df = pd.read_csv("data/daily_consumption.csv", parse_dates=["Date"])
    df = df.set_index("Date").sort_index()

    state["model"]    = model
    state["features"] = features
    state["history"]  = df
    state["holidays"] = _french_holidays(range(2010, 2035))

    logger.info(
        "Prêt en %.2fs — modèle: xgb_best, historique: %d jours",
        time.time() - t0,
        len(df),
    )
    yield
    state.clear()


# ---------------------------------------------------------------------------
# Application FastAPI
# ---------------------------------------------------------------------------
app = FastAPI(
    title="EDF — API de prédiction de consommation électrique",
    description=(
        "Prédit la consommation électrique journalière (MW) en France "
        "à partir de données RTE éco2mix (2012–2024)."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Middleware : log chaque requête avec sa durée
# ---------------------------------------------------------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    t0 = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - t0) * 1000, 1)
    logger.info(
        "%s %s → %s (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


# ---------------------------------------------------------------------------
# Schémas Pydantic
# ---------------------------------------------------------------------------
class PredictionRequest(BaseModel):
    date: str

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError("Format attendu : YYYY-MM-DD")
        return v


class PredictionResponse(BaseModel):
    date: str
    predicted_consumption_mw: float
    is_weekend: bool
    is_holiday: bool
    season: str


class HealthResponse(BaseModel):
    status: str
    model: str
    history_start: str
    history_end: str
    features_count: int


# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------
SEASON_MAP = {
    12: "Hiver", 1: "Hiver",  2: "Hiver",
    3: "Printemps", 4: "Printemps", 5: "Printemps",
    6: "Été",   7: "Été",    8: "Été",
    9: "Automne", 10: "Automne", 11: "Automne",
}


def _build_features(target_date: date) -> dict:
    """Calcule le vecteur de features pour une date donnée."""
    df: pd.DataFrame = state["history"]
    holidays: set    = state["holidays"]

    d     = pd.Timestamp(target_date)
    month = target_date.month
    doy   = d.dayofyear
    dow   = target_date.weekday()

    feat: dict = {
        "month_sin": math.sin(2 * math.pi * month / 12),
        "month_cos": math.cos(2 * math.pi * month / 12),
        "doy_sin":   math.sin(2 * math.pi * doy / 365),
        "doy_cos":   math.cos(2 * math.pi * doy / 365),
        "dow_sin":   math.sin(2 * math.pi * dow / 7),
        "dow_cos":   math.cos(2 * math.pi * dow / 7),
        "is_weekend": int(dow >= 5),
        "is_holiday": int(target_date in holidays),
    }

    fallback = float(df["conso_mean_mw"].mean())

    for lag in [1, 7, 14, 30, 365]:
        lag_ts = d - pd.Timedelta(days=lag)
        feat[f"lag_{lag}"] = (
            float(df.loc[lag_ts, "conso_mean_mw"])
            if lag_ts in df.index
            else fallback
        )

    prev_day = d - pd.Timedelta(days=1)

    window_7  = df.loc[d - pd.Timedelta(days=7)  : prev_day, "conso_mean_mw"]
    window_30 = df.loc[d - pd.Timedelta(days=30) : prev_day, "conso_mean_mw"]
    feat["roll_7"]  = float(window_7.mean())  if len(window_7)  > 0 else feat["lag_1"]
    feat["roll_30"] = float(window_30.mean()) if len(window_30) > 0 else feat["lag_1"]

    return feat


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
def health():
    """Vérifie que le service est opérationnel."""
    df: pd.DataFrame = state["history"]
    return HealthResponse(
        status="ok",
        model="xgb_best",
        history_start=str(df.index.min().date()),
        history_end=str(df.index.max().date()),
        features_count=len(state["features"]),
    )


@app.get("/info", tags=["Monitoring"])
def info():
    """Retourne les métadonnées du modèle et la liste des features."""
    return {
        "model": "XGBoost (xgb_best.json)",
        "features": state["features"],
        "target": "conso_mean_mw (MW moyen journalier)",
        "training_period": "2013–2021",
        "validation_period": "2022",
        "test_period": "2023–2024",
    }


@app.post("/predict", response_model=PredictionResponse, tags=["Prédiction"])
def predict(request: PredictionRequest):
    """
    Prédit la consommation électrique journalière pour une date donnée.

    La date doit être postérieure au 1er janvier 2013 (nécessaire pour les lags).
    """
    target_date = date.fromisoformat(request.date)

    min_date = date(2013, 1, 1)
    if target_date < min_date:
        raise HTTPException(
            status_code=422,
            detail=f"La date doit être ≥ {min_date} (données insuffisantes pour les lags).",
        )

    feat = _build_features(target_date)
    X    = np.array([[feat[f] for f in state["features"]]])
    pred = float(state["model"].predict(X)[0])

    return PredictionResponse(
        date=request.date,
        predicted_consumption_mw=round(pred, 1),
        is_weekend=bool(feat["is_weekend"]),
        is_holiday=bool(feat["is_holiday"]),
        season=SEASON_MAP[target_date.month],
    )


@app.get("/predict/{date_str}", response_model=PredictionResponse, tags=["Prédiction"])
def predict_get(date_str: str):
    """Prédit la consommation via un paramètre d'URL (ex: /predict/2025-12-25)."""
    return predict(PredictionRequest(date=date_str))


@app.get("/predict/range/{start}/{end}", tags=["Prédiction"])
def predict_range(start: str, end: str):
    """
    Prédit la consommation pour une plage de dates.
    Limite : 365 jours maximum.
    """
    try:
        d_start = date.fromisoformat(start)
        d_end   = date.fromisoformat(end)
    except ValueError:
        raise HTTPException(400, "Format de date invalide. Utilisez YYYY-MM-DD.")

    if d_end < d_start:
        raise HTTPException(400, "La date de fin doit être ≥ à la date de début.")

    nb_days = (d_end - d_start).days + 1
    if nb_days > 365:
        raise HTTPException(400, "La plage maximale est de 365 jours.")

    results = []
    for i in range(nb_days):
        d = d_start + timedelta(days=i)
        r = predict(PredictionRequest(date=str(d)))
        results.append(r)

    return {"start": start, "end": end, "count": nb_days, "predictions": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
