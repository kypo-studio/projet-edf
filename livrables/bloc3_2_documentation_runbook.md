# Bloc 3 — Livrable 2 : Documentation technique & Runbook d'exploitation

**Projet :** Prédiction de la consommation électrique — EDF / RTE éco2mix
**Version :** 1.0 | **Date :** Avril 2026

---

## 1. Documentation technique

### 1.1 Modèles implémentés

#### Variables d'entrée (features)

| Feature | Description | Type |
|---|---|---|
| `month_sin` / `month_cos` | Encodage cyclique du mois | Float |
| `doy_sin` / `doy_cos` | Encodage cyclique du jour de l'année | Float |
| `dow_sin` / `dow_cos` | Encodage cyclique du jour de la semaine | Float |
| `is_weekend` | 1 si samedi ou dimanche | Binaire |
| `is_holiday` | 1 si jour férié français | Binaire |
| `lag_1` / `lag_7` / `lag_14` / `lag_30` / `lag_365` | Consommation J-1, J-7, J-14, J-30, J-365 (MW) | Float |
| `roll_7` / `roll_30` | Moyenne glissante 7j et 30j (J-1) | Float |

**Variable cible :** `conso_mean_mw` — puissance moyenne journalière en MW

**Prétraitement :** agrégation journalière des données demi-horaires RTE (moyenne de la puissance appelée sur 24h).

---

#### Réseau de Neurones Artificiels (ANN — MLP)

| Paramètre | Valeur |
|---|---|
| Architecture | Input(15) → Dense(128, ReLU) → BN → Dropout(0.2) → Dense(64, ReLU) → BN → Dropout(0.2) → Dense(32, ReLU) → Dense(1) |
| Optimiseur | Adam (lr=0.001) |
| Fonction de perte | MSE |
| Early stopping | patience=15 (sur val_loss) |
| Batch size | 32 |
| Epochs max | 150 |
| Normalisation | StandardScaler (obligatoire) |

**Avantages :** capture des relations non-linéaires complexes, adaptable.
**Limites :** boîte noire, sensible à l'initialisation, plus lent à entraîner.

---

#### Forêt Aléatoire (Random Forest)

| Paramètre | Valeur |
|---|---|
| Nombre d'arbres | 300 |
| Profondeur max | 12 |
| Min samples leaf | 5 |
| Random state | 42 |

**Avantages :** robuste aux outliers, importance des features interprétable, pas de normalisation requise.
**Limites :** prédictions bornées à la plage d'entraînement (pas d'extrapolation).

---

#### Arbre de Décision (Decision Tree)

| Paramètre | Valeur |
|---|---|
| Profondeur max | 8 |
| Min samples leaf | 10 |
| Random state | 42 |

**Avantages :** totalement interprétable, rapide.
**Limites :** forte variance, surapprentissage possible sans élagage.

---

#### K-Nearest Neighbors (KNN)

| Paramètre | Valeur |
|---|---|
| k (voisins) | 10 |
| Pondération | Distance (1/d) |
| Métrique | Euclidienne |
| Normalisation | StandardScaler (obligatoire) |

**Avantages :** simple, non paramétrique.
**Limites :** lent à l'inférence sur gros jeu, sensible à la dimensionnalité.

---

#### XGBoost (modèle retenu en production)

| Paramètre | Valeur |
|---|---|
| n_estimators | 500 (+ early stopping) |
| learning_rate | 0.05 |
| max_depth | 6 |
| subsample | 0.8 |
| colsample_bytree | 0.8 |
| reg_alpha / lambda | 0.1 / 1.0 |
| Early stopping rounds | 30 (sur validation) |

**Choix pour la production :** meilleur RMSE sur le test set 2023–2024, robuste, rapide à l'inférence (< 5 ms).

---

### 1.2 Description des services de déploiement

#### API FastAPI (`main.py`)

| Endpoint | Méthode | Description |
|---|---|---|
| `/health` | GET | Statut du service, période historique |
| `/info` | GET | Métadonnées du modèle et liste des features |
| `/predict` | POST | Prédiction via JSON `{"date": "YYYY-MM-DD"}` |
| `/predict/{date}` | GET | Prédiction via paramètre d'URL |
| `/predict/range/{start}/{end}` | GET | Prédictions sur une plage (max 365 j) |

**Chargement au démarrage (lifespan) :**
- `models/xgb_best.json` → modèle XGBoost
- `models/features.json` → liste ordonnée des features
- `data/daily_consumption.csv` → historique pour le calcul des lags

#### Dockerfile

Image `python:3.11-slim` — dépendances minimales (sans keras/tensorflow) :
`fastapi`, `uvicorn`, `xgboost`, `scikit-learn`, `numpy`, `pandas`, `pydantic`

HEALTHCHECK intégré : `curl -f http://localhost:8000/health`

#### Pipeline CI/CD (`.github/workflows/ci-cd.yml`)

```
Push main
  │
  ├── Job 1 : test
  │     ├── ruff check main.py
  │     └── pytest tests/ (10 smoke tests)
  │
  ├── Job 2 : build-push (si tests OK)
  │     ├── docker build
  │     └── docker push ghcr.io/<repo>/edf-api:sha-<commit>
  │
  └── Job 3 : deploy (si build OK)
        ├── SSH → docker compose pull api
        ├── docker compose up -d --no-deps api
        └── curl /health (healthcheck post-déploiement)
```

### 1.3 Pré-requis techniques

| Élément | Minimum | Recommandé |
|---|---|---|
| Python | 3.11 | 3.11 |
| RAM (API) | 512 MB | 1 GB |
| Disque | 500 MB | 2 GB |
| CPU | 1 vCPU | 2 vCPU |
| Docker | 24+ | 27+ |
| OS | Linux (Ubuntu 22.04+) | Linux |

---

## 2. Runbook / Guide d'exploitation

### 2.1 Démarrer la solution

```bash
# 1. Cloner le dépôt
git clone <url-repo> && cd projet-edf

# 2. Vérifier que les artefacts sont présents
ls models/xgb_best.json models/features.json
ls data/daily_consumption.csv

# 3. Lancer les services
docker compose up -d

# 4. Vérifier que tout est opérationnel
docker compose ps
curl http://localhost:8000/health
# Réponse attendue : {"status": "ok", ...}
```

### 2.2 Arrêter la solution

```bash
# Arrêt propre (conserve les volumes)
docker compose stop

# Arrêt + suppression des conteneurs (volumes conservés)
docker compose down

# Arrêt complet + suppression des volumes (IRRÉVERSIBLE)
docker compose down -v
```

### 2.3 Déployer une nouvelle version de modèle

```bash
# 1. Archiver l'ancien modèle
cp models/xgb_best.json models/xgb_$(date +%Y%m%d).json

# 2. Placer le nouveau modèle
cp /chemin/vers/nouveau_modele.json models/xgb_best.json

# 3. Redémarrer l'API (le volume est monté en lecture)
docker compose restart api

# 4. Vérifier (le modèle est rechargé au démarrage)
sleep 15
curl http://localhost:8000/health
curl http://localhost:8000/predict/$(date +%Y-%m-%d)
```

### 2.4 Rollback vers la version précédente

```bash
# 1. Restaurer l'ancien modèle (exemple : version du 1er avril)
cp models/xgb_20260401.json models/xgb_best.json

# 2. Redémarrer l'API
docker compose restart api

# 3. Vérifier
sleep 15 && curl http://localhost:8000/health
```

### 2.5 Vérifications essentielles (checks)

```bash
# Statut des conteneurs
docker compose ps

# Logs en temps réel
docker compose logs -f api

# Test de prédiction nominal
curl http://localhost:8000/predict/$(date -d "+1 day" +%Y-%m-%d 2>/dev/null \
  || date -v+1d +%Y-%m-%d)

# Test de la plage de la semaine
curl "http://localhost:8000/predict/range/$(date +%Y-%m-%d)/$(date +%Y-%m-%d)"

# Interface MLflow
open http://localhost:5000
```

---

## 3. Procédures de gestion d'incidents

### 3.1 Performances dégradées (RMSE / MAPE en hausse)

**Symptôme :** les prédictions s'écartent significativement des valeurs réelles.

```
1. Identifier la période de dégradation dans MLflow (localhost:5000)
2. Vérifier si un événement exceptionnel explique l'écart
   (vague de froid, grève, événement national)
3. Si dérive structurelle → déclencher un ré-entraînement
   avec les données récentes
4. Valider le nouveau modèle (RMSE < modèle courant + 5 %)
5. Déployer via la procédure 2.3
```

### 3.2 Service API ne répond plus

**Symptôme :** `curl http://localhost:8000/health` → erreur de connexion.

```
1. docker compose ps              → vérifier l'état du conteneur
2. docker compose logs api --tail=50  → identifier l'erreur
3. Si OOM (Out of Memory) : augmenter la RAM allouée
4. Si erreur chargement modèle : vérifier models/xgb_best.json
5. docker compose restart api     → redémarrage forcé
6. Si échec persistant : docker compose down && docker compose up -d
```

### 3.3 Données entrantes hors format

**Symptôme :** erreurs 422 inhabituelles ou prédictions aberrantes.

```
1. Vérifier le format de data/daily_consumption.csv
   → colonnes attendues : Date, conso_mean_mw
2. Si le fichier RTE éco2mix a changé de format :
   a. Mettre à jour la fonction load_rte_file() dans eda.ipynb
   b. Regénérer daily_consumption.csv
   c. Redémarrer l'API (rechargement de l'historique)
3. Alerter l'équipe Data si le changement est structurel
```

### 3.4 Espace disque insuffisant

```
1. df -h                          → vérifier l'espace disponible
2. docker system prune -f         → nettoyer les images/conteneurs inutilisés
3. ls -lh models/                 → supprimer les anciens modèles archivés
   (conserver les 3 dernières versions minimum)
```

---

## 4. Note d'expertise technique à l'équipe projet

### Choix techniques clés

**Pourquoi XGBoost en production (et non l'ANN) ?**
- Inférence 10× plus rapide (< 5 ms vs ~20 ms pour l'ANN)
- Pas de dépendance TensorFlow/Keras dans le conteneur (image 60 % plus légère)
- Reproductibilité garantie (`random_state=42`), pas de variabilité due à l'initialisation
- RMSE légèrement meilleur ou équivalent sur le test set 2023–2024

**Pourquoi les volumes Docker plutôt que COPY dans l'image ?**
- Permet de mettre à jour le modèle sans reconstruire l'image
- Indépendance entre le cycle de vie du code (CI/CD) et le cycle du modèle (ré-entraînement)

### Recommandations pour l'équipe

| Domaine | Recommandation |
|---|---|
| **Logs** | Utiliser le format structuré actuel (timestamp \| level \| message). Ne jamais logger de données personnelles. |
| **Sécurité** | Avant mise en prod publique : ajouter `X-API-Key` header ou OAuth2. Ne pas exposer `/docs` en production. |
| **Secrets** | Stocker les credentials (DEPLOY_SSH_KEY, etc.) dans GitHub Secrets, jamais dans le code. |
| **Monitoring** | Activer le profil Prometheus (`docker compose --profile monitoring up`) dès que possible. |
| **Backups** | Sauvegarder quotidiennement `data/daily_consumption.csv` et `models/` vers un stockage externe. |
