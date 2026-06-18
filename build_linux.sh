#!/usr/bin/env bash
# Compila ejecutable para Linux (correr EN una máquina Linux).
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt pyinstaller -q

pyinstaller --noconfirm --clean \
    --onefile \
    --windowed \
    --name ProcesadorLiquidacionesTasy \
    --add-data "assets:assets" \
    --hidden-import pdfplumber \
    --hidden-import openpyxl \
    --hidden-import PIL.Image \
    --hidden-import PIL.ImageTk \
    main.py

echo ""
echo "Listo: dist/ProcesadorLiquidacionesTasy"
echo "Ejecutar: ./dist/ProcesadorLiquidacionesTasy"
