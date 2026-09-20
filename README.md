# IA Futurista

Agente Cursor local via Ollama.

## Docker (recomendado no seu PC)

Seu Docker Desktop já tem:

| Container | Porta |
|-----------|-------|
| cursor-docker | 9090 |
| open-webui | 3030 |
| **ia-futurista** | **8742** ← este projeto |

```bash
cd futurista
DOCKER.bat
# ou: docker compose up -d --build
```

Abre em http://127.0.0.1:8742

O container conecta no Ollama do Windows via `host.docker.internal:11434`.
Antes rode: `ollama serve` e `ollama pull qwen2.5-coder:7b`

## Sem Docker

```bash
pip install -r requirements.txt
python -m uvicorn server:app --host 0.0.0.0 --port 8742
```

Ou clique **`INSTALAR.bat`** → instala em `D:\IA_Futurista`

## Windows — primeira instalacao (pasta ainda nao existe)

Se `cd D:\IA_Futurista` der erro **"caminho nao existe"**, cole isto no PowerShell:

```powershell
# 1. Criar pasta
New-Item -ItemType Directory -Force -Path D:\IA_Futurista
cd D:\IA_Futurista

# 2. Baixar projeto (login Cursor/Git se pedir)
git clone https://origin.cursor.com/git/paulo-americo/tmp-a8f6abf409805288.git D:\IA_Futurista\_repo
Copy-Item D:\IA_Futurista\_repo\futurista\* D:\IA_Futurista -Recurse -Force

# 3. Instalar tudo (Docker + Ollama + atalhos)
Set-ExecutionPolicy Bypass -Scope Process -Force
.\INSTALAR_TUDO.ps1
```

**Alternativa:** execute `INSTALAR_DO_ZERO.bat` (cria pasta, clona e instala automaticamente).

### Instalador de 1 clique (recomendado)

Duplo clique em **`INSTALAR_DE_UMA_VEZ.bat`** — faz tudo sozinho:

1. Cria `D:\IA_Futurista`
2. Copia arquivos (ou baixa via Git)
3. Sobe Docker / Python na porta 8742
4. Configura Ollama + modelo
5. Cria atalhos **IA Futurista** e **Futuristico**
6. Abre o navegador

Coloque o `.bat` **dentro da pasta futurista** antes de executar (evita pedir login Git).

Depois da instalacao, abra http://127.0.0.1:8742 ou use o atalho **IA Futurista** na Area de Trabalho.
