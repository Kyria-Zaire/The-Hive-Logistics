# ADR-004 — Sécurité des formulaires publics

| Statut | ACCEPTED |
| Date | 2026-09-12 |
| Ticket | THL-ARCH-001 / 001A / 001B / 001C / **001D** |

## Pipeline HTTP normatif (13 étapes)

1. Content-Type + taille ≤ 64 KiB (413).
2. Parsing JSON strict (400).
3. Validation Pydantic / OpenAPI (422) — **sans Turnstile**.
4. Honeypot non vide → 403 `REQUEST_DENIED` — **stop** (pas Turnstile, pas DB lead).
5. Rate limit `rate_limit_buckets` (429 + Retry-After).
6. Normalisation payload empreinte.
7. Acquisition verrou advisory session `pg_try_advisory_lock` (ADR-003) sur connexion pinnée ; boucle bornée ; deadline **5 s** → 503 `IDEMPOTENCY_BUSY` (**aucun** Turnstile, **aucune** mutation).
8. Relecture `idempotency_records` hors transaction SQL (200 replay / 409 conflit empreinte).
9. Turnstile Siteverify **nouvelle opération uniquement** : action `quote_request` | `contact_message` ; hostname obligatoire ; timeout 3 s ; `remoteip` omis ; invalid → 403 ; outage → 503 + alerte — **sans** transaction SQL ouverte.
10. Transaction PostgreSQL métier (`accepted_at` unique via `transaction_timestamp()` — DATA-MODEL) : INSERT lead, détail, idempotency, notification.
11. COMMIT puis libération verrou `pg_advisory_unlock` dans `finally` (connexion invalidée si unlock échoue).
12. Réponse HTTP 201/200 + `X-Correlation-Id`.
13. Notification worker **après** commit.

**HTTP 503 POST :** Turnstile indisponible ou `IDEMPOTENCY_BUSY` **avant** commit uniquement. Une panne e-mail **après** commit **ne** convertit **pas** un **201** acquise en **503** ; le worker retry (PUBLIC-API-CONTRACT, DATA-MODEL).

Same-origin PROD ; CORS PROD default deny ; credentials false. Trusted proxy SEC-016.

Privacy : client envoie seulement `privacy_acknowledgement: true` ; version serveur (TM-025).

## Réévaluation

Auth utilisateur ; analytics TBD-006.
