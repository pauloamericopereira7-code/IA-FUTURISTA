# ADICIONE ISTO AO FINAL DO multiagent_system.py (antes da classe Orquestrador)

# Tentar carregar novos agentes (se disponíveis)
try:
    from agentes.agente_contagem import AgenteContagem
    _AGENTE_CONTAGEM = AgenteContagem
except ImportError:
    _AGENTE_CONTAGEM = None

try:
    from agentes.agente_sintese import AgenteSintese
    _AGENTE_SINTESE = AgenteSintese
except ImportError:
    _AGENTE_SINTESE = None

try:
    from agentes.agente_validacao import AgenteValidacao
    _AGENTE_VALIDACAO = AgenteValidacao
except ImportError:
    _AGENTE_VALIDACAO = None

try:
    from agentes.agente_traducao import AgenteTraducao
    _AGENTE_TRADUCAO = AgenteTraducao
except ImportError:
    _AGENTE_TRADUCAO = None

try:
    from agentes.agente_sentiment import AgenteSentiment
    _AGENTE_SENTIMENT = AgenteSentiment
except ImportError:
    _AGENTE_SENTIMENT = None

# ============================================================================
# MODIFICAR A FUNCAO _inicializar_agentes DA CLASSE Orquestrador
# ============================================================================

# REMOVA:
#     def _inicializar_agentes(self):
#         """Inicializa todos os agentes"""
#         agentes = [
#             Interpretador(),
#             NucleoTexto(),
#             MotorProgramacao(),
#             MotorPesquisa(),
#             GestorArquivos(),
#             MotorVisual(),
#             Verificador(),
#             GeradorResposta(),
#             GestorErros(),
#         ]
#         
#         for agente in agentes:
#             self.agentes[agente.nome] = agente
#             self.logger.info(f"Agente inicializado: {agente.nome}")

# ADICIONE ISTO:
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
        
        # Adicionar novos agentes se disponíveis
        if _AGENTE_CONTAGEM:
            agentes.append(_AGENTE_CONTAGEM())
        if _AGENTE_SINTESE:
            agentes.append(_AGENTE_SINTESE())
        if _AGENTE_VALIDACAO:
            agentes.append(_AGENTE_VALIDACAO())
        if _AGENTE_TRADUCAO:
            agentes.append(_AGENTE_TRADUCAO())
        if _AGENTE_SENTIMENT:
            agentes.append(_AGENTE_SENTIMENT())
        
        for agente in agentes:
            self.agentes[agente.nome] = agente
            self.logger.info(f"Agente inicializado: {agente.nome}")
