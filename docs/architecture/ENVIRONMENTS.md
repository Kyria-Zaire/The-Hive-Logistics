# Environnements V1

| Version | **0.1.2** | Ticket | THL-ARCH-001 / 001A / **001B** | Statut | APPROVED_FOR_IMPLEMENTATION |

## Règles transverses

| Règle | Application |
|---|---|
| Schéma | Migrations Alembic **identiques** sur les quatre bases |
| Données | **Différentes** par environnement ; synthétiques ou anonymisées hors PROD |
| Restauration | **Interdit** : restore PROD brut → DEV / RECETTE / PREPROD |
| Secrets | Isolés ; **aucun secret PROD** en local DEV |
| Auth / paiement V1 | **Aucun** compte, magic link, OTP, OAuth, paiement |
| Code applicatif | Git + artefacts CI — **jamais** stocké dans PostgreSQL |
| Same-origin PROD | Ingress : `/api/v1/*` → FastAPI ; autres routes → Next.js |
| Promotion PROD | **Manuelle** et approuvée (pas de deploy PROD automatique non validé) |

---

## DEV

| Aspect | Politique |
|---|---|
| **Finalité** | Développement local (Kyria) ; itération rapide API/web/worker |
| **Données autorisées** | Fictives, jetables ; aucune PII réelle |
| **Base PostgreSQL** | Instance locale ou conteneur **dédiée DEV** ; URL distincte |
| **Secrets** | Fichiers env locaux hors dépôt ; clés Turnstile **test** Cloudflare |
| **Turnstile** | Site keys test ; secrets serveur DEV uniquement |
| **Email** | Sink local (ex. Mailpit) ou mock ; pas d’envoi vers destinataires réels |
| **Logs et PII** | Verbose autorisé localement ; discipline SEC-010 (pas de corps formulaire) |
| **Déploiement** | `pnpm dev` / `uvicorn` / worker en processus locaux |
| **Accès** | Développeurs ; pas d’accès PROD |
| **Monitoring** | Optionnel local ; pas d’alerting ops |
| **Sauvegarde** | Non requise (base jetable) |
| **Restauration** | N/A |
| **Promotion** | Merge Git → pipeline **RECETTE** ; pas de promotion automatique |

**CORS / proxy :** rewrite Next.js → API **autorisé en DEV uniquement** (ADR-006).

---

## RECETTE

| Aspect | Politique |
|---|---|
| **Finalité** | Tests E2E, contrat OpenAPI, idempotence, worker, FR-046 procédure synthétique |
| **Données autorisées** | Jeux **synthétiques** reproductibles ; reset autorisé |
| **Base PostgreSQL** | Instance **isolée RECETTE** |
| **Secrets** | Vault/env RECETTE ; Turnstile test ou clés dédiées RECETTE |
| **Turnstile** | Clés non PROD ; hostname RECETTE documenté |
| **Email** | Capture (sink) ou fournisseur sandbox [À CONFIRMER — Owner: Kyria + Jores — Gate: RECETTE] TBD-009 |
| **Logs et PII** | Structurés ; redaction ; tests « absence PII » |
| **Déploiement** | CI/CD ou manuel depuis branche validée |
| **Accès** | Kyria, Jores recette ; moindre privilège |
| **Monitoring** | Métriques basiques ; corrélation sans PII |
| **Sauvegarde** | Optionnelle courte durée |
| **Restauration** | Drill léger avant PREPROD |
| **Promotion** | Critères tests verts → **PREPROD** (manuel) |

**CORS :** allowlist explicite **si** tests cross-origin requis.

---

## PREPROD

| Aspect | Politique |
|---|---|
| **Finalité** | Parité PROD ; perf Lighthouse ; sécurité ; smoke ; gates NFR/SEC |
| **Données autorisées** | Synthétiques ; volume modéré ; pas de copie PROD |
| **Base PostgreSQL** | Instance **isolée PREPROD** |
| **Secrets** | Séparés PROD ; rotation testée |
| **Turnstile** | Clés proches PROD sans réutiliser secrets PROD en poste dev |
| **Email** | Sandbox ou sink ; pas de clients réels |
| **Logs et PII** | Comme cible PROD |
| **Déploiement** | Promotion contrôlée depuis RECETTE |
| **Accès** | Restreint ; pas de données client réelles |
| **Monitoring** | Alertes techniques ; SLO internes |
| **Sauvegarde** | Recommandée ; test restore avant go-live |
| **Restauration** | Exercice documenté |
| **Promotion** | Validation humaine → **PROD** (manuel approuvé) |

**Hébergeur :** [À CONFIRMER — Owner: Jores + Kyria — Gate: PREPROD] TBD-007.

---

## PROD

| Aspect | Politique |
|---|---|
| **Finalité** | Site public français ; leads réels ; notifications MUST |
| **Données autorisées** | Données client réelles ; minimisation PRD DATA-* |
| **Base PostgreSQL** | Instance **isolée PROD** ; moindre privilège compte app |
| **Secrets** | PROD uniquement en runtime prod ; rotation TBD-019 |
| **Turnstile** | Clés PROD ; hostname canonique [À CONFIRMER — Owner: Jores + Kyria — Gate: PROD] TBD-021 |
| **Email** | Fournisseur transactionnel PROD [À CONFIRMER — Owner: Kyria + Jores — Gate: PROD] TBD-009 |
| **Logs et PII** | Redaction stricte SEC-010 ; rétention [À CONFIRMER — Owner: Jores — Gate: PROD] TBD-010 |
| **Déploiement** | **Manuel approuvé** ; rollback testé AC-014 |
| **Accès** | Moindre privilège ; pas de lecture PII large |
| **Monitoring** | Disponibilité, 5xx leads, worker failed_terminal, dépendances |
| **Sauvegarde PostgreSQL** | Automatisée ; PITR si supporté [À CONFIRMER — Owner: Kyria — Gate: PROD] |
| **Restauration** | Procédure + test périodique [À CONFIRMER — Owner: Kyria — Gate: PROD] |
| **Promotion** | N/A (sommet) |

**RPO/RTO :** [À CONFIRMER — Owner: Kyria — Gate: PROD] (PRD §15.3).

**CORS :** **aucune** origine cross-origin autorisée par défaut.

---

## Sauvegarde et restauration (distinct)

| Actif | Méthode |
|---|---|
| PostgreSQL | Backups + PITR si disponible |
| Médias originaux | Stockage objet / archive (hors DB) |
| Frontend / backend | Git tags + artefacts CI immuables |

---

## FR-046 — Reprise exceptionnelle (lecture seule)

| Exigence | Implémentation documentée |
|---|---|
| Périmètre | Consultation d’un lead déjà persisté ; **Kyria** uniquement |
| Interface V1 | **Aucun** export CSV applicatif ; pas d’UI self-service |
| Accès | Rôle DB lecture seule **ou** commande opérateur à privilèges minimaux (runbook) |
| Interdictions | **Aucune** modification, suppression ou re-envoi marketing du lead |
| Audit | Journaliser qui, quand, quelle `public_reference` (sans dump PII) |
| Test | Procédure exécutable en **RECETTE** sur données synthétiques |
| PRD | FR-046 MUST |

Runbook détaillé : `TEST-STRATEGY.md` (FR-046) ; lien matrice `ARCHITECTURE-SPINE.md`.
