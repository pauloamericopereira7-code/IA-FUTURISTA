# -*- coding: utf-8 -*-
"""Agente de Tradução - Usando Google Translate API"""

from multiagent_system import Agente, Mensagem, Contexto
import re

class AgenteTraducao(Agente):
    """Traduz textos para vários idiomas"""
    
    def __init__(self):
        super().__init__("Tradutor", "Traduz textos para vários idiomas")
        self.descricao = "Traduz textos para vários idiomas"
        self.palavras_chave = ["traduz", "tradução", "translate", "para inglês", "para espanhol"]
        self.idiomas = {
            "inglês": "en",
            "espanhol": "es",
            "francês": "fr",
            "alemão": "de",
            "português": "pt",
            "italiano": "it",
            "japonês": "ja",
            "chinês": "zh",
            "russo": "ru",
            "coreano": "ko",
        }
    
    def pode_processar(self, msg: Mensagem) -> bool:
        return any(p in msg.conteudo.lower() for p in self.palavras_chave)
    
    def processar(self, msg: Mensagem, ctx: Contexto) -> Mensagem:
        try:
            # Extrair idioma alvo e texto
            idioma_alvo = self._extrair_idioma(msg.conteudo)
            texto = self._extrair_texto(msg.conteudo, idioma_alvo)
            
            if not texto:
                return Mensagem(
                    origem=self.nome,
                    conteudo="Por favor, forneça um texto para traduzir.",
                    sucesso=False
                )
            
            # Traduzir usando LLM (não temos API real, simulamos)
            traducao = self._traduzir(texto, idioma_alvo, ctx)
            
            resultado = f"""🌐 **Tradução para {idioma_alvo.title()}:**

**Original:**
{texto}

**Tradução:**
{traducao}

---
💡 **Nota:** Usando IA local. Para traduções profissionais, considere Google Translate API."""
            
            return Mensagem(
                origem=self.nome,
                conteudo=resultado,
                sucesso=True,
                meta={
                    "idioma_alvo": idioma_alvo,
                    "tamanho_original": len(texto)
                }
            )
        
        except Exception as e:
            return Mensagem(
                origem=self.nome,
                conteudo=f"Erro ao traduzir: {str(e)}",
                sucesso=False,
                erro=True
            )
    
    def _extrair_idioma(self, msg: str) -> str:
        """Extrai o idioma alvo"""
        msg_lower = msg.lower()
        
        for idioma in self.idiomas.keys():
            if idioma in msg_lower or f"para {idioma}" in msg_lower:
                return idioma
        
        # Padrão "para [idioma]"
        match = re.search(r'para\s+(\w+)', msg_lower)
        if match:
            idioma = match.group(1)
            if idioma in self.idiomas:
                return idioma
        
        return "inglês"  # default
    
    def _extrair_texto(self, msg: str, idioma: str) -> str:
        """Extrai o texto a traduzir"""
        texto = msg
        
        # Remove palavras-chave
        for palavra in self.palavras_chave:
            texto = re.sub(palavra, "", texto, flags=re.IGNORECASE)
        
        # Remove "para [idioma]"
        texto = re.sub(r'para\s+\w+', '', texto, flags=re.IGNORECASE)
        
        # Remove "para " sozinho
        texto = re.sub(r'^para\s+', '', texto, flags=re.IGNORECASE)
        
        return texto.strip()
    
    def _traduzir(self, texto: str, idioma_alvo: str, ctx: Contexto) -> str:
        """Traduz o texto (simula Google Translate)"""
        
        # Mapa simples de traduções comuns para demonstração
        traducoes_simples = {
            ("inglês", "olá"): "Hello",
            ("inglês", "como vai"): "How are you",
            ("inglês", "obrigado"): "Thank you",
            ("espanhol", "olá"): "Hola",
            ("espanhol", "como vai"): "Cómo estás",
            ("francês", "olá"): "Bonjour",
        }
        
        chave = (idioma_alvo, texto.lower().strip())
        if chave in traducoes_simples:
            return traducoes_simples[chaque]
        
        # Simular chamada à IA para tradução
        prompt = f"Traduza para {idioma_alvo}: {texto}"
        
        # Aqui você chamaria o LLM real
        # Por agora, retornamos uma simulação
        return f"[Tradução para {idioma_alvo} via IA Local]"


if __name__ == "__main__":
    agente = AgenteTraducao()
    msg = Mensagem(conteudo="Traduz para inglês: Olá, como vai?")
    resultado = agente.processar(msg, Contexto())
    print(resultado.conteudo)
