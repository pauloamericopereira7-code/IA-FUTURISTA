#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para integrar os 5 novos agentes ao multiagent_system.py
Execute: python integrar_agentes.py
"""

import os
from pathlib import Path

def integrar_agentes():
    """Integra os 5 novos agentes"""
    
    caminho = Path(__file__).parent / "multiagent_system.py"
    
    # Ler arquivo
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Adicionar métodos de factory
    novos_metodos = '''
    def _criar_agente_contagem(self):
        """Factory para criar agente de contagem"""
        try:
            from agentes.agente_contagem import AgenteContagem
            return AgenteContagem()
        except ImportError as e:
            self.logger.warning(f"Agente de Contagem não pode ser carregado: {e}")
            return None

    def _criar_agente_sintese(self):
        """Factory para criar agente de síntese"""
        try:
            from agentes.agente_sintese import AgenteSintese
            return AgenteSintese()
        except ImportError as e:
            self.logger.warning(f"Agente de Síntese não pode ser carregado: {e}")
            return None

    def _criar_agente_validacao(self):
        """Factory para criar agente de validação"""
        try:
            from agentes.agente_validacao import AgenteValidacao
            return AgenteValidacao()
        except ImportError as e:
            self.logger.warning(f"Agente de Validação não pode ser carregado: {e}")
            return None

    def _criar_agente_traducao(self):
        """Factory para criar agente de tradução"""
        try:
            from agentes.agente_traducao import AgenteTraducao
            return AgenteTraducao()
        except ImportError as e:
            self.logger.warning(f"Agente de Tradução não pode ser carregado: {e}")
            return None

    def _criar_agente_sentiment(self):
        """Factory para criar agente de sentiment"""
        try:
            from agentes.agente_sentiment import AgenteSentiment
            return AgenteSentiment()
        except ImportError as e:
            self.logger.warning(f"Agente de Sentiment não pode ser carregado: {e}")
            return None
'''
    
    # Verificar se já foram adicionados
    if '_criar_agente_contagem' in conteudo:
        print("✅ Agentes já foram integrados!")
        return
    
    # Adicionar os novos métodos antes de obter_status
    marca = '    def obter_status(self)'
    if marca in conteudo:
        conteudo = conteudo.replace(marca, novos_metodos + '\n' + marca)
    
    # Modificar _inicializar_agentes para adicionar novos agentes
    lista_antiga = '''        agentes = [
            Interpretador(),
            NucleoTexto(),
            MotorProgramacao(),
            MotorPesquisa(),
            GestorArquivos(),
            MotorVisual(),
            Verificador(),
            GeradorResposta(),
            GestorErros(),
        ]'''
    
    lista_nova = '''        agentes = [
            Interpretador(),
            NucleoTexto(),
            MotorProgramacao(),
            MotorPesquisa(),
            GestorArquivos(),
            MotorVisual(),
            Verificador(),
            GeradorResposta(),
            GestorErros(),
            # Novos agentes
            self._criar_agente_contagem(),
            self._criar_agente_sintese(),
            self._criar_agente_validacao(),
            self._criar_agente_traducao(),
            self._criar_agente_sentiment(),
        ]'''
    
    conteudo = conteudo.replace(lista_antiga, lista_nova)
    
    # Modificar o loop de inicialização
    loop_antigo = '''        for agente in agentes:
            self.agentes[agente.nome] = agente
            self.logger.info(f"Agente inicializado: {agente.nome}")'''
    
    loop_novo = '''        for agente in agentes:
            if agente:  # Verificar se não é None
                self.agentes[agente.nome] = agente
                self.logger.info(f"Agente inicializado: {agente.nome}")'''
    
    conteudo = conteudo.replace(loop_antigo, loop_novo)
    
    # Salvar arquivo
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print("✅ Integração completada!")
    print(f"📝 Arquivo modificado: {caminho}")
    print("\n📊 Novos agentes adicionados:")
    print("  1. ✅ AgenteContagem")
    print("  2. ✅ AgenteSintese")
    print("  3. ✅ AgenteValidacao")
    print("  4. ✅ AgenteTraducao")
    print("  5. ✅ AgenteSentiment")

if __name__ == "__main__":
    print("🔧 Iniciando integração de novos agentes...\n")
    integrar_agentes()
    print("\n✨ Pronto! Teste com: python multiagent_system.py")
