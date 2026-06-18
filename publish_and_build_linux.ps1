# Publica en GitHub, dispara Build Linux y descarga el binario.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host "=== GitHub Actions: compilar Linux ===" -ForegroundColor Cyan

gh auth status 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "No estás logueado en GitHub. Ejecutá:" -ForegroundColor Red
    Write-Host "  gh auth login --web" -ForegroundColor Yellow
    exit 1
}

$remote = (git remote 2>$null | Select-String -Pattern "^origin$" -Quiet)
if (-not $remote) {
    $repoName = "procesador-liquidaciones-tasy"
    Write-Host "Creando repo privado: $repoName" -ForegroundColor Gray
    gh repo create $repoName --private --source=. --remote=origin --push
} else {
    git branch -M main 2>$null
    git push -u origin main 2>&1 | Out-Null
}

Write-Host "Disparando workflow Build Linux..." -ForegroundColor Gray
gh workflow run build-linux.yml
Start-Sleep -Seconds 5
$runId = (gh run list --workflow=build-linux.yml --limit 1 --json databaseId -q '.[0].databaseId')
Write-Host "Esperando run $runId (2-4 min)..." -ForegroundColor Gray
gh run watch $runId --exit-status

$outDir = Join-Path $PSScriptRoot "dist-linux"
if (Test-Path $outDir) { Remove-Item -Recurse -Force $outDir }
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
gh run download $runId -n ProcesadorLiquidacionesTasy-Linux -D $outDir

Write-Host ""
Write-Host "Descargado en:" -ForegroundColor Green
Get-ChildItem $outDir -Recurse | ForEach-Object { Write-Host "  $($_.FullName)" }
