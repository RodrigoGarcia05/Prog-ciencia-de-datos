import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

# Modelo local de Ollama (se puede cambiar en .env con OLLAMA_MODEL)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:4b")
OLLAMA_URL   = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
# Modelo local de Ollama para generar imágenes (solo macOS)
OLLAMA_IMAGE_MODEL = os.getenv("OLLAMA_IMAGE_MODEL", "x/flux2-klein")

MODEL_METADATA: Dict[str, dict] = {
    OLLAMA_MODEL: {"temperature": 0.7, "maxOutputTokens": 4096},
    OLLAMA_IMAGE_MODEL: {"isImage": True, "width": 1024, "height": 1024},
}

MODEL_LABELS: Dict[str, str] = {
    OLLAMA_MODEL: f"RoLu IA ({OLLAMA_MODEL} · Ollama)",
    OLLAMA_IMAGE_MODEL: "RoLu Image (FLUX.2 Klein · Ollama)",
}

DEFAULT_MODEL = OLLAMA_MODEL


def get_visible_models() -> List[str]:
    return list(MODEL_METADATA)


def get_model_label(model_id: str) -> str:
    return MODEL_LABELS.get(model_id, model_id)


def is_image_model(model_id: str) -> bool:
    return bool(MODEL_METADATA.get(model_id, {}).get("isImage"))
