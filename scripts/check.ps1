# Validation non destructive — racine du monorepo
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
pnpm check
$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    exit $exitCode
}
exit 0
