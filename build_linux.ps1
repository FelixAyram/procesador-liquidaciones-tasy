# Elige cómo compilar para Linux SIN instalar Ubuntu.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "  Compilar para LINUX desde Windows" -ForegroundColor Cyan
Write-Host "  (PyInstaller no puede cross-compilar directamente)" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  [1] Docker Desktop  - instalador unico, NO es Ubuntu manual" -ForegroundColor White
Write-Host "  [2] GitHub Actions  - compila en la nube, cero instalacion local" -ForegroundColor White
Write-Host "  [3] WSL + Ubuntu    - Linux dentro de Windows (mas pesado)" -ForegroundColor DarkGray
Write-Host ""
$choice = Read-Host "Elegi 1, 2 o 3"

switch ($choice) {
    "1" { & "$PSScriptRoot\build_linux_docker.ps1" }
    "2" { & "$PSScriptRoot\build_linux_github.ps1" }
    "3" { & "$PSScriptRoot\build_linux_from_windows.ps1" }
    default {
        Write-Host "Opcion invalida. Usa 1, 2 o 3." -ForegroundColor Red
        exit 1
    }
}
