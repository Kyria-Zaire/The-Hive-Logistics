# PRD — Modèle canonique THE HIVE LOGISTICS

> **Type :** Product Requirements Document (PRD)  
> **Statut du modèle :** APPROUVÉ POUR RÉDACTION  
> **Version du modèle :** 1.0.0  
> **Dernière mise à jour :** 2026-09-12  
> **Propriétaire :** Product Owner  
> **Validation :** Sponsor métier + Product Owner + Tech Lead  
> **Usage :** copier ce modèle vers `docs/product/PRD.md`, puis remplacer tous les champs entre chevrons.

---

## 0. Contrat d’utilisation du document

Ce PRD constitue la source de vérité du **quoi** et du **pourquoi**. Il décrit le problème, les utilisateurs, les capacités attendues, les exigences et les signaux de succès. Il ne doit pas devenir un document d’implémentation détaillé.

Les décisions techniques structurantes appartiennent à `ARCHITECTURE-SPINE.md` et aux ADR. Les contrats d’implémentation par epic appartiennent aux fichiers `SPEC.md`. Les tâches unitaires appartiennent aux stories.

### Règles pour les humains et les agents IA

1. Ne jamais inventer une exigence, un chiffre, un témoignage, un partenaire, une certification ou une donnée métier.
2. Préserver les identifiants stables (`OBJ-`, `CAP-`, `FR-`, `NFR-`, `RISK-`, `DEC-`) lors des mises à jour.
3. Marquer toute hypothèse avec `[HYPOTHÈSE]`, toute inconnue avec `[À CONFIRMER]` et tout blocage avec `[BLOQUANT]`.
4. Ne pas transformer une hypothèse en décision sans validation humaine explicite.
5. Lors d’une mise à jour, produire une analyse d’impact avant de modifier le périmètre.
6. Les exigences doivent être observables, testables et rattachées à un objectif.
7. Les choix de stack, de fournisseur ou de structure interne ne doivent apparaître ici que comme contraintes déjà validées, sans détails d’implémentation.
8. Le PRD ne donne aucune autorisation de commit, push, fusion, déploiement ou mutation d’environnement.

### Ordre d’autorité

En cas de conflit, appliquer cet ordre :

1. instruction humaine explicite et actuelle ;
2. décision validée et consignée dans le registre des décisions ;
3. présent PRD approuvé ;
4. architecture et ADR approuvés ;
5. spécification de l’epic ;
6. story active ;
7. suggestions d’un agent ou conventions implicites.

Tout conflit doit être signalé. Il ne doit jamais être résolu silencieusement.

---

## 1. Contrôle documentaire

| Champ | Valeur |
|---|---|
| Produit | `<NOM_DU_PRODUIT>` |
| Référence | `<PRD-ID>` |
| Version | `<X.Y.Z>` |
| Statut | `DRAFT / IN_REVIEW / APPROVED / SUPERSEDED` |
| Sponsor métier | `<NOM>` |
| Product Owner | `<NOM>` |
| Tech Lead | `<NOM_OU_RÔLE>` |
| UX/UI Lead | `<NOM_OU_RÔLE>` |
| Security Reviewer | `<NOM_OU_RÔLE>` |
| Date de création | `<AAAA-MM-JJ>` |
| Dernière révision | `<AAAA-MM-JJ>` |
| Horizon couvert | `<V1 / période / release>` |
| Documents sources | `<LIENS_OU_CHEMINS>` |

### Historique des versions

| Version | Date | Auteur | Nature du changement | Décision associée |
|---|---|---|---|---|
| 0.1.0 | `<DATE>` | `<AUTEUR>` | Première rédaction | `<DEC-ID ou N/A>` |

### Approbations

| Rôle | Nom | Verdict | Date | Réserves |
|---|---|---|---|---|
| Sponsor métier | `<NOM>` | `<APPROUVÉ / REFUSÉ>` | `<DATE>` | `<TEXTE>` |
| Product Owner | `<NOM>` | `<APPROUVÉ / REFUSÉ>` | `<DATE>` | `<TEXTE>` |
| Tech Lead | `<NOM_OU_RÔLE>` | `<APPROUVÉ / REFUSÉ>` | `<DATE>` | `<TEXTE>` |

---

## 2. Résumé exécutif

### 2.1 Produit en une phrase

`<POUR QUI, QUEL PROBLÈME, QUELLE PROPOSITION DE VALEUR>`

### 2.2 Problème à résoudre

`<DÉCRIRE LE PROBLÈME UTILISATEUR OU MÉTIER, SES CAUSES ET SES CONSÉQUENCES>`

### 2.3 Réponse proposée

`<DÉCRIRE LE PRODUIT ET LE RÉSULTAT ATTENDU, SANS DÉTAILLER L’IMPLÉMENTATION>`

### 2.4 Valeur attendue

- Pour les visiteurs : `<VALEUR>`
- Pour l’entreprise : `<VALEUR>`
- Pour les partenaires : `<VALEUR>`

### 2.5 Résultat attendu à la fin de la release

`<ÉTAT OBSERVABLE QUI DEVRA ÊTRE VRAI À LA LIVRAISON>`

---

## 3. Contexte et preuves

### 3.1 Situation actuelle

`<PROCESSUS ACTUEL, OUTILS, LIMITES, RETOURS UTILISATEURS, DONNÉES DISPONIBLES>`

### 3.2 Opportunité

`<POURQUOI LE PROJET EST UTILE MAINTENANT>`

### 3.3 Éléments probants

| Référence | Type | Fait établi | Source | Date | Niveau de confiance |
|---|---|---|---|---|---|
| EVD-001 | `<ENTRETIEN / ANALYTIQUE / DOCUMENT / RECHERCHE>` | `<FAIT>` | `<SOURCE>` | `<DATE>` | `<FORT / MOYEN / FAIBLE>` |

### 3.4 Contraintes héritées

- `<CONTRAINTE CONTRACTUELLE>`
- `<CONTRAINTE RÉGLEMENTAIRE>`
- `<CONTRAINTE DE DÉLAI OU BUDGET>`
- `<CONTRAINTE TECHNIQUE DÉJÀ VALIDÉE>`

---

## 4. Vision, principes et positionnement

### 4.1 Vision produit

`<VISION À 12–36 MOIS>`

### 4.2 Promesse principale

`<PROMESSE CLAIRE ET CRÉDIBLE>`

### 4.3 Principes produit

| ID | Principe | Conséquence concrète |
|---|---|---|
| PP-001 | `<PRINCIPE>` | `<RÈGLE DE DÉCISION>` |

### 4.4 Positionnement

- Segment : `<SEGMENT>`
- Différenciation : `<DIFFÉRENCIATEURS PROUVABLES>`
- Perception recherchée : `<ATTRIBUTS DE MARQUE>`
- Perceptions à éviter : `<RISQUES DE POSITIONNEMENT>`

---

## 5. Utilisateurs et parties prenantes

### 5.1 Segments utilisateurs

| ID | Segment | Besoin principal | Contexte d’utilisation | Fréquence | Priorité |
|---|---|---|---|---|---|
| USR-001 | `<SEGMENT>` | `<BESOIN>` | `<CONTEXTE>` | `<FRÉQUENCE>` | `<P0/P1/P2>` |

### 5.2 Persona ou protagoniste de parcours

**Nom :** `<PRÉNOM FICTIF>`  
**Profil :** `<PROFIL>`  
**Objectif :** `<OBJECTIF>`  
**Freins :** `<FREINS>`  
**Critères de confiance :** `<CRITÈRES>`  
**Appareil et contexte :** `<MOBILE/DESKTOP, LIEU, URGENCE>`

### 5.3 Parties prenantes

| Partie prenante | Responsabilité | Décisions détenues | Mode de consultation |
|---|---|---|---|
| `<RÔLE>` | `<RESPONSABILITÉ>` | `<DÉCISIONS>` | `<CANAL/FRÉQUENCE>` |

### 5.4 RACI simplifié

| Activité | Responsable | Approbateur | Consulté | Informé |
|---|---|---|---|---|
| Validation métier | `<R>` | `<A>` | `<C>` | `<I>` |
| Architecture | `<R>` | `<A>` | `<C>` | `<I>` |
| Mise en production | `<R>` | `<A>` | `<C>` | `<I>` |

---

## 6. Objectifs et signaux de succès

### 6.1 Objectifs

| ID | Objectif | Indicateur | Valeur initiale | Cible | Échéance | Méthode de mesure |
|---|---|---|---|---|---|---|
| OBJ-001 | `<OBJECTIF>` | `<KPI>` | `<BASELINE OU INCONNUE>` | `<CIBLE>` | `<DATE>` | `<SOURCE>` |

### 6.2 Garde-fous

| ID | Signal à ne pas dégrader | Seuil | Action si dépassement |
|---|---|---|---|
| GRD-001 | `<MÉTRIQUE>` | `<SEUIL>` | `<ACTION>` |

### 6.3 Anti-métriques

Ne pas utiliser seules comme preuve de succès :

- volume de pages ou de code produit ;
- nombre d’animations ;
- quantité de fonctionnalités livrées ;
- trafic non qualifié ;
- score synthétique sans mesure réelle du parcours.

---

## 7. Périmètre

### 7.1 Inclus dans la release

| ID | Capacité | Valeur utilisateur | Priorité | Justification |
|---|---|---|---|---|
| CAP-001 | `<CAPACITÉ>` | `<VALEUR>` | `<MUST/SHOULD/COULD>` | `<POURQUOI>` |

### 7.2 Explicitement hors périmètre

| ID | Élément exclu | Motif | Réexamen éventuel |
|---|---|---|---|
| OUT-001 | `<EXCLUSION>` | `<MOTIF>` | `<VERSION/CONDITION/NON>` |

### 7.3 Périmètre différé

| ID | Capacité future | Déclencheur de réévaluation | Dépendances |
|---|---|---|---|
| FUT-001 | `<CAPACITÉ>` | `<SIGNAL>` | `<DÉPENDANCES>` |

### 7.4 Garde-fous validés pour THE HIVE LOGISTICS

Ce bloc reste actif tant qu’une décision formelle ne le remplace pas.

- V1 : site vitrine premium centré sur le convoyage automobile, la gestion de flotte, la logistique automobile et la préparation/remise de véhicules.
- Aucun service immobilier.
- Aucun service de chauffeur privé.
- Médias V1 : photographies ; aucune dépendance obligatoire à une vidéo générée.
- Pas de compte utilisateur, magic link, OTP ou OAuth en V1.
- Pas de réservation automatisée, tarification automatique, paiement ou webhook de paiement en V1.
- La location automobile premium peut être évoquée uniquement comme perspective future, jamais comme service disponible si elle ne l’est pas.
- Les témoignages, volumes de véhicules, partenaires, disponibilités et garanties ne sont publiés qu’après validation et preuve fournies par le client.
- Contraintes techniques déjà validées : frontend Next.js avec TypeScript strict, backend Python avec FastAPI, PostgreSQL et architecture en monolithe modulaire.
- Redis, les microservices, un CMS, un moteur de paiement ou toute autre brique d’infrastructure ne sont pas ajoutés sans besoin démontré et ADR approuvé.
- Toute évolution hors de ce bloc exige une demande de changement et une analyse d’impact.

---

## 8. Parcours utilisateurs

### Parcours JRN-001 — `<NOM DU PARCOURS>`

**Acteur :** `<UTILISATEUR>`  
**Déclencheur :** `<ÉVÉNEMENT>`  
**Résultat recherché :** `<RÉSULTAT>`

| Étape | Action utilisateur | Réponse du produit | Donnée requise | Risque/échec | Récupération |
|---|---|---|---|---|---|
| 1 | `<ACTION>` | `<RÉPONSE>` | `<DONNÉE>` | `<RISQUE>` | `<SOLUTION>` |

### États transverses à décrire

- chargement ;
- succès ;
- erreur technique ;
- erreur de validation ;
- absence de contenu ;
- connexion lente ou interrompue ;
- interaction clavier ;
- réduction des animations ;
- consentement ou indisponibilité d’un service tiers.

---

## 9. Exigences fonctionnelles

Chaque exigence exprime un comportement observable. Éviter les termes non vérifiables comme « moderne », « intuitif » ou « rapide » sans critère associé.

| ID | Capacité liée | Exigence | Priorité | Critère d’acceptation | Source |
|---|---|---|---|---|---|
| FR-001 | CAP-001 | Le produit doit `<COMPORTEMENT OBSERVABLE>`. | MUST | Étant donné `<CONTEXTE>`, lorsque `<ACTION>`, alors `<RÉSULTAT>`. | `<SOURCE>` |

### Règles métier

| ID | Règle | Cas limites | Propriétaire |
|---|---|---|---|
| BR-001 | `<RÈGLE MÉTIER>` | `<CAS LIMITES>` | `<RÔLE>` |

### Contenus et preuves métier

| ID | Contenu | Fournisseur | Statut | Preuve/validation | Fallback autorisé |
|---|---|---|---|---|---|
| CNT-001 | `<TEXTE/PHOTO/LOGO/COORDONNÉE>` | `<PERSONNE>` | `<MANQUANT/REÇU/VALIDÉ>` | `<RÉFÉRENCE>` | `<OUI/NON + DÉTAIL>` |

---

## 10. Exigences UX, UI et marque

### 10.1 Intentions d’expérience

- `<SENTIMENT OU QUALITÉ ATTENDUE>` → preuve observable : `<INDICATEUR/COMPORTEMENT>`

### 10.2 Architecture de l’information

| Route/écran | Objectif | Contenu principal | CTA principal | CTA secondaire |
|---|---|---|---|---|
| `<ROUTE>` | `<OBJECTIF>` | `<CONTENU>` | `<CTA>` | `<CTA>` |

### 10.3 Responsive

Les exigences doivent couvrir au minimum :

- mobile étroit ;
- mobile large ;
- écran moyen/tablette ;
- desktop ;
- grand écran sans étirement excessif du contenu.

Les breakpoints exacts relèvent du système de design. Les parcours, contenus et actions principales doivent rester équivalents sur tous les formats.

### 10.4 Accessibilité

- navigation complète au clavier ;
- ordre de focus cohérent et focus visible ;
- structure sémantique et titres hiérarchisés ;
- textes alternatifs pertinents ;
- contraste compatible avec le niveau WCAG retenu ;
- prise en charge de `prefers-reduced-motion` ;
- libellés et messages d’erreur compréhensibles ;
- zones tactiles adaptées au mobile.

### 10.5 Direction artistique THE HIVE LOGISTICS

- positionnement premium, professionnel, rassurant, moderne et minimaliste ;
- noir profond, blanc, gris anthracite et accent rouge `#FF5757` ;
- ambiance automobile nocturne, lignes fines et espace négatif maîtrisé ;
- photographies réalistes et juridiquement exploitables ;
- animations discrètes au service de la compréhension ;
- aucun effet visuel gratuit, imitation servile d’une marque ou esthétique générique d’IA ;
- qualité mobile considérée comme un livrable de premier rang.

Les références externes servent à analyser des principes, jamais à copier une composition, des textes, une identité ou des actifs protégés.

---

## 11. Exigences non fonctionnelles

| ID | Domaine | Exigence mesurable | Méthode de vérification | Seuil de blocage |
|---|---|---|---|---|
| NFR-PERF-001 | Performance | `<EXIGENCE>` | `<LIGHTHOUSE/RUM/TEST>` | `<SEUIL>` |
| NFR-REL-001 | Fiabilité | `<EXIGENCE>` | `<TEST/MONITORING>` | `<SEUIL>` |
| NFR-SEC-001 | Sécurité | `<EXIGENCE>` | `<SAST/DAST/REVUE>` | `<SEUIL>` |
| NFR-PRIV-001 | Vie privée | `<EXIGENCE>` | `<AUDIT>` | `<SEUIL>` |
| NFR-A11Y-001 | Accessibilité | `<EXIGENCE>` | `<AXE/MANUEL>` | `<SEUIL>` |
| NFR-SEO-001 | Référencement | `<EXIGENCE>` | `<CRAWL/VALIDATION>` | `<SEUIL>` |
| NFR-OBS-001 | Observabilité | `<EXIGENCE>` | `<TEST D’ALERTE>` | `<SEUIL>` |
| NFR-COMP-001 | Compatibilité | `<NAVIGATEURS/APPAREILS>` | `<MATRICE QA>` | `<SEUIL>` |
| NFR-MAINT-001 | Maintenabilité | `<EXIGENCE>` | `<LINT/TYPES/TESTS>` | `<SEUIL>` |

### Baseline recommandée à confirmer dans l’architecture

- validation serveur de toutes les entrées publiques ;
- limitation de débit et protection anti-automatisation proportionnées au risque ;
- honeypot et Turnstile pour le formulaire public si validés par l’architecture ;
- aucun secret dans le navigateur, le dépôt, les logs ou les réponses d’erreur ;
- dépendances verrouillées et contrôlées ;
- politique CSP et en-têtes de sécurité définis avant exposition publique ;
- journalisation sans données sensibles ;
- comportement fonctionnel avec JavaScript ralenti et réseau dégradé lorsque pertinent.

---

## 12. Données, vie privée et rétention

### 12.1 Inventaire des données

| ID | Donnée | Finalité | Base légale | Sensibilité | Rétention | Accès | Suppression |
|---|---|---|---|---|---|---|---|
| DATA-001 | `<DONNÉE>` | `<FINALITÉ>` | `<BASE>` | `<NIVEAU>` | `<DURÉE>` | `<RÔLES>` | `<PROCÉDURE>` |

### 12.2 Principes

- minimisation des données ;
- finalité explicite ;
- durée de conservation documentée ;
- aucune donnée de production dans DEV ;
- données synthétiques en RECETTE et PREPROD, sauf procédure d’anonymisation irréversible approuvée ;
- sauvegardes chiffrées, testées et soumises à la même politique de rétention ;
- droits d’accès selon le moindre privilège.

### 12.3 Consentement et traceurs

`<CATÉGORIES DE TRACEURS, MODE DE CONSENTEMENT, OUTIL, PREUVE, RETRAIT>`

---

## 13. SEO, partage et découvrabilité

| Sujet | Exigence |
|---|---|
| Métadonnées | `<TITLE, DESCRIPTION, CANONICAL>` |
| Indexation | `<ROUTES INDEXABLES/NON INDEXABLES>` |
| Données structurées | `<TYPE SCHEMA.ORG ET JUSTIFICATION>` |
| Réseaux sociaux | `<OPEN GRAPH / CARDS>` |
| Sitemap/robots | `<RÈGLES>` |
| Local SEO | `<COORDONNÉES, ZONE, ÉTABLISSEMENT — UNIQUEMENT SI VALIDÉS>` |
| Mesure | `<SEARCH CONSOLE / ANALYTIQUE>` |

---

## 14. Intégrations et dépendances externes

| ID | Service | Finalité | Données échangées | Mode dégradé | Risque fournisseur | Propriétaire |
|---|---|---|---|---|---|---|
| INT-001 | `<SERVICE>` | `<FINALITÉ>` | `<DONNÉES>` | `<FALLBACK>` | `<RISQUE>` | `<RÔLE>` |

Toute nouvelle intégration requiert une revue de sécurité, de confidentialité, de coût, de disponibilité et de réversibilité.

---

## 15. Environnements, mise en service et exploitation

### 15.1 Environnements

| Environnement | Usage | Données | Accès | Déploiement |
|---|---|---|---|---|
| DEV | Développement local | Synthétiques | Développeur | Manuel/local |
| RECETTE | Validation fonctionnelle | Synthétiques dédiées | Équipe + recette | Contrôlé |
| PREPROD | Répétition production | Synthétiques représentatives | Restreint | Pipeline |
| PROD | Service public | Réelles minimisées | Très restreint | Autorisation humaine |

### 15.2 Promotion

`DEV → RECETTE → PREPROD → PROD`

Aucune promotion ne doit être implicite. Chaque passage conserve la traçabilité de la version, des migrations, des tests, des risques acceptés et de l’approbateur.

### 15.3 Sauvegarde et reprise

- code : dépôt Git distant et artefacts de build traçables ;
- données : sauvegardes automatisées selon RPO/RTO approuvés ;
- restauration : test périodique documenté ;
- médias : stratégie de versionnement et de réplication ;
- aucun backup applicatif ne doit être présenté comme une sauvegarde de base de données.

| Élément | RPO | RTO | Fréquence | Rétention | Test de restauration |
|---|---|---|---|---|---|
| `<ÉLÉMENT>` | `<DURÉE>` | `<DURÉE>` | `<FRÉQUENCE>` | `<DURÉE>` | `<DATE/PROCÉDURE>` |

---

## 16. Sécurité et abus

### 16.1 Surface d’attaque

| Surface | Actif protégé | Menace | Contrôle attendu | Test |
|---|---|---|---|---|
| Formulaire public | Données et disponibilité | Spam, injection, abus | Validation, rate limit, anti-bot | `<TEST>` |

### 16.2 Règles impératives

- aucune opération destructive déclenchée par un webhook sans justification, idempotence et garde-fou validés ;
- vérification de signature sur le corps brut pour tout webhook futur ;
- prévention du rejeu, idempotence, transaction et journal d’audit ;
- authentification et paiement restent hors V1 tant qu’un PRD et une architecture dédiés ne les introduisent pas ;
- tout fournisseur de paiement futur doit proposer sandbox, cartes de test et parcours 3-D Secure testables sans argent réel ;
- aucune mutation PROD par un agent sans autorisation humaine explicite ;
- toute vulnérabilité critique ou élevée exploitable bloque la mise en production jusqu’à correction ou acceptation de risque formelle.

### 16.3 Menaces et abus

| ID | Scénario | Probabilité | Impact | Prévention | Détection | Réponse |
|---|---|---|---|---|---|---|
| RISK-SEC-001 | `<SCÉNARIO>` | `<F/M/F>` | `<F/M/F>` | `<CONTRÔLE>` | `<SIGNAL>` | `<ACTION>` |

---

## 17. Observabilité et analytique produit

| Événement | Finalité | Propriétés autorisées | Données interdites | Conservation |
|---|---|---|---|---|
| `<EVENT_NAME>` | `<MESURE>` | `<PROPRIÉTÉS>` | `<PII/SECRET>` | `<DURÉE>` |

### Signaux opérationnels

- disponibilité ;
- latence et taux d’erreur ;
- échec d’envoi de formulaire ;
- saturation du rate limit ;
- erreur d’intégration tierce ;
- régression Core Web Vitals ;
- alertes de sécurité pertinentes.

---

## 18. Risques, hypothèses et dépendances

### 18.1 Registre des risques

| ID | Risque | Probabilité | Impact | Score | Réduction | Propriétaire | Statut |
|---|---|---|---|---|---|---|---|
| RISK-001 | `<RISQUE>` | `<1–5>` | `<1–5>` | `<P×I>` | `<ACTION>` | `<RÔLE>` | `<OUVERT/TRAITÉ/ACCEPTÉ>` |

### 18.2 Hypothèses

| ID | Hypothèse | Méthode de validation | Échéance | Conséquence si fausse |
|---|---|---|---|---|
| ASM-001 | `<HYPOTHÈSE>` | `<TEST/PREUVE>` | `<DATE>` | `<IMPACT>` |

### 18.3 Dépendances

| ID | Dépendance | Type | Propriétaire | Date requise | Plan de repli |
|---|---|---|---|---|---|
| DEP-001 | `<DÉPENDANCE>` | `<HUMAINE/TECHNIQUE/CONTENU/LÉGALE>` | `<RÔLE>` | `<DATE>` | `<FALLBACK>` |

---

## 19. Découpage de haut niveau

Le PRD définit les epics sans les transformer en listes de fichiers à modifier.

| Epic | Résultat cohérent | Capacités couvertes | Dépendances | Risque | Ordre |
|---|---|---|---|---|---|
| EPIC-001 | `<RÉSULTAT>` | `<CAP-IDs>` | `<DEP-IDs>` | `<F/M/F>` | `<N>` |

Chaque epic doit ensuite recevoir son propre `SPEC.md` et son découpage en stories indépendamment vérifiables.

---

## 20. Stratégie de validation

### 20.1 Validation produit

- revue des parcours avec le Sponsor métier ;
- validation du contenu et des affirmations ;
- comparaison avec les objectifs et non avec la quantité de fonctionnalités ;
- recette sur appareils et navigateurs représentatifs ;
- preuve visuelle responsive pour les écrans concernés.

### 20.2 Validation technique

- lint et formatage ;
- vérification statique des types ;
- tests unitaires et d’intégration ;
- tests API et validation des schémas ;
- tests E2E des parcours critiques ;
- revue de sécurité et dépendances ;
- build reproductible ;
- smoke tests sur chaque environnement ;
- contrôle des migrations et de la restauration lorsque concernés.

### 20.3 Matrice de traçabilité

| Exigence | Objectif | Epic/Spec | Stories | Tests | Preuve | Statut |
|---|---|---|---|---|---|---|
| FR-001 | OBJ-001 | EPIC-001 | `<STORY-ID>` | `<TEST-ID>` | `<LIEN>` | `<PASS/FAIL>` |

---

## 21. Definition of Ready du PRD

Le PRD peut passer à `APPROVED` uniquement si :

- le problème et les utilisateurs sont identifiés ;
- les objectifs disposent de signaux mesurables ou d’un plan de mesure ;
- le périmètre et les non-objectifs sont explicites ;
- les exigences critiques possèdent des identifiants stables ;
- les contenus ou données manquants sont visibles ;
- les risques et dépendances majeurs ont un propriétaire ;
- aucune contradiction ouverte ne bloque l’architecture ;
- le Sponsor métier, le Product Owner et le Tech Lead ont rendu leur verdict.

---

## 22. Definition of Done du produit ou de la release

La release est terminée uniquement si :

- toutes les exigences MUST sont traçables et validées ;
- les critères d’acceptation critiques passent en environnement cible ;
- les parcours principaux sont validés sur mobile, écran moyen et desktop ;
- les contenus publiés sont approuvés et juridiquement exploitables ;
- les contrôles de sécurité applicables passent ;
- aucune vulnérabilité bloquante ni régression critique connue n’est ouverte ;
- l’observabilité, les sauvegardes et le rollback applicables sont vérifiés ;
- les écarts acceptés sont consignés avec propriétaire et échéance ;
- la validation humaine de livraison est enregistrée.

---

## 23. Questions ouvertes

| ID | Question | Impact | Propriétaire | Échéance | Statut/Réponse |
|---|---|---|---|---|---|
| Q-001 | `<QUESTION>` | `<IMPACT>` | `<RÔLE>` | `<DATE>` | `<OUVERTE/RÉSOLUE>` |

---

## 24. Registre des décisions

| ID | Date | Décision | Alternatives | Justification | Décideur | Impact |
|---|---|---|---|---|---|---|
| DEC-001 | `<DATE>` | `<DÉCISION>` | `<OPTIONS>` | `<RAISON>` | `<RÔLE>` | `<SECTIONS/EPICS>` |

Une décision technique complexe doit pointer vers un ADR plutôt que d’être développée dans ce tableau.

---

## 25. Demandes de changement

| ID | Date | Signal de changement | Sections touchées | Impact scope/coût/délai/risque | Verdict | Décision liée |
|---|---|---|---|---|---|---|
| CR-001 | `<DATE>` | `<DEMANDE>` | `<SECTIONS>` | `<ANALYSE>` | `<ACCEPTÉ/REFUSÉ/DÉFÉRÉ>` | `<DEC-ID>` |

### Procédure

1. enregistrer la demande sans modifier le PRD ;
2. analyser les conflits et la traçabilité ;
3. mesurer l’impact produit, UX, technique, sécurité, données, budget et calendrier ;
4. obtenir un verdict humain ;
5. mettre à jour le PRD et son numéro de version ;
6. répercuter la décision dans l’architecture, les specs et les stories concernées ;
7. revalider la préparation à l’implémentation.

---

## 26. Handoff aux étapes suivantes

Lorsque le PRD est approuvé :

1. produire ou mettre à jour `docs/ux/DESIGN.md` et `docs/ux/EXPERIENCE.md` si l’expérience est structurante ;
2. produire ou mettre à jour `docs/architecture/ARCHITECTURE-SPINE.md` et les ADR nécessaires ;
3. vérifier la cohérence PRD ↔ UX ↔ architecture ;
4. créer un `SPEC.md` par epic ;
5. découper chaque spec en stories ordonnées et vérifiables ;
6. appliquer la gate de readiness avant tout build ;
7. implémenter une story par session de travail ;
8. revoir, tester et intégrer chaque slice ;
9. valider l’epic dans son ensemble ;
10. clôturer par une rétrospective et synchroniser les documents devenus obsolètes.

---

## 27. Checklist finale du rédacteur

- [ ] Tous les champs temporaires utiles sont complétés.
- [ ] Les champs inutiles sont supprimés proprement, pas laissés vides.
- [ ] Les faits et affirmations sont sourcés ou marqués à confirmer.
- [ ] Les termes métier sont définis dans un glossaire si nécessaire.
- [ ] Chaque MUST possède un critère d’acceptation.
- [ ] Le périmètre futur n’est pas présenté comme disponible.
- [ ] Les exigences sont indépendantes de la solution sauf contrainte validée.
- [ ] Les risques de contenu, sécurité, données et exploitation sont couverts.
- [ ] Les décisions et désaccords sont visibles.
- [ ] La matrice de traçabilité peut être remplie jusqu’aux preuves de test.
- [ ] Le document a reçu les approbations requises.

---

## 28. Glossaire

| Terme | Définition retenue dans le projet |
|---|---|
| Capacité | Résultat ou comportement que le produit doit rendre possible. |
| Exigence fonctionnelle | Comportement observable exigé du produit. |
| Exigence non fonctionnelle | Niveau de qualité ou contrainte transversale mesurable. |
| Epic | Résultat cohérent nécessitant plusieurs sessions d’implémentation. |
| Spec | Contrat d’implémentation condensé d’un epic. |
| Story | Slice indépendante, implémentable et vérifiable dans une session maîtrisée. |
| Gate | Point de contrôle produisant un verdict explicite avant progression. |
| Preuve | Résultat reproductible : test, capture, log, mesure ou validation signée. |
