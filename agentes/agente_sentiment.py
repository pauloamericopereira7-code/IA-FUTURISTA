# -*- coding: utf-8 -*-
"""Agente de Sentiment - Análise de Sentimentos e Emoções"""

from multiagent_system import Agente, Mensagem, Contexto
import re

class AgenteSentiment(Agente):
    """Analisa sentimento e emoção de textos"""
    
    def __init__(self):
        super().__init__("Analista de Sentimento", "Analisa sentimento (positivo/negativo/neutro)")
        self.descricao = "Analisa sentimento e emoção de textos"
        self.palavras_chave = ["sentimento", "sentimento de", "qual é o sentimento", "emoção", "emocao"]
        
        # Dicionário de palavras
        self.positivas = [
            "adorei", "amei", "excelente", "ótimo", "incrível", "maravilhoso",
            "perfeito", "fantástico", "lindo", "sensacional", "espetacular",
            "bom", "ótima", "legal", "bacana", "show", "top"
        ]
        
        self.negativas = [
            "odeio", "detestei", "horrível", "péssimo", "terrível", "ruim",
            "chato", "entediante", "decepcionante", "frustrado", "irritado",
            "desastroso", "horroroso", "nojento", "asqueroso", "pior"
        ]
        
        self.neutras = [
            "ok", "normal", "comum", "regular", "médio", "razoável",
            "aceitável", "passável", "neutro"
        ]
    
    def pode_processar(self, msg: Mensagem) -> bool:
        return any(p in msg.conteudo.lower() for p in self.palavras_chave)
    
    def processar(self, msg: Mensagem, ctx: Contexto) -> Mensagem:
        try:
            # Extrair texto
            texto = self._extrair_texto(msg.conteudo)
            
            if not texto:
                return Mensagem(
                    origem=self.nome,
                    conteudo="Por favor, forneça um texto para analisar sentimento.",
                    sucesso=False
                )
            
            # Analisar sentimento
            sentimento, score, detalhes = self._analisar_sentimento(texto)
            
            emoji = {"positivo": "😊", "negativo": "😞", "neutro": "😐"}[sentimento]
            
            resultado = f"""{emoji} **Análise de Sentimento:**

**Texto:** "{texto}"

**Resultado:** {sentimento.upper()}
**Confiança:** {score}%

**Análise:**
{detalhes}"""
            
            return Mensagem(
                origem=self.nome,
                conteudo=resultado,
                sucesso=True,
                meta={
                    "sentimento": sentimento,
                    "score": score
                }
            )
        
        except Exception as e:
            return Mensagem(
                origem=self.nome,
                conteudo=f"Erro ao analisar: {str(e)}",
                sucesso=False,
                erro=True
            )
    
    def _extrair_texto(self, msg: str) -> str:
        """Extrai o texto a analisar"""
        texto = msg
        for palavra in self.palavras_chave:
            texto = re.sub(f"{palavra}:?\\s*", "", texto, flags=re.IGNORECASE)
        return texto.strip()
    
    def _analisar_sentimento(self, texto: str) -> tuple:
        """Analisa e retorna (sentimento, score, detalhes)"""
        texto_lower = texto.lower()
        
        # Contar palavras
        positivas = sum(1 for p in self.positivas if p in texto_lower)
        negativas = sum(1 for p in self.negativas if p in texto_lower)
        neutras = sum(1 for p in self.neutras if p in texto_lower)
        
        total = positivas + negativas + neutras
        
        # Determinar sentimento
        if positivas > negativas and positivas > 0:
            sentimento = "positivo"
            score = min(100, (positivas / max(total, 1)) * 100) if total > 0 else 50
        elif negativas > positivas and negativas > 0:
            sentimento = "negativo"
            score = min(100, (negativas / max(total, 1)) * 100) if total > 0 else 50
        else:
            sentimento = "neutro"
            score = 50
        
        # Criar detalhes
        detalhes = f"""
- Palavras positivas encontradas: {positivas}
- Palavras negativas encontradas: {negativas}
- Palavras neutras encontradas: {neutras}
- Total de indicadores: {total}

**Interpretação:**"""
        
        if sentimento == "positivo":
            detalhes += f"\n✅ O texto expressa sentimento POSITIVO com alta confiança."
        elif sentimento == "negativo":
            detalhes += f"\n❌ O texto expressa sentimento NEGATIVO com alta confiança."
        else:
            detalhes += f"\n➡️  O texto é predominantemente NEUTRO."
        
        return sentimento, int(score), detalhes


if __name__ == "__main__":
    agente = AgenteSentimento()
    
    testes = [
        "Qual é o sentimento: Adorei este produto! Excelente qualidade!",
        "Qual é o sentimento: Horrível, péssimo, não recomendo.",
        "Qual é o sentimento: É um produto normal, nada de especial."
    ]
    
    for teste in testes:
        msg = Mensagem(conteudo=teste)
        resultado = agente.processar(msg, Contexto())
        print(f"\n{resultado.conteudo}\n" + "="*50)
