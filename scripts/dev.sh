#!/usr/bin/env sh
# Guide DEV — n'exécute pas les services ; affiche les commandes à lancer.
set -eu
cd "$(dirname "$0")/.."
echo "=== THE HIVE LOGISTICS — guide DEV (001A1) ==="
echo "1. PostgreSQL: docker compose -f infra/compose/docker-compose.dev.yml up -d"
echo "2. API:       pnpm api:dev"
echo "3. Web:       pnpm web:dev"
echo "Doc: docs/development/LOCAL-SETUP.md"
