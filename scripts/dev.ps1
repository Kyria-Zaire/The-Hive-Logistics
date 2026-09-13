# Guide DEV — n'exécute pas les services ; affiche les commandes à lancer.
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
Write-Host "=== THE HIVE LOGISTICS — guide DEV (001A1) ==="
Write-Host "1. PostgreSQL: docker compose -f infra/compose/docker-compose.dev.yml up -d"
Write-Host "2. API:       pnpm api:dev"
Write-Host "3. Web:       pnpm web:dev"
Write-Host "Doc: docs/development/LOCAL-SETUP.md"
