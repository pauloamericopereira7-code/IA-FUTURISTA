# -*- coding: utf-8 -*-
"""API para integração com Sistema Multiagente"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from multiagent_system import Orquestrador

router = APIRouter(prefix="/api/multiagent", tags=["multiagent"])

# Instância global
orquestrador = None

def init_orquestrador():
    """Inicializa orquestrador na primeira requisição"""
    global orquestrador
    if orquestrador is None:
        orquestrador = Orquestrador()
    return orquestrador

class ComandoRequest(BaseModel):
    comando: str
    usuario: str = "sistema"
    sessao_id: str = "default"

class StatusResponse(BaseModel):
    agentes: int
    agentes_detalhes: list
    historico_execucoes: int

@router.post("/execute")
async def executar_comando(req: ComandoRequest):
    """Executa comando através dos agentes multiagente"""
    try:
        orq = init_orquestrador()
        resultado = orq.executar(
            comando=req.comando,
            usuario=req.usuario,
            sessao_id=req.sessao_id
        )
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def obter_status() -> StatusResponse:
    """Obtém status de todos os agentes"""
    try:
        orq = init_orquestrador()
        status = orq.obter_status()
        return StatusResponse(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agentes")
async def listar_agentes():
    """Lista todos os agentes e suas métricas"""
    try:
        orq = init_orquestrador()
        agentes = []
        for nome, agente in orq.agentes.items():
            agentes.append({
                "nome": nome,
                "descricao": agente.descricao,
                "metricas": agente.obter_metricas()
            })
        return {"agentes": agentes, "total": len(agentes)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historico")
async def obter_historico(limite: int = 50):
    """Obtém histórico de execuções"""
    try:
        orq = init_orquestrador()
        return {
            "historico": orq.historico_execucao[-limite:],
            "total": len(orq.historico_execucao)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
