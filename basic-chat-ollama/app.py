from shiny.express import ui

from ollama_client import OllamaChat

# Un cliente por sesión (cada pestaña tiene su propia conversación)
llm = OllamaChat()

ui.page_opts(
    title="ChatBot con qwen3.5:4b",
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
    await chat.append_message_stream(llm.stream(user_input))



