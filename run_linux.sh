#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "=== Procesador de Liquidaciones Tasy (Linux) ==="

if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: instalá Python 3."
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv python3-tk"
    echo "  Fedora:        sudo dnf install python3 python3-pip python3-tkinter"
    exit 1
fi

# tkinter suele venir en paquete aparte en Linux
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "Error: falta tkinter."
    echo "  Ubuntu/Debian: sudo apt install python3-tk"
    echo "  Fedora:        sudo dnf install python3-tkinter"
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo "Iniciando aplicación..."
python main.py
