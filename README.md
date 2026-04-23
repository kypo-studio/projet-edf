# Prédiction de la consommation électrique — EDF / RTE éco2mix

> MSPR EPSI — RNCP36582 | Bloc 3 & Bloc 4
> Déploiement d'une solution IA de prédiction de la consommation électrique journalière en France

---

## Aperçu

Ce projet implémente et déploie plusieurs modèles de Machine Learning pour prédire la **consommation électrique journalière nationale (MW)** à partir des données historiques RTE éco2mix (2012–2024).

La solution est exposée via une **API REST FastAPI** conteneurisée avec Docker, trackée avec MLflow, et déployée automatiquement via un pipeline CI/CD GitHub Actions.

---

## Modèles implémentés

| Modèle | MAPE test (2023–2024) |
|---|---|
| Baseline lag-1 | ~3.5 % |
| Ridge Regression | ~2.5 % |
| Decision Tree | ~2.8 % |
| KNN (k=10) | ~2.2 % |
| Random Forest | ~1.9 % |
| ANN (MLP Keras) | ~2.1 % |
| **XGBoost** ✅ | **~1.8 %** |

---

## Structure du projet

```
projet-edf/
├── app/
│   ├── __init__.py
│   └── main.py                              # API FastAPI (production)
│
├── notebooks/                               # Travail offline (exploration & entraînement)
│   ├── 01_eda.ipynb                         # EDA → génère data/processed/daily_consumption.csv
│   └── 02_modeling.ipynb                    # Entraîne les 7 modèles → models/xgb_best.json
│
├── data/
│   ├── raw/                                 # XLS bruts RTE éco2mix (gitignored)
│   │   └── eCO2mix_RTE_*.xls
│   └── processed/
│       └── daily_consumption.csv            # Dataset journalier agrégé (sortie EDA)
│
├── models/
│   ├── xgb_best.json                        # Modèle XGBoost en production
│   └── features.json                        # Liste ordonnée des 15 features
│
├── monitoring/
│   ├── drift_check.py                       # Détection data drift (PSI)
│   └── reports/                             # Rapports JSON (gitignored)
│
├── tests/
│   └── test_api.py                          # 10 smoke tests FastAPI
│
├── static/
│   └── index.html                           # Interface web minimaliste
│
├── infra/
│   └── prometheus.yml                       # Config collecte métriques
│
├── livrables/                               # Documents MSPR (Bloc 3 & 4)
│   ├── bloc3_1_deploiement_maintenabilite.md
│   ├── bloc3_2_documentation_runbook.md
│   ├── bloc3_3_accompagnement_changement.md
│   ├── bloc4_1_cadrage_cahier_charges.md
│   ├── bloc4_2_pilotage_agile.md
│   └── bloc4_3_inclusion_communication.md
│
├── .github/workflows/ci-cd.yml              # Pipeline CI/CD GitHub Actions
├── Dockerfile                               # Image Docker (API uniquement)
├── docker-compose.yml                       # API + MLflow + Prometheus
├── pyproject.toml
├── requirements-api.txt                     # Dépendances minimales de l'API
└── README.md
```

### Ordre d'exécution du pipeline

```
XLS RTE (data/raw/)
   │
   ▼
notebooks/01_eda.ipynb           → data/processed/daily_consumption.csv
   │
   ▼
notebooks/02_modeling.ipynb      → models/xgb_best.json + models/features.json
   │
   ▼
app/main.py (FastAPI :8000)      ← consomme models/ + data/processed/
   │
   ├── /predict, /predict/range  (prédiction)
   ├── /metrics                  (Prometheus)
   └── /health, /info

monitoring/drift_check.py        → rapport PSI hebdomadaire
```

---

## Démarrage rapide

### Prérequis

- Python 3.11
- Docker & Docker Compose (pour le mode conteneur)

### 1. Mode développement local

```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Lancer l'API (depuis la racine du projet)
python -m app.main
# ou : uvicorn app.main:app --reload
```

API disponible sur **http://localhost:8000**
Documentation interactive sur **http://localhost:8000/docs**

### 2. Mode Docker

```bash
# Construire et démarrer (API + MLflow)
docker compose up --build -d

# Vérifier
docker compose ps
curl http://localhost:8000/health
```

| Service | URL |
|---|---|
| API de prédiction | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| MLflow UI | http://localhost:5000 |

### 3. Notebooks (optionnel — si vous voulez ré-entraîner)

```bash
source .venv/bin/activate
jupyter notebook
```

Exécuter depuis la racine du projet, dans l'ordre :
1. `notebooks/01_eda.ipynb` → génère `data/processed/daily_consumption.csv`
2. `notebooks/02_modeling.ipynb` → génère `models/xgb_best.json` + `models/features.json`

---

## API — Endpoints

| Endpoint | Méthode | Description | Exemple |
|---|---|---|---|
| `/health` | GET | Statut du service | `curl localhost:8000/health` |
| `/info` | GET | Métadonnées du modèle | `curl localhost:8000/info` |
| `/predict/{date}` | GET | Prédiction pour une date | `curl localhost:8000/predict/2025-12-25` |
| `/predict` | POST | Prédiction via JSON | voir ci-dessous |
| `/predict/range/{start}/{end}` | GET | Prédictions sur une plage (max 365j) | `curl localhost:8000/predict/range/2025-01-01/2025-01-07` |

**Exemple de réponse :**
```json
{
  "date": "2025-12-25",
  "predicted_consumption_mw": 54320.5,
  "is_weekend": false,
  "is_holiday": true,
  "season": "Hiver"
}
```

**Exemple POST :**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"date": "2025-12-25"}'
```

---

## CI/CD

Le pipeline GitHub Actions (`.github/workflows/ci-cd.yml`) se déclenche automatiquement sur chaque push vers `main` :

```
Push main
  ├── test    → lint (ruff) + 10 smoke tests (pytest)
  ├── build   → docker build + push vers ghcr.io
  └── deploy  → SSH → docker compose up --no-deps api
```

---

## Données

Source : [RTE éco2mix](https://www.rte-france.com/eco2mix/la-consommation-delectricite-en-franc)
Période : 2012–2024 | Granularité brute : 30 min | Agrégation : journalière (MW moyen)

Les fichiers `.xls` bruts ne sont pas versionnés (trop lourds). Télécharger depuis le site RTE et placer dans `data/raw/`.

---

## Contexte académique

Projet réalisé dans le cadre de la **MSPR EPSI** — Certification RNCP36582 *Chef de Projet Expert en Intelligence Artificielle*

- **Bloc 3** — Préparer la maintenabilité et le déploiement de la solution IA
- **Bloc 4** — Manager un projet informatique avec Agilité avec les parties prenantes
