# Chatbot con Shiny + Ollama (qwen3.5:4b)

Chatbot hecho con [Shiny for Python](https://shiny.posit.co/py/) y [chatlas](https://posit-dev.github.io/chatlas/),
usando un modelo local de [Ollama](https://ollama.com). No necesita API key ni internet.

## Configuración (solo la primera vez)

1. Instala Ollama y descarga el modelo:

   ```bash
   ollama pull qwen3.5:4b
   ```

2. Copia `.env.example` como `.env` (ahí se elige el modelo y la dirección de Ollama):

   ```bash
   cp .env.example .env
   ```

3. Crea el entorno virtual e instala las dependencias:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Ejecutar

Con la app de Ollama abierta (o `ollama serve` corriendo en otra terminal):

```bash
source .venv/bin/activate
shiny run --launch-browser app.py
```

## Notas

- `app.py` = versión Shiny Express (la principal). `app-core.py` = versión Shiny Core.
- `ollama_client.py` maneja la conexión con Ollama. Si Ollama no está corriendo o el modelo no está
  instalado, el chat muestra un mensaje con el comando para arreglarlo.
- Para usar otro modelo, cambia `OLLAMA_MODEL` en `.env` (por ejemplo `OLLAMA_MODEL=llama3.2`) y descárgalo con `ollama pull`.
- No uses `--reload` (o usa `--reload-excludes ".venv/*"`): si no, la página se recarga sola.
- Si mueves la carpeta de lugar, borra `.venv` y vuelve a crearlo (el entorno virtual guarda rutas absolutas).
