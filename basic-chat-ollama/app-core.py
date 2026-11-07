from shiny import App, ui

from ollama_client import OllamaChat

app_ui = ui.page_fillable(
    ui.card(
        ui.card_header("Chat con qwen3.5:4b (Ollama)"),
        ui.chat_ui("chat", greeting="¡Hola! ¿En qué puedo ayudarte hoy?", width="100%"),
        style="width:min(680px, 100%)",
        class_="mx-auto",
    ),
    fillable_mobile=True,
    class_="bg-light-subtle",
)


def server(input, output, session):
    llm = OllamaChat()
    chat = ui.Chat(id="chat", history=False)

    @chat.on_user_submit
    async def handle_user_input(user_input: str):
        await chat.append_message_stream(llm.stream(user_input))


app = App(app_ui, server)
