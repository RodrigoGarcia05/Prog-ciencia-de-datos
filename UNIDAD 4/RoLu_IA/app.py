from shiny.express import ui, input, render
from shiny import reactive, session
import os
import shutil
import time
import logic
import providers
import history as hist

current_chat_id = reactive.Value(None)
is_empty        = reactive.Value(True)


# Borra las imágenes generadas en ejecuciones anteriores
_gen = os.path.join(os.path.dirname(__file__), "www", "gen_images")
shutil.rmtree(_gen, ignore_errors=True)
os.makedirs(_gen, exist_ok=True)

ui.page_opts(
    title=None,
    fillable=True,
    window_title="RoLu IA",
    lang="es"
)
ui.include_css("www/style.css")

ui.head_content(ui.HTML("""
<script>
// ── Sidebar toggle ────────────────────────────────────────────────────────────
function toggleSidebar() {
    const sidebar = document.getElementById('rolu-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const isOpen  = sidebar.classList.contains('sidebar-open');
    if (isOpen) {
        sidebar.classList.remove('sidebar-open');
        overlay.classList.remove('overlay-visible');
    } else {
        sidebar.classList.add('sidebar-open');
        overlay.classList.add('overlay-visible');
    }
}

// ── Toggle búsqueda web ───────────────────────────────────────────────────────
function toggleWebSearch() {
    const btn = document.getElementById('web-search-btn');
    const isOn = btn.classList.toggle('toolbar-btn-active');
    Shiny.setInputValue('web_search', isOn, {priority: 'event'});
}

// ── Modelo selector ───────────────────────────────────────────────────────────
function toggleModelDropdown() {
    const dd = document.getElementById('model-dropdown');
    dd.classList.toggle('model-dd-open');
}

function selectModel(modelId, label, provider) {
    document.getElementById('model-label').textContent    = label;
    document.getElementById('model-provider').textContent = provider;
    Shiny.setInputValue('selected_model', modelId, {priority: 'event'});
    document.getElementById('model-dropdown').classList.remove('model-dd-open');
}

document.addEventListener('click', function(e) {
    const dd      = document.getElementById('model-dropdown');
    const trigger = document.getElementById('model-selector-btn');
    if (dd && trigger && !trigger.contains(e.target) && !dd.contains(e.target)) {
        dd.classList.remove('model-dd-open');
    }
    const cdd      = document.getElementById('config-dropdown');
    const ctrigger = document.getElementById('config-btn');
    if (cdd && ctrigger && !ctrigger.contains(e.target) && !cdd.contains(e.target)) {
        cdd.classList.remove('config-dd-open');
    }
});

// ── Tema ──────────────────────────────────────────────────────────────────────
function toggleConfigDropdown() {
    const dd = document.getElementById('config-dropdown');
    dd.classList.toggle('config-dd-open');
}

function setTheme(theme) {
    const html = document.documentElement;
    if (theme === 'system') {
        const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        html.setAttribute('data-theme', isDark ? 'dark' : 'light');
        localStorage.removeItem('rolu-theme');
    } else {
        html.setAttribute('data-theme', theme);
        localStorage.setItem('rolu-theme', theme);
    }
    updateThemeUI();
    document.getElementById('config-dropdown').classList.remove('config-dd-open');
}

function updateThemeUI() {
    const saved = localStorage.getItem('rolu-theme') || 'system';
    document.querySelectorAll('.theme-btn').forEach(btn => btn.classList.remove('theme-btn-active'));
    const el = document.getElementById('theme-' + saved);
    if (el) el.classList.add('theme-btn-active');
}

(function() {
    const saved = localStorage.getItem('rolu-theme');
    const html  = document.documentElement;
    if (saved) {
        html.setAttribute('data-theme', saved);
    } else {
        const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        html.setAttribute('data-theme', isDark ? 'dark' : 'light');
    }
    window.addEventListener('DOMContentLoaded', updateThemeUI);
})();

// ── CHAT BAR ──────────────────────────────────────────────────────────────────
function sendMessage() {
    const ta = document.getElementById('rolu-textarea');
    if (!ta) return;
    const text = ta.value.trim();
    if (!text) return;

    const origTA  = document.querySelector('shiny-chat-input textarea');
    const origBtn = document.querySelector('shiny-chat-input button.shiny-chat-btn-send');

    if (origTA && origBtn) {
        const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
        setter.call(origTA, text);
        origTA.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertText', data: text }));
        origTA.dispatchEvent(new Event('change', { bubbles: true }));
        setTimeout(() => { origBtn.removeAttribute('disabled'); origBtn.click(); }, 50);
    } else {
        Shiny.setInputValue('chat_user_input', text, { priority: 'event' });
    }

    ta.value = '';
    ta.style.height = 'auto';
    ta.focus();
}

document.addEventListener('DOMContentLoaded', function() {
    const ta = document.getElementById('rolu-textarea');
    if (!ta) return;

    ta.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });

    ta.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
});
</script>
"""))

# ── TOP BAR ───────────────────────────────────────────────────────────────────
ui.HTML("""
<header class="rolu-topbar">
    <div class="topbar-left">
        <button class="topbar-icon-btn" onclick="toggleSidebar()" title="Menú">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="3" y1="6"  x2="21" y2="6"/>
                <line x1="3" y1="12" x2="21" y2="12"/>
                <line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
        </button>
        <div class="topbar-brand">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;">
                <path d="M12 2L3 7V17L12 22L21 17V7L12 2Z"/>
                <path d="M12 22V12"/><path d="M12 12L21 7"/><path d="M12 12L3 7"/>
            </svg>
            ROLU IA
        </div>
    </div>
    <div class="topbar-config-area">
        <button id="config-btn" class="topbar-icon-btn" onclick="toggleConfigDropdown()" title="Configuración">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
        </button>
        <div id="config-dropdown" class="config-dropdown">
            <div class="config-section">
                <div class="config-label">Tema</div>
                <div class="theme-options">
                    <button class="theme-btn" onclick="setTheme('light')" id="theme-light">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
                        Claro
                    </button>
                    <button class="theme-btn" onclick="setTheme('dark')" id="theme-dark">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
                        Oscuro
                    </button>
                    <button class="theme-btn" onclick="setTheme('system')" id="theme-system">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
                        Sistema
                    </button>
                </div>
            </div>
        </div>
    </div>
</header>
""")

# ── SIDEBAR + OVERLAY ─────────────────────────────────────────────────────────
ui.HTML('<div id="sidebar-overlay" class="sidebar-overlay" onclick="toggleSidebar()"></div>')

with ui.div(id="rolu-sidebar", class_="rolu-sidebar"):
    ui.HTML("""
        <div class="sidebar-brand">
            <div class="brand-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;">
                    <path d="M12 2L3 7V17L12 22L21 17V7L12 2Z"/>
                    <path d="M12 22V12"/><path d="M12 12L21 7"/><path d="M12 12L3 7"/>
                </svg>
            </div>
            <div>
                <div class="brand-name">RoLu IA</div>
                <div class="brand-sub">Programacion para Ciencia de Datos</div>
            </div>
        </div>
    """)
    ui.input_action_button("new_chat", "＋  Nuevo Chat", class_="btn-new-chat")
    ui.hr()
    ui.div("🕘 Historial", class_="sidebar-section-title")
    ui.input_text("search_history", None, placeholder="Buscar historial...", width="100%")

    @render.ui
    def chat_history_ui():
        all_chats = hist.get_history()
        query     = (input.search_history() or "").lower()
        active    = current_chat_id.get()
        chats     = [c for c in all_chats if query in c["title"].lower()] if query else all_chats
        if not chats:
            return ui.div(ui.HTML('<div class="history-empty">Sin registros</div>'))
        items = []
        for c in chats:
            is_active = c["id"] == active
            items.append(ui.div(
                ui.div(
                    ui.span(c["title"], class_="history-title"),
                    ui.span(c["created_at"], class_="history-time"),
                    class_="history-meta"
                ),
                ui.div(
                    ui.HTML(
                        f'<button class="history-action" '
                        f'onclick="Shiny.setInputValue(\'edit_chat_id\', \'{c["id"]}\', {{priority:\'event\'}});event.stopPropagation();"'
                        f'title="Editar"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg></button>'
                        f'<button class="history-action" '
                        f'onclick="Shiny.setInputValue(\'delete_chat_id\', \'{c["id"]}\', {{priority:\'event\'}});event.stopPropagation();"'
                        f'title="Eliminar"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg></button>'
                    ),
                    class_="history-actions"
                ),
                class_=f"history-item {'history-item-active' if is_active else ''}",
                onclick=f"Shiny.setInputValue('load_chat_id', '{c['id']}', {{priority:'event'}})"
            ))
        return ui.div(*items, class_="history-list")

    ui.hr()
    ui.div(ui.HTML("© 2026 RoLu IA Lab<br>Desarrollado por Rodrigo Garcia y Luna Prieto"), class_="sidebar-footer")

# ── ÁREA PRINCIPAL ────────────────────────────────────────────────────────────
with ui.div(class_="main-area html-fill-item html-fill-container"):

    @render.ui
    def welcome_ui():
        if not is_empty.get():
            return ui.div()
        return ui.div(
            ui.div(
                ui.HTML("""
                    <div class="welcome-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width:36px;height:36px;">
                            <path d="M12 2L3 7V17L12 22L21 17V7L12 2Z"/>
                            <path d="M12 22V12"/><path d="M12 12L21 7"/><path d="M12 12L3 7"/>
                        </svg>
                    </div>
                    <h2 class="welcome-title">Hola, soy RoLu IA</h2>
                    <p class="welcome-sub">¿En qué puedo ayudarte hoy?</p>
                    <p class="welcome-credits">Desarrollado por Rodrigo Garcia y Luna Prieto</p>
                """),
                class_="welcome-header"
            ),
            ui.div(
                ui.div(
                    ui.HTML("""
                        <div class="suggestion-icon" style="background:#eff6ff;">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
                        </div>
                        <div><div class="suggestion-title">Optimizar Código</div><div class="suggestion-sub">Refactoriza y mejora el rendimiento</div></div>
                    """),
                    class_="suggestion-card",
                    onclick="Shiny.setInputValue('suggestion_prompt', 'Ayúdame a optimizar y refactorizar mi código', {priority:'event'})"
                ),
                ui.div(
                    ui.HTML("""
                        <div class="suggestion-icon" style="background:#fdf4ff;">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#a855f7" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
                        </div>
                        <div><div class="suggestion-title">Explicar Conceptos</div><div class="suggestion-sub">Aprende ciencia de datos paso a paso</div></div>
                    """),
                    class_="suggestion-card",
                    onclick="Shiny.setInputValue('suggestion_prompt', 'Explícame con un ejemplo qué es una regresión lineal', {priority:'event'})"
                ),
                ui.div(
                    ui.HTML("""
                        <div class="suggestion-icon" style="background:#fffbeb;">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                        </div>
                        <div><div class="suggestion-title">Análisis de Datos</div><div class="suggestion-sub">Extrae insights de tus documentos</div></div>
                    """),
                    class_="suggestion-card",
                    onclick="Shiny.setInputValue('suggestion_prompt', 'Ayúdame a analizar y visualizar mis datos', {priority:'event'})"
                ),
                ui.div(
                    ui.HTML("""
                        <div class="suggestion-icon" style="background:#f0fdf4;">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                        </div>
                        <div><div class="suggestion-title">Brainstorming</div><div class="suggestion-sub">Genera ideas para tu próximo proyecto</div></div>
                    """),
                    class_="suggestion-card",
                    onclick="Shiny.setInputValue('suggestion_prompt', 'Necesito ideas creativas para mi próximo proyecto', {priority:'event'})"
                ),
                class_="suggestion-grid"
            ),
            class_="welcome-screen"
        )

    chat = ui.Chat(id="chat")
    chat.ui()

# ── TOOLBAR DEL CHAT ──────────────────────────────────────────────────────────
visible_models = providers.get_visible_models()
default_label  = providers.get_model_label(providers.DEFAULT_MODEL)

def split_label(full_label):
    if "(" in full_label:
        parts = full_label.rsplit("(", 1)
        return parts[0].strip(), parts[1].replace(")", "").strip()
    return full_label, ""

default_name, default_provider = split_label(default_label)

model_options_html = ""
for m in visible_models:
    lbl  = providers.get_model_label(m)
    name, prov = split_label(lbl)
    name_safe = name.replace("'", "\\'")
    prov_safe = prov.replace("'", "\\'")
    model_options_html += f"""
        <div class="model-option" onclick="selectModel('{m}', '{name_safe}', '{prov_safe}')">
            <span class="model-opt-name">{name}</span>
            <span class="model-opt-prov">{prov}</span>
        </div>
    """

ui.HTML(f"""
<div class="chat-toolbar-wrapper">
    <div class="chat-input-slot">
        <textarea id="rolu-textarea" placeholder="Escribe un mensaje..." rows="1"></textarea>
    </div>
    <div class="chat-toolbar">
        <div class="toolbar-model-area">
            <button id="model-selector-btn" class="model-selector-btn" onclick="toggleModelDropdown()">
                <span id="model-label">{default_name}</span>
                <span id="model-provider" class="model-provider-tag">{default_provider}</span>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <polyline points="6 9 12 15 18 9"/>
                </svg>
            </button>
            <div id="model-dropdown" class="model-dropdown">
                {model_options_html}
            </div>
        </div>

        <button id="web-search-btn" class="toolbar-btn" onclick="toggleWebSearch()" title="Búsqueda Web">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="2" y1="12" x2="22" y2="12"/>
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
            </svg>
        </button>

        <div style="flex:1"></div>


        <button id="toolbar-send-btn" title="Enviar" onclick="sendMessage()">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"/>
                <polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
        </button>
    </div>
</div>
""")


# ── HANDLERS ──────────────────────────────────────────────────────────────────
async def handle_ai_response():
    is_empty.set(False)
    messages = list(chat.messages())
    if len(messages) > 10:
        messages = messages[-10:]

    # Estos inputs solo existen tras la primera interacción en el navegador
    try:
        model = input.selected_model() or providers.DEFAULT_MODEL
    except Exception:
        model = providers.DEFAULT_MODEL
    try:
        web_search = bool(input.web_search())
    except Exception:
        web_search = False

    async_gen = logic.stream_chat_response(
        messages=messages,
        model=model,
        web_search_enabled=web_search
    )
    await chat.append_message_stream(async_gen)
    final_msgs = list(chat.messages())
    cid = current_chat_id.get()
    if cid is None:
        cid = str(int(time.time() * 1000))
        current_chat_id.set(cid)
        title = hist.auto_title(final_msgs)
        hist.add_chat(cid, title, final_msgs)
    else:
        hist.update_chat(cid, final_msgs)

@chat.on_user_submit
async def _():
    await handle_ai_response()

@reactive.effect
@reactive.event(input.new_chat)
async def _new_chat():
    current_chat_id.set(None)
    is_empty.set(True)
    await chat.clear_messages()

@reactive.effect
@reactive.event(input.load_chat_id)
async def _load_chat():
    cid = input.load_chat_id()
    if not cid: return
    data = hist.get_chat(cid)
    if not data: return
    current_chat_id.set(cid)
    is_empty.set(False)
    await chat.clear_messages()
    for m in data["messages"]:
        role    = m.get('role', '')    if isinstance(m, dict) else m.role
        content = m.get('content', '') if isinstance(m, dict) else m.content
        await chat.append_message({"role": role, "content": content})

@reactive.effect
@reactive.event(input.delete_chat_id)
async def _delete_chat():
    cid = input.delete_chat_id()
    if not cid: return
    hist.delete_chat(cid)
    if current_chat_id.get() == cid:
        current_chat_id.set(None)
        is_empty.set(True)
        await chat.clear_messages()

@reactive.effect
@reactive.event(input.edit_chat_id)
def _edit_chat():
    cid = input.edit_chat_id()
    if not cid: return
    chat_data = hist.get_chat(cid)
    if not chat_data: return
    m = ui.modal(
        ui.div(
            ui.input_text("new_chat_name", "", value=chat_data["title"], width="100%"),
            ui.input_action_button("save_chat_name", "Guardar Cambios", class_="btn-new-chat"),
            style="display:flex;flex-direction:column;gap:10px;margin-top:10px;"
        ),
        title="Renombrar Chat",
        easy_close=True,
        footer=None
    )
    ui.modal_show(m)

@reactive.effect
@reactive.event(input.save_chat_name)
def _save_chat_name():
    new_name = input.new_chat_name()
    cid = input.edit_chat_id()
    if new_name and cid:
        hist.update_chat_title(cid, new_name)
        ui.modal_remove()

@reactive.effect
@reactive.event(input.suggestion_prompt)
async def _suggestion():
    prompt = input.suggestion_prompt()
    if prompt:
        await chat.append_message({"role": "user", "content": prompt})
        await handle_ai_response()
