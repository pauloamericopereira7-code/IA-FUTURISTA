# -*- coding: utf-8 -*-
"""
EXEMPLO: Agente de Tradução
============================
Este arquivo mostra como adicionar um novo agente à IA Futurista.

Para usar:
1. Copie este arquivo para futurista/agentes/agente_traducao.py
2. Registre em multiagent_system.py
3. Teste: python agentes/agente_traducao.py
"""

from multiagent_system import Agente, Mensagem, Contexto
import re

class AgenteTraducao(Agente):
    """Agente especializado em tradução de textos"""
    
    def __init__(self):
        super().__init__()
        self.nome = "Tradutor"
        self.descricao = "Traduz textos para vários idiomas usando IA"
        self.idiomas_suportados = {
            "inglês": "en",
            "español": "es",
            "francês": "fr",
            "alemão": "de",
            "japonês": "ja",
            "chinês": "zh",
            "russo": "ru",
        }
        self.palavras_chave = [
            "traduz", "traduzir", "tradução", "translate",
            "para inglês", "para espanhol", "para francês"
        ]
    
    def pode_processar(self, msg: Mensagem) -> bool:
        """Verifica se a mensagem é uma solicitação de tradução"""
        conteudo_lower = msg.conteudo.lower()
        
        # Verificar palavras-chave
        tem_palavra_chave = any(
            palavra in conteudo_lower 
            for palavra in self.palavras_chave
        )
        
        # Verificar idiomas mencionados
        tem_idioma = any(
            idioma in conteudo_lower 
            for idioma in self.idiomas_suportados.keys()
        )
        
        return tem_palavra_chave or tem_idioma
    
    def processar(self, msg: Mensagem, ctx: Contexto) -> Mensagem:
        """Processa a solicitação de tradução"""
        try:
            # 1. Extrair idioma alvo
            idioma_alvo = self._extrair_idioma(msg.conteudo)
            
            # 2. Extrair texto a traduzir
            texto = self._extrair_texto(msg.conteudo)
            
            if not texto:
                return Mensagem(
                    agente=self.nome,
                    conteudo="Por favor, forneça o texto que deseja traduzir.",
                    sucesso=False
                )
            
            # 3. Chamar LLM para tradução
            prompt = f"""Você é um tradutor profissional. Traduza o seguinte texto para {idioma_alvo}:

Texto original:
{texto}

Apenas forneça a tradução, sem explicações adicionais."""
            
            resposta = self._chamar_llm(prompt, ctx)
            
            return Mensagem(
                agente=self.nome,
                conteudo=f"**Tradução para {idioma_alvo}:**\n\n{resposta}",
                sucesso=True,
                meta={
                    "idioma_alvo": idioma_alvo,
                    "texto_original_length": len(texto),
                    "traducao_length": len(resposta)
                }
            )
        
        except Exception as e:
            return Mensagem(
                agente=self.nome,
                conteudo=f"Erro ao traduzir: {str(e)}",
                sucesso=False,
                erro=True
            )
    
    def _extrair_idioma(self, texto: str) -> str:
        """Extrai o idioma alvo do texto"""
        texto_lower = texto.lower()
        
        # Procurar por padrões como "para inglês", "em espanhol"
        for idioma, codigo in self.idiomas_suportados.items():
            if idioma in texto_lower or f"para {idioma}" in texto_lower:
                return idioma
        
        # Padrão: "para [idioma]"
        match = re.search(r'para\s+(\w+)', texto_lower)
        if match:
            idioma = match.group(1)
            if idioma in self.idiomas_suportados:
                return idioma
        
        # Default: inglês
        return "inglês"
    
    def _extrair_texto(self, texto: str) -> str:
        """Extrai o texto a ser traduzido"""
        # Remove palavras-chave de tradução
        resultado = texto
        
        for palavra in self.palavras_chave:
            resultado = resultado.replace(palavra, "", 1)
        
        # Remove "para [idioma]"
        resultado = re.sub(r'para\s+\w+', '', resultado, flags=re.IGNORECASE)
        
        # Limpa espaços extras
        resultado = resultado.strip()
        
        return resultado if resultado else None
    
    def _chamar_llm(self, prompt: str, ctx: Contexto) -> str:
        """Chama o modelo LLM para traduzir"""
        # Aqui você chamaria seu agente/modelo
        # Por enquanto, simulamos
        import time
        
        # Simular chamada LLM (remover em produção)
        time.sleep(0.5)
        return f"[Tradução simulada]\n{prompt[:100]}..."
    
    def obter_metricas(self) -> dict:
        """Retorna métricas do agente"""
        return {
            "nome": self.nome,
            "execucoes": self.metricas_internas.get("execucoes", 0),
            "sucesso": self.metricas_internas.get("sucesso", 0),
            "idiomas_suportados": len(self.idiomas_suportados),
            "tempo_medio": self.metricas_internas.get("tempo_medio", 0)
        }


# ============================================================================
# TESTES
# ============================================================================

if __name__ == "__main__":
    print("🧪 Testando AgenteTraducao...")
    
    agente = AgenteTraducao()
    
    # Teste 1: Pode processar?
    msg1 = Mensagem(conteudo="Traduz para inglês: Olá, como vai?")
    print(f"\n✅ Pode processar: {agente.pode_processar(msg1)}")
    
    # Teste 2: Extração de idioma
    texto_teste = "Traduz para francês: Isso é um teste"
    idioma = agente._extrair_idioma(texto_teste)
    print(f"✅ Idioma extraído: {idioma}")
    
    # Teste 3: Extração de texto
    texto_extraido = agente._extrair_texto(texto_teste)
    print(f"✅ Texto extraído: {texto_extraido}")
    
    # Teste 4: Processar mensagem completa
    ctx = Contexto()
    resultado = agente.processar(msg1, ctx)
    print(f"✅ Resultado: {resultado.conteudo[:100]}...")
    print(f"✅ Sucesso: {resultado.sucesso}")
    
    print("\n🎉 Testes completos!")
