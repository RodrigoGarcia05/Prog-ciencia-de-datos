# ------------------------------------------------------------------------------------
# Cliente de Gemini con respaldo automático.
# Si un modelo está saturado (503), con límite de uso (429) o no existe (404),
# se intenta con el siguiente modelo de la lista, conservando el historial.
# ------------------------------------------------------------------------------------
import os
from pathlib import Path

from chatlas import ChatGoogle
from dotenv import load_dotenv
from google.genai import errors

# Busca el .env junto a este archivo, sin importar desde dónde se ejecute la app
load_dotenv(Path(__file__).resolve().parent / ".env")

SYSTEM_PROMPT = "Eres un asistente útil. Responde en español de forma clara y concisa."

# Errores por los que vale la pena probar otro modelo
CODIGOS_REINTENTABLES = {404, 429, 500, 503, 504}


def _es_error_de_red(e: Exception) -> bool:
    """Detecta errores de conexión (sin internet, DNS, timeout)."""
    nombres = {"ConnectError", "ConnectTimeout", "ClientConnectorError", "ServerDisconnectedError"}
    actual = e
    while actual is not None:
        if isinstance(actual, OSError) or type(actual).__name__ in nombres:
            return True
        if "nodename nor servname" in str(actual):
            return True
        actual = actual.__cause__ or actual.__context__
    return False


def _lista_modelos() -> list[str]:
    principal = os.getenv("GEMINI_MODEL", "gemini-flash-latest").strip()
    respaldo = os.getenv(
        "GEMINI_FALLBACK_MODELS",
        "gemini-2.5-flash,gemini-flash-lite-latest,gemini-2.5-flash-lite",
    )
    modelos = [principal] + [m.strip() for m in respaldo.split(",") if m.strip()]
    return list(dict.fromkeys(modelos))  # sin duplicados, en orden


class GeminiConRespaldo:
    """Mantiene una conversación y cambia de modelo si el actual falla."""

    def __init__(self):
        self.modelos = _lista_modelos()
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self._clientes: dict[str, ChatGoogle] = {}
        self._turnos = []  # historial de la conversación

    def _cliente(self, modelo: str) -> ChatGoogle:
        if modelo not in self._clientes:
            self._clientes[modelo] = ChatGoogle(
                model=modelo,
                api_key=self.api_key,
                system_prompt=SYSTEM_PROMPT,
            )
        return self._clientes[modelo]

    async def stream(self, mensaje: str):
        ultimo_error = None
        for modelo in self.modelos:
            cliente = self._cliente(modelo)
            cliente.set_turns(self._turnos)  # mismo historial en cada intento
            try:
                respuesta = await cliente.stream_async(mensaje)
                it = respuesta.__aiter__()
                try:
                    primero = await it.__anext__()  # aquí aparece el 503 si lo hay
                except StopAsyncIteration:
                    primero = None
            except errors.APIError as e:
                if e.code in CODIGOS_REINTENTABLES:
                    print(f"[Gemini] {modelo} falló ({e.code}). Probando el siguiente modelo...")
                    ultimo_error = e
                    continue
                raise
            except Exception as e:
                if _es_error_de_red(e):
                    raise RuntimeError(
                        "No hay conexión con los servidores de Google. Revisa tu "
                        "internet (o VPN/proxy) e inténtalo de nuevo."
                    ) from e
                raise

            if modelo != self.modelos[0]:
                print(f"[Gemini] Respondiendo con el modelo de respaldo: {modelo}")
            if primero is not None:
                yield primero
            async for trozo in it:
                yield trozo
            self._turnos = cliente.get_turns()
            return

        raise RuntimeError(
            "Todos los modelos de Gemini están ocupados o no disponibles en este "
            "momento. Espera unos segundos e inténtalo de nuevo."
        ) from ultimo_error
