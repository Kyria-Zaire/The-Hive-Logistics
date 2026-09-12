# Contrat API publique V1 — Guide d’implémentation

| Version | **1.0.4-doc** | OpenAPI | `contracts/openapi/openapi.yaml` **1.0.1** / 3.1.0 |
| Ticket | THL-ARCH-001 / 001A / 001B / 001C / **001D** | PRD | v0.1.4 |
| Statut | APPROVED_FOR_IMPLEMENTATION |

## Same-origin (PROD)

- Navigateur et API partagent le **même domaine public**.
- Ingress : `/api/v1/*` → FastAPI ; autres routes → Next.js.
- OpenAPI `servers: [{ url: / }]`.
- Next.js **ne** porte **pas** la logique métier leads ; pas de Route Handler BFF PROD.
- Rewrite/proxy vers API : **DEV local uniquement**.

## Pipeline HTTP

Voir ADR-004 (13 étapes). Rappel : Pydantic **avant** honeypot rate-limit idempotence Turnstile ; payloads invalides **sans** Turnstile.

## Endpoints

| Méthode | Chemin |
|---|---|
| POST | `/api/v1/quote-requests` |
| POST | `/api/v1/contact-messages` |
| GET | `/api/v1/health/live` |
| GET | `/api/v1/health/ready` |

## En-têtes

| Header | Rôle |
|---|---|
| `Idempotency-Key` | UUID v4 obligatoire POST |
| `Content-Type` | `application/json` |
| `X-Correlation-Id` | Request optionnel ; **response obligatoire** (validé ou généré) |
| `Idempotency-Replayed` | `false` (201) ou `true` (200 replay) |

## Réponse succès publique

```json
{
  "public_reference": "THL-20260912-7K3M9Q2X",
  "status": "received",
  "created_at": "2026-09-12T18:00:00Z"
}
```

Pas d’état notification email exposé. Worker : états internes uniquement.

Replay : même JSON depuis `idempotency_records.response_body` ; HTTP **200** + `Idempotency-Replayed: true` ; `original_status_code` persisté reste **201** (DATA-MODEL).

## Notifications asynchrones et HTTP POST

- Après **COMMIT** réussi, la réponse **201** (ou **200** replay) est **définitive** pour le client.
- Une panne du fournisseur e-mail **après** commit **ne modifie jamais** une réponse **201** déjà acquise ; le worker `notification_jobs` planifie un retry (DATA-MODEL).
- **503** sur POST : réservé aux dépendances **synchrones avant commit** (Turnstile indisponible, `IDEMPOTENCY_BUSY`, etc.) — **pas** à l’indisponibilité e-mail post-commit.

## Politique de confidentialité

- Client envoie **uniquement** `privacy_acknowledgement: true`.
- Serveur persist `privacy_policy_version` depuis **configuration versionnée** (pas de valeur client).
- DB : `privacy_acknowledged_at` obligatoire.

## Empreinte payload (idempotence)

**Inclus dans JSON canonique :** champs métier validés ; optionnels **présents** ; `scope` endpoint ; `fingerprint_algo_version` (ex. `1`).

**Exclus :** `turnstile_token`, `honeypot`, `X-Correlation-Id`, IP/rate limit, timestamps serveur.

**Canonicalisation :** clés triées UTF-8 ; Unicode **NFC** ; distinguer absent / null / `""` sans normalisation métier destructive.

**Digest :**

`payload_fingerprint = HMAC-SHA-256(fingerprint_secret, scope + "|" + algo_version + "|" + canonical_json)`

Tests : vecteurs déterministes versionnés en repo `tests/fixtures/` (future impl).

## Idempotency-Key stockage

```text
key_digest = HMAC-SHA-256(
  idempotency_hmac_secret,
  scope + "|" + raw_uuid
)
```

Clé brute **jamais** stockée. Colonnes : `key_version`, `fingerprint_key_version`, `fingerprint_algo_version`.

**Verrou advisory session (non persisté en base) :**

```text
lock_material = SHA-256( UTF-8(scope + ":" + idempotency_key) )
lock_id       = bigint signé (8 premiers octets SHA-256, big-endian, complément à deux)
```

Acquisition : connexion PostgreSQL **pinnée** ; boucle `pg_try_advisory_lock(lock_id)` ; deadline monotone **5 s** ; backoff court borné + jitter.

- Timeout → **503** `IDEMPOTENCY_BUSY` ; `X-Correlation-Id` ; **aucune** mutation ; **aucun** appel Turnstile.
- **Aucune** transaction SQL ouverte pendant Siteverify.
- Après lock : lookup idempotence ; replay **200** sans Turnstile si enregistrement trouvé ; sinon Turnstile puis transaction métier (`transaction_timestamp()`).
- `finally` : `pg_advisory_unlock(lock_id)` doit retourner `true` ; sinon invalider/fermer la connexion (ne pas rendre au pool).

`pg_advisory_xact_lock` est **rejeté** pour ce pipeline (transaction longue ou perte du verrou avant la transaction métier — ADR-003).

**Rotation HMAC :** keyring current + previous ; lookup multi-version sous verrou ; `lock_id` **inchangé** lors de la rotation ; tests replay avant/après rotation.

## Instant `accepted_at`

`transaction_timestamp()` lu une fois par transaction ; alimente référence (date UTC), `leads.created_at`, `response_body.created_at`, `privacy_acknowledged_at` (DATA-MODEL). Test minuit UTC obligatoire.

## Turnstile (nouvelle opération)

- Siteverify serveur ; timeout **3 s max**.
- `hostname` attendu **obligatoire**.
- `action` **obligatoire** : `quote_request` | `contact_message`.
- `remoteip` **omis** par défaut.
- Token : non loggé, non persisté.
- Invalid/expired/replayed → **403** générique.
- Timeout/erreur/config → **503** + alerte interne.
- Distinct de toute `idempotency_key` Cloudflare Siteverify.

## Honeypot

Champ obligatoire `writeOnly` ; max 200 chars ; non vide → **403** `REQUEST_DENIED` ; arrêt pipeline.

## Rate limiting

Table `rate_limit_buckets` ; 429 + `Retry-After` (secondes) ; seuils TBD-018 [À CONFIRMER — Owner: Kyria — Gate: RECETTE].

## Taxonomie HTTP

| Code | Usage |
|---|---|
| 400 | JSON malformé, header invalide |
| 403 | Honeypot ou Turnstile refusé |
| 409 | Idempotence payload différent |
| 413 | Body > 64 KiB |
| 415 | Content-Type invalide |
| 422 | Schème / règle métier Pydantic |
| 429 | Rate limit |
| 503 | Turnstile indisponible (Siteverify) ; verrou idempotence occupé (`IDEMPOTENCY_BUSY`) — **avant** commit uniquement |

Problem `type` : URN `urn:thl:problem:*` (pas de faux domaine).

## CORS

PROD : default deny cross-origin. DEV/RECETTE : allowlist explicite si besoin. Credentials **false**.

## TTL idempotence

[À CONFIRMER — Owner: Kyria — Gate: RECETTE] — paramètre env documenté en DATA-MODEL.
