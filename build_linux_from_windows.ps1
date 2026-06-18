# Compila ejecutable Linux desde Windows usando WSL (Ubuntu).
# PyInstaller NO puede cross-compilar: hay que compilar dentro de Linux.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Convert-ToWslPath([string]$WindowsPath) {
    $full = (Resolve-Path $WindowsPath).Path
    if ($full -match '^([A-Za-z]):\\(.*)$') {
        $drive = $Matches[1].ToLower()
        $rest = $Matches[2] -replace '\\', '/'
        return "/mnt/$drive/$rest"
    }
    throw "Ruta no válida: $WindowsPath"
}

function Test-WslReady {
    try {
        $out = wsl.exe -e bash -lc "echo ok" 2>&1
        return ($LASTEXITCODE -eq 0) -and ($out -match "ok")
    } catch {
        return $false
    }
}

$WslProject = Convert-ToWslPath $PSScriptRoot

Write-Host "=== Compilar para Linux desde Windows (WSL) ===" -ForegroundColor Cyan
Write-Host "Proyecto WSL: $WslProject"

if (-not (Test-WslReady)) {
    Write-Host ""
    Write-Host "WSL no está instalado o no tiene una distro Linux." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Paso 1 — Abrí PowerShell COMO ADMINISTRADOR y ejecutá:" -ForegroundColor White
    Write-Host "  wsl --install -d Ubuntu" -ForegroundColor Green
    Write-Host ""
    Write-Host "Paso 2 — Reiniciá la PC si lo pide Windows." -ForegroundColor White
    Write-Host ""
    Write-Host "Paso 3 — Abrí Ubuntu (creá usuario/contraseña la primera vez)." -ForegroundColor White
    Write-Host ""
    Write-Host "Paso 4 — Volvé a ejecutar este script:" -ForegroundColor White
    Write-Host "  .\build_linux_from_windows.ps1" -ForegroundColor Green
    Write-Host ""
    exit 1
}

Write-Host "Compilando dentro de WSL/Ubuntu..." -ForegroundColor Cyan

$buildScript = @"
set -euo pipefail
cd '$WslProject'

export DEBIAN_FRONTEND=noninteractive
if ! command -v python3 >/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y python3 python3-pip python3-venv python3-tk
fi

if ! python3 -c 'import tkinter' 2>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y python3-tk
fi

if [ ! -d .venv-linux ]; then
    python3 -m venv .venv-linux
fi

source .venv-linux/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt pyinstaller -q

pyinstaller --noconfirm --clean \
    --onefile \
    --windowed \
    --name ProcesadorLiquidacionesTasy \
    --add-data 'assets:assets' \
    --hidden-import pdfplumber \
    --hidden-import openpyxl \
    --hidden-import PIL.Image \
    --hidden-import PIL.ImageTk \
    main.py

echo ''
echo 'LISTO: dist/ProcesadorLiquidacionesTasy'
ls -lh dist/ProcesadorLiquidacionesTasy 2>/dev/null || ls -lh dist/
"@

wsl.exe -e bash -lc $buildScript

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error en la compilación." -ForegroundColor Red
    exit 1
}

$outFile = Join-Path $PSScriptRoot "dist\ProcesadorLiquidacionesTasy"
if (Test-Path $outFile) {
    $size = [math]::Round((Get-Item $outFile).Length / 1MB, 1)
    Write-Host ""
    Write-Host "Ejecutable Linux generado:" -ForegroundColor Green
    Write-Host "  $outFile  ($size MB)"
    Write-Host ""
    Write-Host "Copiá ese archivo a Linux y ejecutá:" -ForegroundColor White
    Write-Host "  chmod +x ProcesadorLiquidacionesTasy" -ForegroundColor Gray
    Write-Host "  ./ProcesadorLiquidacionesTasy" -ForegroundColor Gray
} else {
    Write-Host "Compilación terminó pero no se encontró dist/ProcesadorLiquidacionesTasy" -ForegroundColor Yellow
}
