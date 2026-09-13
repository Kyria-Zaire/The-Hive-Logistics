# Environnement local — THE HIVE LOGISTICS

Socle foundation (THL-FOUNDATION-001A) : health checks, PostgreSQL DEV, Next.js minimal.

## Prérequis

| Outil | Version cible |
|---|---|
| Node.js | **24.18.1** (voir `.nvmrc` ; `engine-strict` via `.npmrc`) |
| pnpm | **10.16.1** (verrouillé dans `package.json`) |
| Python | 3.13 (voir `.python-version`) |
| uv | gestionnaire Python du dépôt |
| Docker + Compose | PostgreSQL 18 local |

Aucune donnée réelle ni secret PROD en DEV. Copier les fichiers `.env.template` vers `.env` **local uniquement** (jamais commités).

## PostgreSQL (Docker)

### PowerShell

```powershell
cd infra/compose
Copy-Item .env.template .env
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml ps
```

### POSIX

```sh
cd infra/compose
cp .env.template .env
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml ps
```

Arrêt :

```sh
docker compose -f docker-compose.dev.yml down
```

Volume nommé `thl_postgres_dev_data` — données jetables DEV.

## API FastAPI

```powershell
cd apps/api
Copy-Item .env.template .env
cd ../..
uv run --directory apps/api uvicorn thl_api.main:app --host 127.0.0.1 --port 8000 --reload
```

Endpoints : `GET /api/v1/health/live`, `GET /api/v1/health/ready`.

## Next.js (DEV)

Proxy `/api/v1/*` → FastAPI **uniquement** si `NODE_ENV=development` (voir `apps/web/next.config.ts`).

```powershell
pnpm install
pnpm web:dev
```

Page `/` : écran technique minimal (pas la maquette UX).

## Commandes racine

| Commande | Rôle |
|---|---|
| `pnpm install` | Dépendances workspace |
| `pnpm web:dev` | Next.js DEV |
| `pnpm web:lint` | ESLint web |
| `pnpm web:typecheck` | `tsc --noEmit` |
| `pnpm web:build` | Build production Next |
| `pnpm api:lint` | Ruff API |
| `pnpm api:typecheck` | mypy strict API |
| `pnpm api:dev` | Uvicorn API (reload) |
| `pnpm api:test` | pytest **unitaires** (`-m "not integration"`) |
| `pnpm api:test:integration` | pytest **PostgreSQL réel** (`-m integration`, Docker requis) |
| `pnpm check` | Lint + types + **build web** + API lint/types/tests unitaires |

Les scripts `scripts/dev.ps1` et `scripts/dev.sh` sont un **guide** (affichent les commandes, ne démarrent pas les processus).

PostgreSQL 18 DEV : image `postgres:18.6-alpine3.24`, volume nommé monté sur `/var/lib/postgresql` (layout PG 18 — **pas** `/var/lib/postgresql/data`).

Si le port **5432** est déjà pris localement : `POSTGRES_PORT=5433` (ou autre) dans `infra/compose/.env`, puis aligner `DATABASE_URL` / `INTEGRATION_DATABASE_URL`.

Tests API :

- unitaires : `pnpm api:test`
- intégration PostgreSQL (Docker requis) : `pnpm api:test:integration` — **aucun skip silencieux** ; sous Windows le `conftest` force `WindowsSelectorEventLoopPolicy` pour psycopg async.

`pnpm.onlyBuiltDependencies` (racine) autorise le build de `unrs-resolver` pour ESLint sans prompt interactif.

Scripts : `scripts/check.ps1`, `scripts/check.sh`, `scripts/dev.ps1`, `scripts/dev.sh`.

## Dépannage

- **Node 24** : utiliser `fnm use 24` ou `.nvmrc` avant `pnpm install`.
- **503 /ready** : vérifier PostgreSQL (`docker compose ps`, healthcheck).
- **THL_ENV=prod** : refuse une `DATABASE_URL` contenant des marqueurs DEV (`127.0.0.1`, `thl_dev`, etc.).
