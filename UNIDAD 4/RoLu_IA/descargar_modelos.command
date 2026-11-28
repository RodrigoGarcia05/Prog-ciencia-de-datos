#!/bin/bash
# Descarga los modelos locales de RoLu IA en Ollama.
cd "$(dirname "$0")"
export PATH="/usr/local/bin:/opt/homebrew/bin:/Applications/Ollama.app/Contents/Resources:$PATH"
if ! command -v ollama >/dev/null 2>&1; then echo "No encontré Ollama. Instálalo desde https://ollama.com"; read -r; exit 1; fi
curl -s http://localhost:11434/api/tags >/dev/null || { open -a Ollama; sleep 5; }
echo "Versión de Ollama: $(ollama --version)"
echo "→ Descargando x/flux2-klein (modelo de imágenes)..."
ollama pull x/flux2-klein && echo "✅ x/flux2-klein listo." || echo "⚠️  Falló la descarga (actualiza Ollama a la última versión)."
echo; ollama list
echo; echo "Puedes cerrar esta ventana."
