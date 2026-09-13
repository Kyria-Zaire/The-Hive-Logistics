<!-- THL: gouvernance locale Next.js — le fichier racine reste autoritaire -->

La constitution du dépôt est **[../../AGENTS.md](../../AGENTS.md)**. Ce fichier ne couvre que les règles spécifiques à `apps/web` :

- App Router uniquement ; pas de Pages Router.
- Server Components par défaut ; pas de state manager global en foundation.
- Pas d’appels métier leads ni de BFF PROD ; proxy `/api/v1` limité au DEV (`next.config.ts`).
- Direction visuelle UX : documents `docs/ux/*` ; l’écran foundation n’est pas une maquette.
