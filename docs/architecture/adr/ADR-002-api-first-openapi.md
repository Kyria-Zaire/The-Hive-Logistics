# ADR-002 — Contrat OpenAPI API-first

| Statut | ACCEPTED |
| Date | 2026-09-12 |
| Ticket | THL-ARCH-001 / 001A / **001B** |

## Source de vérité

`contracts/openapi/openapi.yaml` OpenAPI **3.1.0**, info **1.0.1** (inchangé si contrat HTTP stable).

Client TypeScript généré **uniquement** depuis ce YAML.

## Anti-drift CI (décision ferme)

| Outil | Rôle |
|---|---|
| `openapi-spec-validator` | Structure YAML 3.1 valide |
| **Schemathesis** | Tests contrat **runtime** requêtes/réponses vs YAML |
| `scripts/check_openapi_drift.py` | Comparaison canonique YAML vs `app.openapi()` — **création THL-FOUNDATION-001** |

Règles :

- YAML OpenAPI = vérité contractuelle.
- FastAPI produit `app.openapi()` pour implémentation.
- CI canonicalise les deux ; descriptions/ordering/servers normalisables.
- **Aucune** divergence sur paths, methods, parameters, schemas, required, enums, responses, media types, headers → **échec CI**.
- Simple « fichier présent » **insuffisant**.

## Erreurs

`application/problem+json` ; `type` URN `urn:thl:problem:*`.

## Réévaluation

`/api/v2` si breaking change.
