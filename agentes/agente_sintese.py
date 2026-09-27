# -*- coding: utf-8 -*-
"""Agente de Síntese - Resume textos de forma inteligente"""

from multiagent_system import Agente, Mensagem, Contexto
import re

class AgenteSintese(Agente):
    """Resume textos longos mantendo ideias principais"""
    
    def __init__(self):
        super().__init__("Sintetizador", "Resume textos longos preservando a essência")
        self.descricao = "Resume textos longos preservando a essência"
        self.palavras_chave = ["sintetize", "resuma", "resumo", "síntese", "sintetiza"]
    
    def pode_processar(self, msg: Mensagem) -> bool:
        return any(p in msg.conteudo.lower() for p in self.palavras_chave)
    
    def processar(self, msg: Mensagem, ctx: Contexto) -> Mensagem:
        try:
            # Extrair texto
            texto = self._extrair_texto(msg.conteudo)
            
            if not texto or len(texto) < 50:
                return Mensagem(
                    origem=self.nome,
                    conteudo="Texto muito curto para sintetizar. Forneça um texto com pelo menos 50 caracteres.",
                    sucesso=False
                )
            
            # Extrair frases principais
            frases = self._extrair_frases(texto)
            
            # Criar síntese
            sintese = self._criar_sintese(frases)
            
            # Calcular taxa de compressão
            taxa = (len(sintese) / len(texto)) * 100 if texto else 0
            
            resultado = f"""📌 **Síntese do Texto:**

{sintese}

---
📊 **Estatísticas:**
- Texto original: {len(texto)} caracteres
- Síntese: {len(sintese)} caracteres
- Compressão: {taxa:.1f}%"""
            
            return Mensagem(
                origem=self.nome,
                conteudo=resultado,
                sucesso=True,
                meta={
                    "taxa_compressao": taxa,
                    "frases_originais": len(frases)
                }
            )
        
        except Exception as e:
            return Mensagem(
                origem=self.nome,
                conteudo=f"Erro ao sintetizar: {str(e)}",
                sucesso=False,
                erro=True
            )
    
    def _extrair_texto(self, msg: str) -> str:
        """Extrai o texto após os comandos"""
        texto = msg
        for palavra in self.palavras_chave:
            texto = re.sub(f"{palavra}:?\\s*", "", texto, flags=re.IGNORECASE)
        return texto.strip()
    
    def _extrair_frases(self, texto: str) -> list:
        """Divide o texto em frases"""
        frases = re.split(r'[.!?]+', texto)
        return [f.strip() for f in frases if f.strip()]
    
    def _criar_sintese(self, frases: list) -> str:
        """Cria síntese com as 3 primeiras frases principais"""
        if len(frases) <= 3:
            return ". ".join(frases) + "."
        
        # Pegar as 3 frases mais importantes (primeiras)
        principais = frases[:3]
        sintese = ". ".join(principais) + "."
        
        return sintese


if __name__ == "__main__":
    agente = AgenteSintese()
    texto_longo = """A inteligência artificial é um campo fascinante que está transformando 
    o mundo. Muitas empresas estão investindo em IA para melhorar seus produtos. 
    A tecnologia de machine learning permite que computadores aprendam com dados. 
    Isso abre novas possibilidades para automação e análise."""
    
    msg = Mensagem(conteudo=f"Resuma: {texto_longo}")
    resultado = agente.processar(msg, Contexto())
    print(resultado.conteudo)
