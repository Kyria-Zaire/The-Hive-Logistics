# Méthode BMAD adaptée — THE HIVE LOGISTICS

> **Type :** méthode de delivery produit et logiciel assistée par IA  
> **Statut :** CANONIQUE — à approuver avant le premier build  
> **Version :** 1.0.0  
> **Date :** 2026-09-12  
> **Portée :** cadrage, conception, architecture, implémentation, revue, validation et livraison  
> **Référence externe :** adaptation interne inspirée de BMad Method ; ce document n’est pas une distribution officielle de BMad.

---

## 1. Finalité

Cette méthode transforme le travail assisté par Claude Code, Cursor ou un autre agent en processus de développement gouverné, traçable et vérifiable.

Elle vise à garantir que :

- les décisions importantes restent humaines et explicites ;
- le besoin est défini avant le code ;
- chaque agent reçoit un contexte suffisant mais limité ;
- chaque changement est découpé à la bonne taille ;
- le code est revu et testé avant toute promotion ;
- les environnements et les données restent isolés ;
- la vitesse du développement assisté par IA ne dégrade ni l’architecture, ni la sécurité, ni la qualité UX ;
- une preuve remplace toute déclaration non vérifiée de réussite.

La méthode suit une boucle stable :

`Intention → Cadrage → PRD/UX/Architecture → Spec → Stories → Build → Review → Validation → Livraison → Rétrospective`

La profondeur de chaque étape dépend de la taille, du risque et du nombre de personnes ou d’agents impliqués.

---

## 2. Principes non négociables

1. **L’humain garde l’autorité.** Un agent conseille, analyse et exécute dans le périmètre autorisé ; il ne s’auto-approuve pas.
2. **Une source de vérité par niveau.** PRD pour le quoi/pourquoi, architecture pour le comment partagé, spec pour l’epic, story pour l’unité d’exécution.
3. **Une story, une session de build maîtrisée.** Si une story ne peut pas être comprise, implémentée et vérifiée sans deviner, elle doit être redécoupée.
4. **Aucune hypothèse silencieuse.** Utiliser `[HYPOTHÈSE]`, `[À CONFIRMER]` ou `[BLOQUANT]`.
5. **Aucune mutation implicite.** Pas de commit, push, merge, migration distante, déploiement ou opération PROD sans GO explicite.
6. **Read-only avant write.** Tout ticket commence par un préflight et une analyse de l’état réel.
7. **Le périmètre est fermé par défaut.** Toute découverte hors scope devient une observation ou un ticket séparé.
8. **La preuve est obligatoire.** Un test déclaré sans sortie vérifiable ne vaut pas validation.
9. **La sécurité est continue.** Elle intervient au cadrage, dans l’architecture, pendant le build, en review et avant production.
10. **La simplicité est une exigence.** Aucun framework, service, abstraction ou agent supplémentaire sans besoin démontré.
11. **Les documents évoluent avec le produit.** Une décision nouvelle doit être propagée dans toutes les sources de vérité concernées.
12. **Le contexte doit être condensé.** Ne jamais envoyer à un agent une pile brute de documents lorsque seuls quelques faits gouvernent le ticket.

### 2.1 Baseline technique déjà validée

- frontend : Next.js avec TypeScript strict ;
- backend : Python avec FastAPI ;
- persistance : PostgreSQL ;
- architecture initiale : monolithe modulaire ;
- environnements logiques : DEV, RECETTE, PREPROD et PROD ;
- média V1 : photographies statiques optimisées ;
- aucune authentification, réservation automatisée ou fonction de paiement en V1.

Tout remplacement ou ajout structurant — Redis, microservices, CMS, file de messages, fournisseur d’authentification ou de paiement — nécessite un besoin prouvé, une analyse d’alternatives et un ADR approuvé.

---

## 3. Gouvernance des rôles

### 3.1 Rôles humains

| Rôle | Titulaire | Responsabilités | Autorité |
|---|---|---|---|
| Sponsor métier / Client | Jores | Réalité métier, offres, contenus, preuves, identité et acceptation fonctionnelle | Valide le besoin et les contenus publiables |
| Product Owner / Lead Developer | Kyria | Backlog, périmètre, dépôt, arbitrages opérationnels, implémentation et autorisations | Donne les GO de modification, Git et déploiement |
| Tech Lead / CTO | Fonction de pilotage technique | Architecture, qualité, sécurité, découpage, risques et verdicts de gate | Recommande, bloque techniquement et demande arbitrage humain |

Une IA peut tenir temporairement une fonction d’analyse ou de contrôle, mais elle ne devient jamais le responsable légal ou l’approbateur humain d’une opération sensible.

### 3.2 Rôles agents

| Rôle agent | Mission | Artefacts autorisés | Interdictions |
|---|---|---|---|
| Analyste produit | Clarifier problème, utilisateurs, preuves et scope | Brief, questions, analyse | Inventer le métier ou les chiffres |
| Product Manager | Créer, mettre à jour ou valider le PRD | PRD, addendum, rapport de validation | Choisir seul l’architecture |
| UX/UI Designer | Définir parcours, états, responsive et système visuel | DESIGN, EXPERIENCE, maquettes | Dégrader accessibilité ou copier une référence |
| Architecte | Définir les décisions techniques partagées | Architecture Spine, ADR | Implémenter sans story autorisée |
| Senior Developer | Implémenter une story prête | Code, tests, notes de build | Élargir le scope ou déployer |
| Code Reviewer | Examiner le diff et ses risques | Rapport de review, findings | Modifier silencieusement le code revu |
| Security Reviewer | Modéliser les menaces et contrôler les protections | Threat model, rapport sécurité | Déclarer sûr sans preuve |
| QA / Test Engineer | Vérifier les critères et parcours | Tests, matrice, preuves | Adapter le produit pour faire passer le test |
| Workflow Engineer | Maintenir CI/CD et contrôles | Pipelines, procédures | Contourner une gate rouge |

### 3.3 Séparation minimale des fonctions

- L’agent qui implémente ne rend pas seul le verdict final de review.
- La review doit partir du diff réel et des critères de la story.
- Une correction issue de review est re-testée.
- Pour un changement à risque élevé, la sécurité et la QA rendent chacune un verdict indépendant.

---

## 4. Hiérarchie des sources de vérité

| Priorité | Source | Rôle |
|---:|---|---|
| 1 | Instruction humaine explicite actuelle | Autorité de la session |
| 2 | Registre des décisions approuvées | Arbitrages stables |
| 3 | `docs/product/PRD.md` | Quoi et pourquoi |
| 4 | `docs/ux/DESIGN.md`, `EXPERIENCE.md` | Apparence, parcours et comportements |
| 5 | `docs/architecture/ARCHITECTURE-SPINE.md` + ADR | Décisions techniques partagées |
| 6 | `docs/specs/<epic>/SPEC.md` | Contrat de l’epic |
| 7 | Story active | Unité de build et critères |
| 8 | Code et tests vérifiés | État réel de l’implémentation |
| 9 | Suggestion d’agent | Proposition non validée |

En cas de divergence entre document et code, l’agent doit produire `CONFLICT_DETECTED` et demander quelle source doit être corrigée. Le code existant ne transforme pas automatiquement un comportement accidentel en exigence.

---

## 5. Arborescence documentaire cible

```text
/
├── AGENTS.md
├── CLAUDE.md
├── CURSOR.md
├── SKILLS.md
├── PRD-TEMPLATE.md
├── METHODE-BMAD.md
└── docs/
    ├── product/
    │   ├── PRD.md
    │   ├── PRD-ADDENDUM.md
    │   └── CHANGELOG.md
    ├── ux/
    │   ├── DESIGN.md
    │   └── EXPERIENCE.md
    ├── architecture/
    │   ├── ARCHITECTURE-SPINE.md
    │   └── adr/
    │       └── ADR-0001-<slug>.md
    ├── specs/
    │   └── <EPIC-ID>-<slug>/
    │       ├── SPEC.md
    │       ├── stories.yaml
    │       └── implementation-records/
    ├── stories/
    │   └── <STORY-ID>-<slug>.md
    ├── security/
    │   ├── THREAT-MODEL.md
    │   └── RISK-REGISTER.md
    ├── qa/
    │   ├── TEST-STRATEGY.md
    │   └── TRACEABILITY.md
    ├── runbooks/
    │   ├── DEPLOYMENT.md
    │   ├── ROLLBACK.md
    │   ├── BACKUP-RESTORE.md
    │   └── INCIDENT.md
    └── reports/
        └── <TICKET-ID>-REPORT.md
```

Cette arborescence est une cible. Elle est créée progressivement par tickets ; aucun agent ne doit générer tous les fichiers vides « pour faire propre ».

---

## 6. Dimensionnement du travail

### 6.1 Critères

Évaluer :

- clarté de l’intention ;
- nombre de composants et de systèmes touchés ;
- existence ou non d’un pattern établi ;
- impact données et migration ;
- impact sécurité ou conformité ;
- réversibilité ;
- nombre de sessions nécessaires ;
- coordination entre personnes ou agents ;
- impact utilisateur et exposition publique.

### 6.2 Classes

| Classe | Profil | Planification minimale |
|---|---|---|
| XS | Changement évident, local, réversible, faible risque | Ticket + critères + build + review |
| S | Une story, pattern connu, faible surface | Story complète + préflight + tests ciblés |
| M | Plusieurs fichiers/composants ou décision locale | Spec courte + stories + review renforcée |
| EPIC | Plusieurs sessions avec un résultat cohérent | Spec complète + stories ordonnées + checkpoints + validation intégrée |
| PROJECT | Plusieurs epics, produit greenfield ou coordination large | PRD + UX + architecture + spec par epic + gates complètes |
| HIGH-RISK | Sécurité, données, paiement, auth, migration, production | Processus PROJECT ciblé, threat model, rollback et approbation humaine |

### 6.3 Règles de calibration

- Une petite correction ne doit pas subir une cérémonie de projet complet.
- Un projet greenfield comme THE HIVE LOGISTICS nécessite PRD, UX et architecture avant les epics d’implémentation.
- Une story ne doit pas dépasser une session maîtrisable. Si elle comporte plusieurs résultats indépendants, la découper.
- Une modification minuscule mais irréversible ou liée à PROD reste HIGH-RISK.

---

## 7. Cycle projet greenfield

### Phase 0 — Intake et qualification

**Entrées :** demande brute, documents client, contraintes et décisions précédentes.  
**Responsable :** Product Owner avec Analyste/Tech Lead.  
**Sorties :** intention condensée, classe du travail, inconnues, risques initiaux.

Étapes :

1. reformuler l’intention sans la modifier ;
2. séparer faits, hypothèses, souhaits et décisions ;
3. confirmer les exclusions ;
4. identifier les sources et leur fraîcheur ;
5. attribuer une classe de travail ;
6. décider des documents réellement nécessaires.

**Gate G0 — INTENT_READY**

- résultat attendu observable ;
- invariants et exclusions visibles ;
- inconnues importantes identifiées ;
- périmètre assez clair pour produire un PRD ou une spec.

### Phase 1 — Discovery produit

**But :** comprendre le problème avant de figer la solution.

Activités possibles selon les lacunes :

- entretien métier ;
- inventaire des contenus ;
- analyse des utilisateurs ;
- recherche concurrentielle ou technique sourcée ;
- exploration de parcours ;
- analyse des risques ;
- clarification des mesures de succès.

Ces activités sont indépendantes. Elles ne sont pas obligatoirement exécutées dans un ordre fixe et ne produisent aucun code.

**Gate G1 — DISCOVERY_SUFFICIENT**

- problème et utilisateurs identifiés ;
- preuves disponibles distinguées des hypothèses ;
- arbitrages requis visibles ;
- aucune recherche supplémentaire indispensable à la décision suivante.

### Phase 2 — PRD

**But :** aligner les parties prenantes sur ce qui doit être construit et pourquoi.

Procédure :

1. copier `PRD-TEMPLATE.md` vers `docs/product/PRD.md` ;
2. remplir le PRD à partir des sources vérifiées ;
3. attribuer des IDs stables aux objectifs, capacités et exigences ;
4. expliciter le scope, le hors-scope et le futur ;
5. produire les parcours et critères observables ;
6. recenser données, contenus, risques et dépendances ;
7. lancer une validation critique sans modifier le document ;
8. corriger uniquement après arbitrage ;
9. recueillir les approbations.

**Gate G2 — PRD_APPROVED**

- Definition of Ready du PRD satisfaite ;
- validation métier, produit et technique ;
- aucune contradiction bloquante ;
- chaque exigence MUST est testable.

### Phase 3 — UX et architecture

Les deux flux peuvent progresser en parallèle lorsque leurs interfaces sont explicites, puis convergent avant la spec.

#### UX

- architecture de l’information ;
- parcours et états ;
- wireframes/maquettes ;
- composants et tokens ;
- comportement responsive ;
- accessibilité ;
- contenu et microcopy ;
- motion sobre et `prefers-reduced-motion`.

#### Architecture

- limites du système ;
- composants et responsabilités ;
- modèle de données ;
- contrats API ;
- décisions de sécurité ;
- stratégie d’erreur et d’observabilité ;
- environnements ;
- migrations ;
- CI/CD ;
- sauvegarde, restauration et rollback ;
- ADR pour les choix structurants.

**Gate G3 — SOLUTION_ALIGNED**

- UX couvre les parcours critiques et leurs états ;
- architecture couvre les décisions partagées ;
- les contraintes NFR sont adressées ;
- UX et architecture ne contredisent pas le PRD ;
- les risques majeurs possèdent un traitement.

### Phase 4 — Specs par epic

Une spec est le contrat condensé que l’implémentation doit lire. Elle contient au minimum :

1. **Why** — résultat et justification ;
2. **Capabilities** — capacités avec intention et condition de succès ;
3. **Constraints** — invariants produit, UX, architecture, sécurité et données ;
4. **Non-goals** — ce que l’epic ne doit pas construire ;
5. **Success signal** — preuve que l’epic atteint son résultat.

La spec référence le PRD, les designs et l’architecture ; elle ne les recopie pas intégralement.

**Gate G4 — SPEC_READY**

- spec suffisamment courte pour être consommée sans perte de contexte ;
- IDs et sources référencés ;
- contraintes et non-objectifs explicites ;
- aucun choix majeur laissé à improviser pendant le build.

### Phase 5 — Story Breakdown

Chaque story doit produire une slice indépendante et révisable.

Une story contient :

- ID et titre ;
- résultat utilisateur ou technique ;
- contexte nécessaire uniquement ;
- dépendances et préconditions ;
- périmètre inclus ;
- hors périmètre ;
- critères d’acceptation ;
- contraintes de sécurité et données ;
- stratégie de tests ;
- preuves attendues ;
- checkpoint avant/après si nécessaire ;
- autorisations explicites et interdictions.

**Gate G5 — STORY_READY**

- taille compatible avec une session ;
- dépendances satisfaites ;
- critères testables ;
- fichiers potentiellement concernés identifiés après préflight, sans liste artificielle ;
- stratégie de rollback définie si nécessaire ;
- aucun `[BLOQUANT]` ouvert.

### Phase 6 — Sprint planning

Le planning n’autorise pas le build ; il vérifie la préparation et ordonne le travail.

Verdicts autorisés :

- `PASS` — prêt à construire ;
- `CONCERNS` — constructible avec risques explicitement acceptés ;
- `FAIL` — non prêt ;
- `BLOCKED` — dépendance externe ou décision manquante.

Prioriser :

1. fondations et décisions irréversibles ;
2. risques techniques et sécurité ;
3. vertical slice démontrable ;
4. parcours principal ;
5. états secondaires et polish ;
6. intégration finale.

### Phase 7 — Build d’une story

Voir le protocole détaillé en section 10. Une seule story active par session d’agent, sauf autorisation explicite de tâches indépendantes.

### Phase 8 — Review et QA

Le diff, les tests, la sécurité et le comportement réel sont contrôlés séparément. Un build réussi n’équivaut pas à une validation produit.

### Phase 9 — Intégration et clôture d’epic

- tester les stories ensemble ;
- vérifier la matrice de traçabilité ;
- comparer le résultat à la spec parente ;
- vérifier les non-objectifs ;
- documenter les écarts ;
- réaliser une démonstration ;
- obtenir un verdict ;
- conduire une rétrospective ;
- synchroniser les documents.

### Phase 10 — Promotion et livraison

La promotion suit strictement :

`DEV → RECETTE → PREPROD → PROD`

Chaque transition possède son propre GO et ses propres preuves. Aucune réussite dans un environnement ne vaut autorisation automatique pour le suivant.

---

## 8. Workflow d’un ticket

### 8.1 Identifiant et type

Format recommandé :

`THL-<DOMAINE>-<NUMÉRO>-<SLUG>`

Domaines possibles : `FOUNDATION`, `PRODUCT`, `UX`, `WEB`, `API`, `DATA`, `SEC`, `QA`, `INFRA`, `OPS`, `CONTENT`, `SEO`, `HOTFIX`.

### 8.2 États

`DRAFT → READY → IN_PROGRESS → READY_FOR_REVIEW → CHANGES_REQUESTED → READY_FOR_RECETTE → ACCEPTED → DONE`

États exceptionnels : `BLOCKED`, `CANCELLED`, `SUPERSEDED`.

### 8.3 Contrat d’entrée obligatoire

```text
TICKET_ID=
TYPE=
OBJECTIVE=
SOURCE_REQUIREMENTS=
IN_SCOPE=
OUT_OF_SCOPE=
ACCEPTANCE_CRITERIA=
RISKS=
TEST_EXPECTATIONS=
ALLOWED_MUTATIONS=
FORBIDDEN_ACTIONS=
EXPECTED_REPORT=
```

### 8.4 Sortie obligatoire

```text
VERDICT=PASS | PASS_WITH_CONCERNS | FAIL | BLOCKED
TICKET_ID=
BASE_STATE=
FINAL_STATE=
FILES_CHANGED=
TESTS_RUN=
TEST_RESULTS=
SECURITY_CHECKS=
VISUAL_OR_RUNTIME_PROOFS=
WARNINGS=
RISKS_REMAINING=
OUT_OF_SCOPE_OBSERVATIONS=
GIT_ACTIONS=
ENVIRONMENT_MUTATIONS=
NEXT_RECOMMENDED_ACTION=
```

---

## 9. Préflight obligatoire

Avant toute modification, l’agent doit :

1. lire les fichiers de gouvernance applicables ;
2. identifier la story et ses sources ;
3. vérifier la branche, le HEAD, le worktree et l’index si Git existe ;
4. constater les changements préexistants et préserver ceux de l’utilisateur ;
5. vérifier versions d’outils, lockfiles et configuration utile ;
6. identifier les fichiers réellement concernés ;
7. analyser les chemins d’entrée, de sortie et d’erreur ;
8. relever les risques de sécurité, données, migration ou compatibilité ;
9. proposer un plan borné ;
10. s’arrêter si l’autorisation ou le contexte est insuffisant.

Le préflight est en lecture seule. Il ne « nettoie » jamais le dépôt et ne répare pas automatiquement un problème découvert.

---

## 10. Protocole de build

### 10.1 Avant écriture

- confirmer `STORY_READY` ;
- annoncer les fichiers ou zones attendus ;
- obtenir le GO si la gouvernance l’exige ;
- établir un baseline de tests pertinent ;
- vérifier l’absence de secret dans les entrées.

### 10.2 Pendant l’implémentation

- appliquer le changement minimal cohérent ;
- respecter l’architecture existante ;
- ne pas créer d’abstraction « au cas où » ;
- valider les entrées aux frontières ;
- traiter explicitement erreurs et états vides ;
- ajouter ou adapter les tests avec le code ;
- éviter les commentaires qui paraphrasent le code ;
- maintenir les types stricts ;
- ne pas masquer une erreur par un fallback silencieux ;
- ne jamais introduire de secret ou donnée réelle dans un fixture.

### 10.3 Après écriture

1. inspecter le diff complet ;
2. rechercher les fichiers accidentels et changements hors scope ;
3. exécuter les tests ciblés ;
4. exécuter les gates statiques applicables ;
5. construire l’application ;
6. vérifier le comportement réel ;
7. produire les preuves ;
8. effectuer une auto-review ;
9. transmettre à une review distincte ;
10. corriger et revalider si nécessaire.

### 10.4 Actions Git

Par défaut :

- création de branche : uniquement si demandée ou prévue par le ticket ;
- commit : GO explicite ;
- push : GO explicite distinct ou clairement inclus ;
- ouverture/fusion de PR : GO explicite ;
- rebase, reset, suppression de branche ou réécriture d’historique : opération sensible, jamais implicite.

---

## 11. Revue de code

### 11.1 Ordre de revue

1. conformité à la story et à ses non-objectifs ;
2. erreurs fonctionnelles et cas limites ;
3. sécurité, confidentialité et permissions ;
4. intégrité des données et concurrence ;
5. régressions et compatibilité ;
6. architecture et maintenabilité ;
7. tests et qualité des preuves ;
8. performance ;
9. UX, accessibilité et responsive ;
10. style et lisibilité.

### 11.2 Sévérités

| Niveau | Définition | Effet |
|---|---|---|
| P0 | Compromission, perte de données, indisponibilité critique ou danger PROD | Blocage immédiat |
| P1 | Bug majeur, faille élevée, parcours principal cassé | Blocage de merge/promotion |
| P2 | Défaut important mais contournable | Correction avant release ou acceptation formelle |
| P3 | Amélioration de qualité sans risque immédiat | Backlog possible |

### 11.3 Format d’un finding

```text
FINDING_ID=
SEVERITY=
LOCATION=
EVIDENCE=
IMPACT=
REPRODUCTION=
RECOMMENDATION=
BLOCKING=YES|NO
```

Une review sans finding doit tout de même préciser le diff examiné, les tests contrôlés et les limites de l’analyse.

---

## 12. Stratégie de tests

### 12.1 Niveaux

| Niveau | But | Exemples |
|---|---|---|
| Statique | Empêcher erreurs avant exécution | lint, format, types, secret scan, SAST |
| Unitaire | Vérifier une règle isolée | validation, formatage, calcul |
| Composant | Vérifier UI ou module isolé | états de composant, accessibilité |
| Intégration | Vérifier les frontières | API ↔ DB, formulaire ↔ service |
| Contrat | Stabiliser échanges | schéma OpenAPI, payloads, erreurs |
| E2E | Vérifier parcours critique | demande de devis, navigation |
| Visuel | Détecter régression UI | desktop, medium, mobile |
| Performance | Vérifier budgets | Web Vitals, charge API ciblée |
| Sécurité | Vérifier contrôles | DAST, abus, headers, rate limit |
| Résilience | Vérifier mode dégradé | service tiers indisponible, rollback |

### 12.2 Politique

- tester le comportement, pas l’implémentation interne sans raison ;
- toute correction de bug ajoute un test de non-régression lorsque possible ;
- les parcours critiques doivent avoir une preuve runtime ;
- aucun snapshot massif ne remplace des assertions utiles ;
- un test flaky est un défaut à traiter, pas une réussite à relancer jusqu’au vert ;
- un test ignoré doit avoir un motif, un propriétaire et une échéance.

---

## 13. Gate UX/UI

Pour chaque interface concernée :

- comparer au document UX et aux maquettes approuvées ;
- valider mobile, medium et desktop ;
- vérifier les tailles extrêmes, zoom et textes longs ;
- tester clavier, focus, lecteur d’écran de base et contraste ;
- vérifier chargement, erreur, vide, succès et latence ;
- respecter `prefers-reduced-motion` ;
- contrôler l’optimisation et les droits des images ;
- éviter les effets génériques d’IA et les animations non fonctionnelles ;
- vérifier qu’aucun contenu ne présente une offre future comme disponible.

Pour THE HIVE LOGISTICS, la qualité mobile est bloquante au même niveau que le desktop.

---

## 14. Gate sécurité

### 14.1 À chaque ticket

- entrées et sorties ;
- authentification/autorisation si applicable ;
- secrets ;
- exposition de données ;
- logs ;
- dépendances ;
- injection ;
- XSS/CSRF/CORS/CSP selon le contexte ;
- abus, bots et déni de service ;
- accès réseau ou filesystem ;
- impact sur sauvegarde et restauration.

### 14.2 Formulaires publics V1

- validation serveur stricte ;
- schéma partagé ou contrat explicite ;
- normalisation prudente ;
- limitation de taille ;
- honeypot ;
- rate limiting ;
- Turnstile si retenu par ADR ;
- messages d’erreur non révélateurs ;
- journalisation sans contenu sensible ;
- stratégie anti-rejeu si soumission asynchrone ;
- politique de conservation des demandes.

### 14.3 Fonctions futures à gate dédiée

Si authentification, paiement ou webhooks sont introduits plus tard :

- PRD et spec dédiés ;
- threat model ;
- séparation des environnements et des clés ;
- sandbox fournisseur ;
- tests magic link/OTP/OAuth/3-D Secure selon fonction ;
- signature sur corps brut, idempotence et prévention du rejeu pour webhook ;
- aucune suppression par webhook par défaut ;
- réconciliation et journal d’audit ;
- rollback et traitement des événements en erreur.

---

## 15. Données et migrations

### 15.1 Principes

- schéma identique par migrations versionnées ;
- données différentes et isolées par environnement ;
- aucune copie brute de PROD vers un environnement inférieur ;
- migration backward-compatible lorsque le déploiement l’exige ;
- migration destructive séparée et explicitement approuvée ;
- sauvegarde et restauration vérifiées avant une opération à risque ;
- seeds déterministes et synthétiques ;
- aucune migration automatique de PROD depuis un poste développeur.

### 15.2 Checklist migration

- [ ] impact et volumétrie évalués ;
- [ ] chemin forward testé ;
- [ ] rollback ou roll-forward défini ;
- [ ] verrouillage et temps d’exécution évalués ;
- [ ] compatibilité ancienne/nouvelle version vérifiée ;
- [ ] sauvegarde disponible ;
- [ ] observabilité et critères d’arrêt définis ;
- [ ] GO humain enregistré.

---

## 16. Environnements et promotion

| Environnement | Finalité | Données | Gate d’entrée | Mutations agent |
|---|---|---|---|---|
| DEV | Développement et tests locaux | Synthétiques | Story prête | Autorisées dans le scope |
| RECETTE | Acceptation fonctionnelle | Synthétiques dédiées | Review + CI vertes | Déploiement avec GO |
| PREPROD | Répétition de production | Synthétiques représentatives | Recette acceptée | Déploiement avec GO |
| PROD | Service réel | Réelles minimisées | Release candidate approuvée | Interdites sans GO explicite |

### Gate RECETTE

- CI applicable verte ;
- review terminée ;
- P0/P1 fermés ;
- build traçable ;
- notes de recette disponibles.

### Gate PREPROD

- recette fonctionnelle acceptée ;
- configuration et migrations proches de PROD ;
- smoke, sécurité et performance applicables ;
- rollback répété lorsque le risque l’exige.

### Gate PROD

- approbation humaine explicite ;
- version et artefact immuables identifiés ;
- sauvegarde vérifiée si données concernées ;
- migrations validées ;
- monitoring et alertes prêts ;
- rollback exécutable ;
- aucun P0/P1 ouvert ;
- risques résiduels acceptés par leur propriétaire.

---

## 17. CI/CD minimale

Le pipeline cible doit couvrir progressivement :

1. formatage ;
2. lint ;
3. types ;
4. tests unitaires ;
5. tests d’intégration ;
6. build frontend et backend ;
7. validation des migrations ;
8. scan de secrets ;
9. SAST et analyse des dépendances ;
10. tests E2E critiques ;
11. contrôles d’image/conteneur si conteneurisation ;
12. génération d’un artefact traçable ;
13. déploiement par environnement avec approbations.

Les actions CI tierces doivent être épinglées. Les lockfiles sont obligatoires et les mises à jour de dépendances doivent être auditées.

---

## 18. Sauvegarde, restauration et rollback

- Le dépôt Git distant protège l’historique du code ; il ne sauvegarde pas les données.
- Les artefacts de build immuables permettent un rollback applicatif fiable.
- La base de données, les médias et configurations critiques ont des sauvegardes séparées.
- Une sauvegarde non restaurée en test n’est pas considérée comme vérifiée.
- RPO, RTO, fréquence et rétention sont documentés avant mise en production.
- Les secrets ne sont ni exportés avec les backups, ni stockés dans le dépôt.

Toute procédure de rollback doit préciser : déclencheur, décideur, version cible, impact données, commandes, vérifications et communication.

---

## 19. Gestion du contexte IA

### 19.1 Context pack d’une story

Fournir uniquement :

- ticket/story active ;
- extraits PRD et spec référencés ;
- décisions UX/architecture concernées ;
- règles de gouvernance applicables ;
- état Git et fichiers pertinents ;
- tests et erreurs utiles.

### 19.2 Interdictions

- ne pas fournir des secrets ;
- ne pas coller tout le dépôt si une recherche ciblée suffit ;
- ne pas mélanger plusieurs stories non liées ;
- ne pas laisser une ancienne décision contredire la source actuelle ;
- ne pas demander à l’agent de « tout améliorer » sans bornes ;
- ne pas utiliser un long historique de chat comme unique source de vérité.

### 19.3 Mémoire durable

Les décisions durables vivent dans le dépôt. Le chat sert à collaborer ; il ne remplace pas le PRD, les ADR, les specs ni les rapports.

---

## 20. Utilisation des skills

L’agent choisit le minimum de skills nécessaires au ticket et annonce leur usage.

| Besoin | Skill projet suggéré |
|---|---|
| Composant/interface | `constructeur-ui`, `frontend-design-thl`, `ui-ux-pro-max` |
| API et contrats | `architecte-api` |
| Implémentation | `senior-dev`, `ingenieur` |
| Revue | `thl-code-review` |
| Sécurité | `reviewer-securite-code` |
| Workflow/CI | `createur-workflow` |
| Simplification | `simplify` |
| Architecture existante | `improve-codebase-architecture` |
| Composants shadcn | `thl-shadcn` |
| Création/évaluation d’un skill | `skill-lifecycle` |

Les skills ne donnent pas d’autorisation supplémentaire et ne remplacent pas les gates.

### BMAD officiel

L’adaptation présente fonctionne sans installer le package BMAD officiel. Cela évite les doublons et conflits avec la gouvernance déjà déployée. Une éventuelle installation de BMad doit faire l’objet d’un ticket séparé comprenant : audit des commandes, chemins générés, hooks, conflits de règles, mises à jour et procédure de désinstallation.

---

## 21. Gestion des changements

Un signal de changement peut venir du client, des utilisateurs, d’un test, d’un incident, d’une contrainte technique ou réglementaire.

Procédure :

1. enregistrer le signal ;
2. déterminer s’il corrige une erreur ou modifie l’intention ;
3. identifier les sources de vérité touchées ;
4. analyser impacts scope, UX, architecture, sécurité, données, coût et calendrier ;
5. produire options et recommandation ;
6. obtenir la décision humaine ;
7. versionner les documents ;
8. invalider ou mettre à jour les specs/stories devenues obsolètes ;
9. refaire les gates nécessaires.

Une instruction récente ne doit jamais être ajoutée seulement au ticket si elle change le produit entier.

---

## 22. Incident et hotfix

### Critères

Un hotfix concerne un défaut urgent en production : sécurité, perte de données, indisponibilité ou parcours critique cassé.

### Flux raccourci contrôlé

1. qualifier la sévérité ;
2. stabiliser et limiter l’impact ;
3. préserver les preuves ;
4. définir un changement minimal ;
5. tester la reproduction et le correctif ;
6. review sécurité/technique selon l’impact ;
7. obtenir GO PROD ;
8. déployer avec surveillance ;
9. vérifier le rétablissement ;
10. réaliser post-mortem et correction durable.

L’urgence réduit la documentation initiale, jamais les autorisations sensibles ni la rétrospective.

---

## 23. Rétrospective

À la fin de chaque epic ou incident, consigner :

- résultat par rapport à la spec ;
- décisions qui ont bien tenu ;
- hypothèses invalidées ;
- défauts échappés aux tests ;
- temps perdu par manque de contexte ;
- dette créée ou remboursée ;
- efficacité des agents et skills ;
- règles à maintenir, modifier ou retirer ;
- actions, propriétaires et échéances.

Une rétrospective ne modifie pas automatiquement la gouvernance. Toute évolution suit un ticket et des tests de non-régression des hooks/règles.

---

## 24. Definition of Ready d’une story

- [ ] objectif et valeur explicites ;
- [ ] source PRD/spec référencée ;
- [ ] scope et hors-scope bornés ;
- [ ] dépendances satisfaites ;
- [ ] critères d’acceptation testables ;
- [ ] risques sécurité/données évalués ;
- [ ] états UX nécessaires définis ;
- [ ] stratégie de tests précisée ;
- [ ] preuves attendues définies ;
- [ ] autorisations et actions interdites visibles ;
- [ ] taille compatible avec une session ;
- [ ] aucun blocage non résolu.

---

## 25. Definition of Done d’une story

- [ ] critères d’acceptation satisfaits ;
- [ ] diff limité au scope ;
- [ ] code lisible, typé et cohérent avec l’architecture ;
- [ ] erreurs et cas limites traités ;
- [ ] tests nouveaux ou adaptés ;
- [ ] tests ciblés, statiques et build applicables passés ;
- [ ] comportement runtime vérifié ;
- [ ] responsive/accessibilité contrôlés si UI ;
- [ ] sécurité contrôlée selon la surface ;
- [ ] documentation utile synchronisée ;
- [ ] review indépendante terminée ;
- [ ] aucun P0/P1 ouvert ;
- [ ] preuves et risques résiduels consignés ;
- [ ] actions Git/environnement rapportées exactement.

---

## 26. Definition of Done d’un epic

- [ ] toutes les stories requises sont acceptées ;
- [ ] intégration inter-stories testée ;
- [ ] spec et non-objectifs respectés ;
- [ ] matrice exigences → tests → preuves complète ;
- [ ] performance, sécurité et UX validées globalement ;
- [ ] écarts documentés et approuvés ;
- [ ] démonstration réalisée ;
- [ ] documentation et runbooks synchronisés ;
- [ ] rétrospective terminée ;
- [ ] dette restante transformée en tickets propriétaires.

---

## 27. Anti-patterns interdits

- commencer à coder à partir d’une idée vague ;
- demander « construis tout le site » dans une seule session ;
- utiliser plusieurs agents sur les mêmes fichiers sans ownership clair ;
- accepter un rapport de réussite sans sortie de test ;
- ajouter une dépendance parce qu’elle est populaire ;
- créer une abstraction avant le deuxième usage réel ;
- copier une référence visuelle ou du code sans vérifier droits et compatibilité ;
- cacher une erreur derrière un `try/catch` vide ou un fallback silencieux ;
- désactiver un contrôle CI pour obtenir du vert ;
- modifier les tests afin de valider un comportement incorrect ;
- mélanger données DEV, RECETTE, PREPROD et PROD ;
- utiliser des données de production non anonymisées hors PROD ;
- permettre à un webhook de supprimer des données sans garde-fou explicite ;
- annoncer un service, chiffre ou partenaire non confirmé ;
- créer des fichiers, composants ou pages « au cas où » ;
- auto-commiter, auto-pusher ou auto-déployer ;
- traiter le chat comme la seule mémoire du projet.

---

## 28. Indicateurs de santé du delivery

Suivre sans transformer les métriques en objectifs aveugles :

- taux de stories `READY` réellement terminées sans réouverture ;
- défauts découverts après review et après recette ;
- temps de cycle par classe de ticket ;
- fréquence des changements hors scope ;
- taux de tests flaky ;
- vulnérabilités par sévérité et délai de correction ;
- taux de rollback ou d’échec de déploiement ;
- dette ouverte avec propriétaire ;
- cohérence de la traçabilité PRD → spec → story → test ;
- satisfaction du Sponsor métier sur les parcours livrés.

La quantité de code, de prompts ou de messages agents n’est pas un indicateur de valeur.

---

## 29. Workflow initial THE HIVE LOGISTICS

Ordre recommandé avant le premier code produit :

1. `THL-PRODUCT-001` — produire et faire valider le PRD réel à partir de `PRD-TEMPLATE.md` ;
2. `THL-UX-001` — consolider architecture de l’information, parcours et système visuel ;
3. `THL-ARCH-001` — établir Architecture Spine et ADR de stack ;
4. `THL-SEC-001` — threat model V1 et exigences du formulaire public ;
5. `THL-QA-001` — stratégie de tests et matrice de compatibilité ;
6. `THL-FOUNDATION-001` — initialiser Git et le socle du dépôt après validation des documents structurants ;
7. créer une spec par epic ;
8. implémenter le premier vertical slice ;
9. établir RECETTE puis PREPROD ;
10. préparer la mise en production uniquement lorsque les gates métier, légales, sécurité et exploitation sont satisfaites.

Le premier objectif n’est pas de générer toute l’arborescence ou toutes les pages. Il est de produire un vertical slice démontrant que les décisions produit, visuelles et techniques fonctionnent ensemble.

---

## 30. Checklist de démarrage d’une session agent

```text
[ ] Gouvernance lue
[ ] Ticket et story identifiés
[ ] Sources de vérité identifiées
[ ] Préflight read-only terminé
[ ] État Git rapporté
[ ] Changements préexistants préservés
[ ] Scope et hors-scope reformulés
[ ] Risques et inconnues annoncés
[ ] Plan borné proposé
[ ] Autorisation d’écriture confirmée
```

## 31. Checklist de clôture d’une session agent

```text
[ ] Diff inspecté
[ ] Aucun changement hors scope
[ ] Tests et build applicables exécutés
[ ] Vérification runtime effectuée
[ ] Sécurité et données contrôlées
[ ] Preuves enregistrées
[ ] Limites et risques résiduels annoncés
[ ] Documentation synchronisée
[ ] Aucune action Git ou environnement non autorisée
[ ] Verdict explicite rendu
```

---

## 32. Références méthodologiques

Cette adaptation suit les principes actuels de BMad Method : processus dimensionné selon l’intention, contexte durable, rôles spécialisés, PRD pour l’alignement multi-epic, spec comme contrat d’implémentation, découpage en stories, build par session, review et clôture d’epic.

- Documentation : https://docs.bmad-method.org/
- Parcours de planification : https://docs.bmad-method.org/plan/choose-a-planning-path/
- Exigences et spécification : https://docs.bmad-method.org/plan/define-requirements-and-a-specification/
- UX et architecture : https://docs.bmad-method.org/plan/design-ux-and-architecture/
- Référence des agents : https://docs.bmad-method.org/fr/reference/agents/
- Dépôt officiel : https://github.com/bmad-code-org/BMAD-METHOD

Les noms BMad et BMAD-METHOD appartiennent à leurs détenteurs respectifs. Ce fichier définit uniquement la procédure interne du projet THE HIVE LOGISTICS.
