#!/bin/bash
# Doble clic para instalar (la primera vez) y abrir RoLu IA.
cd "$(dirname "$0")"

MODEL=$(grep -E '^OLLAMA_MODEL=' .env 2>/dev/null | cut -d= -f2); MODEL=${MODEL:-qwen3.5:4b}
IMG_MODEL=$(grep -E '^OLLAMA_IMAGE_MODEL=' .env 2>/dev/null | cut -d= -f2); IMG_MODEL=${IMG_MODEL:-x/flux2-klein}

export PATH="/usr/local/bin:/opt/homebrew/bin:/Applications/Ollama.app/Contents/Resources:$PATH"
if ! command -v ollama >/dev/null 2>&1; then
    echo "⚠️  No encontré Ollama. Instálalo desde https://ollama.com y vuelve a abrir este archivo."
    read -r; exit 1
fi
if ! curl -s http://localhost:11434/api/tags >/dev/null; then
    echo "→ Iniciando Ollama..."
    open -a Ollama 2>/dev/null || (ollama serve >/dev/null 2>&1 &)
    sleep 4
fi
for M in "$MODEL" "$IMG_MODEL"; do
    if ! ollama list | awk '{print $1}' | sed 's/:latest$//' | grep -qx "${M%:latest}"; then
        echo "→ Descargando el modelo $M (solo la primera vez)..."
        ollama pull "$M" || echo "⚠️  No se pudo descargar $M."
    fi
done

if [ ! -d ".venv" ]; then
    echo "→ Creando entorno virtual..."
    python3 -m venv .venv || { echo "Instala Python 3 desde https://www.python.org"; read -r; exit 1; }
fi
source .venv/bin/activate
if [ ! -f ".venv/.instalado" ] || [ requirements.txt -nt .venv/.instalado ]; then
    echo "→ Instalando dependencias..."
    pip install --upgrade pip -q
    pip install -r requirements.txt || { echo "Falló la instalación."; read -r; exit 1; }
    touch .venv/.instalado
fi

echo "→ Abriendo RoLu IA ($MODEL) en http://127.0.0.1:8000"
( sleep 3; open http://127.0.0.1:8000 ) &
shiny run app.py --port 8000
