$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv")) {
    Write-Host "Creando entorno virtual..."
    python -m venv .venv
}

$py = ".\.venv\Scripts\python.exe"
$env:PYTHONPATH = ""

Write-Host "Instalando dependencias..."
& $py -m pip install --upgrade pip
& $py -m pip install -r requirements.txt pyinstaller

Write-Host "Generando icono del .exe..."
$iconSrc = "C:\Users\ayram\Downloads\icons8-copybook-48.png"
if (-not (Test-Path $iconSrc)) { $iconSrc = "assets\copybook.png" }
& $py -c @"
from PIL import Image
img = Image.open(r'$iconSrc').convert('RGBA')
img.save('assets/app.ico', sizes=[(s, s) for s in (16, 32, 48, 64, 128, 256)])
"@

Write-Host "Compilando .exe..."
& $py -m PyInstaller --noconfirm --clean ProcesadorLiquidacionesTasy.spec

Write-Host ""
Write-Host "Listo: dist\ProcesadorLiquidacionesTasy.exe"
