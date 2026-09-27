# -*- coding: utf-8 -*-
"""
SISTEMA MULTIAGENTE - Arquitetura Base
Cada agente é responsável por uma função específica
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# ============================================================================
# DEFINIÇÕES BASE
# ============================================================================

@dataclass
class Mensagem:
    """Estrutura de mensagem entre agentes"""
    origem: str
    destino: str
    tipo: str  # "comando", "resposta", "erro", "log"
    conteudo: Any
    timestamp: datetime = None
    metadados: Dict = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadados is None:
            self.metadados = {}


@dataclass
class Contexto:
    """Contexto compartilhado entre agentes"""
    comando_original: str
    usuario: str
    sessao_id: str
    recursos_disponiveis: Dict
    historico: List[Mensagem] = None
    variaveis: Dict = None
    
    def __post_init__(self):
        if self.historico is None:
            self.historico = []
        if self.variaveis is None:
            self.variaveis = {}


# ============================================================================
# CLASSE BASE DE AGENTE
# ============================================================================

class Agente(ABC):
    """Classe abstrata para todos os agentes"""
    
    def __init__(self, nome: str, descricao: str):
        self.nome = nome
        self.descricao = descricao
        self.logger = logging.getLogger(self.nome)
        self.ativo = True
        self.metricas = {
            "execucoes": 0,
            "sucessos": 0,
            "erros": 0,
            "tempo_total": 0
        }
    
    @abstractmethod
    def pode_processar(self, mensagem: Mensagem) -> bool:
        """Verifica se este agente pode processar a mensagem"""
        pass
    
    @abstractmethod
    def processar(self, mensagem: Mensagem, contexto: Contexto) -> Mensagem:
        """Processa a mensagem e retorna resultado"""
        pass
    
    def enviar_mensagem(self, destino: str, conteudo: Any, tipo: str = "resposta") -> Mensagem:
        """Cria uma mensagem para ser enviada"""
        return Mensagem(
            origem=self.nome,
            destino=destino,
            tipo=tipo,
            conteudo=conteudo
        )
    
    def registrar_execucao(self, sucesso: bool = True, tempo: float = 0):
        """Registra métrica de execução"""
        self.metricas["execucoes"] += 1
        if sucesso:
            self.metricas["sucessos"] += 1
        else:
            self.metricas["erros"] += 1
        self.metricas["tempo_total"] += tempo
    
    def obter_metricas(self) -> Dict:
        """Retorna métricas do agente"""
        return {
            "agente": self.nome,
            **self.metricas,
            "taxa_sucesso": (
                self.metricas["sucessos"] / self.metricas["execucoes"] * 100
                if self.metricas["execucoes"] > 0 else 0
            )
        }


# ============================================================================
# AGENTES ESPECIALIZADOS
# ============================================================================

class Interpretador(Agente):
    """Entende comandos do usuário e classifica"""
    
    def __init__(self):
        super().__init__("Interpretador", "Processa e classifica comandos")
        self.palavras_chave = {
            "refatorar": ["refatorar", "otimizar", "melhorar"],
            "explicar": ["explicar", "documentar", "descrever"],
            "pesquisar": ["pesquisar", "buscar", "consultar"],
            "arquivo": ["arquivo", "projeto", "salvar", "carregar"],
            "visual": ["imagem", "diagrama", "visual", "gráfico"],
            "executar": ["executar", "rodar", "testar", "run"],
        }
    
    def pode_processar(self, mensagem: Mensagem) -> bool:
        return mensagem.tipo == "comando"
    
    def processar(self, mensagem: Mensagem, contexto: Contexto) -> Mensagem:
        """Interpreta o comando e classifica"""
        inicio = datetime.now()
        
        try:
            comando = mensagem.conteudo.lower()
            
            # Detectar tipo de comando
            tipo_detectado = "geral"
            for tipo, palavras in self.palavras_chave.items():
                if any(palavra in comando for palavra in palavras):
                    tipo_detectado = tipo
                    break
            
            resultado = {
                "tipo": tipo_detectado,
                "comando_original": comando,
                "confianca": 0.95 if tipo_detectado != "geral" else 0.5
            }
            
            tempo = (datetime.now() - inicio).total_seconds()
            self.registrar_execucao(sucesso=True, tempo=tempo)
            
            return Mensagem(
                origem=self.nome,
                destino="Orquestrador",
                tipo="analise",
                conteudo=resultado
            )
        
        except Exception as e:
            self.logger.error(f"Erro ao interpretar: {e}")
            self.registrar_execucao(sucesso=False)
            return Mensagem(
                origem=self.nome,
                destino="GestorErros",
                tipo="erro",
                conteudo=str(e)
            )


class NucleoTexto(Agente):
    """Gera explicações, documentação e textos"""
    
    def __init__(self):
        super().__init__("NucleoTexto", "Gera explicações e documentação")
    
    def pode_processar(self, mensagem: Mensagem) -> bool:
        return "texto" in mensagem.tipo or "explicar" in str(mensagem.conteudo).lower()
    
    def processar(self, mensagem: Mensagem, contexto: Contexto) -> Mensagem:
        """Gera documentação/explicação"""
        inicio = datetime.now()
        
        try:
            conteudo = mensagem.conteudo
            
            # Gerar documentação
            documentacao = f"""
# Documentação Automática

## Descrição
{conteudo.get('descricao', 'Sem descrição')}

## Detalhes
- Tipo: {conteudo.get('tipo', 'Desconhecido')}
- Complexidade: {conteudo.get('complexidade', 'Média')}
- Status: {conteudo.get('status', 'Ativo')}

## Exemplos de Uso
```python
# Exemplo 1
resultado = processar(dados)
```
            """
            
            tempo = (datetime.now() - inicio).total_seconds()
            self.registrar_execucao(sucesso=True, tempo=tempo)
            
            return Mensagem(
                origem=self.nome,
                destino="GeradorResposta",
                tipo="documentacao",
                conteudo=documentacao
            )
        
        except Exception as e:
            self.logger.error(f"Erro ao gerar texto: {e}")
            self.registrar_execucao(sucesso=False)
            return Mensagem(
                origem=self.nome,
                destino="GestorErros",
                tipo="erro",
                conteudo=str(e)
            )


class MotorProgramacao(Agente):
    """Refatora, otimiza e gera código"""
    
    def __init__(self):
        super().__init__("MotorProgramacao", "Refatora e otimiza código")
    
    def pode_processar(self, mensagem: Mensagem) -> bool:
        return "programacao" in str(mensagem.tipo)
    
    def processar(self, mensagem: Mensagem, contexto: Contexto) -> Mensagem:
        """Refatora código"""
        inicio = datetime.now()
        
        try:
            codigo = mensagem.conteudo.get("codigo", "")
            tipo_refacao = mensagem.conteudo.get("tipo", "basico")
            
            # Refatação básica
            refatorado = codigo.replace("var ", "let ").replace("  ", "    ")
            
            resultado = {
                "codigo_original": codigo,
                "codigo_refatorado": refatorado,
                "tipo_refacao": tipo_refacao,
                "melhorias": ["variáveis modernizadas", "indentação padronizada"]
            }
            
            tempo = (datetime.now() - inicio).total_seconds()
            self.registrar_execucao(sucesso=True, tempo=tempo)
            
            return Mensagem(
                origem=self.nome,
                destino="GeradorResposta",
                tipo="codigo_refatorado",
                conteudo=resultado
            )
        
        except Exception as e:
            self.logger.error(f"Erro ao refatorar: {e}")
            self.registrar_execucao(sucesso=False)
            return Mensagem(
                origem=self.nome,
                destino="GestorErros",
                tipo="erro",
                conteudo=str(e)
            )


class MotorPesquisa(Agente):
    """Conecta à web e realiza pesquisas"""
    
    def __init__(self):
        super().__init__("MotorPesquisa", "Realiza pesquisas na web")
    
    def pode_processar(self, mensagem: Mensagem) -> bool:
        return "pesquisa" in str(mensagem.tipo)
    
    def processar(self, mensagem: Mensagem, contexto: Contexto) -> Mensagem:
        """Realiza pesquisa"""
        inicio = datetime.now()
        
        try:
            query = mensagem.conteudo.get("query", "")
            
            # Simulação de pesquisa
            resultado = {
                "query": query,
                "resultados": [
                    {"titulo": f"Resultado 1 para {query}", "url": "https://example.com/1"},
                    {"titulo": f"Resultado 2 para {query}", "url": "https://example.com/2"},
                ],
                "total": 2
            }
            
            tempo = (datetime.now() - inicio).total_seconds()
            self.registrar_execucao(sucesso=True, tempo=tempo)
            
            return Mensagem(
                origem=self.nome,
                destino="GeradorResposta",
                tipo="pesquisa_resultado",
                conteudo=resultado
            )
        
        except Exception as e:
            self.logger.error(f"Erro ao pesquisar: {e}")
            self.registrar_execucao(sucesso=False)
            return Mensagem(
                origem=self.nome,
                destino="GestorErros",
                tipo="erro",
                conteudo=str(e)
            )


class GestorArquivos(Agente):
    """Manipula arquivos e projetos"""
    
    def __init__(self):
        super().__init__("GestorArquivos", "Gerencia arquivos e projetos")
    
    def pode_processar(self, mensagem: Mensagem) -> bool:
        return "arquivo" in str(mensagem.tipo)
    
    def processar(self, mensagem: Mensagem, contexto: Contexto) -> Mensagem:
        """Gerencia arquivos"""
        inicio = datetime.now()
        
        try:
            operacao = mensagem.conteudo.get("operacao", "listar")
            caminho = mensagem.conteudo.get("caminho", ".")
            
            resultado = {
                "operacao": operacao,
                "caminho": caminho,
                "status": "sucesso",
                "arquivos": ["arquivo1.py", "arquivo2.py"]
            }
            
            tempo = (datetime.now() - inicio).total_seconds()
            self.registrar_execucao(sucesso=True, tempo=tempo)
            
            return Mensagem(
                origem=self.nome,
                destino="GeradorResposta",
                tipo="operacao_arquivo",
                conteudo=resultado
            )
        
        except Exception as e:
            self.logger.error(f"Erro ao gerenciar arquivo: {e}")
            self.registrar_execucao(sucesso=False)
            return Mensagem(
                origem=self.nome,
                destino="GestorErros",
                tipo="erro",
                conteudo=str(e)
            )


class MotorVisual(Agente):
    """Analisa imagens e diagramas"""
    
    def __init__(self):
        super().__init__("MotorVisual", "Analisa imagens e diagramas")
    
    def pode_processar(self, mensagem: Mensagem) -> bool:
        return "visual" in str(mensagem.tipo)
    
    def processar(self, mensagem: Mensagem, contexto: Contexto) -> Mensagem:
        """Analisa conteúdo visual"""
        inicio = datetime.now()
        
        try:
            imagem_url = mensagem.conteudo.get("url", "")
            
            resultado = {
                "url": imagem_url,
                "analise": "Imagem analisada com sucesso",
                "elementos_detectados": ["objeto1", "objeto2"],
                "confianca": 0.85
            }
            
            tempo = (datetime.now() - inicio).total_seconds()
            self.registrar_execucao(sucesso=True, tempo=tempo)
            
            return Mensagem(
                origem=self.nome,
                destino="GeradorResposta",
                tipo="analise_visual",
                conteudo=resultado
            )
        
        except Exception as e:
            self.logger.error(f"Erro ao analisar visual: {e}")
            self.registrar_execucao(sucesso=False)
            return Mensagem(
                origem=self.nome,
                destino="GestorErros",
                tipo="erro",
                conteudo=str(e)
            )


class Verificador(Agente):
    """Verifica recursos disponíveis"""
    
    def __init__(self):
        super().__init__("Verificador", "Verifica recursos e dependências")
    
    def pode_processar(self, mensagem: Mensagem) -> bool:
        return "verificacao" in str(mensagem.tipo)
    
    def processar(self, mensagem: Mensagem, contexto: Contexto) -> Mensagem:
        """Verifica disponibilidade de recursos"""
        inicio = datetime.now()
        
        try:
            verificacoes = {
                "memoria": "disponível",
                "disco": "disponível",
                "internet": "online",
                "dependencias": "todas_instaladas"
            }
            
            tempo = (datetime.now() - inicio).total_seconds()
            self.registrar_execucao(sucesso=True, tempo=tempo)
            
            return Mensagem(
                origem=self.nome,
                destino="GeradorResposta",
                tipo="verificacao_resultado",
                conteudo=verificacoes
            )
        
        except Exception as e:
            self.logger.error(f"Erro ao verificar: {e}")
            self.registrar_execucao(sucesso=False)
            return Mensagem(
                origem=self.nome,
                destino="GestorErros",
                tipo="erro",
                conteudo=str(e)
            )


class GeradorResposta(Agente):
    """Compõe a resposta final"""
    
    def __init__(self):
        super().__init__("GeradorResposta", "Compõe resposta final")
    
    def pode_processar(self, mensagem: Mensagem) -> bool:
        return True  # Processa tudo
    
    def processar(self, mensagem: Mensagem, contexto: Contexto) -> Mensagem:
        """Compõe resposta final"""
        inicio = datetime.now()
        
        try:
            resposta_final = f"""
# Resultado da Execução

## Entrada
{contexto.comando_original}

## Processamento
- Agente: {mensagem.origem}
- Tipo: {mensagem.tipo}

## Resultado
{json.dumps(mensagem.conteudo, indent=2, ensure_ascii=False)}

## Timestamp
{datetime.now().isoformat()}
            """
            
            tempo = (datetime.now() - inicio).total_seconds()
            self.registrar_execucao(sucesso=True, tempo=tempo)
            
            return Mensagem(
                origem=self.nome,
                destino="Usuario",
                tipo="resposta_final",
                conteudo=resposta_final
            )
        
        except Exception as e:
            self.logger.error(f"Erro ao gerar resposta: {e}")
            self.registrar_execucao(sucesso=False)
            return Mensagem(
                origem=self.nome,
                destino="Usuario",
                tipo="erro",
                conteudo=str(e)
            )


class GestorErros(Agente):
    """Trata falhas e exceções"""
    
    def __init__(self):
        super().__init__("GestorErros", "Trata erros e exceções")
    
    def pode_processar(self, mensagem: Mensagem) -> bool:
        return mensagem.tipo == "erro"
    
    def processar(self, mensagem: Mensagem, contexto: Contexto) -> Mensagem:
        """Trata erro"""
        inicio = datetime.now()
        
        try:
            erro_msg = mensagem.conteudo
            
            resultado = {
                "erro": erro_msg,
                "agente": mensagem.origem,
                "sugestao": "Verifique os parâmetros e tente novamente",
                "timestamp": datetime.now().isoformat()
            }
            
            tempo = (datetime.now() - inicio).total_seconds()
            self.registrar_execucao(sucesso=True, tempo=tempo)
            
            return Mensagem(
                origem=self.nome,
                destino="Usuario",
                tipo="resposta_erro",
                conteudo=resultado
            )
        
        except Exception as e:
            self.logger.error(f"Erro ao tratar erro: {e}")
            self.registrar_execucao(sucesso=False)
            return Mensagem(
                origem=self.nome,
                destino="Usuario",
                tipo="erro_critico",
                conteudo=str(e)
            )


# ============================================================================
# ORQUESTRADOR CENTRAL
# ============================================================================

class Orquestrador:
    """Coordena todos os agentes"""
    
    def __init__(self):
        self.logger = logging.getLogger("Orquestrador")
        self.agentes: Dict[str, Agente] = {}
        self.fila_mensagens: List[Mensagem] = []
        self.historico_execucao: List[Dict] = []
        
        # Inicializar agentes
        self._inicializar_agentes()
    
    def _inicializar_agentes(self):
        """Inicializa todos os agentes"""
        agentes = [
            Interpretador(),
            NucleoTexto(),
            MotorProgramacao(),
            MotorPesquisa(),
            GestorArquivos(),
            MotorVisual(),
            Verificador(),
            GeradorResposta(),
            GestorErros(),
        ]
        
        for agente in agentes:
            self.agentes[agente.nome] = agente
            self.logger.info(f"Agente inicializado: {agente.nome}")
    
    def executar(self, comando: str, usuario: str = "sistema", sessao_id: str = "default") -> Dict:
        """Executa um comando orquestrado"""
        
        self.logger.info(f"Executando comando: {comando}")
        
        # Criar contexto
        contexto = Contexto(
            comando_original=comando,
            usuario=usuario,
            sessao_id=sessao_id,
            recursos_disponiveis={}
        )
        
        # Enviar para interpretador
        mensagem_inicial = Mensagem(
            origem="Usuario",
            destino="Interpretador",
            tipo="comando",
            conteudo=comando
        )
        
        # Processar mensagem
        resposta = self._processar_mensagem(mensagem_inicial, contexto)
        
        # Registrar execução
        self.historico_execucao.append({
            "comando": comando,
            "usuario": usuario,
            "timestamp": datetime.now().isoformat(),
            "resposta_resumo": str(resposta.conteudo)[:100]
        })
        
        return {
            "sucesso": True,
            "resposta": resposta.conteudo,
            "agente": resposta.origem,
            "timestamp": resposta.timestamp.isoformat()
        }
    
    def _processar_mensagem(self, mensagem: Mensagem, contexto: Contexto) -> Mensagem:
        """Processa uma mensagem através dos agentes"""
        
        # Encontrar agente apropriado
        agente = self.agentes.get(mensagem.destino)
        
        if not agente:
            self.logger.warning(f"Agente {mensagem.destino} não encontrado")
            return self._processar_mensagem(
                Mensagem(
                    origem="Orquestrador",
                    destino="GestorErros",
                    tipo="erro",
                    conteudo=f"Agente {mensagem.destino} não encontrado"
                ),
                contexto
            )
        
        # Verificar se agente pode processar
        if not agente.pode_processar(mensagem):
            self.logger.debug(f"Agente {agente.nome} não pode processar {mensagem.tipo}")
            return self._encaminhar_para_erro(mensagem, contexto)
        
        # Processar
        try:
            resultado = agente.processar(mensagem, contexto)
            contexto.historico.append(resultado)
            
            # Se resultado é para outro agente, continuar cadeia
            if resultado.destino != "Usuario":
                return self._processar_mensagem(resultado, contexto)
            
            return resultado
        
        except Exception as e:
            self.logger.error(f"Erro ao processar com {agente.nome}: {e}")
            return self._encaminhar_para_erro(mensagem, contexto)
    
    def _encaminhar_para_erro(self, mensagem: Mensagem, contexto: Contexto) -> Mensagem:
        """Encaminha para gestor de erros"""
        mensagem_erro = Mensagem(
            origem="Orquestrador",
            destino="GestorErros",
            tipo="erro",
            conteudo=f"Não pude processar: {mensagem.conteudo}"
        )
        return self._processar_mensagem(mensagem_erro, contexto)
    
    def obter_status(self) -> Dict:
        """Retorna status de todos os agentes"""
        return {
            "agentes": len(self.agentes),
            "agentes_detalhes": [agente.obter_metricas() for agente in self.agentes.values()],
            "historico_execucoes": len(self.historico_execucao),
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  SISTEMA MULTIAGENTE - DEMONSTRAÇÃO")
    print("="*70 + "\n")
    
    # Criar orquestrador
    orq = Orquestrador()
    
    # Exemplos de comandos
    comandos = [
        "Refatorar esta função: var x = 10",
        "Explicar como funciona o código",
        "Pesquisar sobre Python asyncio",
    ]
    
    for comando in comandos:
        print(f"\n[COMANDO] {comando}")
        resultado = orq.executar(comando, usuario="usuario_teste")
        resposta_str = str(resultado['resposta'])[:200]
        print(f"[RESULTADO] {resposta_str}...")
    
    # Status final
    print("\n" + "="*70)
    print("  STATUS FINAL DOS AGENTES")
    print("="*70)
    status = orq.obter_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))
