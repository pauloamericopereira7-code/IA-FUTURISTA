@echo off
setlocal EnableExtensions
chcp 65001 >nul 2>&1
title IA Futurista — Instalador Completo (1 clique)
color 0B

echo.
echo  ============================================
echo    IA FUTURISTA — Instalador de 1 clique
echo  ============================================
echo.
echo  Duplo clique e pronto. Pode pedir login Git 1x.
echo.

set "BAT_ORIGEM=%~dp0"
set "BAT_ORIGEM=%BAT_ORIGEM:~0,-1%"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$raw = Get-Content -LiteralPath '%~f0' -Raw -Encoding UTF8;" ^
  "$mark = ':POWERSHELL';" ^
  "$i = $raw.IndexOf($mark);" ^
  "if ($i -lt 0) { Write-Host 'ERRO interno do instalador.' -ForegroundColor Red; exit 1 };" ^
  "$script = $raw.Substring($i + $mark.Length);" ^
  "$env:BAT_ORIGEM = '%BAT_ORIGEM%';" ^
  "Invoke-Expression $script"

set "ERR=%ERRORLEVEL%"
echo.
if not "%ERR%"=="0" (
    echo  Algo falhou. Leia as mensagens acima.
)
pause
exit /b %ERR%

:POWERSHELL
# =============================================================================
# IA FUTURISTA — Instalador completo (embutido no .bat)
# =============================================================================
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$NomeIA     = "IA Futurista"
$PastaDest  = if (Test-Path "D:\") { "D:\IA_Futurista" } else { "C:\IA_Futurista" }
$RepoUrl    = "https://origin.cursor.com/git/paulo-americo/tmp-a8f6abf409805288.git"
$Porta      = 8742
$Modelo     = "qwen2.5-coder:7b"
$Desktop    = [Environment]::GetFolderPath("Desktop")
$BatOrigem  = $env:BAT_ORIGEM

function Step($n, $total, $msg) {
    Write-Host "[$n/$total] $msg" -ForegroundColor Cyan
}
function Ok($msg)  { Write-Host "      $msg" -ForegroundColor Green }
function Warn($msg){ Write-Host "      $msg" -ForegroundColor Yellow }
function Fail($msg){ Write-Host " ERRO: $msg" -ForegroundColor Red }

$total = 9

# --- 1: Criar pasta ---
Step 1 $total "Criando pasta $PastaDest ..."
New-Item -ItemType Directory -Path $PastaDest -Force | Out-Null
New-Item -ItemType Directory -Path "$PastaDest\projetos" -Force | Out-Null
Ok "Pasta criada"

# --- 2: Obter arquivos ---
Step 2 $total "Obtendo arquivos do projeto ..."
$temArquivos = $false

# Se .bat esta na raiz do repo, usar subpasta futurista
if ($BatOrigem -and -not (Test-Path "$BatOrigem\server.py")) {
    $subFuturista = Join-Path $BatOrigem "futurista"
    if (Test-Path "$subFuturista\server.py") {
        $BatOrigem = $subFuturista
    }
    # Se bat esta em futurista mas origem errada, subir um nivel
    $pai = Split-Path $BatOrigem -Parent
    if (-not (Test-Path "$BatOrigem\server.py") -and (Test-Path "$pai\futurista\server.py")) {
        $BatOrigem = "$pai\futurista"
    }
}

if ($BatOrigem -and (Test-Path "$BatOrigem\server.py")) {
    Copy-Item -Path "$BatOrigem\*" -Destination $PastaDest -Recurse -Force `
        -Exclude @(".venv", "__pycache__", ".git", "INSTALAR_DE_UMA_VEZ.bat")
    Copy-Item -Path "$BatOrigem\INSTALAR_DE_UMA_VEZ.bat" -Destination $PastaDest -Force -ErrorAction SilentlyContinue
    $temArquivos = Test-Path "$PastaDest\server.py"
    if ($temArquivos) { Ok "Copiado de $BatOrigem" }
}
elseif (Test-Path "$PastaDest\server.py") {
    $temArquivos = $true
    Warn "Arquivos ja existem em $PastaDest"
}
else {
    $git = Get-Command git -ErrorAction SilentlyContinue
    if ($git) {
        Warn "Git vai pedir login Cursor (1x) — preencha e clique Continue"
        $cloneDir = Join-Path $env:TEMP "ia-futurista-clone"
        if (Test-Path $cloneDir) { Remove-Item $cloneDir -Recurse -Force }
        & git clone --depth 1 $RepoUrl $cloneDir 2>&1 | Out-Host
        if (Test-Path "$cloneDir\futurista\server.py") {
            Copy-Item "$cloneDir\futurista\*" $PastaDest -Recurse -Force
            $temArquivos = $true
            Ok "Baixado via Git"
        }
        elseif (Test-Path "$cloneDir\server.py") {
            Copy-Item "$cloneDir\*" $PastaDest -Recurse -Force
            $temArquivos = $true
            Ok "Baixado via Git"
        }
    }
}

if (-not $temArquivos -and (Test-Path "D:\IA_Futurista.zip")) {
    Expand-Archive -Path "D:\IA_Futurista.zip" -DestinationPath $PastaDest -Force
    $temArquivos = Test-Path "$PastaDest\server.py"
    if ($temArquivos) { Ok "Extraido de IA_Futurista.zip" }
}

if (-not $temArquivos) {
    Write-Host ""
    Fail "Nao encontrei os arquivos do projeto."
    Write-Host ""
    Write-Host "  Solucao mais facil:" -ForegroundColor Yellow
    Write-Host "  1. Copie a pasta 'futurista' do Cursor para qualquer lugar" -ForegroundColor White
    Write-Host "  2. Coloque este .bat DENTRO dessa pasta" -ForegroundColor White
    Write-Host "  3. Duplo clique de novo" -ForegroundColor White
    Write-Host ""
    Write-Host "  Ou faca login no Git quando pedir e rode novamente." -ForegroundColor White
    Write-Host "  Pasta ja criada em: $PastaDest" -ForegroundColor Gray
    exit 1
}

Set-Location $PastaDest

# --- 3: Docker ---
Step 3 $total "Verificando Docker ..."
$dockerOk = $false
try {
    $null = docker info 2>$null
    if ($LASTEXITCODE -eq 0) { $dockerOk = $true; Ok "Docker OK" }
    else { Warn "Sem Docker — usando Python local" }
} catch {
    Warn "Sem Docker — usando Python local"
}

# --- 4: Ollama ---
Step 4 $total "Verificando Ollama ..."
$ollamaOk = $false
try {
    $null = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 3
    $ollamaOk = $true
    Ok "Ollama rodando"
} catch {
    $ollamaExe = Get-Command ollama -ErrorAction SilentlyContinue
    if ($ollamaExe) {
        Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
        Start-Sleep -Seconds 4
        try {
            $null = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5
            $ollamaOk = $true
            Ok "Ollama iniciado"
        } catch {
            Warn "Inicie manualmente: ollama serve"
        }
    } else {
        Warn "Instale Ollama em https://ollama.com"
    }
}

if ($ollamaOk) {
    Write-Host "      Baixando modelo $Modelo (pode demorar) ..." -ForegroundColor Gray
    & ollama pull $Modelo
}

# --- 5: Subir servidor ---
Step 5 $total "Iniciando IA Futurista na porta $Porta ..."
if ($dockerOk -and (Test-Path "$PastaDest\docker-compose.yml")) {
    docker compose -f "$PastaDest\docker-compose.yml" down 2>$null
    docker compose -f "$PastaDest\docker-compose.yml" up -d --build
    if ($LASTEXITCODE -ne 0) {
        $dockerOk = $false
        Warn "Docker falhou — tentando Python ..."
    } else {
        Ok "Container ia-futurista rodando"
    }
}

if (-not $dockerOk) {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        Fail "Python nao encontrado. Instale Python 3.10+"
        exit 1
    }
    if (-not (Test-Path "$PastaDest\.venv")) {
        python -m venv "$PastaDest\.venv"
    }
    & "$PastaDest\.venv\Scripts\pip.exe" install -q -r "$PastaDest\requirements.txt"
    Get-NetTCPConnection -LocalPort $Porta -ErrorAction SilentlyContinue |
        ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
    Start-Process -FilePath "$PastaDest\.venv\Scripts\python.exe" `
        -ArgumentList "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", $Porta `
        -WorkingDirectory $PastaDest -WindowStyle Hidden
    Ok "Servidor Python iniciado"
}

# --- 6: Aguardar online ---
Step 6 $total "Aguardando servidor ..."
$url = "http://127.0.0.1:$Porta"
$online = $false
for ($i = 1; $i -le 30; $i++) {
    try {
        $null = Invoke-WebRequest -Uri $url -TimeoutSec 2 -UseBasicParsing
        $online = $true
        break
    } catch {
        Start-Sleep -Seconds 2
    }
}
if ($online) { Ok "Servidor online!" } else { Warn "Abra manualmente: $url" }

# --- 7: Atalhos ---
Step 7 $total "Criando atalhos na Area de Trabalho ..."
$Wsh = New-Object -ComObject WScript.Shell
$launcher = Join-Path $PastaDest "abrir_ia.bat"
@"
@echo off
cd /d "$PastaDest"
where docker >nul 2>&1 && docker compose up -d 2>nul
start "" "$url"
"@ | Set-Content -Path $launcher -Encoding ASCII

foreach ($nome in @("IA Futurista", "Futuristico")) {
    $lnk = Join-Path $Desktop "$nome.lnk"
    $s = $Wsh.CreateShortcut($lnk)
    $s.TargetPath       = $launcher
    $s.WorkingDirectory = $PastaDest
    $s.Description      = "$NomeIA — Agente Cursor (porta $Porta)"
    $s.IconLocation     = "$env:SystemRoot\System32\imageres.dll,109"
    $s.Save()
    Ok $nome
}

# --- 8: ZIP backup ---
Step 8 $total "Criando ZIP de backup ..."
$zipPath = if (Test-Path "D:\") { "D:\IA_Futurista.zip" } else { "C:\IA_Futurista.zip" }
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path "$PastaDest\*" -DestinationPath $zipPath -Force
Ok $zipPath

# --- 9: Copiar instalador para destino ---
Step 9 $total "Salvando instalador em $PastaDest ..."
if ($BatOrigem -and (Test-Path "$BatOrigem\INSTALAR_DE_UMA_VEZ.bat")) {
    Copy-Item "$BatOrigem\INSTALAR_DE_UMA_VEZ.bat" $PastaDest -Force
    Ok "INSTALAR_DE_UMA_VEZ.bat copiado"
}

# --- Concluido ---
Write-Host ""
Write-Host " ============================================" -ForegroundColor Cyan
Write-Host "   INSTALACAO CONCLUIDA!" -ForegroundColor Green
Write-Host " ============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Pasta:   $PastaDest"
Write-Host "  URL:     $url"
Write-Host "  Atalhos: IA Futurista + Futuristico"
Write-Host "  ZIP:     $zipPath"
Write-Host ""

Start-Process $url
Start-Process $launcher
