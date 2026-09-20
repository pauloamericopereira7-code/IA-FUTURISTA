# -*- coding: utf-8 -*-
"""Motor agente IA Futurista — replica capacidades do Cursor Cloud Agent."""

from __future__ import annotations

import base64
import json
import logging
import os
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import requests
from duckduckgo_search import DDGS
from googlesearch import search as pesquisa_google

logger = logging.getLogger("agente")
logger.setLevel(logging.DEBUG)

# ---------------------------------------------------------------------------
# Caminhos e configuração
# ---------------------------------------------------------------------------

def _montar_workspaces() -> list[str]:
    raiz = Path(__file__).resolve().parent
    if sys.platform == "win32":
        pastas = [
            os.environ.get("FUTURISTA_PROJETOS", r"D:\IA_Futurista\projetos"),
            os.environ.get("PASTA_IA_SUPREMA", r"C:\IASuprema\ProgramasCriados"),
            os.environ.get("PASTA_POWERSHELL", r"C:\Windows\System32\WindowsPowerShell\v1.0\projetos"),
            str(raiz / "projetos"),
        ]
    else:
        pastas = [str(raiz / "projetos")]
    validas = []
    for p in pastas:
        if sys.platform != "win32" and (":" in p or p.startswith("\\")):
            continue
        os.makedirs(p, exist_ok=True)
        validas.append(p)
    return validas or [str(raiz / "projetos")]


WORKSPACES = _montar_workspaces()
PASTA_PRINCIPAL = WORKSPACES[0]
PASTA_RAIZ = os.environ.get(
    "FUTURISTA_RAIZ",
    r"D:\IA_Futurista" if sys.platform == "win32" and os.path.exists("D:\\") else str(Path(__file__).parent),
)
PYTHON_EXEC = (
    os.path.join(PASTA_RAIZ, ".venv", "Scripts", "python.exe")
    if os.path.exists(os.path.join(PASTA_RAIZ, ".venv", "Scripts", "python.exe"))
    else sys.executable
)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b")
OLLAMA_VISION = os.environ.get("OLLAMA_VISION", "llava:7b")

OLLAMA_OPTIONS = {
    "temperature": float(os.environ.get("OLLAMA_TEMP", "0.7")),
    "top_p": float(os.environ.get("OLLAMA_TOP_P", "0.9")),
    "num_ctx": int(os.environ.get("OLLAMA_NUM_CTX", "8192")),
    "num_predict": int(os.environ.get("OLLAMA_NUM_PREDICT", "2048")),
}

EXTENSOES = (".py", ".html", ".txt", ".rb", ".ps1", ".js", ".ts", ".json", ".md", ".bat")

from identidade import IDENTIDADE, MENSAGEM_BOAS_VINDAS, SYSTEM_PROMPT
from knowledge_cache import cache
from automation_queue import queue, AutomationTask

# ---------------------------------------------------------------------------
# Ollama
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def ollama_online() -> bool:
    """Check if Ollama is online. Result cached for performance."""
    try:
        result = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3).status_code == 200
        if result:
            logger.debug("Ollama online")
        else:
            logger.warning("Ollama returned non-200 status")
        return result
    except requests.RequestException as e:
        logger.error(f"Ollama offline: {e}")
        return False


@lru_cache(maxsize=1)
def listar_modelos() -> list[str]:
    """List available Ollama models. Result cached."""
    try:
        res = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        models = [m["name"] for m in res.json().get("models", [])]
        logger.info(f"Models available: {models}")
        return models
    except Exception as e:
        logger.warning(f"Could not fetch models, using default: {e}")
        return [OLLAMA_MODEL]


def chamar_ollama(mensagens: list[dict], placeholder, imagem_b64: str | None = None, modelo: str | None = None) -> str:
    """Call Ollama API with full message history.
    
    Args:
        mensagens: Full message history including system, user, and assistant
        placeholder: Streamlit placeholder for streaming output (or None)
        imagem_b64: Base64 image data if vision model
        modelo: Model name override
    
    Returns:
        Complete response text from model
    """
    modelo_final = modelo or OLLAMA_MODEL
    logger.debug(f"Calling Ollama with model={modelo_final}, msgs={len(mensagens)}")
    
    payload: dict = {
        "model": modelo_final,
        "messages": mensagens,
        "stream": True,
        "options": OLLAMA_OPTIONS,
    }
    if imagem_b64 and mensagens:
        payload["messages"] = [dict(m) for m in mensagens]
        payload["messages"][-1]["images"] = [imagem_b64]
        logger.debug("Vision image attached")

    try:
        res = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, stream=True, timeout=180)
        res.raise_for_status()
    except requests.ConnectionError as e:
        logger.error(f"Ollama connection failed: {e}")
        raise ConnectionError("Ollama offline — execute: ollama serve") from e
    except requests.Timeout as e:
        logger.error(f"Ollama timeout after 180s: {e}")
        raise TimeoutError("Ollama demorou demais — tente pergunta mais curta") from e

    resposta = ""
    for linha in res.iter_lines():
        if not linha:
            continue
        try:
            pedaco = json.loads(linha.decode("utf-8")).get("message", {}).get("content", "")
            resposta += pedaco
            if placeholder:
                placeholder.markdown(resposta + "▌")
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse Ollama stream line: {e}")
            continue
    
    if placeholder:
        placeholder.markdown(resposta)
    
    logger.info(f"Ollama response: {len(resposta)} chars")
    return resposta


# ---------------------------------------------------------------------------
# Workspace
# ---------------------------------------------------------------------------

def listar_arquivos() -> list[tuple[str, str]]:
    vistos: set[str] = set()
    lista: list[tuple[str, str]] = []
    for pasta in WORKSPACES:
        if not os.path.isdir(pasta):
            continue
        for nome in sorted(os.listdir(pasta)):
            if not nome.endswith(EXTENSOES):
                continue
            caminho = os.path.join(pasta, nome)
            if caminho in vistos:
                continue
            vistos.add(caminho)
            rotulo = nome if pasta == PASTA_PRINCIPAL else f"{nome} [{os.path.basename(pasta)}]"
            lista.append((rotulo, caminho))
    return lista


def resolver_caminho(relativo: str) -> str:
    relativo = relativo.strip().replace("/", os.sep)
    for pasta in WORKSPACES:
        candidato = os.path.join(pasta, relativo)
        if os.path.isfile(candidato):
            return candidato
    return os.path.join(PASTA_PRINCIPAL, relativo)


def snapshot_workspace(max_chars: int = 12000) -> str:
    linhas = ["=== WORKSPACE ==="]
    for pasta in WORKSPACES:
        linhas.append(f"\n📂 {pasta}")
        if not os.path.isdir(pasta):
            continue
        for nome in sorted(os.listdir(pasta)):
            if nome.endswith(EXTENSOES):
                caminho = os.path.join(pasta, nome)
                try:
                    tam = os.path.getsize(caminho)
                    linhas.append(f"  - {nome} ({tam} bytes)")
                except OSError:
                    linhas.append(f"  - {nome}")
    texto = "\n".join(linhas)
    return texto[:max_chars]


# ---------------------------------------------------------------------------
# Ferramentas do agente
# ---------------------------------------------------------------------------

def ferramenta_ler_arquivo(caminho: str) -> str:
    try:
        path = resolver_caminho(caminho)
        with open(path, encoding="utf-8", errors="replace") as f:
            return f"Conteúdo de {path}:\n```\n{f.read()}\n```"
    except Exception as e:
        return f"Erro ao ler: {e}"


def ferramenta_escrever_arquivo(caminho: str, conteudo: str) -> str:
    try:
        path = resolver_caminho(caminho)
        pasta = os.path.dirname(path)
        if pasta:
            os.makedirs(pasta, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(conteudo)
        return f"✅ Arquivo salvo: {path} ({len(conteudo)} chars)"
    except Exception as e:
        return f"Erro ao escrever: {e}"


def pergunta_simples(pergunta: str) -> bool:
    p = pergunta.lower().strip().strip("?!.")
    simples = {"ola", "olá", "oi", "hi", "hello", "ok", "sim", "nao", "não", "hey", "eae", "e aí"}
    return p in simples or len(p) < 12


def pesquisar_web(pergunta: str, motores: list[str]) -> str:
    """Search web with intelligent caching."""
    if pergunta_simples(pergunta):
        return ""
    
    cache_key = f"search:{pergunta[:50]}"
    cached_result = cache.get(cache_key)
    if cached_result:
        logger.info(f"Web search cache hit for: {pergunta[:50]}")
        return cached_result["content"].get("resultado", "")
    
    ctx = ""
    if any("Google" in m for m in motores):
        try:
            for url in pesquisa_google(pergunta, num_results=2):
                ctx += f"\n- Google: {url}"
        except Exception as e:
            logger.warning(f"Google search failed: {e}")
    
    if any("Duck" in m for m in motores):
        try:
            with DDGS(timeout=8) as ddgs:
                for r in ddgs.text(pergunta, max_results=2):
                    ctx += f"\n- DDG: {r['title']}: {r['body'][:150]}"
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed: {e}")
    
    # Cache the result
    if ctx:
        cache.set(cache_key, {"resultado": ctx}, source="web_search", ttl_hours=12)
    
    return ctx


def ferramenta_listar_pasta(caminho: str = ".") -> str:
    try:
        path = resolver_caminho(caminho) if caminho != "." else PASTA_PRINCIPAL
        if os.path.isfile(path):
            path = os.path.dirname(path)
        itens = os.listdir(path)
        return f"Conteúdo de {path}:\n" + "\n".join(f"  - {i}" for i in sorted(itens))
    except Exception as e:
        return f"Erro ao listar: {e}"


def ferramenta_executar_comando(comando: str) -> str:
    bloqueados = ["format", "del /f", "rm -rf /", "shutdown", "mkfs"]
    if any(b in comando.lower() for b in bloqueados):
        return "Comando bloqueado por segurança."
    try:
        proc = subprocess.run(
            comando, shell=True, capture_output=True, text=True,
            timeout=60, cwd=PASTA_PRINCIPAL,
        )
        saida = (proc.stdout or "") + (proc.stderr or "")
        return f"Exit {proc.returncode}:\n{saida[:8000]}" or "(sem saída)"
    except subprocess.TimeoutExpired:
        return "Timeout — comando excedeu 60s"
    except Exception as e:
        return f"Erro: {e}"


def ferramenta_executar_python(codigo: str) -> str:
    try:
        proc = subprocess.run(
            [PYTHON_EXEC, "-c", codigo],
            capture_output=True, text=True, timeout=30, cwd=PASTA_PRINCIPAL,
        )
        saida = (proc.stdout or "") + (proc.stderr or "")
        return f"Exit {proc.returncode}:\n{saida[:8000]}"
    except Exception as e:
        return f"Erro: {e}"


def executar_ferramenta(acao: str, params: dict) -> str:
    mapa = {
        "ler_arquivo": lambda: ferramenta_ler_arquivo(params.get("caminho", params.get("path", ""))),
        "escrever_arquivo": lambda: ferramenta_escrever_arquivo(
            params.get("caminho", params.get("path", "novo.py")),
            params.get("conteudo", params.get("content", "")),
        ),
        "listar_pasta": lambda: ferramenta_listar_pasta(params.get("caminho", ".")),
        "executar_comando": lambda: ferramenta_executar_comando(params.get("comando", params.get("command", ""))),
        "executar_python": lambda: ferramenta_executar_python(params.get("codigo", params.get("code", ""))),
    }
    fn = mapa.get(acao)
    return fn() if fn else f"Ferramenta desconhecida: {acao}"


def extrair_ferramentas(texto: str) -> list[dict]:
    encontrados = []
    for bloco in re.findall(r"```ferramenta\s*(.*?)\s*```", texto, re.DOTALL):
        try:
            encontrados.append(json.loads(bloco.strip()))
        except json.JSONDecodeError:
            pass
    return encontrados


def executar_programa(caminho: str) -> None:
    if sys.platform == "win32":
        subprocess.Popen([PYTHON_EXEC, caminho], creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        subprocess.Popen([PYTHON_EXEC, caminho], start_new_session=True)


def imagem_b64(upload) -> str | None:
    if upload is None:
        return None
    return base64.b64encode(upload.getvalue()).decode("utf-8")


def auto_salvar_codigo(resposta: str, caminho_atual: str | None) -> str | None:
    for lang, ext in [("python", ".py"), ("ruby", ".rb"), ("html", ".html"), ("javascript", ".js")]:
        match = re.search(rf"```{lang}\s*(.*?)\s*```", resposta, re.DOTALL)
        if match:
            cod = match.group(1).strip()
            if lang == "python" and "mainloop()" in cod and "root.mainloop()" not in cod:
                cod += "\n\nroot.mainloop()"
            dest = caminho_atual or os.path.join(PASTA_PRINCIPAL, f"app_autonomo{ext}")
            with open(dest, "w", encoding="utf-8") as f:
                f.write(cod)
            return dest
    return None


def contexto_automatico(pergunta: str) -> str:
    """Coleta contexto só quando necessário — evita lentidão em 'ola'."""
    if pergunta_simples(pergunta):
        return "(saudação — contexto mínimo)"
    partes = [ferramenta_listar_pasta(".")]
    for _, caminho in listar_arquivos()[:3]:
        try:
            if os.path.getsize(caminho) < 4000:
                partes.append(ferramenta_ler_arquivo(os.path.basename(caminho)))
        except OSError:
            pass
    return "\n\n".join(partes)[:6000]


def montar_contexto_sistema(
    pergunta: str,
    motores: list[str],
    codigo_aberto: str,
    caminho_aberto: str | None,
    img_anexada: bool,
) -> str:
    web = pesquisar_web(pergunta, motores)
    msg = SYSTEM_PROMPT
    msg += f"\n\nUsuário: {IDENTIDADE['usuario']}\nAgente: {IDENTIDADE['nome']} ({IDENTIDADE['nome_exibicao']})"
    msg += f"\n\n{snapshot_workspace()}"
    msg += f"\n\n--- CONTEXTO ---\n{contexto_automatico(pergunta)}"
    if caminho_aberto:
        msg += f"\n\nArquivo aberto: {caminho_aberto}\n```\n{codigo_aberto}\n```"
    if web:
        msg += f"\n\nPesquisa web automática:\n{web}"
    if img_anexada:
        msg += "\n\n[Imagem anexada pelo usuário — analise visualmente]"
    msg += f"\n\nPython: {PYTHON_EXEC}\nOllama: {OLLAMA_URL}\nModelo: {OLLAMA_MODEL}"
    return msg


def rodar_agente(
    pergunta: str,
    historico_msgs: list[dict],
    placeholder,
    motores: list[str],
    codigo_aberto: str,
    caminho_aberto: str | None,
    imagem_b64_val: str | None,
    modelo: str,
    max_iteracoes: int = 5,
) -> tuple[str, list[str]]:
    """Loop agente: chama Ollama, executa ferramentas, repete até concluir.
    
    IMPORTANT: historico_msgs is the FULL agent history (all previous user/assistant exchanges).
    This preserves context across multiple turns in the same session.
    """
    log_ferramentas: list[str] = []
    sistema = montar_contexto_sistema(pergunta, motores, codigo_aberto, caminho_aberto, bool(imagem_b64_val))

    # Build messages: system + full history + new question
    mensagens = [{"role": "system", "content": sistema}]
    
    # Include ALL historical messages, not just last 20 (preserve full context)
    for m in historico_msgs:
        if m["role"] in ("user", "assistant") and "content" in m:
            mensagens.append({"role": m["role"], "content": m["content"]})
    
    # Current question
    mensagens.append({"role": "user", "content": pergunta})

    resposta_final = ""
    iteracao = 0
    for iteracao in range(max_iteracoes):
        logger.info(f"Iteration {iteracao+1}/{max_iteracoes}, context msgs={len(mensagens)}")
        
        resposta = chamar_ollama(mensagens, placeholder, imagem_b64_val if iteracao == 0 else None, modelo)
        resposta_final = resposta
        mensagens.append({"role": "assistant", "content": resposta})
        logger.debug(f"Assistant response added, total msgs now={len(mensagens)}")

        ferramentas = extrair_ferramentas(resposta)
        if not ferramentas:
            logger.info(f"No tools extracted, ending loop at iteration {iteracao+1}")
            break

        logger.info(f"Found {len(ferramentas)} tools to execute")
        resultados = []
        for f in ferramentas:
            acao = f.get("acao", f.get("action", ""))
            params = f.get("parametros", f.get("params", {}))
            logger.info(f"Executing tool: {acao}")
            resultado = executar_ferramenta(acao, params)
            log_ferramentas.append(f"{acao}: {resultado[:200]}")
            resultados.append(f"[{acao}] {resultado}")

        tool_results_msg = "Resultados das ferramentas:\n" + "\n\n".join(resultados)
        mensagens.append({"role": "user", "content": tool_results_msg})
        logger.debug(f"Tool results added, total msgs now={len(mensagens)}")
        imagem_b64_val = None

    logger.info(f"Agent loop completed after {iteracao+1} iterations, final response: {len(resposta_final)} chars")
    return resposta_final, log_ferramentas
