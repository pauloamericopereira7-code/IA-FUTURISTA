# -*- coding: utf-8 -*-
"""Painel de automações para Streamlit UI."""

import streamlit as st
import requests
import json
from datetime import datetime

from automation_queue import queue, AutomationTask, TaskStatus
from knowledge_cache import cache


def render_automation_panel():
    """Render automation management panel in Streamlit."""
    st.markdown("### ⚙️ Central de Automações")
    
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 Fila", "🚀 Executar", "📊 Histórico", "💾 Cache"]
    )

    # TAB 1: Fila de Aprovações
    with tab1:
        st.markdown("#### Tarefas Aguardando Aprovação")
        pending = queue.get_pending()
        
        if not pending:
            st.info("✓ Nenhuma tarefa aguardando aprovação")
        else:
            for task in pending:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{task.name}**")
                        st.caption(task.description)
                        with st.expander("Detalhes técnicos"):
                            st.json({
                                "action": task.action,
                                "params": task.params,
                                "created": task.created_at,
                            })
                    
                    with col2:
                        if st.button("✓ Aprovar", key=f"approve_{task.id}"):
                            queue.approve(task.id)
                            st.success(f"Tarefa {task.id} aprovada!")
                            st.rerun()
                        
                        if st.button("✗ Rejeitar", key=f"reject_{task.id}"):
                            queue.reject(task.id, "Rejeitado pelo usuário")
                            st.info(f"Tarefa {task.id} rejeitada")
                            st.rerun()

    # TAB 2: Criar e Executar
    with tab2:
        st.markdown("#### Criar Nova Automação")
        
        with st.form("automation_form", border=False):
            name = st.text_input("Nome da tarefa", placeholder="ex: Backup de arquivos")
            description = st.text_area("Descrição", placeholder="O que essa tarefa faz?")
            
            action = st.selectbox(
                "Tipo de ação",
                ["run_command", "run_script", "write_file", "scrape_web"]
            )
            
            # Parâmetros baseados no tipo de ação
            params = {}
            if action == "run_command":
                params["command"] = st.text_input(
                    "Comando",
                    placeholder="ex: dir /s"
                )
            elif action == "run_script":
                params["script"] = st.text_area(
                    "Código Python",
                    placeholder="print('Hello')"
                )
            elif action == "write_file":
                params["path"] = st.text_input("Caminho do arquivo")
                params["content"] = st.text_area("Conteúdo")
            elif action == "scrape_web":
                params["url"] = st.text_input("URL")
                params["selector"] = st.text_input("CSS Selector", value="body")
            
            requires_approval = st.toggle(
                "Requer aprovação",
                value=True,
                help="Tarefa aguarda confirmação antes de executar"
            )
            
            submitted = st.form_submit_button("📤 Criar Tarefa", use_container_width=True)
            
            if submitted and name and action:
                task = AutomationTask(
                    name=name,
                    description=description,
                    action=action,
                    params=params,
                    requires_approval=requires_approval,
                )
                task_id = queue.enqueue(task)
                
                if requires_approval:
                    st.warning(f"✋ Tarefa criada (ID: {task_id}). Aguardando aprovação...")
                else:
                    result = queue.execute(task_id)
                    st.success(f"✓ Tarefa executada: {result.get('result', 'OK')}")

    # TAB 3: Histórico
    with tab3:
        st.markdown("#### Histórico de Execuções")
        
        history = queue.get_history(limit=30)
        
        if not history:
            st.info("Nenhuma tarefa executada ainda")
        else:
            # Filtro por status
            status_filter = st.multiselect(
                "Filtrar por status",
                ["pending", "approved", "running", "completed", "failed", "rejected"],
                default=["completed", "failed"],
            )
            
            filtered = [
                h for h in history
                if h["status"] in status_filter
            ]
            
            for task_dict in filtered:
                status_emoji = {
                    "pending": "⏳",
                    "approved": "👍",
                    "running": "🔄",
                    "completed": "✅",
                    "failed": "❌",
                    "rejected": "🚫",
                }
                
                emoji = status_emoji.get(task_dict["status"], "❓")
                
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(
                            f"{emoji} **{task_dict['name']}**"
                        )
                        st.caption(f"ID: {task_dict['id']} | "
                                   f"Criada: {task_dict['created_at'][:10]}")
                        
                        if task_dict.get("result"):
                            st.success(f"📌 {task_dict['result'][:100]}")
                        if task_dict.get("error"):
                            st.error(f"⚠️ {task_dict['error'][:100]}")
                    
                    with col2:
                        st.metric(
                            "Tempo",
                            "✓" if task_dict["status"] == "completed" else "...",
                        )

    # TAB 4: Cache de Conhecimento
    with tab4:
        st.markdown("#### 💾 Cache Inteligente")
        
        stats = cache.get_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Entradas em Cache", stats["cache_entries"])
        col2.metric("Total de Hits", stats["total_hits"])
        col3.metric("Base de Conhecimento", stats["knowledge_base_entries"])
        col4.metric("Tamanho", f"{stats['cache_size_mb']:.2f} MB")
        
        st.divider()
        
        with st.form("cache_manage"):
            st.markdown("**Gerenciar Cache**")
            
            action = st.radio(
                "Ação",
                ["Limpar tudo", "Adicionar conhecimento", "Scrape web"],
                horizontal=True,
            )
            
            if action == "Limpar tudo":
                if st.form_submit_button("🗑️ Limpar Cache", use_container_width=True):
                    import os
                    if os.path.exists(cache.db_path):
                        os.remove(cache.db_path)
                    cache._init_db()
                    st.success("✓ Cache limpo")
                    st.rerun()
            
            elif action == "Adicionar conhecimento":
                topic = st.text_input("Tópico")
                content = st.text_area("Conteúdo")
                sources = st.text_input("Fontes (separadas por vírgula)")
                
                if st.form_submit_button("💾 Adicionar", use_container_width=True):
                    cache.add_knowledge(
                        topic,
                        content,
                        sources.split(",") if sources else []
                    )
                    st.success(f"✓ Conhecimento adicionado: {topic}")
            
            elif action == "Scrape web":
                url = st.text_input("URL para scrape")
                selector = st.text_input("CSS Selector", value="body")
                ttl = st.slider("TTL (horas)", 1, 168, 24)
                
                if st.form_submit_button("🌐 Scrape", use_container_width=True):
                    result = cache.scrape_safely(url, selector, ttl)
                    if result:
                        st.success(f"✓ Scraped {len(result['content'])} caracteres")
                        st.code(result["content"][:500])
                    else:
                        st.error("Falha ao fazer scrape")


if __name__ == "__main__":
    render_automation_panel()
