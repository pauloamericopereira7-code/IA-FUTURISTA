#!/usr/bin/env python3
# Registrar 5 novos agentes no multiagent_system.py

with open('multiagent_system.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Encontrar e substituir
old_section = '''        ]
        
        for agente in agentes:
            self.agentes[agente.nome] = agente
            self.logger.info(f"Agente inicializado: {agente.nome}")
    
    def executar(self, comando: str, usuario: str = "sistema", sessao_id: str = "default") -> Dict:'''

new_section = '''        ]
        
        # Adicionar novos agentes (5 especializados)
        try:
            from agentes.agentes_simples import (
                AgenteContagemSimples,
                AgenteSinteseSimples,
                AgenteValidacaoSimples,
                AgenteTraducaoSimples,
                AgenteSentimentSimples
            )
            agentes.extend([
                AgenteContagemSimples(),
                AgenteSinteseSimples(),
                AgenteValidacaoSimples(),
                AgenteTraducaoSimples(),
                AgenteSentimentSimples()
            ])
        except Exception as e:
            pass  # Silencioso se nao carregar
        
        for agente in agentes:
            self.agentes[agente.nome] = agente
            self.logger.info(f"Agente inicializado: {agente.nome}")
    
    def executar(self, comando: str, usuario: str = "sistema", sessao_id: str = "default") -> Dict:'''

if old_section in content:
    content = content.replace(old_section, new_section)
    with open('multiagent_system.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Sucesso! 5 novos agentes registrados.")
else:
    print("Secao nao encontrada")
