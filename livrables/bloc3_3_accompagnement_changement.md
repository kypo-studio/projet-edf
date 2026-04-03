# Bloc 3 — Livrable 3 : Plan d'accompagnement du changement & bonne utilisation de l'IA

**Projet :** Prédiction de la consommation électrique — EDF / RTE éco2mix
**Version :** 1.0 | **Date :** Avril 2026

---

## 1. Analyse d'impact du déploiement IA

### 1.1 Processus actuels impactés

| Processus | Situation actuelle | Après déploiement IA | Impact |
|---|---|---|---|
| Prévision de la consommation | Prévision manuelle / modèles RTE J-1 | Prédiction automatisée (API) + prévision RTE en comparaison | **Fort** — nouveau workflow |
| Gestion du mix énergétique | Décision basée sur données historiques et expertise | Décision assistée par les prédictions ML | **Moyen** — aide à la décision |
| Reporting journalier | Extraction manuelle de fichiers XLS | Requête API + dashboard MLflow | **Moyen** — simplification |
| Ré-entraînement des modèles | Inexistant | Cycle mensuel formalisé | **Fort** — nouveau processus |

### 1.2 Parties prenantes concernées

| Partie prenante | Rôle | Impact | Besoin principal |
|---|---|---|---|
| Équipe exploitation réseau | Utilisateur final des prédictions | Fort | Comprendre les limites du modèle |
| Data Scientists EDF R&D | Administrateurs du modèle | Fort | Accès MLflow, procédures de ré-entraînement |
| DSI / Infra | Hébergement, sécurité | Moyen | Documentation technique, runbook |
| Direction / Sponsors | Validation ROI | Faible | KPIs de performance, tableau de bord |
| Partenaires RTE | Fournisseur de données | Faible | Garantie de continuité du format de données |

### 1.3 Bénéfices attendus

- **Précision accrue** : MAPE ≈ 1–2 % (XGBoost) vs ~2–3 % (prévision RTE J-1 manuelle)
- **Automatisation** : gain de temps sur la production des prévisions journalières
- **Traçabilité** : chaque prédiction loggée avec ses features (audit possible)
- **Scalabilité** : prédictions sur 365 jours via un seul appel API

---

## 2. Stratégie d'accompagnement du changement

### 2.1 Plan en 4 phases

```
Phase 1 — Sensibilisation (Semaines 1–2)
│  Présentation du projet aux équipes concernées
│  Démonstration live de l'API
│  Communication sur les objectifs et bénéfices attendus
│
Phase 2 — Formation (Semaines 3–4)
│  Formation utilisateurs finaux (½ journée)
│  Formation administrateurs système (1 journée)
│  Mise à disposition du guide d'utilisation
│
Phase 3 — Pilote (Semaines 5–8)
│  Déploiement en parallèle (prévision IA + prévision actuelle)
│  Collecte de feedback via formulaire simple
│  Ajustements selon les retours terrain
│
Phase 4 — Généralisation (À partir de la semaine 9)
   Déploiement production complet
   Support continu (référent technique désigné)
   Revue trimestrielle des performances
```

### 2.2 Communication

| Action | Cible | Fréquence | Support |
|---|---|---|---|
| Newsletter projet | Tous les acteurs | Bi-mensuelle | Email |
| Dashboard de performance | Direction + équipes | Hebdomadaire | MLflow / rapport PDF |
| Réunion de suivi | Équipes techniques | Mensuelle | Teams / présentiel |
| Rapport de dérive | Data Scientists | Quotidien (automatique) | Email automatisé |

---

## 3. Kit de bonne utilisation de l'IA

### 3.1 Guide "Comment utiliser les prédictions ?"

#### Ce que l'API prédit
L'API retourne la **puissance électrique moyenne journalière (MW)** pour une date donnée, estimée à partir de :
- Patterns saisonniers et hebdomadaires historiques (2012–2024)
- Consommation des jours précédents (lags J-1, J-7, J-365)
- Caractéristique du jour (week-end, jour férié)

#### Comment interpréter le résultat

```json
{
  "date": "2025-12-25",
  "predicted_consumption_mw": 54320.5,
  "is_weekend": false,
  "is_holiday": true,
  "season": "Hiver"
}
```

→ Le 25 décembre 2025 est un **jour férié d'hiver** : la prédiction tient compte de la baisse habituelle de consommation lors des jours fériés (~15 % sous la moyenne de la saison).

#### Marges d'erreur à connaître

| Période | MAPE estimé | Intervalle de confiance (±) |
|---|---|---|
| Jour ouvrable standard | ~1.5 % | ± 800 MW |
| Week-end / jour férié | ~2.0 % | ± 1 100 MW |
| Période estivale (canicule) | ~3.0 % | ± 1 600 MW |
| Événement exceptionnel | Non fiable | — |

#### Cas où NE PAS se fier uniquement à l'IA
- Événement exceptionnel non prévu (vague de froid exceptionnelle, événement national)
- Changement structurel du réseau (nouvelle grande industrie, fermeture de site)
- Date plus de 30 jours dans le futur (les lags deviennent imprécis)

---

### 3.2 Check-list d'utilisation responsable

Avant d'utiliser une prédiction pour une décision opérationnelle :

- [ ] La date demandée est-elle dans une plage raisonnable (< 30 jours) ?
- [ ] Y a-t-il un événement exceptionnel prévu ce jour-là (non capturé par le modèle) ?
- [ ] La prédiction est-elle cohérente avec la saison et le type de jour ?
- [ ] En cas de doute, ai-je comparé avec la prévision RTE J-1 ?
- [ ] En cas d'écart > 5 %, ai-je signalé l'anomalie à l'équipe Data ?

---

### 3.3 Processus de remontée des problèmes (Lean / Amélioration continue)

**Formulaire de feedback simplifié** (à remplir en cas d'anomalie) :

| Champ | Exemple |
|---|---|
| Date concernée | 2025-02-10 |
| Valeur prédite (MW) | 72 000 |
| Valeur réelle observée (MW) | 85 000 |
| Contexte | Vague de froid non anticipée |
| Criticité | Haute / Moyenne / Faible |

**Circuit de traitement :**
```
Utilisateur → Formulaire feedback → Équipe Data
    └── Analyse de la cause racine (A3 amélioration continue)
    └── Si dérive confirmée → ré-entraînement anticipé
    └── Si cas structurel → mise à jour du modèle + documentation
```

**Outil de suivi :** ticket GitHub Issues avec label `model-feedback` pour traçabilité.
