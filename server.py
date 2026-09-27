# -*- coding: utf-8 -*-
"""Backend FastAPI — IA Futurista."""

import base64
import time
import uuid
from pathlib import Path
from typing import Literal

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import agente as ag
from identidade import IDENTIDADE, MENSAGEM_BOAS_VINDAS
from api_automation import router as automation_router
from api_mouse_keyboard import router as mouse_keyboard_router
from api_multiagent import router as multiagent_router

app = FastAPI(title="IA Futurista")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(automation_router)
app.include_router(mouse_keyboard_router)
app.include_router(multiagent_router)

STATIC = Path(__file__).parent / "static"
SESSOES: dict[str, dict] = {}


class ChatReq(BaseModel):
    mensagem: str
    sessao_id: str | None = None
    modelo: str | None = None
    imagem_b64: str | None = None
    agente: Literal[
        "auto", "geral", "programacao", "pesquisa", "visao", "automacao",
        "design", "dados", "escrita", "suporte_windows",
    ] = "auto"


class NovaSessaoReq(BaseModel):
    titulo: str = "Novo chat"


class AcessoPCReq(BaseModel):
    enabled: bool


def ollama_ok_com_retry(tentativas: int = 3) -> bool:
    for _ in range(tentativas):
        if ag.ollama_online():
            return True
        time.sleep(1)
    return False


def deve_preview(resposta: str, pergunta: str) -> bool:
    p = pergunta.lower()
    return any(w in p for w in ("preview", "prévia", "pre-visualizar", "pré-visualizar"))


def validar_imagem(imagem_b64: str) -> tuple[str, str]:
    if len(imagem_b64) > 11_184_812:
        raise ValueError("A imagem excede o limite de 8 MB.")
    dados = base64.b64decode(imagem_b64, validate=True)
    if dados.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png", imagem_b64
    if dados.startswith(b"\xff\xd8\xff"):
        return "image/jpeg", imagem_b64
    if dados[:4] == b"RIFF" and dados[8:12] == b"WEBP":
        return "image/webp", imagem_b64
    raise ValueError("Formato de imagem inválido. Use PNG, JPEG ou WebP.")


def msg_erro_pt(exc: Exception) -> str:
    txt = str(exc).lower()
    if "language model unavailable" in txt or "connection" in txt or "ollama" in txt:
        return (
            "**Modelo de linguagem indisponível**\n\n"
            "O Ollama não está respondendo. No terminal execute:\n"
            "```\nollama serve\nollama pull qwen2.5-coder:7b\n```\n"
            "Depois recarregue a página (Ctrl+R)."
        )
    if "timeout" in txt or "timed out" in txt:
        return (
            "**Tempo esgotado**\n\n"
            "A pergunta demorou demais. Tente algo mais curto ou aguarde o Ollama carregar o modelo."
        )
    return f"**Erro**\n\n{exc}"


@app.get("/")
async def root():
    novo = STATIC / "index_multiagent.html"
    if novo.exists():
        return FileResponse(novo)
    return FileResponse(STATIC / "index.html")


@app.get("/api/status")
async def status():
    online = ag.ollama_online()
    modelos = ag.listar_modelos() if online else [ag.OLLAMA_MODEL]
    return {
        "ollama": online,
        "modelos": modelos,
        "modelo_padrao": ag.OLLAMA_MODEL,
        "modelo_codigo": ag.OLLAMA_CODE,
        "capacidades": {
            "visao": online and ag.OLLAMA_VISION in modelos,
            "geracao_imagem": False,
            "geracao_video": False,
        },
        "agentes": [{"id": chave, "nome": perfil["nome"]} for chave, perfil in ag.AGENTES.items()],
        "workspace": ag.WORKSPACES,
        "acesso_pc": ag.estado_acesso_pc(),
        "identidade": IDENTIDADE,
        "boas_vindas": MENSAGEM_BOAS_VINDAS,
    }


@app.post("/api/acesso-pc")
async def configurar_acesso_pc(req: AcessoPCReq):
    if req.enabled and not ag.host_companion_available():
        raise HTTPException(status_code=503, detail="A ponte Windows não está conectada.")
    ag.configurar_acesso_pc(req.enabled)
    return ag.estado_acesso_pc()


def _sessao_inicial() -> dict:
    sid = str(uuid.uuid4())[:8]
    return {
        "id": sid,
        "titulo": "IA Futurista",
        "msgs": [{
            "role": "assistant",
            "content": MENSAGEM_BOAS_VINDAS,
            "worked": 1,
        }],
        "agente": [],
        "logs": [],
    }


@app.get("/api/sessoes")
async def listar_sessoes():
    if not SESSOES:
        s = _sessao_inicial()
        SESSOES[s["id"]] = s
    return list(SESSOES.values())


@app.post("/api/sessoes")
async def nova_sessao(req: NovaSessaoReq):
    sid = str(uuid.uuid4())[:8]
    SESSOES[sid] = {"id": sid, "titulo": req.titulo, "msgs": [], "agente": [], "logs": []}
    return SESSOES[sid]


@app.post("/api/chat")
async def chat(req: ChatReq):
    sid = req.sessao_id
    if not sid or sid not in SESSOES:
        sid = str(uuid.uuid4())[:8]
        SESSOES[sid] = _sessao_inicial()
        SESSOES[sid]["id"] = sid

    s = SESSOES[sid]
    s["msgs"].append({"role": "user", "content": req.mensagem})
    t0 = time.time()

    try:
        if not ollama_ok_com_retry():
            raise ConnectionError("Ollama offline")

        imagem_b64 = req.imagem_b64
        if imagem_b64:
            mime, imagem_b64 = validar_imagem(imagem_b64)
            if ag.OLLAMA_VISION not in ag.listar_modelos():
                raise RuntimeError(f"Modelo visual não instalado: {ag.OLLAMA_VISION}")
            s["msgs"][-1]["imagem"] = f"data:{mime};base64,{imagem_b64}"

        perfil = ag.escolher_agente(req.agente, req.mensagem, bool(imagem_b64))
        modelo = req.modelo or ag.OLLAMA_MODEL
        if imagem_b64:
            modelo = ag.OLLAMA_VISION
        elif perfil in ("programacao", "design") and ag.OLLAMA_CODE in ag.listar_modelos():
            modelo = ag.OLLAMA_CODE

        resposta, logs = ag.rodar_agente(
            pergunta=req.mensagem,
            historico_msgs=s["agente"],
            placeholder=None,
            motores=["Google Search API", "DuckDuckGo Engine"] if perfil == "pesquisa" else [],
            codigo_aberto="",
            caminho_aberto=None,
            imagem_b64_val=imagem_b64,
            modelo=modelo,
            max_iteracoes=3,
            perfil_agente=perfil,
        )
        s["agente"].append({"role": "user", "content": req.mensagem})
        s["agente"].append({"role": "assistant", "content": resposta})
        s["logs"].extend(logs)

        if s["titulo"] in ("Novo chat", "IA Futurista") and len(s["msgs"]) <= 3:
            titulo = req.mensagem[:36] + ("..." if len(req.mensagem) > 36 else "")
            if titulo.lower() not in ("ola", "olá", "oi", "ok"):
                s["titulo"] = titulo

        elapsed = max(1, int(time.time() - t0))

        ai: dict = {
            "role": "assistant",
            "content": resposta or "Pronto! Como posso ajudar mais?",
            "worked": elapsed,
            "agente": perfil,
        }
        if deve_preview(resposta, req.mensagem):
            ai["preview"] = {
                "title": IDENTIDADE["nome_exibicao"],
                "desc": "Clique Preview para abrir o app.",
                "url": "http://127.0.0.1:8742",
            }
        s["msgs"].append(ai)
        return {"sessao_id": sid, "sessao": s, "resposta": ai}

    except Exception as e:
        elapsed = max(1, int(time.time() - t0))
        err = {"role": "assistant", "content": msg_erro_pt(e), "worked": elapsed, "erro": True}
        s["msgs"].append(err)
        return {"sessao_id": sid, "sessao": s, "resposta": err, "erro": str(e)}


app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")
