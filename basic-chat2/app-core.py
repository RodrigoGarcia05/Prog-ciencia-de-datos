# ------------------------------------------------------------------------------------
# Chatbot básico en Shiny (versión Core) usando Google Gemini.
# Ejecuta:  shiny run --launch-browser app-core.py
# ------------------------------------------------------------------------------------
from shiny import App, ui

from gemini_client import GeminiConRespaldo

app_ui = ui.page_fillable(
    ui.card(
        ui.card_header("Chat con Google Gemini"),
        ui.chat_ui("chat", greeting="¡Hola! ¿En qué puedo ayudarte hoy?", width="100%"),
        style="width:min(680px, 100%)",
        class_="mx-auto",
    ),
    fillable_mobile=True,
    class_="bg-light-subtle",
)


def server(input, output, session):
    gemini = GeminiConRespaldo()
    chat = ui.Chat(id="chat", history=False)

    @chat.on_user_submit
    async def handle_user_input(user_input: str):
        await chat.append_message_stream(gemini.stream(user_input))


app = App(app_ui, server)
