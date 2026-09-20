# -*- coding: utf-8 -*-
"""IA Futurista — clone perfeito Cursor Cloud Agent."""

import logging
import time
import uuid

import streamlit as st

import agente as ag
import interface_cloud as cloud
from automation_panel import render_automation_panel

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

st.set_page_config(page_title="IA Futurista — Cloud Agent", layout="wide")
st.markdown(cloud.CSS_CLOUD, unsafe_allow_html=True)
st.markdown(cloud.menubar(), unsafe_allow_html=True)


def _init_session_state():
    """Initialize or verify session state structure."""
    if "sessoes" not in st.session_state:
        sid = str(uuid.uuid4())[:8]
        st.session_state.sessoes = {
            sid: {
                "titulo": "IA Futurista",
                "msgs": [],
                "agente": [],  # Full agent conversation history
                "logs": [],
            }
        }
        st.session_state.sessao_ativa = sid
        logger.info(f"Init session {sid}")

    if "usuario_nome" not in st.session_state:
        st.session_state.usuario_nome = "Paulo Americo"
    if "modo_design" not in st.session_state:
        st.session_state.modo_design = False
    if "modo_cloud" not in st.session_state:
        st.session_state.modo_cloud = True
    if "preview_url" not in st.session_state:
        st.session_state.preview_url = "http://127.0.0.1:8742"
    if "getting_started" not in st.session_state:
        st.session_state.getting_started = 2
    if "motor_modelo" not in st.session_state:
        st.session_state.motor_modelo = None


_init_session_state()

@st.cache_resource(ttl=30)
def _cached_ollama_status():
    """Cache Ollama status for 30 seconds."""
    return ag.ollama_online(), ag.listar_modelos()


sessao = st.session_state.sessoes[st.session_state.sessao_ativa]
ollama_ok, modelos = _cached_ollama_status()
if not modelos:
    modelos = [ag.OLLAMA_MODEL]

# Layout: sidebar | main
col_side, col_main = st.columns([1, 3.2])

with col_side:
    st.markdown('<div class="cloud-sidebar">', unsafe_allow_html=True)

    if st.button("✏️  New Chat", use_container_width=True, key="new_chat"):
        nid = str(uuid.uuid4())[:8]
        st.session_state.sessoes[nid] = {"titulo": "Novo chat", "msgs": [], "agente": [], "logs": []}
        st.session_state.sessao_ativa = nid
        st.rerun()

    if st.button("🔍  Search", use_container_width=True, key="nav_search"):
        st.session_state.nav = "search"
    if st.button("⚡  Automations", use_container_width=True, key="nav_auto"):
        st.session_state.nav = "automations"
    if st.button("🎨  Customize", use_container_width=True, key="nav_custom"):
        st.session_state.nav = "customize"

    st.markdown('<div class="cloud-section-title">Repositories</div>', unsafe_allow_html=True)
    st.caption("No Repo")

    st.markdown('<div class="cloud-section-title">Histórico</div>', unsafe_allow_html=True)
    for sid, s in list(st.session_state.sessoes.items())[::-1][:8]:
        ativo = "● " if sid == st.session_state.sessao_ativa else ""
        label = f"{ativo}{s['titulo'][:28]}"
        if st.button(label, key=f"chat_{sid}", use_container_width=True):
            st.session_state.sessao_ativa = sid
            st.rerun()

    prog = st.session_state.getting_started
    st.markdown(
        f'<div class="cloud-progress">Getting Started <b>{prog}/3</b>'
        f'<div class="cloud-progress-bar"><div class="cloud-progress-fill" style="width:{prog/3*100}%"></div></div></div>',
        unsafe_allow_html=True,
    )
    if st.button("💬 Connect Slack", use_container_width=True):
        st.toast("Slack — configure em futurista/config/slack.json")

    iniciais = "".join(p[0] for p in st.session_state.usuario_nome.split()[:2]).upper()
    st.markdown(
        f'<div class="cloud-user"><div class="cloud-avatar">{iniciais}</div>'
        f'<span>{st.session_state.usuario_nome}</span> ⚙️</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col_main:
    s = st.session_state.sessoes[st.session_state.sessao_ativa]

    # Header
    hc1, hc2, hc3 = st.columns([3, 1, 1])
    hc1.markdown(f"### {s['titulo']}")
    hc2.caption("☁️ Online" if ollama_ok else "⚠️ Offline")
    if hc3.button("IDE ↗", key="open_ide"):
        st.session_state.mostrar_ide = True

    # Área de chat
    chat_container = st.container()
    with chat_container:
        for msg in s["msgs"]:
            if msg["role"] == "user":
                st.markdown(cloud.msg_usuario(msg["content"]), unsafe_allow_html=True)
            else:
                if msg.get("worked"):
                    st.markdown(cloud.worked_badge(msg["worked"]), unsafe_allow_html=True)
                st.markdown(f'<div class="cloud-msg-ai">{msg["content"]}</div>', unsafe_allow_html=True)
                if msg.get("preview"):
                    st.markdown(
                        cloud.preview_card(msg["preview"]["title"], msg["preview"]["desc"], msg["preview"]["url"]),
                        unsafe_allow_html=True,
                    )

    # Toolbar acima do input
    tb1, tb2, tb3 = st.columns([1, 1, 2])
    if tb1.button("Create repo"):
        st.toast("Crie o repositório pelo painel Cursor → Create repo")
    st.session_state.modo_design = tb2.toggle("Design Mode", value=st.session_state.modo_design)

    with tb3:
        modelo_selecionado = st.selectbox(
            "Modelo",
            modelos,
            index=0 if st.session_state.motor_modelo is None else (modelos.index(st.session_state.motor_modelo) if st.session_state.motor_modelo in modelos else 0),
            label_visibility="collapsed",
            key="sel_modelo"
        )
        st.session_state.motor_modelo = modelo_selecionado

    # Input principal
    if prompt := st.chat_input("Send follow-up"):
        # Append to UI messages immediately (optimistic update)
        s["msgs"].append({"role": "user", "content": prompt})
        st.session_state.sessoes[st.session_state.sessao_ativa] = s
        t0 = time.time()

        with st.spinner("Trabalhando..."):
            try:
                if not ollama_ok:
                    raise ConnectionError("Language model unavailable")

                # Pass FULL agent history for context retention
                resposta, logs = ag.rodar_agente(
                    pergunta=prompt,
                    historico_msgs=s["agente"],  # ← Complete agent history
                    placeholder=None,
                    motores=["Google Search API", "DuckDuckGo Engine"],
                    codigo_aberto="",
                    caminho_aberto=None,
                    imagem_b64_val=None,
                    modelo=st.session_state.motor_modelo or ag.OLLAMA_MODEL,
                    max_iteracoes=5,
                )
                
                # CRITICAL: Append to agent history BEFORE rerun
                s["agente"].append({"role": "user", "content": prompt})
                s["agente"].append({"role": "assistant", "content": resposta})
                s["logs"].extend(logs)

                if s["titulo"] == "Novo chat":
                    s["titulo"] = prompt[:40] + ("..." if len(prompt) > 40 else "")

                elapsed = max(1, int(time.time() - t0))
                ai_msg = {
                    "role": "assistant",
                    "content": resposta,
                    "worked": elapsed,
                    "preview": {
                        "title": "IA Futurista",
                        "desc": "Interface Cursor completa — clique Preview se não aparecer na tela.",
                        "url": st.session_state.preview_url,
                    },
                }
                s["msgs"].append(ai_msg)
                st.session_state.getting_started = min(3, st.session_state.getting_started + 1)

                # Persist changes
                st.session_state.sessoes[st.session_state.sessao_ativa] = s
                ag.auto_salvar_codigo(resposta, None)
                
                logger.info(f"Response saved for {st.session_state.sessao_ativa}")
            except Exception as e:
                error_msg = {
                    "role": "assistant",
                    "content": f"**Language model unavailable**\n\n{e}",
                    "worked": max(1, int(time.time() - t0)),
                }
                s["msgs"].append(error_msg)
                st.session_state.sessoes[st.session_state.sessao_ativa] = s
                logger.error(f"Error in rodar_agente: {e}")
        
        st.rerun()

    # Footer bar
    fc1, fc2, fc3, fc4 = st.columns([1, 1, 1, 1])
    fc1.caption("⎇ main")
    fc2.caption("☁️ Cloud" if st.session_state.modo_cloud else "💻 Local")
    fc3.caption(f"🤖 {st.session_state.get('motor_modelo', modelos[0])}")
    fc4.caption("🎤")

# Painel IDE (expansível — editor escuro completo)
if st.session_state.get("mostrar_ide"):
    with st.expander("🖥️ IDE — Editor + Terminal + Agente", expanded=True):
        from app_ide import render as render_ide
        render_ide()

# Painel de Automações
with st.expander("⚙️ Automações", expanded=False):
    render_automation_panel()
