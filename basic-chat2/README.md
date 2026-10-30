# Chatbot con Shiny + Google Gemini

Chatbot hecho con [Shiny for Python](https://shiny.posit.co/py/) y [chatlas](https://posit-dev.github.io/chatlas/),
usando los modelos de Google Gemini.

## Configuración (solo la primera vez)

1. Consigue una API key en [Google AI Studio](https://aistudio.google.com/api-keys).
2. Copia `.env.example` como `.env` y pega tu clave:

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

```bash
source .venv/bin/activate
shiny run --launch-browser app.py
```

## Notas

- `app.py` = versión Shiny Express (la principal). `app-core.py` = versión Shiny Core.
- `gemini_client.py` maneja la conexión con Gemini. Si el modelo principal está saturado (503) o falla,
  prueba solo los modelos de respaldo (`gemini-2.5-flash`, `gemini-flash-lite-latest`, `gemini-2.5-flash-lite`).
  Puedes cambiar la lista agregando en `.env`: `GEMINI_FALLBACK_MODELS=modelo1,modelo2`.
- No uses `--reload` (o usa `--reload-excludes ".venv/*"`): si no, la página se recarga sola.
- El archivo `.env` contiene tu clave y está en `.gitignore`: **no lo subas a GitHub**.
- Si mueves la carpeta de lugar, borra `.venv` y vuelve a crearlo (el entorno virtual guarda rutas absolutas).
