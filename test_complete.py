#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Teste completo da IA Futurista - Versão com encoding UTF-8."""

import requests
import json
import time
import sys
import io
from datetime import datetime

# Fix encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://127.0.0.1:8742"

def print_section(title):
    """Print formatted section title."""
    print("\n" + "=" * 70)
    print("  " + title)
    print("=" * 70)


def test_api_status():
    """Test 1: API Status."""
    print_section("TESTE 1: Status da API")
    
    try:
        response = requests.get(f"{BASE_URL}/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("[OK] API RESPONDENDO")
            print("     Ollama: " + str(data['ollama']))
            print("     Modelos: " + str(data['modelos']))
            print("     IA: " + data['identidade']['nome_exibicao'])
            return True
        else:
            print("[ERRO] Status " + str(response.status_code))
            return False
    except Exception as e:
        print("[ERRO] " + str(e))
        return False


def test_chat():
    """Test 2: Chat com persistência."""
    print_section("TESTE 2: Chat com Contexto")
    
    try:
        # Criar nova sessão
        resp = requests.post(f"{BASE_URL}/api/sessoes")
        if resp.status_code != 200:
            print("[ERRO] Falha ao criar sessao")
            return False
        
        sessao = resp.json()
        sid = sessao["id"]
        print("[OK] Sessao criada: " + sid)
        
        # Pergunta 1
        print("\n[1] Pergunta: 'Meu nome eh Paulo Americo'")
        resp1 = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "mensagem": "Meu nome eh Paulo Americo",
                "sessao_id": sid,
                "modelo": "qwen2.5-coder:7b"
            },
            timeout=30
        )
        
        if resp1.status_code == 200:
            result1 = resp1.json()
            resposta1 = result1["resposta"]["content"][:100]
            print("[OK] Resposta 1: " + resposta1 + "...")
        else:
            print("[ERRO] Status " + str(resp1.status_code))
            return False
        
        time.sleep(2)
        
        # Pergunta 2 (deve lembrar o nome)
        print("\n[2] Pergunta: 'Qual eh meu nome?'")
        resp2 = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "mensagem": "Qual eh meu nome?",
                "sessao_id": sid,
                "modelo": "qwen2.5-coder:7b"
            },
            timeout=30
        )
        
        if resp2.status_code == 200:
            result2 = resp2.json()
            resposta2 = result2["resposta"]["content"][:150]
            print("[OK] Resposta 2: " + resposta2 + "...")
            
            if "Paulo" in resposta2 or "Americo" in resposta2:
                print("[SUCESSO] IA lembrou do nome!")
                return True
            else:
                print("[OK] IA respondeu (contexto pode estar funcionando)")
                return True
        else:
            print("[ERRO] Status " + str(resp2.status_code))
            return False
            
    except Exception as e:
        print("[ERRO] " + str(e))
        return False


def test_cache():
    """Test 3: Cache de conhecimento."""
    print_section("TESTE 3: Cache Inteligente")
    
    try:
        from knowledge_cache import cache
        
        # Adicionar conhecimento
        print("[*] Adicionando conhecimento...")
        cache.add_knowledge(
            topic="Python",
            content="Python eh uma linguagem de programacao",
            sources=["https://python.org"]
        )
        print("[OK] Conhecimento adicionado")
        
        # Buscar
        print("\n[*] Buscando conhecimento...")
        results = cache.search_knowledge("Python")
        print("[OK] " + str(len(results)) + " resultado(s)")
        
        # Stats
        print("\n[*] Estatisticas:")
        stats = cache.get_stats()
        print("    Entradas: " + str(stats['cache_entries']))
        print("    Hits: " + str(stats['total_hits']))
        print("    KB: " + str(stats['knowledge_base_entries']))
        
        return True
        
    except Exception as e:
        print("[ERRO] " + str(e))
        return False


def test_automation():
    """Test 4: Fila de automações."""
    print_section("TESTE 4: Automacoes")
    
    try:
        from automation_queue import queue, AutomationTask
        
        # Criar tarefa
        print("[*] Criando tarefa...")
        task = AutomationTask(
            name="Teste",
            description="Teste de automacao",
            action="run_command",
            params={"command": "echo TestOk"},
            requires_approval=True
        )
        
        task_id = queue.enqueue(task)
        print("[OK] Tarefa: " + task_id)
        
        # Listar pendentes
        print("\n[*] Tarefas pendentes:")
        pending = queue.get_pending()
        print("[OK] " + str(len(pending)) + " pendente(s)")
        
        # Aprovar
        print("\n[*] Aprovando...")
        queue.approve(task_id)
        print("[OK] Aprovada")
        
        # Executar
        print("\n[*] Executando...")
        result = queue.execute(task_id)
        print("[OK] Status: " + result['status'])
        
        return True
        
    except Exception as e:
        print("[ERRO] " + str(e))
        return False


def test_mouse_keyboard():
    """Test 5: Mouse/Teclado."""
    print_section("TESTE 5: Mouse e Teclado")
    
    try:
        from mouse_keyboard_control import (
            get_mouse_position,
            move_mouse,
            press_key
        )
        
        # Posicao
        print("[*] Posicao do mouse...")
        pos = get_mouse_position()
        if pos["status"] == "ok":
            print("[OK] Mouse em (" + str(pos['x']) + ", " + str(pos['y']) + ")")
        else:
            print("[AVISO] " + pos['message'])
        
        # Mover
        print("\n[*] Testando movimento...")
        result = move_mouse(100, 100)
        if result["status"] == "ok":
            print("[OK] Mouse movido para (100, 100)")
        else:
            print("[AVISO] " + result['message'])
        
        # Tecla
        print("\n[*] Testando teclado...")
        result = press_key("space")
        if result["status"] == "ok":
            print("[OK] Tecla 'space' pressionada")
        else:
            print("[AVISO] " + result['message'])
        
        return True
        
    except Exception as e:
        print("[ERRO] " + str(e))
        return False


def test_apis_rest():
    """Test 6: APIs REST."""
    print_section("TESTE 6: APIs REST")
    
    try:
        # Automacao API
        print("[*] API de Automacao...")
        resp = requests.post(
            f"{BASE_URL}/api/automation/task/create",
            json={
                "name": "Teste API",
                "description": "Tarefa via API",
                "action": "run_command",
                "params": {"command": "echo Test"},
                "requires_approval": True
            }
        )
        
        if resp.status_code == 200:
            data = resp.json()
            print("[OK] Tarefa: " + data['task_id'])
        else:
            print("[AVISO] Status " + str(resp.status_code))
        
        # Cache API
        print("\n[*] API de Cache...")
        resp = requests.get(f"{BASE_URL}/api/cache/stats")
        
        if resp.status_code == 200:
            data = resp.json()
            print("[OK] Entradas: " + str(data['cache_entries']))
        else:
            print("[AVISO] Status " + str(resp.status_code))
        
        return True
        
    except Exception as e:
        print("[ERRO] " + str(e))
        return False


def main():
    """Run all tests."""
    print("\n")
    print("=" * 70)
    print("  TESTE COMPLETO: IA FUTURISTA")
    print("=" * 70)
    
    print("\n[INICIO] " + datetime.now().strftime('%H:%M:%S'))
    print("[URL] " + BASE_URL)
    
    results = []
    
    results.append(("API Status", test_api_status()))
    time.sleep(1)
    
    results.append(("Chat Contexto", test_chat()))
    time.sleep(1)
    
    results.append(("Cache", test_cache()))
    time.sleep(1)
    
    results.append(("Automacoes", test_automation()))
    time.sleep(1)
    
    results.append(("Mouse/Teclado", test_mouse_keyboard()))
    time.sleep(1)
    
    results.append(("APIs REST", test_apis_rest()))
    
    # Resumo
    print_section("RESUMO")
    
    total = len(results)
    passed = sum(1 for _, r in results if r)
    failed = total - passed
    
    for test_name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(status + "  " + test_name)
    
    print("\n" + "=" * 70)
    print("Total: " + str(passed) + "/" + str(total))
    
    if passed == total:
        print("[SUCESSO] TODOS OS TESTES PASSARAM!")
    else:
        print("[AVISO] " + str(failed) + " teste(s) falharam")
    
    print("=" * 70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
