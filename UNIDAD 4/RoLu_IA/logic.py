import os
import json
import time
import re
import base64
import asyncio
from datetime import datetime
from typing import AsyncGenerator, List, Dict

import httpx
from dotenv import load_dotenv
from providers import MODEL_METADATA, OLLAMA_URL, DEFAULT_MODEL, OLLAMA_IMAGE_MODEL, is_image_model

load_dotenv()


def _get(m, key: str):
    """Lee role/content tanto de dicts como de objetos ChatMessage."""
    return getattr(m, key) if hasattr(m, key) else m.get(key, "")


# ── Búsqueda web (opcional, requiere TAVILY_API_KEY) ─────────────────────────
tavily_client = None
if os.getenv("TAVILY_API_KEY"):
    try:
        from tavily import TavilyClient
        tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    except ImportError:
        print("[Tavily] Instala 'tavily-python' para usar la búsqueda web.")


async def get_web_search_context(query: str) -> str:
    if not tavily_client or not query:
        return ""
    try:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None, lambda: tavily_client.search(query, search_depth="basic", max_results=5)
        )
        results = response.get("results", [])
        if not results:
            return "\n\n⚠️ No se encontraron resultados.\n"
        context = "\n\n📰 RESULTADOS DE BÚSQUEDA WEB:\n"
        for i, r in enumerate(results, 1):
            context += f"[{i}] \"{r.get('title', 'Sin título')}\" — {r.get('url', '')}\n   {r.get('content', '')[:600]}\n\n"
        return context + "FIN DE RESULTADOS.\n"
    except Exception as e:
        print(f"[Tavily] Error: {e}")
        return "\n\n⚠️ La búsqueda web falló.\n"


# Frases como "genérame una imagen de…", "dibuja un…", "crea un logo de…"
_IMAGE_INTENT = re.compile(
    r"^\s*(por\s+favor\s+)?(gen[eé]ra(me|nos)?|crea(me|nos)?|haz(me|nos)?|dib[uú]ja(me|nos)?|"
    r"pinta(me|nos)?|dise[nñ]a(me|nos)?|quiero|necesito)\s+(una?\s+|el\s+|la\s+)?"
    r"(imagen|imágen|foto|fotograf[ií]a|dibujo|ilustraci[oó]n|logo|logotipo|p[oó]ster|retrato)\b",
    re.IGNORECASE,
)
_DRAW_INTENT = re.compile(r"^\s*(dib[uú]ja(me|nos)?|pinta(me|nos)?)\s+", re.IGNORECASE)


def wants_image(text: str) -> bool:
    """Detecta si el mensaje pide generar una imagen."""
    return bool(_IMAGE_INTENT.search(text or "") or _DRAW_INTENT.search(text or ""))


def get_system_prompt(search_context: str = "", timezone: str = "America/Monterrey") -> str:
    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo(timezone)).strftime("%d/%m/%Y %H:%M")
    except Exception:
        now = datetime.now().strftime("%d/%m/%Y %H:%M")

    prompt = (
        "Eres RoLu IA, un asistente de inteligencia artificial desarrollado por Rodrigo Garcia y Luna Prieto. "
        "Responde siempre en español, de forma clara y bien estructurada.\n"
        f"Fecha actual: {now} ({timezone}).\n"
    )
    if search_context:
        prompt += (
            "\nPROTOCOLO CON FUENTES:\n"
            "- Usa SOLO los datos de los resultados de búsqueda adjuntos.\n"
            "- Cita cada fuente con [n] donde n es el número del resultado.\n"
            "- Si algo no aparece en los resultados, dilo explícitamente.\n"
            f"\nCONTEXTO DE BÚSQUEDA:\n{search_context}"
        )
    return prompt


async def stream_chat_response(
    messages: List[Dict[str, str]],
    model: str = DEFAULT_MODEL,
    web_search_enabled: bool = False,
) -> AsyncGenerator[str, None]:
    # Si el usuario pide una imagen con el modelo de texto, se usa el de imágenes
    if not is_image_model(model) and messages:
        last = _get(messages[-1], "content") or ""
        if _get(messages[-1], "role") == "user" and wants_image(last):
            model = OLLAMA_IMAGE_MODEL

    if is_image_model(model):
        async for piece in generate_image(messages, model):
            yield piece
        return

    # 1. Búsqueda web (si está activada y hay key)
    search_context = ""
    if web_search_enabled:
        if not tavily_client:
            yield "_(Búsqueda web desactivada: falta TAVILY_API_KEY en .env)_\n\n"
        else:
            last_user = next((_get(m, "content") for m in reversed(messages) if _get(m, "role") == "user"), "")
            search_context = await get_web_search_context(last_user)

    # 2. Mensajes para Ollama
    llm_messages = [{"role": "system", "content": get_system_prompt(search_context)}]
    for m in messages:
        role, content = _get(m, "role"), _get(m, "content")
        # No reenviar al LLM los mensajes con imágenes generadas
        if role and content and "gen_images/" not in content:
            llm_messages.append({"role": role, "content": content})

    meta = MODEL_METADATA.get(model, {})
    payload = {
        "model": model,
        "messages": llm_messages,
        "stream": True,
        "think": os.getenv("OLLAMA_THINK", "false").lower() == "true",
        "options": {
            "temperature": 0.2 if search_context else meta.get("temperature", 0.7),
            "num_predict": meta.get("maxOutputTokens", 4096),
        },
    }

    # 3. Streaming desde Ollama local
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(600.0, connect=5.0)) as client:
            async with client.stream("POST", f"{OLLAMA_URL}/api/chat", json=payload) as resp:
                if resp.status_code != 200:
                    body = (await resp.aread()).decode("utf-8", "ignore")
                    if "think" in body.lower() and payload["think"] is False:
                        # Modelo sin soporte de 'think': reintentar sin ese parámetro
                        payload.pop("think")
                        async for piece in _retry(client, payload):
                            yield piece
                        return
                    if resp.status_code == 404:
                        yield (f"⚠️ El modelo **{model}** no está instalado en Ollama. "
                               f"Ejecuta en la Terminal: `ollama pull {model}`")
                    else:
                        yield f"⚠️ Ollama respondió {resp.status_code}: {body[:300]}"
                    return
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    data = json.loads(line)
                    if data.get("error"):
                        yield f"\n⚠️ {data['error']}"
                        return
                    delta = data.get("message", {}).get("content", "")
                    if delta:
                        yield delta
                    if data.get("done"):
                        break
    except httpx.ConnectError:
        yield ("⚠️ No me pude conectar a Ollama en "
               f"{OLLAMA_URL}. Abre la app de Ollama (o ejecuta `ollama serve`) y vuelve a intentar.")
    except Exception as e:
        yield f"🔥 Error en el motor de IA: {e}"


async def _retry(client: httpx.AsyncClient, payload: dict) -> AsyncGenerator[str, None]:
    async with client.stream("POST", f"{OLLAMA_URL}/api/chat", json=payload) as resp:
        async for line in resp.aiter_lines():
            if line:
                data = json.loads(line)
                delta = data.get("message", {}).get("content", "")
                if delta:
                    yield delta


# ── Generación de imágenes con Ollama ────────────────────────────────────────
GEN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "www", "gen_images")


async def _to_english_prompt(client: httpx.AsyncClient, text: str) -> str:
    """Usa el modelo de texto local para pasar el prompt a inglés (mejora la imagen)."""
    try:
        r = await client.post(f"{OLLAMA_URL}/api/chat", json={
            "model": DEFAULT_MODEL,
            "stream": False,
            "think": False,
            "keep_alive": 0,  # libera la RAM para que quepa el modelo de imágenes
            "messages": [
                {"role": "system", "content": "Translate the user's image description to English. "
                 "Reply ONLY with the translated prompt, no quotes, no explanations."},
                {"role": "user", "content": text},
            ],
        }, timeout=120.0)
        out = r.json().get("message", {}).get("content", "").strip()
        return out or text
    except Exception:
        return text


async def generate_image(messages, model: str) -> AsyncGenerator[str, None]:
    """
    Genera una imagen con un modelo de difusión de Ollama (p. ej. x/flux2-klein).

    IMPORTANTE: los modelos de imagen NO aceptan /api/chat (Ollama responde
    400 "does not support chat"). Se deben llamar por /api/generate, que
    devuelve la imagen en base64 en el campo "image" y el avance en
    "completed"/"total".
    """
    prompt = (_get(messages[-1], "content") or "").strip() if messages else ""
    if not prompt:
        yield "Escribe una descripción de la imagen que quieres generar."
        return

    meta = MODEL_METADATA.get(model, {})
    yield "🎨 Generando imagen en tu Mac… (puede tardar 1-2 minutos)\n\n"

    img_b64 = None
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(900.0, connect=5.0)) as client:
            en_prompt = await _to_english_prompt(client, prompt)
            payload = {
                "model": model,
                "prompt": en_prompt,
                "stream": True,
                "width": meta.get("width", 1024),
                "height": meta.get("height", 1024),
            }
            if meta.get("steps"):
                payload["steps"] = meta["steps"]

            async with client.stream("POST", f"{OLLAMA_URL}/api/generate", json=payload) as resp:
                if resp.status_code != 200:
                    body = (await resp.aread()).decode("utf-8", "ignore")
                    try:
                        err = json.loads(body).get("error", body)
                    except Exception:
                        err = body
                    yield _image_error_message(model, resp.status_code, err)
                    return

                last_shown = 0
                async for line in resp.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if data.get("error"):
                        yield _image_error_message(model, 500, data["error"])
                        return
                    total, done_steps = data.get("total") or 0, data.get("completed") or 0
                    if total and done_steps > last_shown:
                        yield f"`{done_steps}/{total}` "
                        last_shown = done_steps
                    img = data.get("image") or (data.get("images") or [None])[0]
                    if img:
                        img_b64 = img
                    if data.get("done"):
                        break
    except httpx.ConnectError:
        yield f"⚠️ No me pude conectar a Ollama en {OLLAMA_URL}. Abre la app de Ollama."
        return
    except Exception as e:
        yield f"🔥 Error generando la imagen: {e}"
        return

    if not img_b64:
        yield ("\n\n⚠️ Ollama no devolvió una imagen. Actualiza Ollama a la versión más "
               "reciente (la generación de imágenes es experimental y solo funciona en macOS).")
        return

    if "," in img_b64[:64] and img_b64.startswith("data:"):
        img_b64 = img_b64.split(",", 1)[1]  # por si llega como data-URL

    os.makedirs(GEN_DIR, exist_ok=True)
    name = f"rolu_img_{int(time.time() * 1000)}.png"
    with open(os.path.join(GEN_DIR, name), "wb") as f:
        f.write(base64.b64decode(img_b64))
    url = f"gen_images/{name}"
    alt = prompt.replace("[", "").replace("]", "")[:100]
    yield f"\n\n![{alt}]({url})\n\n[⬇️ Abrir / descargar imagen]({url})"


def _image_error_message(model: str, status: int, err: str) -> str:
    """Traduce los errores típicos de Ollama a un mensaje claro en español."""
    low = (err or "").lower()
    if status == 404 or "not found" in low:
        return (f"⚠️ El modelo **{model}** no está instalado. "
                f"Ejecuta en la Terminal: `ollama pull {model}`")
    if "does not support chat" in low:
        return (f"⚠️ **{model}** es un modelo de imágenes y no admite chat. "
                "Selecciona **RoLu Image** en el selector de modelo.")
    if "does not support generate" in low or "not supported" in low or "unknown" in low:
        return ("⚠️ Tu versión de Ollama no soporta generación de imágenes. "
                "Actualiza Ollama desde https://ollama.com/download (solo macOS por ahora).")
    if "memory" in low or "insufficient" in low:
        return ("⚠️ No hay memoria suficiente para cargar el modelo de imágenes. "
                "Cierra otras apps o baja la resolución en providers.py (width/height = 768).")
    return f"⚠️ Ollama respondió {status}: {err[:300]}"
