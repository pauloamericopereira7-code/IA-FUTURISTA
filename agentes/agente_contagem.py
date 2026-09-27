# -*- coding: utf-8 -*-
"""Agente de Contagem - Conta palavras, caracteres, linhas"""

from multiagent_system import Agente, Mensagem, Contexto
import re

class AgenteContagem(Agente):
    """Conta palavras, caracteres, parágrafos, linhas"""
    
    def __init__(self):
        super().__init__("Contador", "Conta palavras, caracteres, linhas e parágrafos")
        self.descricao = "Conta palavras, caracteres, linhas e parágrafos"
        self.palavras_chave = ["conte", "contar", "quantas", "quantos", "contagem"]
    
    def pode_processar(self, msg: Mensagem) -> bool:
        return any(p in msg.conteudo.lower() for p in self.palavras_chave)
    
    def processar(self, msg: Mensagem, ctx: Contexto) -> Mensagem:
        try:
            # Extrair texto (remover comando)
            texto = self._extrair_texto(msg.conteudo)
            
            if not texto:
                return Mensagem(
                    origem=self.nome,
                    conteudo="Por favor, forneça um texto para contar.",
                    sucesso=False
                )
            
            # Contar
            palavras = len(texto.split())
            caracteres = len(texto)
            caracteres_sem_espacos = len(texto.replace(" ", ""))
            linhas = len(texto.strip().split("\n"))
            paragrafos = len([p for p in texto.split("\n\n") if p.strip()])
            frases = len(re.split(r'[.!?]+', texto)) - 1
            
            resultado = f"""📊 **Análise de Contagem:**

📝 **Palavras:** {palavras:,}
🔤 **Caracteres:** {caracteres:,}
🔡 **Caracteres (sem espaços):** {caracteres_sem_espacos:,}
📄 **Linhas:** {linhas}
¶ **Parágrafos:** {paragrafos}
💬 **Frases:** {frases}

**Média:**
- Caracteres por palavra: {caracteres/max(palavras, 1):.1f}
- Palavras por frase: {palavras/max(frases, 1):.1f}"""
            
            return Mensagem(
                origem=self.nome,
                conteudo=resultado,
                sucesso=True,
                meta={
                    "palavras": palavras,
                    "caracteres": caracteres,
                    "linhas": linhas
                }
            )
        
        except Exception as e:
            return Mensagem(
                origem=self.nome,
                conteudo=f"Erro ao contar: {str(e)}",
                sucesso=False,
                erro=True
            )
    
    def _extrair_texto(self, msg: str) -> str:
        """Extrai o texto após os comandos"""
        texto = msg
        for palavra in self.palavras_chave:
            texto = re.sub(f"{palavra}:?\\s*", "", texto, flags=re.IGNORECASE)
        return texto.strip()


if __name__ == "__main__":
    agente = AgenteContagem()
    msg = Mensagem(conteudo="Conte: Este é um texto de teste para verificar a contagem.")
    resultado = agente.processar(msg, Contexto())
    print(resultado.conteudo)
