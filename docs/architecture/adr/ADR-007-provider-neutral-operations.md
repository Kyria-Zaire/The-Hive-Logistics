# ADR-007 — Exploitation neutre vis-à-vis du fournisseur

| Champ | Valeur |
|---|---|
| Statut | ACCEPTED |
| Date | 2026-09-12 |
| Ticket | THL-ARCH-001 / 001A / **001B** |

## Contexte

TBD-007, TBD-009, TBD-021 ouverts. Le ticket interdit de choisir un hébergeur définitif.

## Décision

Documenter des **interfaces** d’exploitation indépendantes du cloud :

- Artefacts : conteneur ou bundle Python + build Next.js depuis CI Git ;
- PostgreSQL managé ou self-hosted via URL + TLS ;
- Email transactionnel via interface SMTP/API abstraite (adapter par env) ;
- Ingress TLS termination + en-têtes sécurité ;
- Backups DB + PITR [À CONFIRMER — Owner: Kyria — Gate: PROD] ;
- Médias originaux : stockage objet ou archive contrôlée (PRD §15.3), **pas** dans PostgreSQL ;
- Code frontend/backend : Git + artefacts CI — **jamais** « sauvegardé dans la base ».

Monitoring/logs : correlation_id, métriques HTTP, queue notification_jobs, sans PII.

## Alternatives

| Alternative | Rejet |
|---|---|
| Lock-in propriétaire documenté comme obligatoire | Contredit ticket + TBD-007 |

## Réévaluation

- Choix hébergeur PROD validé → ADR addendum ou ADR-008 futur.
