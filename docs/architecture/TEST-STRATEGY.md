# Stratégie de tests V1

| Version | **0.1.4** | Ticket | THL-ARCH-001 / 001A / 001B / 001C / **001D** | Statut | APPROVED_FOR_IMPLEMENTATION |

## Backend

Unitaires, services, repositories, intégration PostgreSQL réel, migrations, contrat OpenAPI, validation, idempotence, concurrence, worker, fournisseurs.

### Idempotence / concurrence / verrou advisory (001C)

| # | Scénario | Attendu |
|---|---|---|
| 1 | Deux requêtes **concurrentes**, même `Idempotency-Key` et **même** payload | Un seul lead ; un seul appel Turnstile ; seconde requête → **200** replay |
| 2 | Même clé, **payload différent** | **409** conflit empreinte ; pas de second lead |
| 3 | Acquisition verrou : contention prolongée | Après **5 s** deadline → **503** `IDEMPOTENCY_BUSY` |
| 4 | Timeout acquisition verrou | **Aucun** appel Turnstile (mock compteur = 0) |
| 5 | Replay idempotent commité | **200** + `Idempotency-Replayed: true` ; **aucun** nouvel appel Turnstile |
| 6 | Succès création (201) | `pg_advisory_unlock` appelé et retourne `true` ; connexion rendue au pool |
| 7 | Échec Turnstile (403/503) après lock | `pg_advisory_unlock` dans `finally` ; pas de lead persisté |
| 8 | Rollback transaction métier après lock + Turnstile OK | `pg_advisory_unlock` ; pas de lead commité |
| 9 | `pg_advisory_unlock` retourne `false` ou connexion incertaine | Connexion **invalidée/fermée** ; non retournée au pool |
| 10 | Conversion `lock_id` | Vecteurs identiques Python ↔ PostgreSQL (8 octets big-endian, bigint signé) |
| 11 | Rotation HMAC current/previous | Replay OK ; **`lock_id` identique** (matériel SHA-256 scope:key, pas les secrets HMAC) |

Compléments existants :

- Replay 200 + body JSONB identique à `response_body`.
- Fingerprint exclut token/honeypot (vecteurs déterministes).
- **Aucun lock résiduel** après succès, exception ou timeout.

### Horodatage / référence

- Test **minuit UTC** : `accepted_at`, segment date référence, `created_at` public cohérents.
- Collision référence : retry aléatoire sans changer `accepted_at`.

### OpenAPI / schémas

- oneOf `PreferredTiming` ; condition `other` ; regex téléphone +/- ; UUID v4 header.
- `company` **chaîne vide** acceptée côté API et persistée conformément à OpenAPI (`char_length(company) <= 160`, DATA-MODEL).
- Replay HTTP **200** : `idempotency_records.original_status_code` reste **201**.

### Notifications asynchrones (001D)

- Job `pending` créé avec `next_attempt_at = accepted_at` : réclamable dès le commit (`next_attempt_at <= now()`).
- `sent` / `failed_terminal` : non réclamables (`next_attempt_at IS NULL`).
- Panne fournisseur e-mail **après** commit POST : réponse client reste **201** ; worker planifie retry (pas de **503** POST).

### Worker

- Index partiels utilisés : **EXPLAIN** en intégration sur claim pending/retry et reclaim processing.
- 5ᵉ échec → `failed_terminal`.
- Crash après email accepté fournisseur → reclaim documenté ; at-least-once.
- Backoff 1/5/15/60 min ; max_attempts 5 ; lock lease 60 s.

### Rate limit

- Multi-instance via `rate_limit_buckets`.

### Migrations

- `upgrade base → head` ; `upgrade n-1 → head` ; downgrade seulement si sûr.

### Environnements / FR-046

- Quatre configs isolées smoke (secrets/URLs distincts).
- FR-046 : lecture seule Kyria + audit ; RECETTE synthétique ; pas CSV V1.

### Threat model

- Document contient **≥ TM-001 … TM-025** (contrôle non-régression doc).

## Frontend

RTL, Playwright, axe, clavier, reduced-motion, viewports 320–1920, Lighthouse PREPROD.

## Sécurité / supply chain

- Scan secrets ; `uvx pip-audit` (lock CI) ; `pnpm audit` ;
- **openapi-spec-validator** + **Schemathesis** + futur `check_openapi_drift.py` (ADR-002) ;
- Absence PII logs ; **X-Correlation-Id** toutes réponses.

## Contrôles non-régression documentaire

Échec revue / CI doc si :

| Règle | Critère |
|---|---|
| Threat model | `< 25` lignes `TM-*` |
| ENVIRONMENTS | Absence sections **DEV, RECETTE, PREPROD, PROD** distinctes |
| Phrase interdite | « Politiques identiques à v0.1.0 » |
| Résumé non autonome | ENVIRONMENTS ou THREAT MODEL réduit à extrait sans tables complètes |
| Régression architecture | Disparition same-origin, UUID v4, `status: received`, `rate_limit_buckets`, verrou `pg_try_advisory_lock`, etc. |

## CI future

format → lint → typecheck → tests → build → OpenAPI validate → drift → migrations → intégration → sécurité.
