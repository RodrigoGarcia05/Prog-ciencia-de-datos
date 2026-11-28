# RoLu IA

Desarrollado por **Rodrigo Garcia y Luna Prieto**.

Chat de IA hecho con Shiny para Python que usa modelos **locales** de Ollama. No necesita API keys.

- Texto: `qwen3.5:4b`
- Imágenes: `x/flux2-klein` (FLUX.2 Klein). Elige **RoLu Image** en el selector de modelo y describe la imagen (también funciona si con el modelo de texto escribes "genérame una imagen de…"). Requiere macOS y Ollama actualizado; se recomiendan 16 GB de RAM o más.

## Cómo usar

1. Ten abierta la app de **Ollama** con el modelo `qwen3.5:4b` (si no lo tienes, el script lo descarga).
2. Doble clic en `iniciar.command` (la primera vez instala todo; si macOS lo bloquea: clic derecho → Abrir).
3. Se abre http://127.0.0.1:8000

Manual: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && shiny run app.py`

## Configuración (`.env`)

- `OLLAMA_MODEL` — modelo a usar (cualquiera de `ollama list`).
- `OLLAMA_IMAGE_MODEL` — modelo de imágenes (`x/flux2-klein` o `x/z-image-turbo`, más pesado).
- `OLLAMA_THINK` — `true` para que el modelo razone antes de responder (más lento).
- `TAVILY_API_KEY` — opcional, activa el botón de búsqueda web.

## Error `400 Bad Request: "x/flux2-klein" does not support chat`

Los modelos de imagen de Ollama **no funcionan en la ventana de chat de la app de Ollama** ni por `/api/chat`.
Se usan por `/api/generate` (es lo que hace RoLu IA) o desde la Terminal:

```bash
ollama run x/flux2-klein "un perro golden retriever en un parque"
```

Si ves "no soporta generación de imágenes", actualiza Ollama desde https://ollama.com/download.
