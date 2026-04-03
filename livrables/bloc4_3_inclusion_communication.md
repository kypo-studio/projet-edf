# Bloc 4 — Livrable 3 : Plan d'inclusion, de communication & de collaboration d'équipe

**Projet :** Prédiction de la consommation électrique — EDF / RTE éco2mix
**Version :** 1.0 | **Date :** Avril 2026

---

## 1. Stratégie d'accueil et d'inclusion des handicaps

### 1.1 Types de handicap pris en compte

| Type de handicap | Adaptations mises en place |
|---|---|
| **Moteur** (mobilité réduite) | Toutes les réunions disponibles en distanciel. Accès aux documents en ligne (pas de format papier obligatoire). |
| **Visuel** (malvoyance, daltonisme) | Documents en format texte accessible (markdown). Graphiques avec palettes non-ambiguës (accessibles aux daltoniens). Alt-text sur les visuels. |
| **Auditif** (surdité, malentendance) | Compte-rendu écrit systématique après chaque réunion. Transcription automatique activée sur Teams/Zoom. Communication écrite privilégiée (Teams, GitHub). |
| **Cognitif** (dyslexie, TDAH) | Documents structurés avec titres clairs, bullet points. Délais de réflexion lors des estimations (planning poker asynchrone possible). |
| **Psychique** | Environnement de travail bienveillant. Charge de travail visible et négociée en sprint planning. |

### 1.2 Adaptations concrètes dans le projet

- **Format des documents :** Markdown (lisible par les lecteurs d'écran, convertible en tout format)
- **Réunions :** ordre du jour envoyé 24h à l'avance, durée max 45 min, compte-rendu dans les 2h
- **Outils :** GitHub (commentaires écrits), Teams (sous-titrage automatique), Miro (alternatives textuelles)
- **Planning :** capacité individuelle discutée en début de sprint (pas de surcharge imposée)

### 1.3 Articulation avec le référent handicap EDF

Dans le cadre d'un déploiement en entreprise EDF :
- Le référent handicap est consulté dès la phase de cadrage pour identifier les besoins spécifiques
- Un point de suivi semestriel est prévu pour vérifier l'adéquation des adaptations
- Toute adaptation demandée par un membre de l'équipe est traitée dans un délai de 5 jours ouvrés

---

## 2. Communication interculturelle & prévention des conflits

### 2.1 Contexte international du projet

EDF est un groupe international avec des centres R&D en France, Chine, USA, Royaume-Uni, Allemagne, Italie, Asie-Pacifique et Bruxelles. Le projet peut impliquer des collaborateurs de cultures différentes.

### 2.2 Modes de communication adaptés

| Contexte | Adaptation |
|---|---|
| **Fuseaux horaires multiples** | Réunions planifiées dans la fenêtre 9h–18h Paris. Enregistrement disponible pour les absents. Toutes les décisions importantes sont résumées par écrit. |
| **Barrière de la langue** | Langue du projet : français. Pour les échanges internationaux : anglais professionnel. Acronymes et termes techniques explicités à la première utilisation. |
| **Cultures à communication indirecte** (Asie, certains pays d'Europe du Nord) | Encourager les retours écrits asynchrones. Ne pas interpréter le silence comme un accord. |
| **Cultures hiérarchiques** | Créer des espaces sécurisés pour que chacun puisse exprimer un désaccord (rétrospective anonyme possible). |

### 2.3 Exemples de malentendus multiculturels & stratégies de prévention

| Malentendu | Cause culturelle | Stratégie |
|---|---|---|
| Un collaborateur asiatique dit "oui" mais n'est pas d'accord | Culture indirecte (éviter le conflit frontal) | Poser des questions ouvertes ("Qu'est-ce que tu en penses ?") plutôt que fermées ("C'est OK ?") |
| Un collaborateur américain perçu comme "agressif" | Culture directe (feedback franc) | Rappeler en début de projet que le feedback direct est une marque de respect, pas d'hostilité |
| Absence à une réunion non signalée | Rapport différent à la ponctualité | Règle explicite : prévenir 1h avant toute absence. Pas de jugement culturel, règle commune. |
| Désaccord sur une décision technique non exprimé | Hiérarchie perçue | Tour de parole structuré en réunion. Sondage anonyme pour les décisions importantes. |

### 2.4 Solutions innovantes pour favoriser les interactions

- **Binômes mixtes :** chaque tâche est assignée à un binôme d'origine différente (favorise le transfert de connaissances)
- **Ice-breaker culturel :** en début de sprint, 5 min de partage libre (tradition, actualité du pays) pour renforcer la cohésion
- **Carte d'équipe Miro :** chaque membre présente sa culture de travail (horaires préférés, style de feedback, timezone) → visible par tous
- **Rétro "Glad/Sad/Mad" :** format universel, simple, favorise l'expression des émotions dans toutes les cultures

---

## 3. Processus de communication inclusif & réunions

### 3.1 Rituels agiles adaptés

| Cérémonie | Fréquence | Durée | Format | Support |
|---|---|---|---|---|
| **Daily standup** | Quotidien (jours ouvrés) | 15 min | Hybride ou asynchrone | Teams ou message écrit |
| **Sprint planning** | Toutes les 2 semaines | 1h30 | Distanciel | Miro + GitHub Projects |
| **Sprint review** | Toutes les 2 semaines | 45 min | Distanciel | Démo live de l'API |
| **Rétrospective** | Toutes les 2 semaines | 45 min | Distanciel | FunRetro (anonyme possible) |
| **Comité projet** | Mensuel | 1h | Distanciel | PowerPoint + KPIs |

### 3.2 Fil de discussion — règles de fonctionnement

**Outil principal :** Microsoft Teams (ou Slack)

| Canal | Usage |
|---|---|
| `#général` | Annonces, informations de l'équipe |
| `#dev-ml` | Questions techniques ML, modèles, notebooks |
| `#déploiement` | API, Docker, CI/CD, incidents |
| `#daily` | Compte-rendu quotidien asynchrone |
| `#revue-sprint` | Résultats de sprint, démos |
| `#random` | Échanges informels, cohésion d'équipe |

**Règles :**
- Réponse attendue sous 4h ouvrées (pas d'urgence = pas d'appel direct)
- Pas de messages après 19h (sauf urgence critique)
- Toute décision importante documentée dans GitHub Issues ou Wiki
- Pas de communication sensible par message privé : utiliser les canaux officiels

### 3.3 Kit de réunion à distance

**Structure type d'une réunion de sprint (45 min)**

```
00:00 — Accueil & vérification technique (son, caméra)        [5 min]
00:05 — Rappel ordre du jour & règles (parole, micro)         [2 min]
00:07 — Point sur les US terminées (démo si applicable)      [15 min]
00:22 — Discussion / questions sur les blocages               [10 min]
00:32 — Prochaines priorités (backlog)                        [8 min]
00:40 — Actions à noter (qui fait quoi avant quand)           [4 min]
00:44 — Clôture + envoi du CR dans l'heure                    [1 min]
```

**Bonnes pratiques pour garder la dynamique de groupe :**
- **Caméra activée** (sauf contrainte réseau) — renforce le sentiment de présence
- **Tour de parole explicite** — le facilitateur distribue la parole, évite les monopoles
- **Outil interactif** — Miro pour le planning poker, Mentimeter pour les votes rapides
- **Parking lot** — sujets hors agenda notés sur un post-it Miro, traités après la réunion
- **Timeboxing strict** — minuteur visible pour chaque point de l'agenda
- **Résumé écrit** — CR envoyé dans Teams dans l'heure suivant la réunion

**Outils interactifs utilisés :**

| Outil | Usage |
|---|---|
| **Miro** | Rétro, planning poker, brainstorming visuel |
| **GitHub Projects** | Kanban, burn-down, suivi des issues |
| **FunRetro** | Rétrospective anonyme (Glad/Sad/Mad) |
| **Mentimeter** | Votes rapides, sondages en réunion |
| **Teams / Zoom** | Réunions vidéo, sous-titrage automatique |

**Gestion des incidents de réunion :**
- Participant absent : notification dans Teams + CR envoyé
- Problème technique : plan B asynchrone (questions par écrit, réponse sous 2h)
- Conflit ou tension : le Scrum Master prend acte, propose une discussion bilatérale hors réunion
