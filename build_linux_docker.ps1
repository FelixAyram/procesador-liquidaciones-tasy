# Compila para Linux desde Windows con DOCKER (sin instalar Ubuntu).
# Solo necesitás Docker Desktop: https://www.docker.com/products/docker-desktop/
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== Compilar Linux con Docker (sin Ubuntu) ===" -ForegroundColor Cyan

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host ""
    Write-Host "Docker no está instalado." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1) Instalá Docker Desktop (no es Ubuntu, es un instalador):" -ForegroundColor White
    Write-Host "   https://www.docker.com/products/docker-desktop/" -ForegroundColor Green
    Write-Host ""
    Write-Host "2) Abrí Docker Desktop y esperá que diga 'Running'." -ForegroundColor White
    Write-Host ""
    Write-Host "3) Volvé a ejecutar:" -ForegroundColor White
    Write-Host "   .\build_linux_docker.ps1" -ForegroundColor Green
    Write-Host ""
    Write-Host "Alternativa SIN instalar nada local:" -ForegroundColor White
    Write-Host "   .\build_linux_github.ps1" -ForegroundColor Green
    Write-Host "   (compila en la nube con GitHub Actions)" -ForegroundColor Gray
    exit 1
}

Write-Host "Verificando Docker..." -ForegroundColor Gray
docker info 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker está instalado pero no está corriendo. Abrí Docker Desktop." -ForegroundColor Red
    exit 1
}

$projectPath = (Resolve-Path $PSScriptRoot).Path
Write-Host "Compilando con imagen batonogov/pyinstaller-linux..." -ForegroundColor Cyan
Write-Host "(Primera vez puede tardar varios minutos descargando la imagen)" -ForegroundColor Gray

docker run --rm `
    -v "${projectPath}:/src" `
    -w /src `
    -e SPECFILE=ProcesadorLiquidacionesTasy-linux.spec `
    --entrypoint /bin/bash `
    batonogov/pyinstaller-linux:latest `
    -c @"
set -e
apt-get update -qq
apt-get install -y -qq python3-tk >/dev/null
pip install -q -r requirements.txt
pyinstaller --noconfirm --clean ProcesadorLiquidacionesTasy-linux.spec
"@

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error en la compilación Docker." -ForegroundColor Red
    exit 1
}

$out = Join-Path $PSScriptRoot "dist\ProcesadorLiquidacionesTasy"
if (Test-Path $out) {
    $mb = [math]::Round((Get-Item $out).Length / 1MB, 1)
    Write-Host ""
    Write-Host "Listo: $out  ($mb MB)" -ForegroundColor Green
    Write-Host "En Linux: chmod +x ProcesadorLiquidacionesTasy && ./ProcesadorLiquidacionesTasy" -ForegroundColor Gray
} else {
    Write-Host "Revisá la carpeta dist\" -ForegroundColor Yellow
    Get-ChildItem dist -ErrorAction SilentlyContinue
}
