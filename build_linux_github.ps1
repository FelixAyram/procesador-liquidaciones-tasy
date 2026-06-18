# Compila para Linux en la NUBE con GitHub Actions (sin instalar Ubuntu ni Docker).
# Requiere: cuenta GitHub + repo con el proyecto + gh CLI (opcional).
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== Compilar Linux en GitHub (sin instalar nada en la PC) ===" -ForegroundColor Cyan

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host ""
    Write-Host "Pasos manuales (sin gh CLI):" -ForegroundColor White
    Write-Host ""
    Write-Host "1. Subí la carpeta procesador_liquidaciones a un repo en GitHub" -ForegroundColor Gray
    Write-Host "2. En GitHub: Actions -> Build Linux -> Run workflow" -ForegroundColor Gray
    Write-Host "3. Descargá el artefacto 'ProcesadorLiquidacionesTasy-Linux'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "O instalá GitHub CLI para automatizar:" -ForegroundColor White
    Write-Host "  winget install GitHub.cli" -ForegroundColor Green
  Write-Host "  gh auth login" -ForegroundColor Green
    Write-Host "  .\build_linux_github.ps1" -ForegroundColor Green
    exit 0
}

$remote = git remote get-url origin 2>$null
if (-not $remote) {
    Write-Host "Este proyecto no tiene remote de GitHub configurado." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Creá un repo en github.com, luego:" -ForegroundColor White
    Write-Host "  git init" -ForegroundColor Green
    Write-Host "  git add ." -ForegroundColor Green
    Write-Host "  git commit -m 'Procesador Liquidaciones Tasy'" -ForegroundColor Green
    Write-Host "  git remote add origin https://github.com/TU_USUARIO/TU_REPO.git" -ForegroundColor Green
    Write-Host "  git push -u origin main" -ForegroundColor Green
    Write-Host "  .\build_linux_github.ps1" -ForegroundColor Green
    exit 1
}

Write-Host "Disparando workflow Build Linux..." -ForegroundColor Gray
gh workflow run build-linux.yml
Start-Sleep -Seconds 3
$runId = (gh run list --workflow=build-linux.yml --limit 1 --json databaseId -q '.[0].databaseId')

Write-Host "Esperando compilación (run $runId)..." -ForegroundColor Gray
gh run watch $runId --exit-status

$outDir = Join-Path $PSScriptRoot "dist-linux"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
gh run download $runId -n ProcesadorLiquidacionesTasy-Linux -D $outDir

Write-Host ""
Write-Host "Descargado en: $outDir" -ForegroundColor Green
Get-ChildItem $outDir
