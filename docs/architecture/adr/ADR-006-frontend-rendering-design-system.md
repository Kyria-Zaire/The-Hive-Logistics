# ADR-006 — Next.js App Router et design system custom

| Champ | Valeur |
|---|---|
| Statut | ACCEPTED |
| Date | 2026-09-12 |
| Ticket | THL-ARCH-001 / **001A** |

## Contexte

UX v0.1.3 (Home) ; PRD §10 ; stack ticket THL-ARCH-001. Pas de state global V1.

## Décision

- Next.js 16 App Router, React compatible, TypeScript strict.
- **Server Components par défaut** ; Client Components pour formulaires, Turnstile widget, micro-interactions.
- Tailwind CSS 4 ; primitives Radix/shadcn adaptées identité THL (docs/ux).
- Formulaires : React Hook Form + Zod côté client ; **FastAPI/Pydantic autoritaire**.
- Client API généré OpenAPI ; appels leads en **same-origin** `/api/v1` (PROD) ; rewrite proxy API **DEV local uniquement** — pas de logique métier dans Route Handlers Next.
- Animations : CSS, WAAPI, IntersectionObserver ; pas GSAP sans preuve perf (NFR-PERF).

## Alternatives

| Alternative | Rejet |
|---|---|
| Pages Router legacy | Moins aligné long terme |
| Redux/Zustand global V1 | Complexité inutile vitrine |

## Réévaluation

- Parcours multi-étapes devis complexe (spec UX à produire).
