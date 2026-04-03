# Bloc 4 — Livrable 1 : Dossier de cadrage & Cahier des charges

**Projet :** Prédiction de la consommation électrique — EDF / RTE éco2mix
**Version :** 1.0 | **Date :** Avril 2026

---

## 1. Cadrage du projet

### 1.1 Objectifs

**Objectifs métier :**
- Améliorer la précision des prévisions de consommation électrique nationale (MAPE < 3 %)
- Automatiser la production des prévisions journalières pour les équipes exploitation
- Réduire la dépendance à la prévision RTE J-1 comme unique référence

**Objectifs techniques :**
- Implémenter et comparer 5 modèles ML : ANN, Random Forest, Decision Tree, KNN, XGBoost
- Déployer la solution dans un conteneur Docker avec CI/CD automatisé
- Mettre en place un processus de maintenabilité (monitoring, ré-entraînement, versioning)

### 1.2 Périmètre

| Dans le périmètre | Hors périmètre |
|---|---|
| Prédiction journalière (échelle nationale) | Prédiction régionale ou par site |
| Données RTE éco2mix 2012–2024 | Données temps réel (< 30 min) |
| Modèles ML tabulaires | Séries temporelles (LSTM, Prophet) |
| API REST de prédiction | Interface graphique (front-end) |
| Déploiement Docker (VPS/Cloud) | Déploiement embarqué (edge) |

### 1.3 Étapes de réalisation du SI

| Phase | Description | Durée estimée |
|---|---|---|
| **1. Cadrage & analyse** | Définition des besoins, choix des données, architecture | S1–S2 |
| **2. Exploration (EDA)** | Analyse des données RTE, identification des features | S3–S5 |
| **3. Modélisation** | Implémentation des 5 modèles, comparaison, MLflow | S6–S10 |
| **4. Déploiement** | API FastAPI, Docker, CI/CD GitHub Actions | S11–S13 |
| **5. Tests & validation** | Smoke tests, simulation virtuelle, recette | S14–S15 |
| **6. Documentation & formation** | Runbook, livrables, soutenance | S16–S19 |

### 1.4 WBS (Work Breakdown Structure)

```
Projet EDF — Prédiction consommation électrique
│
├── 1. Gestion de projet
│   ├── 1.1 Cadrage & kick-off
│   ├── 1.2 Suivi agile (sprints, rétros)
│   └── 1.3 Reporting & soutenance
│
├── 2. Data Engineering
│   ├── 2.1 Collecte données RTE éco2mix (2012–2024)
│   ├── 2.2 EDA & nettoyage
│   └── 2.3 Feature engineering (lags, cyclique, fériés)
│
├── 3. Machine Learning
│   ├── 3.1 Baseline (lag-1, lag-7)
│   ├── 3.2 Ridge Regression
│   ├── 3.3 Decision Tree
│   ├── 3.4 KNN
│   ├── 3.5 Random Forest
│   ├── 3.6 XGBoost
│   ├── 3.7 ANN (Keras MLP)
│   └── 3.8 Comparaison & sélection du meilleur modèle
│
├── 4. Déploiement & Infra
│   ├── 4.1 API FastAPI
│   ├── 4.2 Dockerfile & docker-compose
│   └── 4.3 Pipeline CI/CD (GitHub Actions)
│
└── 5. Documentation
    ├── 5.1 Documentation technique & runbook
    ├── 5.2 Plan d'accompagnement du changement
    └── 5.3 Supports de soutenance
```

### 1.5 Planification macro (Roadmap)

```
Jan 2026    Fév 2026    Mar 2026    Avr 2026    Mai 2026
    │           │           │           │           │
    ├─ Cadrage ─┤
                ├── EDA ────┤
                            ├── ML ─────┤
                                        ├─ Deploy ──┤
                                        ├─ Tests ───┤
                                                    ├─ Docs & Soutenance ─┤
```

### 1.6 Ressources mobilisées

**Humaines :**

| Rôle | Responsabilité | Charge |
|---|---|---|
| Chef de projet | Pilotage agile, coordination, reporting | 20 % |
| Data Scientist (×2) | EDA, modélisation, MLflow | 50 % |
| Dev MLOps | API, Docker, CI/CD, tests | 30 % |

**Techniques :**
- Serveur VPS ou instance Cloud (2 vCPU, 4 GB RAM, 50 GB disque)
- GitHub (code, CI/CD, Issues)
- MLflow (tracking expériences)

**Financières (estimation) :**

| Poste | Coût estimé |
|---|---|
| Hébergement Cloud (12 mois) | ~600 €/an |
| Licences outils | 0 € (open source) |
| Formation équipe | ~800 € (2 jours) |

---

## 2. Cahier des charges fonctionnel & technique

### 2.1 Profil des acteurs (utilisateurs)

| Acteur | Profil | Cas d'usage |
|---|---|---|
| **Opérateur exploitation** | Non technique, utilisateur final | Consulter la prévision du jour/lendemain |
| **Data Scientist R&D** | Expert ML | Ré-entraîner, comparer les modèles, analyser les dérives |
| **DSI** | Responsable infra | Superviser le déploiement, gérer la sécurité |
| **Direction** | Décideur | Suivre les KPIs de performance du système |

### 2.2 Cahier des charges fonctionnel

**User Stories principales :**

| ID | En tant que... | Je veux... | Afin de... | Priorité |
|---|---|---|---|---|
| US-01 | Opérateur | Obtenir la prévision de consommation pour une date | Anticiper les besoins en production | Must |
| US-02 | Opérateur | Obtenir les prévisions pour une semaine | Planifier la gestion du mix énergétique | Must |
| US-03 | Opérateur | Savoir si le service fonctionne | M'assurer que les données sont fiables | Must |
| US-04 | Data Scientist | Consulter les performances des modèles | Détecter une dérive et décider d'un ré-entraînement | Must |
| US-05 | Data Scientist | Déployer un nouveau modèle sans interruption | Mettre à jour sans impacter les utilisateurs | Should |
| US-06 | DSI | Revenir à la version précédente du modèle | Limiter l'impact d'une régression | Should |
| US-07 | Direction | Visualiser les KPIs dans un tableau de bord | Piloter la qualité du système | Could |

**Règles de gestion :**
- RG-01 : La prédiction est disponible pour toute date ≥ 01/01/2013
- RG-02 : La plage maximale d'une requête multi-dates est de 365 jours
- RG-03 : En cas de données historiques manquantes, la moyenne globale est utilisée comme fallback
- RG-04 : La saison et le statut jour-férié/week-end sont retournés avec chaque prédiction

### 2.3 Cahier des charges technique

**Contraintes d'architecture :**
- L'API doit être stateless (pas de session)
- Le modèle et les données historiques sont montés en volumes Docker (mise à jour sans rebuild)
- La solution doit fonctionner sur Linux (Ubuntu 22.04+)

**Contraintes de données :**
- Source : fichiers RTE éco2mix (.xls, encodage ISO-8859-1, séparateur tabulation)
- Fréquence de mise à jour : annuelle (données définitives) + mensuelle (données consolidées)
- Historique minimum requis : 1 an (pour lag_365)

**Contraintes de performance :**
- Latence p95 < 200 ms (requête unique)
- Disponibilité ≥ 99 % (hors maintenance planifiée)
- MAPE < 3 % sur 30 jours glissants

**Contraintes de sécurité :**
- Pas de données personnelles traitées
- Authentification par API Key à ajouter avant exposition publique
- Les secrets de déploiement sont stockés dans GitHub Secrets

**Intégrations :**
- MLflow : tracking des expériences d'entraînement (localhost:5000)
- GitHub Actions : déploiement automatisé sur push main
- Prometheus (optionnel) : collecte des métriques système
