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
        adicionais = os.environ.get("FUTURISTA_WORKSPACES", "")
        pastas.extend(adicionais.split(os.pathsep))
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
OLLAMA_CODE = os.environ.get("OLLAMA_CODE", "qwen2.5-coder:3b")

OLLAMA_OPTIONS = {
    "temperature": float(os.environ.get("OLLAMA_TEMP", "0.7")),
    "top_p": float(os.environ.get("OLLAMA_TOP_P", "0.9")),
    "num_ctx": int(os.environ.get("OLLAMA_NUM_CTX", "8192")),
    "num_predict": int(os.environ.get("OLLAMA_NUM_PREDICT", "2048")),
}

EXTENSOES = (".py", ".html", ".txt", ".rb", ".ps1", ".js", ".ts", ".json", ".md", ".bat")

AGENTES = {
    "geral": {
        "nome": "Geral",
        "instrucoes": "Atenda perguntas gerais com clareza. Use ferramentas apenas quando agregarem valor.",
    },
    "programacao": {
        "nome": "Programação",
        "instrucoes": "Especialista em programação. Inspecione o projeto, proponha alterações pequenas e valide com testes. Não invente que editou arquivos.",
    },
    "pesquisa": {
        "nome": "Pesquisa",
        "instrucoes": "Pesquise na web quando necessário, diferencie fatos de inferências e cite as fontes encontradas. Não invente fontes.",
    },
    "visao": {
        "nome": "Visão",
        "instrucoes": "Especialista em imagens. Descreva apenas o que consegue observar e indique incertezas; peça a imagem se ela não foi anexada.",
    },
    "automacao": {
        "nome": "Automação",
        "instrucoes": "Planeje automações com escopo mínimo. Para abrir Google, YouTube ou outra página use abrir_url, que abre o navegador padrão do Windows; nunca use o comando `start` no shell Linux. Antes de ações destrutivas, compras, envio de mensagens ou mudanças fora do projeto, explique o impacto e solicite confirmação.",
    },
    "design": {
        "nome": "Design",
        "instrucoes": "Especialista em design visual e interfaces. Quando o usuário pedir um visual ou arquivo, crie o artefato de verdade com escrever_arquivo, escolhendo um caminho nas pastas pessoais disponíveis se nenhum for especificado. Não devolva JSON de ferramenta nem pare num plano. Só confirme após receber sucesso da ferramenta.",
    },
    "dados": {
        "nome": "Dados",
        "instrucoes": "Analise CSV, JSON e dados fornecidos. Explique premissas, confira cálculos e não invente valores ausentes.",
    },
    "escrita": {
        "nome": "Escrita",
        "instrucoes": "Ajude a redigir, resumir e revisar textos no tom pedido. Preserve fatos e sinalize quando faltar contexto.",
    },
    "suporte_windows": {
        "nome": "Suporte Windows",
        "instrucoes": "Diagnostique problemas do Windows com passos reversíveis primeiro. Explique o impacto e peça confirmação antes de alterar configurações do sistema.",
    },
}


PC_ACCESS_ENABLED = os.environ.get("IRIS_PC_ACCESS_ENABLED", "false").lower() in {"1", "true", "yes", "on"}
SCREENSHOT_MARKER = "IRIS_SCREENSHOT_BASE64:"


def configurar_acesso_pc(enabled: bool) -> None:
    global PC_ACCESS_ENABLED
    PC_ACCESS_ENABLED = enabled


def estado_acesso_pc() -> dict:
    return {"ativo": PC_ACCESS_ENABLED, "conectado": host_companion_available()}


def escolher_agente(preferencia: str, pergunta: str, tem_imagem: bool = False) -> str:
    if preferencia in AGENTES:
        return preferencia
    if tem_imagem:
        return "visao"

    texto = pergunta.lower()
    if any(p in texto for p in ("automatize", "automatizar", "clique", "mouse", "teclado", "abra o programa")):
        return "automacao"
    if any(p in texto for p in ("pesquise", "pesquisa", "notícias", "noticias", "fontes", "na internet", "na web", "atualizado")):
        return "pesquisa"
    if any(p in texto for p in ("visual", "design", "interface", "estilo", "layout", "cursor")):
        return "design"
    if any(p in texto for p in ("planilha", "csv", "dados", "estatística", "estatistica", "gráfico", "grafico")):
        return "dados"
    if any(p in texto for p in ("windows", "computador", "drivers", "erro no pc", "configurar o sistema")):
        return "suporte_windows"
    if any(p in texto for p in ("programa", "programar", "código", "codigo", "bug", "depurar", "script", "python", "javascript", "html")):
        return "programacao"
    if any(p in texto for p in ("escreva", "redija", "revise", "resuma", "e-mail", "email", "artigo", "roteiro")):
        return "escrita"
    if any(p in texto for p in ("imagem", "foto", "print", "screenshot")):
        return "visao"
    return "geral"

from identidade import IDENTIDADE, MENSAGEM_BOAS_VINDAS, SYSTEM_PROMPT
from knowledge_cache import cache
from automation_queue import queue, AutomationTask
from mouse_keyboard_control import execute_mouse_keyboard_action, host_companion_available

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


def _ferramenta_ollama(nome: str, descricao: str, propriedades: dict, obrigatorias: list[str] | None = None) -> dict:
    return {
        "type": "function",
        "function": {
            "name": nome,
            "description": descricao,
            "parameters": {
                "type": "object",
                "properties": propriedades,
                "required": obrigatorias or [],
            },
        },
    }


def ferramentas_ollama(modelo: str, perfil_agente: str = "geral") -> list[dict]:
    if modelo == OLLAMA_VISION:
        return []
    texto = {"type": "string"}
    tools = [
        _ferramenta_ollama("ler_arquivo", "Lê um arquivo em projetos, Desktop, Documentos, Downloads ou Imagens.", {"caminho": texto}, ["caminho"]),
        _ferramenta_ollama("escrever_arquivo", "Cria ou substitui um arquivo nas pastas disponíveis sem pedir confirmação para cada arquivo.", {"caminho": texto, "conteudo": texto}, ["caminho", "conteudo"]),
        _ferramenta_ollama("listar_pasta", "Lista arquivos em uma pasta autorizada.", {"caminho": texto}),
    ]
    if perfil_agente not in {"design", "escrita", "dados", "visao"}:
        tools.extend([
            _ferramenta_ollama("executar_comando", "Executa um comando no ambiente do agente.", {"comando": texto}, ["comando"]),
            _ferramenta_ollama("executar_python", "Executa código Python no ambiente do agente.", {"codigo": texto}, ["codigo"]),
        ])
    if perfil_agente in {"automacao", "suporte_windows", "visao"} and PC_ACCESS_ENABLED and host_companion_available():
        tools.extend([
            _ferramenta_ollama("abrir_url", "Abre uma URL http/https no navegador padrão do Windows; para pesquisar, monte a URL adequada.", {"url": texto}, ["url"]),
            _ferramenta_ollama("posicao_mouse", "Retorna a posição atual do mouse." , {}),
            _ferramenta_ollama("capturar_tela", "Captura a tela atual para análise visual." , {}),
            _ferramenta_ollama("mover_mouse", "Move o cursor para coordenadas da tela." , {"x": {"type": "integer"}, "y": {"type": "integer"}}, ["x", "y"]),
            _ferramenta_ollama("clicar_mouse", "Clica com o botão indicado na posição atual." , {"button": texto, "clicks": {"type": "integer"}}),
            _ferramenta_ollama("digitar_texto", "Digita texto na janela ativa." , {"text": texto}),
            _ferramenta_ollama("pressionar_tecla", "Pressiona uma tecla permitida." , {"key": texto}),
            _ferramenta_ollama("atalho_teclado", "Pressiona um atalho de 2 a 4 teclas." , {"keys": {"type": "array", "items": texto}}, ["keys"]),
        ])
    return tools


def chamar_ollama(
    mensagens: list[dict],
    placeholder,
    imagem_b64: str | None = None,
    modelo: str | None = None,
    perfil_agente: str = "geral",
) -> tuple[str, list[dict]]:
    modelo_final = modelo or OLLAMA_MODEL
    payload: dict = {
        "model": modelo_final,
        "messages": mensagens,
        "stream": False,
        "options": OLLAMA_OPTIONS,
    }
    tools = ferramentas_ollama(modelo_final, perfil_agente)
    if tools:
        payload["tools"] = tools
    if imagem_b64 and mensagens:
        payload["messages"] = [dict(m) for m in mensagens]
        payload["messages"][-1]["images"] = [imagem_b64]

    try:
        res = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=180)
        res.raise_for_status()
        message = res.json().get("message", {})
    except requests.ConnectionError as e:
        logger.error(f"Ollama connection failed: {e}")
        raise ConnectionError("Ollama offline — execute: ollama serve") from e
    except requests.Timeout as e:
        logger.error(f"Ollama timeout after 180s: {e}")
        raise TimeoutError("Ollama demorou demais — tente pergunta mais curta") from e

    resposta = message.get("content", "")
    chamadas = message.get("tool_calls", [])
    if placeholder:
        placeholder.markdown(resposta)
    logger.info("Ollama response: %s chars, %s tool calls", len(resposta), len(chamadas))
    return resposta, chamadas


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
    caminho = str(relativo).strip().replace("\\", "/")
    if caminho.casefold().startswith("c:/host/"):
        caminho = caminho[2:]
    aliases = {Path(pasta).name.casefold(): Path(pasta) for pasta in WORKSPACES}
    for nome, alias in (
        ("area de trabalho", "desktop"),
        ("área de trabalho", "desktop"),
        ("documentos", "documents"),
        ("imagens", "pictures"),
    ):
        if alias in aliases:
            aliases[nome] = aliases[alias]

    raiz_usuario = os.environ.get("IRIS_WINDOWS_USER_ROOT", "C:/Users/Administrador").replace("\\", "/")
    prefixo = raiz_usuario.rstrip("/").casefold() + "/"
    if caminho.casefold().startswith(prefixo):
        restante = caminho[len(prefixo) :]
        pasta_windows, _, cauda = restante.partition("/")
        montagem = {"desktop": "desktop", "documents": "documents", "downloads": "downloads", "pictures": "pictures"}.get(pasta_windows.casefold())
        if montagem in aliases:
            caminho = str(aliases[montagem] / cauda)

    candidato = None
    caminho_sem_barra = caminho.lstrip("/")
    for alias, raiz in sorted(aliases.items(), key=lambda item: len(item[0]), reverse=True):
        if caminho_sem_barra.casefold() == alias or caminho_sem_barra.casefold().startswith(alias + "/"):
            cauda = caminho_sem_barra[len(alias) :].lstrip("/")
            candidato = raiz / cauda
            break

    if candidato is None:
        caminho_path = Path(caminho)
        if caminho_path.is_absolute():
            candidato = caminho_path
        else:
            candidato = Path(PASTA_PRINCIPAL) / caminho
            for pasta in WORKSPACES:
                existente = Path(pasta) / caminho
                if existente.is_file():
                    candidato = existente
                    break

    resolvido = candidato.resolve()
    raizes_permitidas = [Path(pasta).resolve() for pasta in WORKSPACES]
    if not any(resolvido == raiz or raiz in resolvido.parents for raiz in raizes_permitidas):
        raise PermissionError("O caminho está fora das pastas pessoais autorizadas.")
    return str(resolvido)


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
    if not motores:
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
    acoes_pc = {
        "abrir_url": "open_url",
        "posicao_mouse": "get_position",
        "capturar_tela": "screenshot",
        "mover_mouse": "move_mouse",
        "clicar_mouse": "click",
        "digitar_texto": "type",
        "pressionar_tecla": "press_key",
        "atalho_teclado": "hotkey",
    }
    if acao in acoes_pc:
        if not PC_ACCESS_ENABLED:
            return json.dumps({"status": "error", "message": "Acesso ao PC desativado."}, ensure_ascii=False)
        resultado = execute_mouse_keyboard_action(acoes_pc[acao], params)
        if acao == "capturar_tela" and resultado.get("status") == "ok":
            return SCREENSHOT_MARKER + resultado.get("image_b64", "")
        return json.dumps(resultado, ensure_ascii=False)

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


def _extrair_escritas_multilinha(texto: str) -> list[dict]:
    padrao = re.compile(
        r'"name"\s*:\s*"escrever_arquivo"\s*,\s*"parameters"\s*:\s*\{\s*'
        r'"caminho"\s*:\s*"(?P<caminho>(?:\\.|[^"\\])*)"\s*,\s*'
        r'"conteudo"\s*:\s*"'
    )
    correspondencias = list(padrao.finditer(texto))
    if not correspondencias or not re.match(r'^\s*\{\s*"name"\s*:', texto):
        return []

    def decodificar(valor: str) -> str:
        saida = []
        indice = 0
        escapes = {"n": "\n", "r": "\r", "t": "\t", '"': '"', "\\": "\\", "/": "/"}
        while indice < len(valor):
            if valor[indice] == "\\" and indice + 1 < len(valor):
                seguinte = valor[indice + 1]
                saida.append(escapes.get(seguinte, seguinte))
                indice += 2
            else:
                saida.append(valor[indice])
                indice += 1
        return "".join(saida)

    chamadas = []
    fim_anterior = 0
    for match in correspondencias:
        intervalo = texto[fim_anterior : match.start()]
        if re.sub(r"[\s{}]", "", intervalo):
            return []
        inicio = match.end()
        indice = inicio
        escapado = False
        while indice < len(texto):
            caractere = texto[indice]
            if escapado:
                escapado = False
            elif caractere == "\\":
                escapado = True
            elif caractere == '"':
                break
            indice += 1
        if indice == len(texto):
            return []
        caminho = decodificar(match.group("caminho"))
        conteudo = decodificar(texto[inicio:indice])
        chamada = {"function": {"name": "escrever_arquivo", "arguments": {"caminho": caminho, "conteudo": conteudo}}}
        if chamadas and chamadas[-1]["function"]["arguments"]["caminho"] == caminho:
            anterior = chamadas[-1]["function"]["arguments"]["conteudo"]
            if conteudo.startswith(anterior):
                chamadas[-1]["function"]["arguments"]["conteudo"] = conteudo
            elif not anterior.startswith(conteudo):
                chamadas[-1]["function"]["arguments"]["conteudo"] += conteudo
        else:
            chamadas.append(chamada)
        fim_anterior = indice + 1

    if re.sub(r"[\s{}]", "", texto[fim_anterior:]):
        return []
    return chamadas


def extrair_chamadas_texto(texto: str) -> list[dict]:
    decoder = json.JSONDecoder()
    restante = texto.strip()
    chamadas: list[dict] = []
    nomes_permitidos = {
        "ler_arquivo", "escrever_arquivo", "listar_pasta", "executar_comando", "executar_python",
        "abrir_url", "posicao_mouse", "capturar_tela", "mover_mouse", "clicar_mouse", "digitar_texto",
        "pressionar_tecla", "atalho_teclado",
    }
    while restante:
        try:
            objeto, consumidos = decoder.raw_decode(restante)
        except json.JSONDecodeError:
            return _extrair_escritas_multilinha(texto)
        nome = objeto.get("name") if isinstance(objeto, dict) else None
        parametros = objeto.get("parameters") if isinstance(objeto, dict) else None
        if nome not in nomes_permitidos or not isinstance(parametros, dict):
            return []
        if nome == "escrever_arquivo":
            caminho = parametros.get("caminho", parametros.get("path"))
            conteudo = parametros.get("conteudo", parametros.get("content"))
            if not isinstance(caminho, str) or not isinstance(conteudo, str):
                return []
            parametros = {"caminho": caminho, "conteudo": conteudo}
            if chamadas and chamadas[-1]["function"]["name"] == nome:
                anterior = chamadas[-1]["function"]["arguments"]
                if anterior["caminho"] == caminho:
                    parte_anterior = anterior["conteudo"]
                    if conteudo.startswith(parte_anterior):
                        anterior["conteudo"] = conteudo
                    elif not parte_anterior.startswith(conteudo):
                        anterior["conteudo"] += conteudo
                    restante = restante[consumidos:].lstrip()
                    continue
        chamadas.append({"function": {"name": nome, "arguments": parametros}})
        restante = restante[consumidos:].lstrip()
    return chamadas


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
    perfil_agente: str = "geral",
) -> str:
    web = pesquisar_web(pergunta, motores)
    msg = SYSTEM_PROMPT
    perfil = AGENTES.get(perfil_agente, AGENTES["geral"])
    msg += f"\n\n--- ESPECIALIDADE ATIVA: {perfil['nome']} ---\n{perfil['instrucoes']}"
    msg += "\n\nPastas de gravação disponíveis: /app/projetos, /host/Desktop, /host/Documents, /host/Downloads e /host/Pictures. Use o caminho da pasta solicitado pelo usuário."
    if PC_ACCESS_ENABLED and host_companion_available():
        msg += "\n\nControle do PC ativo: abrir_url (abre no navegador padrão do Windows), posicao_mouse, capturar_tela, mover_mouse, clicar_mouse, digitar_texto, pressionar_tecla e atalho_teclado. Para sites, use abrir_url e nunca o comando start no shell Linux. Só use quando a solicitação envolver uma ação no desktop; nunca alegue ações sem retorno da ferramenta."
    else:
        msg += "\n\nControle do PC desativado ou desconectado. Não alegue que usou mouse, teclado ou tela."
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
    perfil_agente: str = "geral",
) -> tuple[str, list[str]]:
    """Loop agente: chama Ollama, executa ferramentas, repete até concluir.
    
    IMPORTANT: historico_msgs is the FULL agent history (all previous user/assistant exchanges).
    This preserves context across multiple turns in the same session.
    """
    log_ferramentas: list[str] = []
    sistema = montar_contexto_sistema(
        pergunta, motores, codigo_aberto, caminho_aberto, bool(imagem_b64_val), perfil_agente
    )

    # Build messages: system + full history + new question
    mensagens = [{"role": "system", "content": sistema}]
    
    # Include ALL historical messages, not just last 20 (preserve full context)
    for m in historico_msgs:
        if m["role"] in ("user", "assistant") and "content" in m:
            mensagens.append({"role": m["role"], "content": m["content"]})
    
    # Current question
    mensagens.append({"role": "user", "content": pergunta})

    resposta_final = ""
    imagem_para_analise = imagem_b64_val
    modelo_atual = modelo
    iteracao = 0
    for iteracao in range(max_iteracoes):
        logger.info(f"Iteration {iteracao+1}/{max_iteracoes}, context msgs={len(mensagens)}")
        resposta, chamadas = chamar_ollama(
            mensagens, placeholder, imagem_para_analise, modelo_atual, perfil_agente
        )
        imagem_para_analise = None
        chamadas_nativas = bool(chamadas)
        if not chamadas_nativas:
            chamadas = extrair_chamadas_texto(resposta)
        resposta_final = "" if chamadas else resposta

        mensagem_assistente = {"role": "assistant", "content": resposta}
        if chamadas_nativas:
            mensagem_assistente["tool_calls"] = chamadas
        mensagens.append(mensagem_assistente)
        if not chamadas:
            break

        logger.info("Executing %s native tool calls", len(chamadas))
        imagem_capturada = None
        resultados_texto = []
        for chamada in chamadas:
            funcao = chamada.get("function", {})
            acao = funcao.get("name", "")
            parametros = funcao.get("arguments", {})
            if isinstance(parametros, str):
                try:
                    parametros = json.loads(parametros)
                except json.JSONDecodeError:
                    parametros = {}
            resultado = executar_ferramenta(acao, parametros)
            if acao == "capturar_tela" and resultado.startswith(SCREENSHOT_MARKER):
                imagem_capturada = resultado[len(SCREENSHOT_MARKER) :]
                resultado = "Captura realizada e anexada para análise visual."
                log_ferramentas.append("capturar_tela: captura anexada para análise")
            else:
                log_ferramentas.append(f"{acao}: {resultado[:200]}")
            if chamadas_nativas:
                mensagens.append({"role": "tool", "tool_name": acao, "content": resultado})
            else:
                resultados_texto.append(f"[{acao}] {resultado}")

        if resultados_texto:
            mensagens.append({"role": "user", "content": "Resultados reais das ferramentas:\n" + "\n\n".join(resultados_texto)})

        if imagem_capturada:
            mensagens.append({"role": "user", "content": "Analise a captura da tela anexada e responda ao pedido."})
            imagem_para_analise = imagem_capturada
            modelo_atual = OLLAMA_VISION

    logger.info(f"Agent loop completed after {iteracao+1} iterations, final response: {len(resposta_final)} chars")
    return resposta_final, log_ferramentas
