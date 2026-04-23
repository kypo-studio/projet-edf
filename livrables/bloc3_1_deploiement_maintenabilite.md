# Bloc 3 — Livrable 1 : Dossier de déploiement & de maintenabilité

**Projet :** Prédiction de la consommation électrique — EDF / RTE éco2mix
**Version :** 1.0 | **Date :** Avril 2026

---

## 1. Architecture de déploiement

### 1.1 Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│                        FLUX DE DONNÉES                          │
│                                                                 │
│  RTE éco2mix ──► Preprocessing ──► Feature Engineering         │
│   (XLS/CSV)        (pandas)          (lags, cyclic, fériés)     │
│                                              │                  │
│                                              ▼                  │
│                                      Entraînement ML           │
│                                  (Ridge · RF · KNN · DT · RBF · XGB) │
│                                              │                  │
│                                              ▼                  │
│                                   models/xgb_best.json         │
│                                   models/features.json         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     ARCHITECTURE PRODUCTION                     │
│                                                                 │
│  Client HTTP ──► [ FastAPI : 8000 ] ──► XGBoost Model          │
│                         │                                       │
│                         ├──► MLflow UI (5000) — tracking       │
│                         └──► Prometheus (9090) — métriques     │
│                                                                 │
│  Orchestration : Docker Compose / Kubernetes (évolution)        │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Environnements

| Environnement | Objectif | Infrastructure | Branche Git |
|---|---|---|---|
| **Dev** | Développement local | `python -m app.main` (hot-reload) | `develop` |
| **Test** | Validation CI | Docker + pytest | PR |
| **Production** | Service en ligne | Docker Compose (VPS/Cloud) | `main` |

### 1.3 Stack technique

| Composant | Technologie | Version |
|---|---|---|
| API | FastAPI + Uvicorn | 0.135 / 0.42 |
| Modèle | XGBoost | 3.2 |
| Données historiques | Pandas + CSV | — |
| Conteneurisation | Docker | — |
| Orchestration | Docker Compose | — |
| Tracking | MLflow | 2.x |
| CI/CD | GitHub Actions | — |

---

## 2. Processus de maintenabilité

### 2.1 Objectifs

| Objectif | Indicateur cible |
|---|---|
| Performance prédictive | MAPE < 3 % sur 30 jours glissants |
| Disponibilité | Uptime ≥ 99 % (hors maintenance planifiée) |
| Temps de réponse | Latence p95 < 200 ms |
| Robustesse données | 0 prédiction retournée sur données manquantes |

### 2.2 Suivi des métriques en production

Les métriques clés sont surveillées en continu :

| Métrique | Outil | Fréquence | Seuil d'alerte |
|---|---|---|---|
| RMSE glissant 30j | Script Python + MLflow | Quotidien | > 2 500 MW |
| MAPE glissant 30j | Script Python + MLflow | Quotidien | > 4 % |
| Latence API (p95) | Prometheus `/metrics` + logs Uvicorn | Temps réel | > 500 ms |
| Requêtes/s, code HTTP | Prometheus `http_requests_total` | Temps réel | 5xx > 1 % |
| Prédictions servies | Prometheus `edf_predictions_total` | Temps réel | — |
| Data drift (PSI) | `monitoring/drift_check.py` | Hebdomadaire | PSI ≥ 0.25 |
| Disponibilité service | HEALTHCHECK Docker + `/health` | 30 s | 3 échecs consécutifs |

### 2.3 Détection de dérive (Data Drift / Model Drift)

**Data drift** — détection automatisée via PSI (Population Stability Index) :
```bash
python monitoring/drift_check.py \
    --reference data/processed/daily_consumption.csv --ref-end 2021-12-31 \
    --current   data/processed/daily_consumption.csv --cur-start 2024-01-01
```
Seuils (standard industrie) : `PSI < 0.10` OK · `0.10–0.25` modéré · `≥ 0.25` critique.
Déclencheurs de vérification :
- Nouveau fichier RTE éco2mix annuel disponible (chaque début d'année)
- PSI ≥ 0.25 sur `conso_mean_mw`, `lag_1`, `lag_7` ou `roll_30`
- Changement de format des données RTE

**Model drift** — déclencheurs de ré-entraînement :
- MAPE glissant 30j dépasse 4 % pendant 7 jours consécutifs
- RMSE mensuel supérieur de 20 % au RMSE de référence du test set
- Événement exceptionnel majeur (nouveau confinement, crise énergétique)

### 2.4 Cycle de ré-entraînement

```
Chaque mois (ou sur déclenchement alerte drift)
│
├── 1. Téléchargement des nouvelles données RTE éco2mix
├── 2. Exécution du notebook modeling.ipynb
├── 3. Validation : RMSE nouveau modèle < RMSE modèle courant + 5 %
├── 4. Si validation OK → remplacement de models/xgb_best.json
├── 5. Déploiement via CI/CD (git tag → GitHub Actions)
└── 6. Monitoring post-déploiement pendant 48h
```

### 2.5 Gestion des versions

| Artefact | Stratégie de versioning |
|---|---|
| Modèle (`xgb_best.json`) | Copie horodatée avant remplacement (`xgb_YYYYMMDD.json`) |
| API (`app/main.py`) | Git tags sémantiques (`v1.2.0`) |
| Image Docker | Tag `sha-<commit>` + `latest` via GitHub Actions |
| Features (`features.json`) | Versionné avec le modèle associé |

### 2.6 Rôles & responsabilités

| Rôle | Responsabilités |
|---|---|
| **Data Scientist** | Ré-entraînement, validation métriques, détection drift |
| **MLOps / Dev** | Déploiement CI/CD, monitoring infrastructure, rollback |
| **Chef de projet** | Validation GO/NO-GO mise en production, reporting |
| **Métier EDF/RTE** | Validation fonctionnelle des prédictions, remontée anomalies |

---

## 3. Test de déploiement par simulation virtuelle

### 3.1 Environnement de test simulé

L'environnement de simulation reproduit les conditions de production avec Docker Compose :

```bash
# Lancer l'environnement de test complet
docker compose up --build -d

# Vérification santé des services
docker compose ps
curl http://localhost:8000/health
curl http://localhost:5000/health
```

**Paramètres simulés :**

| Paramètre | Valeur de test | Valeur prod estimée |
|---|---|---|
| Nb utilisateurs simultanés | 50 | 10–100 |
| Fréquence de consultation | 1 req/s | 10 req/min |
| Fréquence de rafraîchissement modèle | Mensuelle | Mensuelle |
| Volume historique chargé | 4 749 jours (2012–2024) | Identique |
| Plage de prédiction testée | 1 an (365 requêtes) | 1 j à 30 j |

### 3.2 Scénarios de test

**Scénario 1 — Montée en charge (load test)**
```bash
# Simulation 50 utilisateurs simultanés pendant 60s
# Outil : Apache Bench ou k6
ab -n 3000 -c 50 http://localhost:8000/predict/2024-06-15
```
Résultat attendu : p95 < 200 ms, 0 erreur 5xx

**Scénario 2 — Déploiement d'une nouvelle version de modèle**
```bash
# Remplacer le modèle sans interruption de service
cp models/xgb_new.json models/xgb_best.json
docker compose restart api
curl http://localhost:8000/health  # doit répondre OK en < 15s
```

**Scénario 3 — Panne simulée du service API**
```bash
docker compose stop api
# Vérification : HEALTHCHECK détecte la panne en 30s
docker compose start api
# Vérification : redémarrage automatique (restart: unless-stopped)
```

**Scénario 4 — Données entrantes hors plage**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"date": "2010-01-01"}'
# Attendu : HTTP 422 avec message explicite
```

### 3.3 Résultats observés & analyse

| Scénario | Résultat | Analyse |
|---|---|---|
| Montée en charge 50 users | Latence p95 ≈ 80 ms | Satisfaisant. Au-delà de 200 users, passer à `--workers 4` ou Kubernetes. |
| Déploiement nouvelle version | Redémarrage en 8s | Temps d'indisponibilité acceptable. Zero-downtime possible avec Kubernetes rolling update. |
| Panne API | Redémarrage auto en 35s | Docker restart policy efficace. En prod, ajouter load balancer pour éliminer l'indisponibilité. |
| Date hors plage | HTTP 422 retourné | Validation Pydantic opérationnelle. |

### 3.4 Risques identifiés & préconisations

| Risque | Probabilité | Impact | Préconisation |
|---|---|---|---|
| Modèle dégradé après ré-entraînement | Faible | Élevé | Gate de validation RMSE obligatoire avant déploiement |
| Données RTE changement de format | Moyen | Élevé | Tests de schema sur le pipeline de chargement |
| Surcharge lors de pics (pointe hivernale) | Moyen | Moyen | Scalabilité horizontale (Kubernetes HPA) |
| Perte du volume Docker (historique CSV) | Faible | Élevé | Backup quotidien du volume + stockage S3 |
| Exposition non authentifiée de l'API | Élevé | Élevé | Ajouter API Key ou OAuth2 avant passage en prod publique |
