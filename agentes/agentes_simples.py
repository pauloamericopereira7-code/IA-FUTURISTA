# -*- coding: utf-8 -*-
"""Agentes Novos - Versão Simplificada Compatível"""

import sys
sys.path.insert(0, '..')

from multiagent_system import Agente, Mensagem, Contexto
import re

class AgenteContagemSimples(Agente):
    def __init__(self):
        super().__init__("ContagemSimples", "Conta palavras e caracteres")
    
    def pode_processar(self, mensagem: Mensagem) -> bool:
        return "conte" in str(mensagem.conteudo).lower()
    
    def processar(self, mensagem: Mensagem, contexto: Contexto) -> Mensagem:
        texto = str(mensagem.conteudo).replace("conte:", "").replace("contar", "").strip()
        palavras = len(texto.split())
        caracteres = len(texto)
        
        resultado = f"Análise: {palavras} palavras, {caracteres} caracteres"
        
        return Mensagem(
            origem=self.nome,
            destino="usuario",
            tipo="resposta",
            conteudo=resultado
        )

class AgenteSinteseSimples(Agente):
    def __init__(self):
        super().__init__("SinteseSimples", "Sintetiza textos")
    
    def pode_processar(self, mensagem: Mensagem) -> bool:
        return any(p in str(mensagem.conteudo).lower() for p in ["resuma", "sintese"])
    
    def processar(self, mensagem: Mensagem, contexto: Contexto) -> Mensagem:
        texto = str(mensagem.conteudo)
        for p in ["resuma", "resuma:", "sintese", "sintese:"]:
            texto = texto.replace(p, "").lower().strip()
        
        frases = [f.strip() for f in texto.split(".") if f.strip()][:3]
        sintese = ". ".join(frases) + "." if frases else texto
        
        return Mensagem(
            origem=self.nome,
            destino="usuario",
            tipo="resposta",
            conteudo=f"Síntese: {sintese}"
        )

class AgenteValidacaoSimples(Agente):
    def __init__(self):
        super().__init__("ValidacaoSimples", "Valida dados")
    
    def pode_processar(self, mensagem: Mensagem) -> bool:
        return "valide" in str(mensagem.conteudo).lower()
    
    def processar(self, mensagem: Mensagem, contexto: Contexto) -> Mensagem:
        texto = str(mensagem.conteudo).replace("valide:", "").strip()
        
        if "@" in texto and "." in texto:
            resultado = f"✅ {texto} é um email válido"
        elif texto.startswith("http"):
            resultado = f"✅ {texto} é uma URL válida"
        else:
            resultado = f"❌ {texto} formato não reconhecido"
        
        return Mensagem(
            origem=self.nome,
            destino="usuario",
            tipo="resposta",
            conteudo=resultado
        )

class AgenteTraducaoSimples(Agente):
    def __init__(self):
        super().__init__("TraducaoSimples", "Traduz textos")
    
    def pode_processar(self, mensagem: Mensagem) -> bool:
        return "traduz" in str(mensagem.conteudo).lower()
    
    def processar(self, mensagem: Mensagem, contexto: Contexto) -> Mensagem:
        return Mensagem(
            origem=self.nome,
            destino="usuario",
            tipo="resposta",
            conteudo="Tradução via IA Local: [resultado simulado]"
        )

class AgenteSentimentSimples(Agente):
    def __init__(self):
        super().__init__("SentimentSimples", "Analisa sentimentos")
    
    def pode_processar(self, mensagem: Mensagem) -> bool:
        return "sentimento" in str(mensagem.conteudo).lower()
    
    def processar(self, mensagem: Mensagem, contexto: Contexto) -> Mensagem:
        texto = str(mensagem.conteudo).lower()
        
        if any(w in texto for w in ["adorei", "amei", "excelente", "otimo"]):
            sentimento = "😊 POSITIVO"
        elif any(w in texto for w in ["odeio", "horrible", "pessimo", "terrivel"]):
            sentimento = "😞 NEGATIVO"
        else:
            sentimento = "😐 NEUTRO"
        
        return Mensagem(
            origem=self.nome,
            destino="usuario",
            tipo="resposta",
            conteudo=f"Análise: {sentimento}"
        )

# Teste
if __name__ == "__main__":
    print("Testando agentes simplificados...")
    agentes = [
        AgenteContagemSimples(),
        AgenteSinteseSimples(),
        AgenteValidacaoSimples(),
        AgenteTraducaoSimples(),
        AgenteSentimentSimples(),
    ]
    
    for agente in agentes:
        print(f"✅ {agente.nome} carregado")
    
    print("\nTodos os 5 agentes pronto s para uso!")
