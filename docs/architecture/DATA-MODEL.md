# Modèle de données V1 — Leads et notifications

| Champ | Valeur |
|---|---|
| Version | **0.1.4** |
| Ticket | THL-ARCH-001 / 001A / 001B / 001C / **001D** |
| PRD | v0.1.4 |
| Statut | APPROVED_FOR_IMPLEMENTATION |

PostgreSQL 18 ; colonnes horodatées en `timestamptz` (UTC) ; schéma versionné par migrations Alembic.

## Tables (6)

`leads`, `quote_request_details`, `contact_message_details`, `idempotency_records`, `notification_jobs`, `rate_limit_buckets`.

Relations : `leads` (1) — (0..1) `quote_request_details` ; `leads` (1) — (0..1) `contact_message_details` ; `leads` (1) — (n) `notification_jobs` (V1 : un job `internal_email` à la création) ; `idempotency_records` référence le `lead_id` créé dans la même transaction métier.

Identifiant interne : `bigint` `GENERATED ALWAYS AS IDENTITY` (non exposé HTTP). Référence publique : `leads.public_reference` (DEC-007, OpenAPI `PublicReference`).

## Types PostgreSQL énumérés

Valeurs alignées sur `contracts/openapi/openapi.yaml` (snake_case API).

| Type | Valeurs |
|---|---|
| `lead_type_enum` | `quote`, `contact` |
| `lead_operational_status_enum` | `received` |
| `service_type_enum` | `convoyage_premium`, `fleet_coordination`, `automotive_logistics`, `vehicle_preparation` |
| `timing_kind_enum` | `exact_date`, `period` |
| `vehicle_category_enum` | `city_sedan`, `suv_4x4`, `premium_sport`, `light_commercial`, `classic_collector`, `other` |
| `contact_preference_enum` | `email`, `phone`, `no_preference` |
| `contact_subject_enum` | `information`, `quote`, `partnership`, `other` |
| `idempotency_scope_enum` | `quote_requests`, `contact_messages` |
| `notification_kind_enum` | `internal_email` |
| `notification_status_enum` | `pending`, `processing`, `retry_scheduled`, `sent`, `failed_terminal` |
| `rate_limit_scope_enum` | `quote_requests`, `contact_messages` |

## Règle `updated_at` (V1)

Aucun trigger PostgreSQL en V1. L’application (services Python) assigne `updated_at = now()` (horloge applicative UTC) à **chaque** `UPDATE` explicite sur `leads`, `notification_jobs` et `rate_limit_buckets`.

## Horodatage autoritaire — `accepted_at`

Dans chaque **transaction métier** de création de lead (après acquisition du verrou advisory session et validation Turnstile pour une nouvelle opération — voir ADR-003 et ADR-004) :

```text
accepted_at := transaction_timestamp()   -- une seule lecture par transaction
```

Séquence normative dans la transaction :

1. Lire `accepted_at` **une fois**.
2. Dériver `YYYYMMDD` en UTC pour le segment date de `public_reference`.
3. Générer `public_reference` (nouvelle valeur aléatoire si violation `UNIQUE` ; **conserver** le même `accepted_at`).
4. Renseigner avec **exactement** `accepted_at` : `leads.created_at`, `leads.privacy_acknowledged_at`, `created_at` dans `idempotency_records.response_body`, segment date de la référence.
5. Construire `response_body` JSONB (clés `public_reference`, `status`, `created_at` uniquement).
6. `INSERT` `leads`, table de détail, `idempotency_records`, `notification_jobs`.
7. `COMMIT`.

Collision sur `public_reference` : retry avec nouvelle valeur aléatoire ; **ne pas** relire `transaction_timestamp()` ; utiliser savepoint ou INSERT conflict-safe pour ne pas annuler toute la transaction.

Test obligatoire frontière **minuit UTC** : voir `TEST-STRATEGY.md`.

---

## 1. Table `leads`

| Colonne | Type PostgreSQL | Null | Défaut | Description |
|---|---|---|---|---|
| `id` | `bigint` | NOT NULL | `GENERATED ALWAYS AS IDENTITY` | Clé surrogate interne |
| `public_reference` | `varchar(21)` | NOT NULL | — | Référence publique DEC-007 |
| `lead_type` | `lead_type_enum` | NOT NULL | — | `quote` ou `contact` |
| `first_name` | `varchar(80)` | NOT NULL | — | Prénom |
| `last_name` | `varchar(80)` | NOT NULL | — | Nom |
| `email` | `varchar(254)` | NOT NULL | — | E-mail contact |
| `phone` | `varchar(32)` | NULL | — | Téléphone ; obligatoire si devis |
| `company` | `varchar(160)` | NULL | — | Société optionnelle |
| `privacy_acknowledgement` | `boolean` | NOT NULL | — | Doit être `true` |
| `privacy_policy_version` | `varchar(64)` | NOT NULL | — | Version politique **serveur** (config déploiement) |
| `privacy_acknowledged_at` | `timestamptz` | NOT NULL | — | Égal à `accepted_at` transaction |
| `operational_status` | `lead_operational_status_enum` | NOT NULL | `'received'` | Statut opérationnel V1 |
| `created_at` | `timestamptz` | NOT NULL | — | Égal à `accepted_at` transaction |
| `updated_at` | `timestamptz` | NOT NULL | — | Mis à jour par l’application |

**Clé primaire :** `PRIMARY KEY (id)`.

**Contraintes UNIQUE :**

- `UNIQUE (public_reference)` — nom suggéré migration : `uq_leads_public_reference`.

**Contraintes CHECK :**

- `chk_leads_public_reference_format` : `public_reference ~ '^THL-[0-9]{8}-[0-9A-HJKMNP-TV-Z]{8}$'`.
- `chk_leads_first_name_length` : `char_length(first_name) BETWEEN 1 AND 80`.
- `chk_leads_last_name_length` : `char_length(last_name) BETWEEN 1 AND 80`.
- `chk_leads_email_length` : `char_length(email) BETWEEN 1 AND 254`.
- `chk_leads_company_length` : `company IS NULL OR char_length(company) <= 160` (OpenAPI autorise `company: ""` sans `minLength`).
- `chk_leads_privacy_ack` : `privacy_acknowledgement IS TRUE`.
- `chk_leads_privacy_policy_version_length` : `char_length(privacy_policy_version) BETWEEN 1 AND 64`.
- `chk_leads_phone_quote` : `(lead_type <> 'quote') OR (phone IS NOT NULL AND char_length(phone) BETWEEN 6 AND 32 AND phone ~ '^[+0-9().\s-]+$')`.
- `chk_leads_phone_contact` : `(lead_type <> 'contact') OR (phone IS NULL OR (char_length(phone) BETWEEN 6 AND 32 AND phone ~ '^[+0-9().\s-]+$'))`.

**Index (non unique) :**

- `idx_leads_created_at` ON `(created_at)`.
- `idx_leads_lead_type_created_at` ON `(lead_type, created_at)`.

**Clés étrangères entrantes (depuis tables enfants) :** toutes référencent `leads(id)` avec `ON DELETE RESTRICT` (aucune suppression cascade de lead en V1).

**Rétention PII :** [À CONFIRMER — Owner: Jores — Gate: PREPROD] (TBD-010).

---

## 2. Table `quote_request_details`

Une ligne par lead de type `quote` ; clé primaire = clé étrangère vers `leads`.

| Colonne | Type PostgreSQL | Null | Défaut | Description |
|---|---|---|---|---|
| `lead_id` | `bigint` | NOT NULL | — | PK et FK vers `leads.id` |
| `service` | `service_type_enum` | NOT NULL | — | Service demandé (OpenAPI `ServiceType`) |
| `departure_city` | `varchar(120)` | NOT NULL | — | Ville départ |
| `departure_postal_code` | `varchar(12)` | NOT NULL | — | Code postal départ |
| `arrival_city` | `varchar(120)` | NOT NULL | — | Ville arrivée |
| `arrival_postal_code` | `varchar(12)` | NOT NULL | — | Code postal arrivée |
| `timing_kind` | `timing_kind_enum` | NOT NULL | — | `exact_date` ou `period` |
| `exact_date` | `date` | NULL | — | Date si `timing_kind = exact_date` |
| `period_text` | `varchar(500)` | NULL | — | Texte période si `timing_kind = period` |
| `vehicle_category` | `vehicle_category_enum` | NOT NULL | — | Catégorie véhicule |
| `vehicle_category_other_detail` | `varchar(200)` | NULL | — | Détail si `vehicle_category = other` |
| `vehicle_make` | `varchar(80)` | NOT NULL | — | Marque |
| `vehicle_model` | `varchar(80)` | NOT NULL | — | Modèle |
| `vehicle_rolling` | `boolean` | NOT NULL | — | Véhicule roulant |
| `special_constraints` | `text` | NULL | — | Contraintes particulières |
| `additional_message` | `text` | NULL | — | Message complémentaire |
| `contact_preference` | `contact_preference_enum` | NULL | — | Préférence contact |

**Clé primaire :** `PRIMARY KEY (lead_id)`.

**Clé étrangère :** `FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE RESTRICT`.

**Contraintes CHECK :**

- `chk_quote_departure_city_length` : `char_length(departure_city) BETWEEN 1 AND 120`.
- `chk_quote_departure_postal_length` : `char_length(departure_postal_code) BETWEEN 4 AND 12`.
- `chk_quote_arrival_city_length` : `char_length(arrival_city) BETWEEN 1 AND 120`.
- `chk_quote_arrival_postal_length` : `char_length(arrival_postal_code) BETWEEN 4 AND 12`.
- `chk_quote_timing_exact_date` : `(timing_kind <> 'exact_date') OR (exact_date IS NOT NULL AND period_text IS NULL)`.
- `chk_quote_timing_period` : `(timing_kind <> 'period') OR (period_text IS NOT NULL AND char_length(period_text) BETWEEN 3 AND 500 AND exact_date IS NULL)`.
- `chk_quote_vehicle_other` : `(vehicle_category <> 'other') OR (vehicle_category_other_detail IS NOT NULL AND char_length(vehicle_category_other_detail) BETWEEN 2 AND 200)`.
- `chk_quote_vehicle_other_absent` : `(vehicle_category = 'other') OR (vehicle_category_other_detail IS NULL)`.
- `chk_quote_vehicle_make_length` : `char_length(vehicle_make) BETWEEN 1 AND 80`.
- `chk_quote_vehicle_model_length` : `char_length(vehicle_model) BETWEEN 1 AND 80`.
- `chk_quote_special_constraints_length` : `special_constraints IS NULL OR char_length(special_constraints) <= 2000`.
- `chk_quote_additional_message_length` : `additional_message IS NULL OR char_length(additional_message) <= 4000`.

**Index :** aucun index supplémentaire requis V1 (accès par `lead_id` PK).

**Cohérence métier :** la ligne n’existe que si `leads.lead_type = 'quote'` (enforced applicatif V1 ; pas de trigger cross-table).

---

## 3. Table `contact_message_details`

Une ligne par lead de type `contact`.

| Colonne | Type PostgreSQL | Null | Défaut | Description |
|---|---|---|---|---|
| `lead_id` | `bigint` | NOT NULL | — | PK et FK vers `leads.id` |
| `subject` | `contact_subject_enum` | NOT NULL | — | Objet (FR-044) |
| `message` | `text` | NOT NULL | — | Corps du message |

**Clé primaire :** `PRIMARY KEY (lead_id)`.

**Clé étrangère :** `FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE RESTRICT`.

**Contraintes CHECK :**

- `chk_contact_message_length` : `char_length(message) BETWEEN 10 AND 8000`.

**Index :** aucun index supplémentaire requis V1.

---

## 4. Table `idempotency_records`

Persistance du résultat idempotent par `(scope, key_digest)`. La clé brute `Idempotency-Key` (UUID v4) **n’est jamais stockée**.

| Colonne | Type PostgreSQL | Null | Défaut | Description |
|---|---|---|---|---|
| `id` | `bigint` | NOT NULL | `GENERATED ALWAYS AS IDENTITY` | Surrogate |
| `scope` | `idempotency_scope_enum` | NOT NULL | — | `quote_requests` ou `contact_messages` |
| `key_digest` | `char(64)` | NOT NULL | — | Hex lowercase HMAC-SHA-256 (voir ci-dessous) |
| `key_version` | `smallint` | NOT NULL | — | Version secret HMAC clé idempotence |
| `fingerprint_key_version` | `smallint` | NOT NULL | — | Version secret HMAC empreinte payload |
| `fingerprint_algo_version` | `smallint` | NOT NULL | — | Version canonicalisation empreinte |
| `payload_fingerprint` | `char(64)` | NOT NULL | — | Hex HMAC empreinte payload |
| `lead_id` | `bigint` | NOT NULL | — | Lead associé |
| `response_body` | `jsonb` | NOT NULL | — | Réponse publique figée |
| `original_status_code` | `smallint` | NOT NULL | `201` | Code HTTP de la **création initiale** (V1 : toujours `201`) |
| `created_at` | `timestamptz` | NOT NULL | — | Horodatage insertion (transaction métier) |
| `expires_at` | `timestamptz` | NOT NULL | — | Fin de validité enregistrement |

**Clé primaire :** `PRIMARY KEY (id)`.

**Clé étrangère :** `FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE RESTRICT`.

**Contraintes UNIQUE :**

- `UNIQUE (scope, key_digest)` — nom suggéré : `uq_idempotency_scope_key_digest`.

**Contraintes CHECK :**

- `chk_idempotency_key_digest_hex` : `key_digest ~ '^[0-9a-f]{64}$'`.
- `chk_idempotency_payload_fingerprint_hex` : `payload_fingerprint ~ '^[0-9a-f]{64}$'`.
- `chk_idempotency_original_status` : `original_status_code = 201`.

**Sémantique replay :** une requête replay répond **HTTP 200** avec `Idempotency-Replayed: true` ; `original_status_code` en base reste **201** (jamais mis à jour au replay).
- `chk_idempotency_response_body_shape` : `(response_body - 'public_reference' - 'status' - 'created_at') = '{}'::jsonb AND (response_body->>'status') = 'received'`.

**Index :**

- `idx_idempotency_expires_at` ON `(expires_at)` (purge TTL).

**Formule normative `key_digest` :**

```text
key_digest = hex_lower(
  HMAC-SHA-256(
    idempotency_hmac_secret,
    UTF-8(scope + "|" + raw_uuid)
  )
)
```

`raw_uuid` = valeur header `Idempotency-Key` (UUID v4, non normalisée côté stockage).

**Empreinte payload :** voir `PUBLIC-API-CONTRACT.md` (HMAC, `fingerprint_key_version`, `fingerprint_algo_version`, JSON canonique).

**TTL :** [À CONFIRMER — Owner: Kyria — Gate: RECETTE] (paramètre environnement ; purge job ou requête planifiée sur `expires_at`).

### Verrou advisory session (non persisté en base)

Distinct de `key_digest`. Sérialise les requêtes concurrentes portant la **même** clé idempotence brute avant la transaction métier.

**Matériel de verrou :**

```text
lock_material = SHA-256( UTF-8(scope + ":" + idempotency_key) )
```

`idempotency_key` = UUID v4 brut du header (même chaîne que `raw_uuid` pour le digest, séparateur `:` ici).

**Identifiant PostgreSQL `lock_id` :**

- Prendre les **8 premiers octets** du digest SHA-256 (big-endian).
- Interpréter comme entier signé 64 bits (complément à deux).
- Même conversion **obligatoire** en Python et en SQL/tests (voir `TEST-STRATEGY.md`).

**Fonction normative :** `pg_try_advisory_lock(lock_id)` sur une connexion PostgreSQL **pinnée** (dédiée à la requête HTTP jusqu’au `finally`).

**Rejet explicite :** `pg_advisory_xact_lock` n’est **pas** utilisé pour ce pipeline, car il lie le verrou à une transaction SQL (transaction longue si Turnstile inclus, ou perte du verrou avant la transaction métier).

**Algorithme (résumé — autorité ADR-003) :**

1. Boucle : `pg_try_advisory_lock(lock_id)` ; backoff court borné avec jitter ; deadline monotone **5 s** maximum.
2. Si deadline dépassée : HTTP **503** `IDEMPOTENCY_BUSY`, `X-Correlation-Id`, **aucune** mutation, **aucun** appel Turnstile.
3. **Aucune** transaction SQL ouverte pendant l’appel Turnstile Siteverify.
4. Après acquisition : lookup `idempotency_records` (digests multi-version sous verrou) ; replay **200** si trouvé ; **409** si même clé empreinte différente.
5. Sinon Turnstile (nouvelle opération) **hors** transaction SQL.
6. Ouvrir transaction métier sur **la même** connexion ; `accepted_at` via `transaction_timestamp()` ; inserts atomiques ; `COMMIT`.
7. `finally` : `pg_advisory_unlock(lock_id)` doit retourner `true` ; sinon invalider/fermer la connexion (ne pas la rendre au pool).

Rotation HMAC `current` / `previous` : ne modifie **pas** `lock_id` (indépendant des secrets HMAC).

---

## 5. Table `notification_jobs`

File de notifications internes (e-mail ops) ; sémantique **at-least-once** (ADR-003, TM-023).

| Colonne | Type PostgreSQL | Null | Défaut | Description |
|---|---|---|---|---|
| `id` | `bigint` | NOT NULL | `GENERATED ALWAYS AS IDENTITY` | Surrogate |
| `lead_id` | `bigint` | NOT NULL | — | Lead source |
| `notification_kind` | `notification_kind_enum` | NOT NULL | — | V1 : `internal_email` |
| `status` | `notification_status_enum` | NOT NULL | — | Cycle de vie worker |
| `attempt_count` | `integer` | NOT NULL | `0` | Tentatives (incrément au claim) |
| `max_attempts` | `integer` | NOT NULL | `5` | Plafond V1 (config env) |
| `next_attempt_at` | `timestamptz` | NULL | — | Prochaine exécution si retry |
| `locked_at` | `timestamptz` | NULL | — | Début verrou worker |
| `lock_expires_at` | `timestamptz` | NULL | — | Expiration lease worker |
| `locked_by` | `varchar(64)` | NULL | — | Identifiant instance worker |
| `provider_message_id` | `varchar(128)` | NULL | — | Id fournisseur (sans PII) |
| `last_error_code` | `varchar(64)` | NULL | — | Code erreur assaini |
| `created_at` | `timestamptz` | NOT NULL | — | Création job |
| `updated_at` | `timestamptz` | NOT NULL | — | Mis à jour par l’application |

**Clé primaire :** `PRIMARY KEY (id)`.

**Clé étrangère :** `FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE RESTRICT`.

**Contraintes UNIQUE :**

- `UNIQUE (lead_id, notification_kind)` — nom suggéré : `uq_notification_jobs_lead_kind`.

**Contraintes CHECK :**

- `chk_notification_attempt_count_nonneg` : `attempt_count >= 0`.
- `chk_notification_max_attempts_positive` : `max_attempts >= 1`.
- `chk_notification_pending_retry_next` : `(status NOT IN ('pending', 'retry_scheduled')) OR (next_attempt_at IS NOT NULL)`.
- `chk_notification_sent_no_next` : `(status <> 'sent') OR (next_attempt_at IS NULL)`.
- `chk_notification_failed_terminal_no_next` : `(status <> 'failed_terminal') OR (next_attempt_at IS NULL)`.
- `chk_notification_processing_lock` : `(status <> 'processing') OR (locked_at IS NOT NULL AND lock_expires_at IS NOT NULL AND locked_by IS NOT NULL)`.
- `chk_notification_non_processing_unlocked` : `(status = 'processing') OR (locked_at IS NULL AND lock_expires_at IS NULL AND locked_by IS NULL)`.

**Création à l’INSERT lead (transaction métier, même `accepted_at`) :**

| Colonne | Valeur V1 |
|---|---|
| `status` | `pending` |
| `attempt_count` | `0` |
| `max_attempts` | `5` |
| `next_attempt_at` | `accepted_at` (éligible au claim dès le commit) |
| `locked_at`, `lock_expires_at`, `locked_by` | `NULL` |

**Requête normative de claim worker :**

```sql
SELECT … FROM notification_jobs
WHERE status IN ('pending', 'retry_scheduled')
  AND next_attempt_at <= now()
ORDER BY next_attempt_at, id
FOR UPDATE SKIP LOCKED
LIMIT 1;
```

États terminaux `sent` et `failed_terminal` : **hors** claim ( `next_attempt_at IS NULL` ).

**Transition sortie de `processing` :** remettre `locked_at`, `lock_expires_at` et `locked_by` à `NULL` (succès → `sent` ou échec → `retry_scheduled` / `failed_terminal`).

**Paramètres worker V1 (configuration environnement, colonnes stables) :**

| Paramètre | Valeur |
|---|---|
| `max_attempts` | 5 |
| Backoff après échec | 1 min, 5 min, 15 min, 60 min |
| Timeout appel e-mail | 10 s |
| Durée lease `processing` | 60 s |

**Comportement :**

- `attempt_count` incrémenté au **claim**, avant envoi.
- Échec non terminal : `retry_scheduled` et `next_attempt_at` selon backoff.
- 5ᵉ échec : `failed_terminal` ; `next_attempt_at = NULL`.
- `sent` : `next_attempt_at = NULL`.
- Reclaim d’un `processing` expiré (`lock_expires_at < now()`) : compte comme tentative incertaine ; at-least-once maintenu.

**Clé déduplication fournisseur (si supportée) :**

```text
provider_dedup_key = "thl:" + public_reference + ":" + notification_kind + ":v1"
```

Exactly-once **non** promis.

**Index :**

- `idx_notification_jobs_claim` : index partiel `(next_attempt_at, id)` WHERE `status IN ('pending', 'retry_scheduled')`.
- `idx_notification_jobs_reclaim` : index partiel `(lock_expires_at, id)` WHERE `status = 'processing'`.

---

## 6. Table `rate_limit_buckets`

Autorité distribuée V1 pour rate limiting multi-instance (pas de limiteur mémoire seul).

| Colonne | Type PostgreSQL | Null | Défaut | Description |
|---|---|---|---|---|
| `id` | `bigint` | NOT NULL | `GENERATED ALWAYS AS IDENTITY` | Surrogate |
| `scope` | `rate_limit_scope_enum` | NOT NULL | — | Endpoint logique |
| `subject_digest` | `char(64)` | NOT NULL | — | Hex HMAC sujet (IP/proxy de confiance) |
| `key_version` | `smallint` | NOT NULL | — | Version secret HMAC rate limit |
| `window_started_at` | `timestamptz` | NOT NULL | — | Début fenêtre compteur |
| `request_count` | `integer` | NOT NULL | — | Compteur requêtes fenêtre |
| `expires_at` | `timestamptz` | NOT NULL | — | Fin fenêtre / purge |
| `created_at` | `timestamptz` | NOT NULL | — | Création bucket |
| `updated_at` | `timestamptz` | NOT NULL | — | Mis à jour par l’application |

**Clé primaire :** `PRIMARY KEY (id)`.

**Contraintes UNIQUE :**

- `UNIQUE (scope, subject_digest, window_started_at)` — nom suggéré : `uq_rate_limit_bucket_window`.

**Contraintes CHECK :**

- `chk_rate_limit_subject_digest_hex` : `subject_digest ~ '^[0-9a-f]{64}$'`.
- `chk_rate_limit_request_count_nonneg` : `request_count >= 0`.

**Index :**

- `idx_rate_limit_expires_at` ON `(expires_at)` (purge).

**Opérations :** incrément atomique SQL (`INSERT … ON CONFLICT DO UPDATE`) dans une transaction courte ; HTTP **429** + en-tête `Retry-After` si seuil dépassé.

Seuils numériques : TBD-018 [À CONFIRMER — Owner: Kyria — Gate: RECETTE].

Aucune adresse IP brute persistée.

---

## Transaction métier HTTP (après pipeline ADR-004)

Pour une **nouvelle** opération (pas un replay idempotent) :

1. Turnstile Siteverify réussi **sans** transaction SQL ouverte.
2. `BEGIN` sur la connexion verrouillée advisory.
3. `accepted_at := transaction_timestamp()` (une lecture).
4. Génération `public_reference` et construction `response_body`.
5. `INSERT` `leads`, détail métier, `idempotency_records` (`original_status_code = 201`), `notification_jobs` (`pending`, `attempt_count = 0`, `max_attempts = 5`, `next_attempt_at = accepted_at`).
6. `COMMIT`.
7. Réponse HTTP **201** puis worker notification **après** commit (échec e-mail post-commit : retry worker uniquement, sans modifier le **201** déjà émis).

Notification asynchrone : **jamais** dans la même transaction que la création lead.
