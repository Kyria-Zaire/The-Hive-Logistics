# ADR-001 — Monorepo modulaire et monolithe applicatif V1

| Champ | Valeur |
|---|---|
| Statut | ACCEPTED |
| Date | 2026-09-12 |
| Ticket | THL-ARCH-001 / **001A** |
| Décideur | Kyria |

## Contexte

THE HIVE LOGISTICS V1 est une vitrine + capture de leads (PRD v0.1.4). L’équipe est petite ; le PRD exclut microservices, event bus et sur-architecture. Il faut néanmoins séparer clairement frontend, API, contrats et documentation pour la livraison et la CI future.

## Décision

Adopter un **monorepo cible** documentaire :

- `apps/web` — Next.js 16 App Router ;
- `apps/api` — FastAPI ;
- `packages/api-client` — client TypeScript généré depuis OpenAPI ;
- `packages/shared-config` — constantes non secrètes partagées ;
- `contracts/openapi` — contrat public versionné ;
- `docs/` — produit, UX, architecture ;
- `infra/` — templates IaC futurs (vide en V1 doc) ;
- `scripts/` — automatisation locale/CI.

**Runtime V1 :** monolithe modulaire — une API FastAPI, un worker notifications issu du **même** code Python, une base PostgreSQL, un ingress/reverse proxy. **Same-origin PROD :** ingress route `/api/v1/*` → FastAPI ; reste → Next.js ; pas de BFF Route Handler métier. Pas de microservices.

## Alternatives étudiées

| Alternative | Rejet |
|---|---|
| Dépôts séparés web/api | Friction contrat, drift OpenAPI, CI plus lourde pour une petite équipe |
| Microservices leads / notifications | Coût ops disproportionné ; PRD §7.4 anti-surarchitecture |
| Backend dans Next.js Route Handlers seul | Validation PRD : FastAPI autoritaire, worker durable, séparation des concerns |

## Conséquences positives

- Contrat OpenAPI co-localisé ; génération client typée.
- Une seule revue de sécurité et une pipeline CI unifiée (future).
- Évolution V1.1 sans refonte topology.

## Coûts et limites

- Discipline de boundaries dans le monorepo (pas de imports sauvages web→api).
- Taille du dépôt croît avec médias doc ; code applicatif reste modulaire.

## Conditions de réévaluation

- Trafic ou équipe imposant déploiements indépendants **mesurés** ;
- Nouveau PRD authentification/paiement avec contraintes réglementaires distinctes.
