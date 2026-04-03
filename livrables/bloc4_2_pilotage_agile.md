# Bloc 4 — Livrable 2 : Dossier de pilotage agile & suivi du projet

**Projet :** Prédiction de la consommation électrique — EDF / RTE éco2mix
**Version :** 1.0 | **Date :** Avril 2026

---

## 1. Organisation agile du projet

### 1.1 Méthode choisie : Scrum adapté

**Justification :** Scrum est adapté car le projet est innovant (incertitude sur les performances des modèles), l'équipe est réduite (4 personnes), et les besoins métier peuvent évoluer en cours de développement. Les sprints de 2 semaines permettent des livraisons régulières et des ajustements rapides.

**Adaptations au contexte académique :**
- Pas de Product Owner dédié → rôle assumé par le chef de projet
- Cérémonies allégées (daily asynchrone via canal Teams)

### 1.2 Rôles

| Rôle | Personne | Responsabilités |
|---|---|---|
| **Product Owner / Chef de projet** | Membre 1 | Backlog, priorités, lien avec le "client" EDF, reporting |
| **Scrum Master** | Membre 2 | Facilitation des cérémonies, suppression des blocages |
| **Data Scientist** | Membres 3 & 4 | EDA, modélisation, MLflow, feature engineering |
| **Dev MLOps** | Membre 2 | API, Docker, CI/CD, tests |

### 1.3 Backlog produit

#### Épics & User Stories priorisées (MoSCoW)

**Épic 1 — Data Engineering**

| ID | User Story | Priorité | Story Points | Sprint |
|---|---|---|---|---|
| US-D01 | Collecter et charger les données RTE éco2mix 2012–2024 | Must | 3 | S1 |
| US-D02 | Réaliser l'EDA complète (saisonnalité, mix, autocorrélation) | Must | 5 | S1–S2 |
| US-D03 | Produire le dataset journalier agrégé (`daily_consumption.csv`) | Must | 2 | S2 |
| US-D04 | Construire les features (lags, cyclique, fériés) | Must | 3 | S3 |

**Épic 2 — Modélisation ML**

| ID | User Story | Priorité | Story Points | Sprint |
|---|---|---|---|---|
| US-M01 | Implémenter les baselines (lag-1, lag-7, RTE J-1) | Must | 2 | S3 |
| US-M02 | Implémenter et évaluer Ridge + Random Forest | Must | 3 | S4 |
| US-M03 | Implémenter et évaluer XGBoost | Must | 3 | S4 |
| US-M04 | Implémenter et évaluer Decision Tree + KNN | Must | 2 | S5 |
| US-M05 | Implémenter et évaluer ANN (Keras MLP) | Must | 5 | S5–S6 |
| US-M06 | Tracker tous les runs dans MLflow | Must | 2 | S4 |
| US-M07 | Comparer les modèles et sélectionner le meilleur | Must | 2 | S6 |

**Épic 3 — Déploiement**

| ID | User Story | Priorité | Story Points | Sprint |
|---|---|---|---|---|
| US-P01 | Développer l'API FastAPI avec endpoints predict/health/info | Must | 5 | S7 |
| US-P02 | Créer le Dockerfile et docker-compose | Must | 3 | S7–S8 |
| US-P03 | Mettre en place le pipeline CI/CD GitHub Actions | Should | 5 | S8 |
| US-P04 | Écrire les smoke tests de l'API | Must | 3 | S8 |
| US-P05 | Ajouter MLflow et Prometheus au docker-compose | Should | 2 | S9 |

**Épic 4 — Documentation & maintenabilité**

| ID | User Story | Priorité | Story Points | Sprint |
|---|---|---|---|---|
| US-DO01 | Rédiger le dossier de déploiement & maintenabilité | Must | 5 | S9 |
| US-DO02 | Rédiger la documentation technique & runbook | Must | 5 | S9 |
| US-DO03 | Rédiger le plan d'accompagnement du changement | Must | 3 | S10 |
| US-DO04 | Préparer les supports de soutenance Bloc 3 & Bloc 4 | Must | 5 | S10 |

### 1.4 Déroulement des sprints

| Sprint | Durée | Objectif principal | Vélocité cible |
|---|---|---|---|
| S1 | 2 sem. | Data collection + début EDA | 8 SP |
| S2 | 2 sem. | EDA complète + dataset journalier | 10 SP |
| S3–S4 | 2×2 sem. | Feature engineering + modèles ML | 12 SP |
| S5–S6 | 2×2 sem. | Modèles restants + comparaison | 12 SP |
| S7–S8 | 2×2 sem. | API + Docker + CI/CD + tests | 13 SP |
| S9–S10 | 2×2 sem. | Documentation + soutenance | 13 SP |

**Definition of Done :**
- Code reviewé par un autre membre de l'équipe
- Tests unitaires / smoke tests passants
- Résultats visibles dans MLflow (pour les modèles)
- Documenté (docstring ou commentaire si logique non évidente)

**Definition of Ready :**
- User Story décrite, critères d'acceptation définis
- Pas de dépendance bloquante non résolue
- Story Points estimés en planning poker

---

## 2. Tableaux de bord de suivi de projet

### 2.1 KPIs projet

| KPI | Description | Fréquence | Cible |
|---|---|---|---|
| **Vélocité** | Story Points livrés par sprint | Par sprint | ≥ 10 SP/sprint |
| **Taux de complétion** | % US terminées / planifiées | Par sprint | ≥ 90 % |
| **Burn-down** | SP restants vs courbe idéale | Quotidien | Sur la courbe |
| **Nb anomalies ouvertes** | Bugs/blocages en cours | Quotidien | 0 bloquant |
| **Couverture de tests** | % endpoints testés | Par sprint | 100 % endpoints critiques |

### 2.2 Maquette de tableau de bord

**Vue Sponsor (hebdomadaire)**

```
┌───────────────────────────────────────────────────────┐
│  EDF IA — Tableau de bord projet   Semaine 14 / 2026  │
├───────────────────┬───────────────────────────────────┤
│  Avancement       │  Sprint en cours : S8             │
│  ████████░░ 78 %  │  SP livrés : 10 / 13              │
├───────────────────┼───────────────────────────────────┤
│  MAPE modèle      │  Risques                          │
│  XGBoost : 1.8 %  │  🟡 Délai documentation (S9)     │
│  ANN      : 2.1 % │  🟢 Déploiement Docker : OK       │
├───────────────────┴───────────────────────────────────┤
│  Prochains jalons                                     │
│  • 15/04 : Soutenance Bloc 3                         │
│  • 29/04 : Soutenance Bloc 4                         │
└───────────────────────────────────────────────────────┘
```

**Vue Chef de projet (quotidienne via GitHub Projects)**
- Kanban board : Backlog / In Progress / Review / Done
- Burn-down chart automatique (GitHub Insights)
- Liste des blocages identifiés lors du daily

### 2.3 Utilisation des indicateurs pour corriger les écarts

| Situation détectée | Action corrective |
|---|---|
| Vélocité < 8 SP deux sprints consécutifs | Réduction du scope du sprint suivant, revue des estimations |
| Anomalie bloquante ouverte > 2 jours | Mob programming pour résolution rapide |
| MAPE modèle dépasse 3 % en test | Revue du feature engineering, envisager hyperparameter tuning |
| Retard sur la documentation | Priorisation en haut du backlog du sprint suivant |

---

## 3. Pilotage des prestataires & du SI existant

### 3.1 Cartographie des systèmes et prestataires

```
┌─────────────────────────────────────────────────────┐
│                    SI EDF IA                        │
│                                                     │
│  ┌─────────────┐    ┌──────────────┐               │
│  │  RTE éco2mix│    │  GitHub      │               │
│  │  (données)  │    │  (code/CI)   │               │
│  └──────┬──────┘    └──────┬───────┘               │
│         │                  │                        │
│         ▼                  ▼                        │
│  ┌─────────────────────────────────┐               │
│  │       Infrastructure Cloud      │               │
│  │   (VPS / AWS EC2 / Azure VM)    │               │
│  │  Docker Compose (api + mlflow)  │               │
│  └─────────────────────────────────┘               │
└─────────────────────────────────────────────────────┘
```

### 3.2 RACI

| Tâche | Chef de projet | Data Scientist | Dev MLOps | DSI |
|---|---|---|---|---|
| Mise à jour données RTE | I | R / A | I | — |
| Ré-entraînement modèle | A | R | I | — |
| Déploiement nouvelle version | A | I | R | I |
| Monitoring infrastructure | I | I | R | A |
| Gestion des secrets | A | — | R | I |
| Validation GO prod | A / R | C | C | C |

*R = Responsible, A = Accountable, C = Consulted, I = Informed*

### 3.3 Modalités de pilotage

| Prestataire / Système | Comité | SLA | Point de contrôle |
|---|---|---|---|
| RTE (données éco2mix) | — | Format stable (ISO-8859-1, TSV) | Chargement mensuel + test de schéma |
| GitHub (CI/CD) | — | 99.9 % (SLA GitHub) | Alert si pipeline échoue |
| Hébergeur Cloud | Mensuel | Uptime 99 % | Monitoring Prometheus |
