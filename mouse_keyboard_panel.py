# -*- coding: utf-8 -*-
"""Painel de controle de mouse e teclado na UI."""

import streamlit as st
import requests


def render_mouse_keyboard_panel():
    """Render mouse/keyboard control panel."""
    
    st.markdown("### 🖱️ Controle de Mouse e Teclado")
    st.caption("A IA pode controlar seu mouse e teclado. Seja cuidadoso!")
    
    tab1, tab2, tab3, tab4 = st.tabs(
        ["🖱️ Mouse", "⌨️ Teclado", "📸 Screenshot", "🎯 Automação"]
    )

    # TAB 1: Mouse Control
    with tab1:
        st.markdown("#### Controlar Mouse")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Mover para coordenadas:**")
            x = st.number_input("X", value=500, min_value=0, max_value=2560)
            y = st.number_input("Y", value=500, min_value=0, max_value=1440)
            
            if st.button("🖱️ Mover", key="move_mouse", use_container_width=True):
                try:
                    response = requests.post(
                        "http://127.0.0.1:8742/api/mouse_keyboard/move",
                        params={"x": x, "y": y}
                    )
                    if response.status_code == 200:
                        st.success(f"✓ Mouse movido para ({x}, {y})")
                    else:
                        st.error(f"Erro: {response.text}")
                except Exception as e:
                    st.error(f"Erro de conexão: {e}")
        
        with col2:
            st.markdown("**Clicar:**")
            button = st.selectbox(
                "Botão",
                ["left", "right", "middle"],
                key="click_button"
            )
            clicks = st.number_input(
                "Quantas vezes",
                value=1,
                min_value=1,
                max_value=5,
                key="click_count"
            )
            
            if st.button("🖱️ Clicar", key="do_click", use_container_width=True):
                try:
                    response = requests.post(
                        "http://127.0.0.1:8742/api/mouse_keyboard/click",
                        params={"button": button, "clicks": clicks}
                    )
                    if response.status_code == 200:
                        st.success(f"✓ Clique {button} x{clicks}")
                    else:
                        st.error(f"Erro: {response.text}")
                except Exception as e:
                    st.error(f"Erro de conexão: {e}")

    # TAB 2: Keyboard Control
    with tab2:
        st.markdown("#### Controlar Teclado")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Digitar texto:**")
            text = st.text_area(
                "Texto",
                placeholder="Digite o que a IA deve escrever",
                height=80,
                key="type_text"
            )
            interval = st.slider(
                "Intervalo entre caracteres (segundos)",
                0.01,
                0.5,
                0.05,
                key="type_interval"
            )
            
            if st.button("⌨️ Digitar", key="do_type", use_container_width=True):
                if text:
                    try:
                        response = requests.post(
                            "http://127.0.0.1:8742/api/mouse_keyboard/type",
                            params={"text": text, "interval": interval}
                        )
                        if response.status_code == 200:
                            st.success(f"✓ Digitado: {len(text)} caracteres")
                        else:
                            st.error(f"Erro: {response.text}")
                    except Exception as e:
                        st.error(f"Erro de conexão: {e}")
                else:
                    st.warning("Digite algo primeiro")
        
        with col2:
            st.markdown("**Pressionar tecla:")
            key_options = {
                "Enter": "return",
                "Space": "space",
                "Tab": "tab",
                "Escape": "esc",
                "Backspace": "backspace",
                "Delete": "delete",
                "Home": "home",
                "End": "end",
                "Page Up": "pageup",
                "Page Down": "pagedown",
                "Seta Cima": "up",
                "Seta Baixo": "down",
                "Seta Esquerda": "left",
                "Seta Direita": "right",
            }
            
            key_display = st.selectbox(
                "Tecla",
                list(key_options.keys()),
                key="key_select"
            )
            
            if st.button("⌨️ Pressionar", key="do_press", use_container_width=True):
                try:
                    response = requests.post(
                        "http://127.0.0.1:8742/api/mouse_keyboard/key",
                        params={"key": key_options[key_display]}
                    )
                    if response.status_code == 200:
                        st.success(f"✓ Tecla pressionada: {key_display}")
                    else:
                        st.error(f"Erro: {response.text}")
                except Exception as e:
                    st.error(f"Erro de conexão: {e}")

    # TAB 3: Screenshot
    with tab3:
        st.markdown("#### Tirar Screenshot")
        
        st.write("A IA pode tirar screenshots para analisar o que está na tela")
        
        if st.button("📸 Tirar Screenshot", use_container_width=True, key="do_screenshot"):
            try:
                response = requests.post(
                    "http://127.0.0.1:8742/api/mouse_keyboard/screenshot",
                    params={"path": "futurista_screenshot.png"}
                )
                if response.status_code == 200:
                    st.success("✓ Screenshot salvo: futurista_screenshot.png")
                    st.info("Você pode usar para pedir análise à IA")
                else:
                    st.error(f"Erro: {response.text}")
            except Exception as e:
                st.error(f"Erro de conexão: {e}")

    # TAB 4: Automation Examples
    with tab4:
        st.markdown("#### 🎯 Exemplos de Automação")
        
        st.info("Estas são ações que a IA pode fazer automaticamente quando você pedir")
        
        examples = {
            "Abrir Bloco de Notas": {
                "steps": [
                    "Pressionar Windows+R",
                    'Digitar "notepad"',
                    "Pressionar Enter"
                ]
            },
            "Copiar-Colar": {
                "steps": [
                    "Mover para campo de texto",
                    'Digitar "Olá Mundo"',
                    "Selecionar tudo (Ctrl+A)",
                    "Copiar (Ctrl+C)"
                ]
            },
            "Tirar Screenshot": {
                "steps": [
                    "Tirar screenshot (Print Screen)",
                    "Colar em Paint (Ctrl+V)",
                    "Salvar"
                ]
            },
            "Abrir URL no Navegador": {
                "steps": [
                    "Pressionar Ctrl+L (barra de endereço)",
                    "Digitar URL",
                    "Pressionar Enter"
                ]
            }
        }
        
        for name, details in examples.items():
            with st.expander(f"📌 {name}"):
                for step in details["steps"]:
                    st.write(f"→ {step}")
        
        st.warning(
            "⚠️ **CUIDADO**: A IA vai executar EXATAMENTE o que você pedir. "
            "Revise sempre antes de aprovar automações que usam mouse/teclado!"
        )


if __name__ == "__main__":
    render_mouse_keyboard_panel()
