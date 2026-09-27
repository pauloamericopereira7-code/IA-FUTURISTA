# -*- coding: utf-8 -*-
"""Agente de Validação - Valida email, CPF, URL, etc"""

from multiagent_system import Agente, Mensagem, Contexto
import re

class AgenteValidacao(Agente):
    """Valida vários tipos de dados"""
    
    def __init__(self):
        super().__init__("Validador", "Valida emails, URLs, CPF, telefone, etc")
        self.descricao = "Valida vários tipos de dados"
        self.palavras_chave = ["valide", "valida", "validação", "é válido", "é valida"]
    
    def pode_processar(self, msg: Mensagem) -> bool:
        return any(p in msg.conteudo.lower() for p in self.palavras_chave)
    
    def processar(self, msg: Mensagem, ctx: Contexto) -> Mensagem:
        try:
            # Extrair texto
            texto = self._extrair_texto(msg.conteudo)
            
            if not texto:
                return Mensagem(
                    origem=self.nome,
                    conteudo="Por favor, forneça um valor para validar.",
                    sucesso=False
                )
            
            # Determinar tipo e validar
            tipo, eh_valido, detalhes = self._validar(texto)
            
            status = "✅ VÁLIDO" if eh_valido else "❌ INVÁLIDO"
            
            resultado = f"""🔍 **Resultado da Validação:**

**Tipo:** {tipo}
**Status:** {status}

**Detalhes:**
{detalhes}"""
            
            return Mensagem(
                origem=self.nome,
                conteudo=resultado,
                sucesso=True,
                meta={
                    "tipo": tipo,
                    "valido": eh_valido
                }
            )
        
        except Exception as e:
            return Mensagem(
                origem=self.nome,
                conteudo=f"Erro ao validar: {str(e)}",
                sucesso=False,
                erro=True
            )
    
    def _extrair_texto(self, msg: str) -> str:
        """Extrai o valor a validar"""
        texto = msg
        for palavra in self.palavras_chave:
            texto = re.sub(f"{palavra}:?\\s*", "", texto, flags=re.IGNORECASE)
        return texto.strip()
    
    def _validar(self, valor: str) -> tuple:
        """Valida e retorna (tipo, é_válido, detalhes)"""
        valor = valor.strip()
        
        # Email
        if self._validar_email(valor):
            return "Email", True, f"✉️  {valor} é um email válido"
        
        # URL
        if self._validar_url(valor):
            return "URL", True, f"🌐 {valor} é uma URL válida"
        
        # CPF (simples)
        if self._validar_cpf(valor):
            return "CPF", True, f"🆔 {valor} é um CPF válido"
        
        # Telefone
        if self._validar_telefone(valor):
            return "Telefone", True, f"☎️  {valor} é um telefone válido"
        
        # Tentar identificar tipo mesmo sendo inválido
        if "@" in valor:
            return "Email", False, f"❌ {valor} não é um email válido"
        elif valor.startswith(("http://", "https://", "www.")):
            return "URL", False, f"❌ {valor} não é uma URL válida"
        elif valor.isdigit() and len(valor) == 11:
            return "CPF", False, f"❌ {valor} não é um CPF válido"
        elif valor.isdigit():
            return "Telefone", False, f"❌ {valor} não é um telefone válido"
        
        return "Desconhecido", False, f"❓ Não pude identificar o tipo de: {valor}"
    
    def _validar_email(self, email: str) -> bool:
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _validar_url(self, url: str) -> bool:
        """Valida formato de URL"""
        pattern = r'^(https?://|www\.)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return bool(re.match(pattern, url))
    
    def _validar_cpf(self, cpf: str) -> bool:
        """Valida formato básico de CPF"""
        cpf = cpf.replace(".", "").replace("-", "")
        if len(cpf) != 11 or not cpf.isdigit():
            return False
        # Validação básica (não é validação real de CPF)
        return len(set(cpf)) > 1
    
    def _validar_telefone(self, telefone: str) -> bool:
        """Valida formato de telefone"""
        telefone = telefone.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
        return len(telefone) >= 10 and len(telefone) <= 11 and telefone.isdigit()


if __name__ == "__main__":
    agente = AgenteValidacao()
    
    testes = [
        "Valide: usuario@email.com",
        "Valide: https://www.google.com",
        "Valide: 123.456.789-00",
        "Valide: (11) 99999-9999"
    ]
    
    for teste in testes:
        msg = Mensagem(conteudo=teste)
        resultado = agente.processar(msg, Contexto())
        print(f"\n{resultado.conteudo}")
