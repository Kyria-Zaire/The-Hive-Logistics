# ADR-003 — Transaction lead, idempotence et worker PostgreSQL

| Statut | ACCEPTED |
| Date | 2026-09-12 |
| Ticket | THL-ARCH-001 / 001A / 001B / **001C** |

## Idempotence — digests

**Idempotency-Key (UUID v4 brut, jamais stocké) :**

```text
key_digest = HMAC-SHA-256(
  idempotency_hmac_secret,
  scope + "|" + raw_uuid
)
```

**Empreinte payload :** voir PUBLIC-API-CONTRACT (HMAC fingerprint_key, scope, fingerprint_algo_version, JSON canonique).

**Versions en base :** `key_version` (digest clé) ; `fingerprint_key_version` ; `fingerprint_algo_version`.

### Rotation HMAC

- Keyring **current + previous** pour idempotency et fingerprint.
- Anciennes clés conservées ≥ TTL max idempotency records.
- Sous verrou advisory session : calculer digests avec **toutes** versions actives ; lookup ; écriture avec version courante.
- Replay : recalcul empreinte avec versions du **record** retrouvé.
- Interdiction de retirer une clé avant purge records associés.
- Tests : replay avant/après rotation (TEST-STRATEGY).
- La rotation HMAC **ne modifie pas** `lock_id` (matériel de verrou indépendant des secrets).

### Verrou advisory session (distinct de key_digest)

**Matériel :**

```text
lock_material = SHA-256( UTF-8(scope + ":" + idempotency_key) )
```

`idempotency_key` = valeur header UUID v4 (chaîne brute).

**Conversion `lock_id` :** octets 0–7 du digest SHA-256, big-endian, interprétés comme `bigint` signé (complément à deux). Identique Python ↔ PostgreSQL (tests obligatoires).

**Fonction :** `pg_try_advisory_lock(lock_id)` sur connexion **pinnée** jusqu’au `finally`.

**Rejet de `pg_advisory_xact_lock` :** imposerait une transaction SQL ouverte pendant Turnstile, ou libérerait le verrou avant la transaction métier — incompatible avec le pipeline V1.

**Algorithme normatif :**

1. Après validation Pydantic, rate limit et normalisation empreinte (ADR-004), acquérir le verrou : boucle `pg_try_advisory_lock(lock_id)` avec backoff court borné + jitter ; deadline monotone **5 s** max.
2. Si échec acquisition : **503** `IDEMPOTENCY_BUSY`, `X-Correlation-Id`, **aucune** mutation, **aucun** Turnstile.
3. Sous verrou, **sans** transaction SQL ouverte : lookup `idempotency_records` (multi-version HMAC).
   - Même clé + empreinte commitée → **200** + `response_body` + `Idempotency-Replayed: true` ; pas Siteverify.
   - Même clé + empreinte différente → **409**.
4. Nouvelle opération : Turnstile Siteverify (≤ 3 s) **hors** transaction SQL.
5. `BEGIN` sur la **même** connexion : `accepted_at = transaction_timestamp()` ; inserts atomiques lead, détail, idempotency, notification ; `COMMIT`.
6. `finally` : `SELECT pg_advisory_unlock(lock_id)` doit être `true`. Sinon : fermer/invalider la connexion ; **ne pas** la rendre au pool.

- **Non persisté** en base ; collision advisory sérialise seulement ; vérité métier = `(scope, key_digest)`.
- Deux requêtes concurrentes identiques → un Siteverify ; la seconde attend le verrou puis replay.

## Transaction — `accepted_at`

`accepted_at = transaction_timestamp()` une fois ; référence + `created_at` + `response_body.created_at` alignés ; collision référence sans changer `accepted_at` (DATA-MODEL).

## Worker notifications

États : `pending`, `processing`, `retry_scheduled`, `sent`, `failed_terminal`.

| Paramètre V1 | Valeur |
|---|---|
| max_attempts | 5 |
| backoff | 1, 5, 15, 60 min |
| email timeout | 10 s |
| lock lease | 60 s |

Claim : transaction courte `FOR UPDATE SKIP LOCKED` ; envoi **hors** transaction ; update finale nouvelle transaction ; reclaim `lock_expires_at < now()`.

**At-least-once** ; crash après accept fournisseur → email possiblement dupliqué (TM-023) ; `provider_dedup_key` si supporté.

Pas de `BackgroundTasks` pour notifications durables.

## Réévaluation

Volume jobs > confort polling PostgreSQL.
