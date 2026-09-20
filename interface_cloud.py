# -*- coding: utf-8 -*-
"""Interface Cursor Cloud Agent — clone visual fiel (tema claro)."""

CSS_CLOUD = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden !important; height: 0 !important; }
.stApp {
    background: #f4f3ee !important;
    color: #1a1a1a !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* Menu superior */
.cloud-menubar {
    background: #f4f3ee; border-bottom: 1px solid #e5e4df;
    padding: 6px 16px; font-size: 13px; color: #555; display: flex; gap: 16px;
}
.cloud-menubar span { cursor: pointer; }
.cloud-menubar span:hover { color: #000; }

/* Shell */
.cloud-layout { display: flex; min-height: calc(100vh - 32px); }

/* Sidebar esquerda */
.cloud-sidebar {
    width: 240px; background: #eceae4; border-right: 1px solid #dddcd6;
    padding: 12px 8px; flex-shrink: 0;
}
.cloud-nav-item {
    display: flex; align-items: center; gap: 10px; padding: 8px 12px;
    border-radius: 8px; font-size: 14px; color: #333; cursor: pointer; margin-bottom: 2px;
}
.cloud-nav-item:hover { background: #e0ded8; }
.cloud-nav-item.active { background: #d8d6d0; font-weight: 500; }
.cloud-section-title {
    font-size: 11px; font-weight: 600; color: #888; text-transform: uppercase;
    padding: 16px 12px 6px; letter-spacing: 0.4px;
}
.cloud-chat-item {
    padding: 8px 12px; border-radius: 8px; font-size: 13px; color: #444;
    cursor: pointer; display: flex; justify-content: space-between; align-items: center;
}
.cloud-chat-item:hover { background: #e0ded8; }
.cloud-chat-item.active { background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
.cloud-dot { width: 8px; height: 8px; background: #007aff; border-radius: 50%; }
.cloud-progress {
    margin: 12px; padding: 12px; background: #fff; border-radius: 10px;
    font-size: 12px; color: #666; border: 1px solid #e0ded8;
}
.cloud-progress-bar { height: 4px; background: #e0ded8; border-radius: 2px; margin-top: 8px; }
.cloud-progress-fill { height: 100%; background: #007aff; border-radius: 2px; }
.cloud-slack-btn {
    margin: 8px 12px; padding: 10px; background: #fff; border: 1px solid #e0ded8;
    border-radius: 10px; font-size: 13px; text-align: center; cursor: pointer;
}
.cloud-user {
    position: fixed; bottom: 12px; left: 12px; width: 216px;
    padding: 10px 12px; display: flex; align-items: center; gap: 10px;
    font-size: 13px; color: #333;
}
.cloud-avatar {
    width: 28px; height: 28px; background: linear-gradient(135deg,#667eea,#764ba2);
    border-radius: 50%; color: #fff; display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 600;
}

/* Área principal chat */
.cloud-main { flex: 1; display: flex; flex-direction: column; background: #f4f3ee; min-width: 0; }
.cloud-header {
    padding: 12px 24px; border-bottom: 1px solid #e5e4df; display: flex;
    align-items: center; justify-content: space-between; background: #f4f3ee;
}
.cloud-header h1 { font-size: 15px; font-weight: 600; color: #1a1a1a; margin: 0; }
.cloud-header-actions { display: flex; gap: 8px; align-items: center; }
.cloud-btn-ghost {
    padding: 6px 12px; border: 1px solid #ddd; border-radius: 8px;
    font-size: 13px; background: #fff; color: #333;
}
.cloud-chat-area { flex: 1; overflow-y: auto; padding: 24px 48px; max-width: 820px; margin: 0 auto; width: 100%; }

/* Mensagens */
.cloud-msg-user {
    background: #fff; border: 1px solid #e8e7e2; border-radius: 16px;
    padding: 14px 18px; margin-bottom: 20px; font-size: 15px; line-height: 1.6;
    box-shadow: 0 1px 2px rgba(0,0,0,.04);
}
.cloud-msg-ai { font-size: 15px; line-height: 1.7; color: #1a1a1a; margin-bottom: 16px; }
.cloud-worked {
    font-size: 12px; color: #888; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;
}

/* Preview card */
.cloud-preview {
    background: #fff; border: 1px solid #e0ded8; border-radius: 12px;
    padding: 16px 20px; margin: 16px 0; display: flex; align-items: center;
    justify-content: space-between; box-shadow: 0 2px 8px rgba(0,0,0,.06);
}
.cloud-preview-info h3 { margin: 0 0 4px; font-size: 15px; font-weight: 600; }
.cloud-preview-info p { margin: 0; font-size: 13px; color: #666; }
.cloud-preview-btn {
    background: #1a1a1a; color: #fff; padding: 8px 20px; border-radius: 8px;
    font-size: 13px; font-weight: 500; text-decoration: none; white-space: nowrap;
}
.cloud-preview-btn:hover { background: #333; color: #fff; }

/* Input inferior */
.cloud-input-wrap {
    border-top: 1px solid #e5e4df; padding: 12px 24px 16px; background: #f4f3ee;
}
.cloud-input-toolbar { display: flex; gap: 8px; margin-bottom: 10px; }
.cloud-chip {
    padding: 5px 12px; border: 1px solid #ddd; border-radius: 20px;
    font-size: 12px; background: #fff; color: #444;
}
.cloud-input-box {
    background: #fff; border: 1px solid #ddd; border-radius: 14px;
    padding: 4px 8px; display: flex; align-items: center;
}
.cloud-footer-bar {
    display: flex; justify-content: space-between; align-items: center;
    margin-top: 8px; font-size: 12px; color: #888;
}
.cloud-footer-bar .branch { display: flex; align-items: center; gap: 6px; }

/* Streamlit overrides */
.stChatInputContainer {
    background: transparent !important; border: none !important; padding: 0 !important;
}
.stChatInputContainer textarea {
    background: #fff !important; border: 1px solid #ddd !important;
    border-radius: 12px !important; color: #1a1a1a !important; font-size: 14px !important;
}
.stButton > button[kind="secondary"] {
    background: #fff !important; border: 1px solid #ddd !important; color: #333 !important;
    border-radius: 8px !important; font-size: 13px !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] { border-color: #e0ded8 !important; }
</style>
"""


def menubar() -> str:
    return """
<div class="cloud-menubar">
  <span>File</span><span>Edit</span><span>View</span><span>Help</span>
</div>
"""


def preview_card(titulo: str, descricao: str, url: str) -> str:
    return f"""
<div class="cloud-preview">
  <div class="cloud-preview-info">
    <h3>{titulo}</h3>
    <p>{descricao}</p>
  </div>
  <a class="cloud-preview-btn" href="{url}" target="_blank">Preview</a>
</div>
"""


def msg_usuario(texto: str) -> str:
    return f'<div class="cloud-msg-user">{texto}</div>'


def worked_badge(segundos: int) -> str:
    return f'<div class="cloud-worked">✓ Worked for {segundos}s ▾</div>'
