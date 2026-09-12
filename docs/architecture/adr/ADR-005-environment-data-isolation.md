# ADR-005 — Isolation environnements et données

| Champ | Valeur |
|---|---|
| Statut | ACCEPTED |
| Date | 2026-09-12 |
| Ticket | THL-ARCH-001 / 001A / 001B / **001C** |

## Contexte

AGENTS.md + PRD : DEV, RECETTE, PREPROD, PROD isolés. Interdiction copie PROD vers env inférieurs.

## Décision

- Quatre bases PostgreSQL logiquement séparées ; même schéma via Alembic identique.
- Secrets et clés Turnstile/email distincts par env.
- Données hors PROD : **synthétiques** ou anonymisées irreversiblement avec approbation Kyria.
- Aucune auth/paiement/compte V1 (pas de magic link, OTP, OAuth) tant qu’un PRD dédié ne l’introduit pas.
- Hébergeur cloud : [À CONFIRMER — Owner: Jores + Kyria — Gate: PREPROD] (TBD-007).

## Alternatives

| Alternative | Rejet |
|---|---|
| Une base partagée multi-env | Fuite PII, non-conformité gouvernance |
| Restore PROD → DEV | Interdit AGENTS.md |

## Réévaluation

- Besoin debug prod-like → snapshots anonymisés pipeline documenté.
