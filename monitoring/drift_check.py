"""
Data drift detection via PSI (Population Stability Index).

Compare la distribution d'un jeu de référence (train) à la distribution
d'un jeu courant (production / derniers jours) sur les features clés du
modèle XGBoost.

PSI :
    PSI = Σ (p_c - p_r) * ln(p_c / p_r)

Interprétation (standard industrie — crédit scoring, banque) :
    PSI < 0.10            : pas de drift significatif
    0.10 ≤ PSI < 0.25     : drift modéré (à surveiller)
    PSI ≥ 0.25            : drift important (ré-entraînement conseillé)

Usage :
    python monitoring/drift_check.py \\
        --reference data/processed/daily_consumption.csv \\
        --current   data/processed/daily_consumption.csv \\
        --ref-end   2021-12-31 \\
        --cur-start 2024-01-01

Sortie :
    - tableau PSI par feature (stdout)
    - exit code 0 si tout va bien, 1 si au moins une feature est en drift important
    - rapport JSON dans monitoring/reports/drift_<timestamp>.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

REPORT_DIR = Path(__file__).parent / "reports"

# Features surveillées (issues de features.json)
MONITORED = [
    "conso_mean_mw",  # cible (proxy drift de la distribution globale)
    "lag_1",
    "lag_7",
    "lag_365",
    "roll_7",
    "roll_30",
]

THRESHOLD_MODERATE = 0.10
THRESHOLD_HIGH     = 0.25


def _add_lags(df: pd.DataFrame) -> pd.DataFrame:
    """Reconstitue lag_1/7/365 et roll_7/30 pour permettre l'analyse de drift."""
    df = df.sort_values("Date").reset_index(drop=True).copy()
    for lag in (1, 7, 365):
        df[f"lag_{lag}"] = df["conso_mean_mw"].shift(lag)
    df["roll_7"]  = df["conso_mean_mw"].shift(1).rolling(7).mean()
    df["roll_30"] = df["conso_mean_mw"].shift(1).rolling(30).mean()
    return df


def psi(reference: np.ndarray, current: np.ndarray, n_bins: int = 10) -> float:
    """
    Calcule le Population Stability Index entre deux distributions numériques.

    Les bornes de binning sont les quantiles de la distribution de référence,
    ce qui garantit ~1/n_bins d'effectifs par bin côté référence.
    """
    ref = np.asarray(reference, dtype=float)
    cur = np.asarray(current,   dtype=float)
    ref = ref[~np.isnan(ref)]
    cur = cur[~np.isnan(cur)]

    if len(ref) == 0 or len(cur) == 0:
        return float("nan")

    quantiles = np.linspace(0, 1, n_bins + 1)
    edges = np.unique(np.quantile(ref, quantiles))
    if len(edges) < 3:
        return 0.0  # distribution dégénérée → pas de drift mesurable
    edges[0], edges[-1] = -np.inf, np.inf

    ref_counts, _ = np.histogram(ref, bins=edges)
    cur_counts, _ = np.histogram(cur, bins=edges)

    # Laplace smoothing pour éviter les log(0)
    ref_pct = (ref_counts + 1) / (ref_counts.sum() + len(ref_counts))
    cur_pct = (cur_counts + 1) / (cur_counts.sum() + len(cur_counts))

    return float(np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct)))


def classify(value: float) -> str:
    if np.isnan(value):
        return "n/a"
    if value < THRESHOLD_MODERATE:
        return "OK"
    if value < THRESHOLD_HIGH:
        return "MODERATE"
    return "HIGH"


def run(
    reference_path: Path,
    current_path: Path,
    ref_end: str | None,
    cur_start: str | None,
) -> dict:
    ref = pd.read_csv(reference_path, parse_dates=["Date"])
    cur = pd.read_csv(current_path,   parse_dates=["Date"])

    ref = _add_lags(ref)
    cur = _add_lags(cur)

    if ref_end:
        ref = ref[ref["Date"] <= pd.Timestamp(ref_end)]
    if cur_start:
        cur = cur[cur["Date"] >= pd.Timestamp(cur_start)]

    results = {}
    worst = 0.0
    print(f"{'Feature':<18} {'PSI':>8}   Statut")
    print("-" * 42)
    for feat in MONITORED:
        score = psi(ref[feat].values, cur[feat].values)
        status = classify(score)
        worst = max(worst, 0.0 if np.isnan(score) else score)
        results[feat] = {"psi": round(score, 4), "status": status}
        print(f"{feat:<18} {score:>8.4f}   {status}")

    overall = classify(worst)
    print("-" * 42)
    print(f"{'WORST':<18} {worst:>8.4f}   {overall}")

    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "reference": {
            "path": str(reference_path),
            "end":  ref_end,
            "n":    int(len(ref)),
        },
        "current": {
            "path":  str(current_path),
            "start": cur_start,
            "n":     int(len(cur)),
        },
        "features":        results,
        "worst_psi":       round(worst, 4),
        "overall_status":  overall,
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORT_DIR / f"drift_{datetime.utcnow():%Y%m%dT%H%M%S}.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"\nRapport écrit → {out}")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Détection de data drift (PSI).")
    parser.add_argument("--reference", type=Path, default=Path("data/processed/daily_consumption.csv"))
    parser.add_argument("--current",   type=Path, default=Path("data/processed/daily_consumption.csv"))
    parser.add_argument("--ref-end",   type=str, default="2021-12-31",
                        help="Fin de la période de référence (train).")
    parser.add_argument("--cur-start", type=str, default="2024-01-01",
                        help="Début de la période courante (production).")
    args = parser.parse_args()

    report = run(args.reference, args.current, args.ref_end, args.cur_start)
    return 0 if report["overall_status"] != "HIGH" else 1


if __name__ == "__main__":
    sys.exit(main())
