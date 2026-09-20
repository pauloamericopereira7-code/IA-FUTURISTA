# -*- coding: utf-8 -*-
"""Backend FastAPI — IA Futurista."""

import time
import uuid
from pathlib import Path

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import agente as ag
from identidade import IDENTIDADE, MENSAGEM_BOAS_VINDAS
from api_automation import router as automation_router

app = FastAPI(title="IA Futurista")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(automation_router)

STATIC = Path(__file__).parent / "static"
SESSOES: dict[str, dict] = {}


class ChatReq(BaseModel):
    mensagem: str
    sessao_id: str | None = None
    modelo: str | None = None


class NovaSessaoReq(BaseModel):
    titulo: str = "Novo chat"


def ollama_ok_com_retry(tentativas: int = 3) -> bool:
    for _ in range(tentativas):
        if ag.ollama_online():
            return True
        time.sleep(1)
    return False


def deve_preview(resposta: str, pergunta: str) -> bool:
    p = pergunta.lower()
    if any(w in p for w in ("preview", "abra", "abrir", "interface", "app", "site")):
        return True
    return "```" in resposta and len(resposta) > 200


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
    return FileResponse(STATIC / "index.html")


@app.get("/api/status")
async def status():
    online = ag.ollama_online()
    return {
        "ollama": online,
        "modelos": ag.listar_modelos() if online else [ag.OLLAMA_MODEL],
        "modelo_padrao": ag.OLLAMA_MODEL,
        "workspace": ag.WORKSPACES,
        "identidade": IDENTIDADE,
        "boas_vindas": MENSAGEM_BOAS_VINDAS,
    }


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

        resposta, logs = ag.rodar_agente(
            pergunta=req.mensagem,
            historico_msgs=s["agente"],
            placeholder=None,
            motores=["Google Search API", "DuckDuckGo Engine"],
            codigo_aberto="",
            caminho_aberto=None,
            imagem_b64_val=None,
            modelo=req.modelo or ag.OLLAMA_MODEL,
            max_iteracoes=3,
        )
        s["agente"].append({"role": "user", "content": req.mensagem})
        s["agente"].append({"role": "assistant", "content": resposta})
        s["logs"].extend(logs)

        if s["titulo"] in ("Novo chat", "IA Futurista") and len(s["msgs"]) <= 3:
            titulo = req.mensagem[:36] + ("..." if len(req.mensagem) > 36 else "")
            if titulo.lower() not in ("ola", "olá", "oi", "ok"):
                s["titulo"] = titulo

        ag.auto_salvar_codigo(resposta, None)
        elapsed = max(1, int(time.time() - t0))

        ai: dict = {
            "role": "assistant",
            "content": resposta or "Pronto! Como posso ajudar mais?",
            "worked": elapsed,
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
