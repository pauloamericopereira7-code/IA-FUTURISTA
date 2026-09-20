# -*- coding: utf-8 -*-
"""Interface visual completa — clone Cursor / VS Code para IA Futurista."""

CSS_CURSOR = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

/* Reset Streamlit */
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
.stApp { background: #1e1e1e; color: #cccccc; font-family: 'Segoe UI', sans-serif; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* Barra de título */
.cursor-titlebar {
    background: #323233; height: 35px; display: flex; align-items: center;
    padding: 0 12px; border-bottom: 1px solid #1e1e1e; font-size: 12px; color: #ccc;
}
.cursor-titlebar .title { flex: 1; text-align: center; }
.cursor-titlebar .dot { width: 12px; height: 12px; border-radius: 50%; margin-right: 6px; display: inline-block; }
.dot-r { background: #ff5f57; } .dot-y { background: #febc2e; } .dot-g { background: #28c840; }

/* Layout principal */
.cursor-shell { display: flex; height: calc(100vh - 35px); overflow: hidden; }

/* Activity bar (ícones esquerda) */
.cursor-activity {
    width: 48px; background: #333333; display: flex; flex-direction: column;
    align-items: center; padding-top: 8px; border-right: 1px solid #1e1e1e;
}
.cursor-activity .icon {
    width: 48px; height: 48px; display: flex; align-items: center; justify-content: center;
    font-size: 22px; cursor: pointer; opacity: 0.6; border-left: 2px solid transparent;
}
.cursor-activity .icon.active { opacity: 1; border-left-color: #007acc; }

/* Sidebar painel */
.cursor-sidebar {
    width: 260px; background: #252526; border-right: 1px solid #1e1e1e;
    overflow-y: auto; font-size: 13px;
}
.cursor-sidebar-header {
    padding: 10px 20px 6px; font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.5px; color: #bbbbbb;
}
.cursor-tree-item {
    padding: 3px 8px 3px 20px; cursor: pointer; display: flex; align-items: center; gap: 6px;
}
.cursor-tree-item:hover { background: #2a2d2e; }
.cursor-tree-item.active { background: #37373d; color: #fff; }
.cursor-tree-folder { padding-left: 8px; color: #cccccc; font-weight: 500; }

/* Área central */
.cursor-main { flex: 1; display: flex; flex-direction: column; min-width: 0; }

/* Abas do editor */
.cursor-tabs {
    display: flex; background: #2d2d2d; height: 35px; overflow-x: auto; border-bottom: 1px solid #1e1e1e;
}
.cursor-tab {
    padding: 0 16px; display: flex; align-items: center; gap: 8px; font-size: 13px;
    background: #2d2d2d; color: #969696; border-right: 1px solid #1e1e1e; white-space: nowrap;
}
.cursor-tab.active { background: #1e1e1e; color: #fff; border-top: 1px solid #007acc; }
.cursor-tab .close { opacity: 0.5; font-size: 16px; }

/* Breadcrumb */
.cursor-breadcrumb {
    padding: 4px 16px; font-size: 12px; color: #888; background: #1e1e1e;
    border-bottom: 1px solid #2d2d2d;
}

/* Editor */
.cursor-editor-wrap { flex: 1; overflow: hidden; background: #1e1e1e; }
.cursor-editor-wrap textarea {
    background: #1e1e1e !important; color: #d4d4d4 !important;
    font-family: 'JetBrains Mono', 'Consolas', monospace !important;
    font-size: 14px !important; line-height: 1.5 !important; border: none !important;
}

/* Painel chat direita */
.cursor-chat {
    width: 380px; background: #252526; border-left: 1px solid #1e1e1e;
    display: flex; flex-direction: column;
}
.cursor-chat-header {
    padding: 12px 16px; font-size: 11px; font-weight: 700; letter-spacing: 1px;
    color: #ccc; border-bottom: 1px solid #1e1e1e; display: flex; justify-content: space-between;
}
.cursor-chat-toolbar {
    padding: 8px 12px; display: flex; gap: 6px; flex-wrap: wrap; border-bottom: 1px solid #1e1e1e;
}
.cursor-pill {
    background: #3c3c3c; color: #ccc; padding: 3px 10px; border-radius: 4px;
    font-size: 11px; border: 1px solid #4c4c4c;
}
.cursor-pill.active { background: #007acc; color: #fff; border-color: #007acc; }

/* Mensagens chat */
.cursor-msg-user { background: #2d2d2d; margin: 8px 12px; padding: 10px 12px; border-radius: 6px; font-size: 13px; }
.cursor-msg-ai { margin: 8px 12px; padding: 10px 12px; font-size: 13px; line-height: 1.6; }
.cursor-msg-error { background: #5a1d1d; border: 1px solid #f14c4c; margin: 8px 12px; padding: 10px; border-radius: 6px; font-size: 12px; }

/* Painel inferior */
.cursor-bottom {
    height: 180px; background: #1e1e1e; border-top: 1px solid #007acc;
}
.cursor-bottom-tabs {
    display: flex; background: #252526; height: 30px;
}
.cursor-bottom-tab {
    padding: 0 14px; font-size: 12px; display: flex; align-items: center;
    color: #888; cursor: pointer; border-right: 1px solid #1e1e1e;
}
.cursor-bottom-tab.active { color: #fff; border-bottom: 2px solid #007acc; }
.cursor-terminal {
    padding: 8px 12px; font-family: 'JetBrains Mono', monospace; font-size: 12px;
    color: #cccccc; height: 150px; overflow-y: auto; white-space: pre-wrap;
}

/* Status bar */
.cursor-statusbar {
    height: 22px; background: #007acc; color: #fff; font-size: 12px;
    display: flex; align-items: center; padding: 0 10px; gap: 16px;
}
.cursor-statusbar span { opacity: 0.95; }

/* Atalhos welcome */
.cursor-welcome { padding: 40px; color: #888; }
.cursor-welcome kbd {
    background: #3c3c3c; padding: 2px 8px; border-radius: 3px;
    font-family: monospace; color: #ccc; border: 1px solid #555;
}

/* Streamlit overrides */
.stChatInputContainer { background: #3c3c3c !important; border: 1px solid #007acc !important; }
.stChatInputContainer textarea { color: #fff !important; font-size: 13px !important; }
div[data-testid="stVerticalBlock"] > div { gap: 0 !important; }
.stButton > button {
    background: #0e639c !important; color: #fff !important; border: none !important;
    font-size: 12px !important; padding: 4px 12px !important;
}
.stTextInput input, .stSelectbox div[data-baseweb="select"] {
    background: #3c3c3c !important; color: #ccc !important; font-size: 12px !important;
}
</style>
"""

ATALHOS = [
    ("Abrir Chat", "Ctrl + Alt + I"),
    ("Paleta de Comandos", "Ctrl + Shift + P"),
    ("Buscar em Arquivos", "Ctrl + Shift + F"),
    ("Salvar", "Ctrl + S"),
    ("Executar", "F5"),
]

PAINEL_EXPLORER = "explorer"
PAINEL_BUSCA = "search"
PAINEL_CHAT = "chat"
PAINEL_CONFIG = "config"

def render_titlebar(workspace: str) -> str:
    return f"""
<div class="cursor-titlebar">
  <span><span class="dot dot-r"></span><span class="dot dot-y"></span><span class="dot dot-g"></span></span>
  <span class="title">IA Futurista — {workspace}</span>
  <span style="opacity:0.6">Pro Editor v7.0</span>
</div>
"""

def render_welcome() -> str:
    linhas = "".join(f"<p><kbd>{k}</kbd> &nbsp; {v}</p>" for k, v in ATALHOS)
    return f"""
<div class="cursor-welcome">
  <h2 style="color:#ccc;font-weight:300">IA Futurista</h2>
  <p style="color:#888">Agente Cursor local — sem filtros — português</p>
  <br>{linhas}
</div>
"""

def render_statusbar(ollama_ok: bool, modelo: str, arquivo: str | None, branch: str = "main") -> str:
    status = "Ollama ● Online" if ollama_ok else "Ollama ○ Offline"
    cor = "#007acc" if ollama_ok else "#5a1d1d"
    arq = arquivo or "Sem arquivo aberto"
    return f"""
<div class="cursor-statusbar" style="background:{cor}">
  <span>⎇ {branch}</span>
  <span>{status}</span>
  <span>🤖 {modelo}</span>
  <span style="flex:1"></span>
  <span>{arq}</span>
  <span>UTF-8</span>
  <span>IA Futurista</span>
</div>
"""

def render_tree_html(pastas: list[str], arquivos: list[tuple[str, str]], ativo: str | None) -> str:
    html = '<div class="cursor-sidebar-header">Explorador</div>'
    for pasta in pastas:
        nome = pasta.split("/")[-1] or pasta.split("\\")[-1]
        html += f'<div class="cursor-tree-folder">📁 {nome}</div>'
        for rotulo, caminho in arquivos:
            if not caminho.startswith(pasta):
                continue
            cls = "active" if caminho == ativo else ""
            icone = "🐍" if caminho.endswith(".py") else "📄"
            html += f'<div class="cursor-tree-item {cls}">{icone} {rotulo}</div>'
    return html

def icone_painel(painel: str, atual: str) -> str:
    cls = "active" if painel == atual else ""
    icones = {"explorer": "📁", "search": "🔍", "chat": "💬", "config": "⚙️"}
    return f'<div class="icon {cls}">{icones.get(painel, "•")}</div>'
