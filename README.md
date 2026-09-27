# IA Futurista

Agente Cursor local via Ollama.

## Início rápido no Windows

Para abrir o chat com a ponte de mouse/teclado, use `abrir_ia.bat` ou o atalho **Íris IA** criado na Área de Trabalho. O inicializador sobe a ponte Windows autenticada, inicia o contêiner e abre http://localhost:8742.

O pacote local criado para esta máquina fica em `Desktop\IrisIA`; `Abrir_Iris.bat` chama o inicializador do projeto em `Downloads\IA_Futurista\futurista`. Se o projeto for movido, atualize o caminho `PROJECT` nesse arquivo.

O usuário e o token da ponte são locais. `.iris_host_token` é ignorado pelo Git e montado como somente leitura no contêiner. A porta web fica limitada a `127.0.0.1`; a ponte aceita somente o contêiner autenticado na rede Docker configurada.

## Modelos e custos

A instalação padrão usa Ollama local: `llama3.2:3b` para conversa e `llava:7b` para análise de imagens. Programação e Design usam `qwen2.5-coder:3b` quando esse modelo estiver instalado; caso contrário, o app usa o modelo padrão.

```powershell
ollama pull llama3.2:3b
ollama pull llava:7b
ollama pull qwen2.5-coder:3b
```

Inferência local não consome créditos de API paga. Isso não altera limites de crédito de GitHub Copilot ou de outros serviços externos. Geração de imagens e vídeos ainda não está conectada.

## Pastas e acesso ao PC

O agente pode gravar sem confirmação por arquivo em `projetos`, Área de Trabalho, Documentos, Downloads e Imagens. O controle de mouse/teclado fica disponível pelo interruptor **Controle do computador** na barra lateral. Desative-o para revogar a permissão.

Os mounts do Compose usam `C:\Users\Administrador`; em outra conta Windows, atualize os caminhos de volume e `IRIS_WINDOWS_USER_ROOT` em `docker-compose.yml`.

## Execução sem a ponte

É possível iniciar apenas a API/chat com `docker compose up -d --build`, mas o controle do desktop requer a ponte Windows iniciada pelo `abrir_ia.bat`.

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
