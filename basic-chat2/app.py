# ------------------------------------------------------------------------------------
# Chatbot básico en Shiny (versión Express) usando Google Gemini.
# Ejecuta:  shiny run --launch-browser app.py
# ------------------------------------------------------------------------------------
from shiny.express import ui

from gemini_client import GeminiConRespaldo

# Un cliente por sesión (cada pestaña tiene su propia conversación)
gemini = GeminiConRespaldo()

ui.page_opts(
    title="ChatBot de Rodri Garcia",
    fillable=True,
    fillable_mobile=True,
    class_="bg-light-subtle",
)

chat = ui.Chat(id="chat", history=False)

with ui.card(style="width:min(680px, 100%)", class_="mx-auto"):
    ui.card_header("Chatbot de Rodri")
    chat.ui(greeting="¡Hola! ¿En qué puedo ayudarte hoy?", width="100%")


@chat.on_user_submit
async def handle_user_input(user_input: str):
    await chat.append_message_stream(gemini.stream(user_input))
