# Modèle de menaces V1 — Surface publique leads

| Version | **0.1.2** | Ticket | THL-ARCH-001 / 001A / **001B** | Statut | APPROVED_FOR_IMPLEMENTATION |

## Périmètre

Navigateur → CDN/WAF/Ingress (same-origin) → Next.js (pages) / FastAPI (`/api/v1`) → PostgreSQL ; worker notifications ; Cloudflare Turnstile ; fournisseur email [À CONFIRMER — Owner: Kyria + Jores — Gate: RECETTE] TBD-009.

Hors V1 actif : webhooks entrants, auth client, SSRF applicatif (surveillance future).

## Synthèse des menaces (TM-001 à TM-025)

| ID | Actif | Scénario | Impact | Prévention | Détection | Risque résiduel | Exigence |
|---|---|---|---|---|---|---|---|
| TM-001 | API leads | Spam volume POST | Disponibilité, bruit ops | `rate_limit_buckets`, Turnstile, honeypot | 429, GRD-001 | Modéré | FR-018, SEC-004 |
| TM-002 | API | Bot automatisé | Leads faux | Turnstile serveur | Taux 403 | Faible | FR-006, SEC-003 |
| TM-003 | PostgreSQL | Injection SQL | Fuite/modification | ORM paramétré, SEC-018 | Erreurs SQL logs | Faible | SEC-001 |
| TM-004 | Navigateur | XSS stockée (message contact) | Utilisateurs futurs | Encodage sortie, CSP | CSP reports | Faible | SEC-009 |
| TM-005 | API | CSRF / cross-site POST | Leads non sollicités | CORS deny PROD, pas cookies auth | Anomalie origin | Faible | SEC-012 |
| TM-006 | API future | SSRF via URL user | Scan interne | Pas fetch URL user V1 | — | N/A V1 | ADR futur |
| TM-007 | Rate limit | IP spoof X-Forwarded-For | Bypass limites | Trusted proxy SEC-016, HMAC digest | Comparaison proxy vs direct | Modéré | SEC-016 |
| TM-008 | API | Replay POST | Doublons | Idempotency SEC-017 | Empreinte/clé | Faible | FR-043 |
| TM-009 | UX/API | Double soumission clic | 2 leads | Idempotency-Key client | Tests e2e | Faible | FR-043 |
| TM-010 | DB | Concurrence même clé | Double lead | Advisory lock + UNIQUE | Tests PG concurrence | Faible | ADR-003 |
| TM-011 | Logs | PII dans logs | RGPD | SEC-010 redaction | Scan logs RECETTE | Modéré | DATA-007 |
| TM-012 | Frontend | Secret Turnstile in JS | Abus clé | Secret serveur only | Scan repo CI | Faible | SEC-007 |
| TM-013 | Email | Header injection CRLF | Relay abuse | SEC-014 sanitize | Tests notification | Faible | SEC-014 |
| TM-014 | Supply chain | CVE dépendance | RCE | pip-audit, pnpm audit, SEC-011 | CI alerts | Modéré | NFR-SEC |
| TM-015 | Email provider | Compte compromis | Envoi frauduleux | Moindre privilège, rotation | Billing/alerts | Modéré | TBD-009 |
| TM-016 | Redirect | Open redirect param | Phishing | Pas redirect user V1 | — | N/A | — |
| TM-017 | API | Enumération référence THL-* | Vie privée | Pas GET by ref | — | Faible | DEC-007 |
| TM-018 | Turnstile | Panne siteverify | Indispo formulaires | 503 fail closed | Health/alerts | Modéré | BR-005, ADR-004 |
| TM-019 | Webhook futur | Callback non signé | Action non auth | Signatures futures | — | N/A V1 | AGENTS.md |
| TM-020 | Rate limit | Bypass multi-instance | Abus | `rate_limit_buckets` PG autorité | TM-020 tests multi-pod | Faible | NFR-SEC-003 |
| TM-021 | PostgreSQL | Épuisement connexions / advisory | DoS partiel | Timeout 5s, pool policy | Métriques connexions | Modéré | ADR-003 |
| TM-022 | Idempotence | Rotation HMAC ratée | Replay manqué ou faux 409 | Keyring current+previous, TTL | Tests rotation | Faible | ADR-003, 001B |
| TM-023 | Worker | Crash post-accept email | Email dupliqué | provider_dedup_key, at-least-once doc | Reclaim tests | Modéré | ADR-003 |
| TM-024 | Worker | Job processing bloqué | Starvation notifications | lock_expires_at reclaim, index partiels | Métriques queue | Modéré | DATA-MODEL §5 |
| TM-025 | API | Falsification privacy version client | Non-conformité | Version serveur only (001A) | Config audit | Faible | TM-025, PUBLIC-API-CONTRACT |

## Contrôles transverses

- Rate limiting : **PostgreSQL** autorité V1 ; WAF edge = couche additionnelle optionnelle.
- Idempotence : `key_digest` HMAC ; verrou advisory **distinct** (SHA-256 → bigint) ; timeout → 503 `IDEMPOTENCY_BUSY`.
- Worker : at-least-once ; **exactly-once email non garanti** (TM-023).

## Journalisation

Interdit : corps formulaire, jeton Turnstile, email/téléphone en clair. Autorisé : `correlation_id`, `public_reference`, codes stables.
