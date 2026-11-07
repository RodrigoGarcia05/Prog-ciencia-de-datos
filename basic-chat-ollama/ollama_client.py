import os

from chatlas import ChatOllama
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = "Eres un asistente útil. Responde en español de forma clara y concisa."


def _es_error_de_red(e: Exception) -> bool:
    """Detecta errores de conexión con el servidor de Ollama."""
    nombres = {"ConnectError", "ConnectTimeout", "APIConnectionError", "APITimeoutError"}
    actual = e
    while actual is not None:
        if isinstance(actual, OSError) or type(actual).__name__ in nombres:
            return True
        actual = actual.__cause__ or actual.__context__
    return False


class OllamaChat:
    """Mantiene una conversación con un modelo local de Ollama."""

    def __init__(self):
        self.modelo = os.getenv("OLLAMA_MODEL", "qwen3.5:4b").strip()
        self.host = os.getenv("OLLAMA_HOST", "http://localhost:11434").strip()
        self._cliente = None  # se crea con el primer mensaje

    def _mensaje_sin_conexion(self) -> str:
        return (
            f"No pude conectarme a Ollama en {self.host}. Asegúrate de que la app "
            "de Ollama esté abierta (o ejecuta `ollama serve`) e inténtalo de nuevo."
        )

    def _obtener_cliente(self):
        # ChatOllama verifica al crearse que Ollama esté corriendo y que el
        # modelo esté instalado; por eso se crea aquí y no al importar la app.
        if self._cliente is None:
            try:
                self._cliente = ChatOllama(
                    model=self.modelo,
                    base_url=self.host,
                    system_prompt=SYSTEM_PROMPT,
                )
            except ValueError as e:
                raise RuntimeError(
                    f"El modelo '{self.modelo}' no está instalado en Ollama. "
                    f"Ejecuta `ollama pull {self.modelo}` en la terminal."
                ) from e
            except RuntimeError as e:
                raise RuntimeError(self._mensaje_sin_conexion()) from e
        return self._cliente

    async def stream(self, mensaje: str):
        cliente = self._obtener_cliente()
        try:
            # El objeto Chat de chatlas guarda el historial automáticamente.
            respuesta = await cliente.stream_async(mensaje)
            async for trozo in respuesta:
                yield trozo
        except Exception as e:
            if _es_error_de_red(e):
                raise RuntimeError(self._mensaje_sin_conexion()) from e
            raise
