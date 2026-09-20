# -*- coding: utf-8 -*-
"""Subpainel IDE escuro — abre dentro do Cloud Agent via botão IDE."""

import streamlit as st

import agente as ag


def render():
    lista = ag.listar_arquivos()
    if not lista:
        st.info("Nenhum arquivo no workspace.")
        return
    rotulos = [r[0] for r in lista]
    caminhos = [r[1] for r in lista]
    idx = st.selectbox("Arquivo", range(len(rotulos)), format_func=lambda i: rotulos[i], key="ide_file")
    caminho = caminhos[idx]
    with open(caminho, encoding="utf-8", errors="replace") as f:
        cod = f.read()
    editado = st.text_area("Editor", cod, height=300, key="ide_editor")
    c1, c2 = st.columns(2)
    if c1.button("Salvar", key="ide_save"):
        open(caminho, "w", encoding="utf-8").write(editado)
        st.toast("Salvo!")
    if c2.button("Executar", key="ide_run"):
        open(caminho, "w", encoding="utf-8").write(editado)
        ag.executar_programa(caminho)

    cmd = st.text_input("Terminal $", key="ide_term")
    if st.button("Executar comando", key="ide_exec") and cmd:
        st.code(ag.ferramenta_executar_comando(cmd))
