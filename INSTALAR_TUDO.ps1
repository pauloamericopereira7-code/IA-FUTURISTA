#Requires -Version 5.1
# =============================================================================
# IA FUTURISTA — Instalador automatico completo
# Copie este arquivo INTEIRO, cole no PowerShell como Administrador OU:
#   powershell -ExecutionPolicy Bypass -File INSTALAR_TUDO.ps1
# =============================================================================

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$NomeIA     = "IA Futurista"
$PastaDest  = if (Test-Path "D:\") { "D:\IA_Futurista" } else { "C:\IA_Futurista" }
$Porta      = 8742
$Modelo     = "qwen2.5-coder:7b"
$Desktop    = [Environment]::GetFolderPath("Desktop")

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  INSTALADOR AUTOMATICO — $NomeIA" -ForegroundColor Magenta
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# --- PASSO 0: Garantir que a pasta de destino existe ---
Write-Host "[0/8] Criando pasta $PastaDest (se nao existir) ..."
New-Item -ItemType Directory -Path $PastaDest -Force | Out-Null
New-Item -ItemType Directory -Path "$PastaDest\projetos" -Force | Out-Null
Write-Host "      OK" -ForegroundColor Green

# --- PASSO 1: Origem dos arquivos ---
$PastaOrigem = $PSScriptRoot
if (-not (Test-Path "$PastaOrigem\server.py")) {
    if (Test-Path "$PastaDest\server.py") {
        $PastaOrigem = $PastaDest
        Write-Host "[1/8] Usando instalacao existente em $PastaDest" -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "ERRO: Arquivos do projeto nao encontrados." -ForegroundColor Red
        Write-Host ""
        Write-Host "A pasta $PastaDest foi criada, mas esta vazia." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Execute primeiro o bootstrap (cria pasta + baixa arquivos):" -ForegroundColor Cyan
        Write-Host "  powershell -ExecutionPolicy Bypass -File INSTALAR_DO_ZERO.ps1" -ForegroundColor White
        Write-Host ""
        Write-Host "Ou copie manualmente a pasta 'futurista' para $PastaDest" -ForegroundColor White
        Write-Host "Arquivos necessarios: server.py, docker-compose.yml, Dockerfile" -ForegroundColor Gray
        Write-Host ""
        Read-Host "Pressione Enter para sair"
        exit 1
    }
} else {
    Write-Host "[1/8] Origem: $PastaOrigem" -ForegroundColor Green
}

# --- PASSO 2: Copiar para D:\IA_Futurista (se origem for outra pasta) ---
if ($PastaOrigem -ne $PastaDest) {
    Write-Host "[2/8] Copiando para $PastaDest ..."
    Copy-Item -Path "$PastaOrigem\*" -Destination $PastaDest -Recurse -Force `
        -Exclude @(".venv", "__pycache__", ".git")
    Write-Host "      OK" -ForegroundColor Green
} else {
    Write-Host "[2/8] Arquivos ja em $PastaDest" -ForegroundColor Green
}

Set-Location $PastaDest

# --- PASSO 3: Verificar Docker ---
Write-Host "[3/8] Verificando Docker ..."
$dockerOk = $false
try {
    $null = docker info 2>$null
    if ($LASTEXITCODE -eq 0) { $dockerOk = $true }
} catch {}

if ($dockerOk) {
    Write-Host "      Docker OK" -ForegroundColor Green
} else {
    Write-Host "      AVISO: Docker nao encontrado — instalando modo Python local" -ForegroundColor Yellow
}

# --- PASSO 4: Verificar / instalar Ollama ---
Write-Host "[4/8] Verificando Ollama ..."
$ollamaOk = $false
try {
    $r = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 3
    $ollamaOk = $true
    Write-Host "      Ollama ja esta rodando" -ForegroundColor Green
} catch {
    $ollamaExe = Get-Command ollama -ErrorAction SilentlyContinue
    if ($ollamaExe) {
        Write-Host "      Iniciando Ollama em segundo plano ..."
        Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
        Start-Sleep -Seconds 4
        try {
            $null = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5
            $ollamaOk = $true
            Write-Host "      Ollama iniciado" -ForegroundColor Green
        } catch {
            Write-Host "      AVISO: Inicie manualmente: ollama serve" -ForegroundColor Yellow
        }
    } else {
        Write-Host "      AVISO: Instale Ollama em https://ollama.com" -ForegroundColor Yellow
    }
}

if ($ollamaOk) {
    Write-Host "      Baixando modelo $Modelo (pode demorar) ..."
    & ollama pull $Modelo
}

# --- PASSO 5: Subir IA Futurista ---
Write-Host "[5/8] Iniciando IA Futurista na porta $Porta ..."
if ($dockerOk -and (Test-Path "$PastaDest\docker-compose.yml")) {
    docker compose -f "$PastaDest\docker-compose.yml" down 2>$null
    docker compose -f "$PastaDest\docker-compose.yml" up -d --build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "      Docker falhou — tentando Python local ..." -ForegroundColor Yellow
        $dockerOk = $false
    } else {
        Write-Host "      Container ia-futurista rodando" -ForegroundColor Green
    }
}

if (-not $dockerOk) {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        Write-Host "      ERRO: Python nao encontrado. Instale Python 3.10+" -ForegroundColor Red
        exit 1
    }
    if (-not (Test-Path "$PastaDest\.venv")) {
        python -m venv "$PastaDest\.venv"
    }
    & "$PastaDest\.venv\Scripts\pip.exe" install -q -r "$PastaDest\requirements.txt"
    # Mata processo anterior na porta 8742
    Get-NetTCPConnection -LocalPort $Porta -ErrorAction SilentlyContinue |
        ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
    Start-Process -FilePath "$PastaDest\.venv\Scripts\python.exe" `
        -ArgumentList "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", $Porta `
        -WorkingDirectory $PastaDest -WindowStyle Hidden
    Write-Host "      Servidor Python iniciado" -ForegroundColor Green
}

# --- PASSO 6: Aguardar servidor ---
Write-Host "[6/8] Aguardando servidor ..."
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
if ($online) {
    Write-Host "      Servidor online!" -ForegroundColor Green
} else {
    Write-Host "      AVISO: Servidor demorou — tente abrir $url manualmente" -ForegroundColor Yellow
}

# --- PASSO 7: Atalhos na Area de Trabalho ---
Write-Host "[7/8] Criando atalhos na Area de Trabalho ..."
$Wsh = New-Object -ComObject WScript.Shell
$launcher = Join-Path $PastaDest "abrir_ia.bat"
if (-not (Test-Path $launcher)) {
    @"
@echo off
cd /d "$PastaDest"
where docker >nul 2>&1 && docker compose up -d 2>nul
start "" "$url"
"@ | Set-Content -Path $launcher -Encoding ASCII
}

foreach ($nome in @("IA Futurista", "Futuristico")) {
    $lnk = Join-Path $Desktop "$nome.lnk"
    $s = $Wsh.CreateShortcut($lnk)
    $s.TargetPath       = $launcher
    $s.WorkingDirectory = $PastaDest
    $s.Description      = "$NomeIA — Agente Cursor (porta $Porta)"
    $s.IconLocation     = "$env:SystemRoot\System32\imageres.dll,109"
    $s.Save()
    Write-Host "      Criado: $nome" -ForegroundColor Green
}

# --- PASSO 8: ZIP de backup ---
Write-Host "[8/8] Criando ZIP de backup ..."
$zipPath = if (Test-Path "D:\") { "D:\IA_Futurista.zip" } else { "C:\IA_Futurista.zip" }
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path "$PastaDest\*" -DestinationPath $zipPath -Force
Write-Host "      ZIP: $zipPath" -ForegroundColor Green

# --- Concluido ---
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  INSTALACAO CONCLUIDA!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Pasta:    $PastaDest"
Write-Host "  URL:      $url"
Write-Host "  Atalhos:  IA Futurista + Futuristico (Area de Trabalho)"
Write-Host "  ZIP:      $zipPath"
Write-Host ""
Write-Host "  Docker Desktop: container 'ia-futurista' porta $Porta"
Write-Host "  Ollama:         $Modelo"
Write-Host ""

Start-Process $url
Start-Process $launcher

Read-Host "Pressione Enter para fechar"
