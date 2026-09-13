# Preuve : scripts/check.ps1 propage le code de sortie d'une commande native en échec (pnpm stub).
$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "../..")
$checkPath = Join-Path $root "scripts/check.ps1"

$checkContent = Get-Content -LiteralPath $checkPath -Raw
if ($checkContent -notmatch '\$LASTEXITCODE') {
    Write-Error "scripts/check.ps1 ne récupère pas `$LASTEXITCODE"
    exit 1
}

$stubDir = Join-Path $env:TEMP ("thl-pnpm-stub-" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $stubDir -Force | Out-Null
try {
    @(
        '@echo off'
        'exit /b 9'
    ) | Set-Content -LiteralPath (Join-Path $stubDir "pnpm.cmd") -Encoding ASCII

    $env:PATH = "$stubDir;$env:PATH"
    $proc = Start-Process -FilePath "powershell.exe" -ArgumentList @(
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        $checkPath
    ) -Wait -PassThru -NoNewWindow

    if ($proc.ExitCode -ne 9) {
        Write-Error "scripts/check.ps1 attendu exit 9 (pnpm stub), obtenu $($proc.ExitCode)"
        exit 1
    }

    Write-Host "CHECK_PS1_EXIT_PROPAGATION = PASS (scripts/check.ps1 exit $($proc.ExitCode))"
    exit 0
}
finally {
    Remove-Item -LiteralPath $stubDir -Recurse -Force -ErrorAction SilentlyContinue
}
