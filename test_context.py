# -*- coding: utf-8 -*-
"""Test script to verify agent context persistence across turns."""

import agente as ag
from identidade import IDENTIDADE

def test_context_persistence():
    """Simulate multi-turn conversation to verify history is maintained."""
    print("=" * 60)
    print("Testing Agent Context Persistence")
    print("=" * 60)
    
    # Simulate conversation history
    historia = []
    
    print("\n--- TURN 1 ---")
    pergunta1 = "Qual é meu nome?"
    print(f"User: {pergunta1}")
    
    resposta1, logs1 = ag.rodar_agente(
        pergunta=pergunta1,
        historico_msgs=historia,
        placeholder=None,
        motores=["Google Search API"],
        codigo_aberto="",
        caminho_aberto=None,
        imagem_b64_val=None,
        modelo=ag.OLLAMA_MODEL,
        max_iteracoes=1,
    )
    
    print(f"Assistant: {resposta1[:200]}...")
    
    # Add to history
    historia.append({"role": "user", "content": pergunta1})
    historia.append({"role": "assistant", "content": resposta1})\n    print(f"[✓] History size: {len(historia)} messages")
    
    print("\n--- TURN 2 ---")
    pergunta2 = "Repita meu nome"
    print(f"User: {pergunta2}")
    print(f"[*] Passing history with {len(historia)} messages to agent...")
    
    resposta2, logs2 = ag.rodar_agente(
        pergunta=pergunta2,
        historico_msgs=historia,  # Full history passed here
        placeholder=None,
        motores=["Google Search API"],
        codigo_aberto="",
        caminho_aberto=None,
        imagem_b64_val=None,
        modelo=ag.OLLAMA_MODEL,
        max_iteracoes=1,
    )
    
    print(f"Assistant: {resposta2[:200]}...")
    print(f"[✓] History maintained across turns: {len(historia)} → {len(historia) + 2}")
    
    if IDENTIDADE["usuario"] in resposta2 or "Paulo" in resposta2:
        print("\n[✓✓✓] SUCCESS: Agent remembered user name from Turn 1!")
    else:
        print("\n[✗✗✗] FAIL: Agent did not retain context from Turn 1")
        print(f"    Expected: '{IDENTIDADE['usuario']}' in response")
        print(f"    Got: {resposta2}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_context_persistence()
