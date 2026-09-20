#Requires -Version 5.1
# =============================================================================
# IA FUTURISTA — Bootstrap completo (cria pasta + baixa arquivos + instala)
#
# Cole ESTE BLOCO INTEIRO no PowerShell (nao precisa de cd antes):
#
#   irm https://raw.githubusercontent.com/...  (nao disponivel)
#
# Ou salve este arquivo e execute:
#   powershell -ExecutionPolicy Bypass -File INSTALAR_DO_ZERO.ps1
# =============================================================================

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$NomeIA    = "IA Futurista"
$PastaDest = if (Test-Path "D:\") { "D:\IA_Futurista" } else { "C:\IA_Futurista" }
$RepoUrl   = "https://origin.cursor.com/git/paulo-americo/tmp-a8f6abf409805288.git"
$PastaOrigem = $PSScriptRoot

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  $NomeIA — Instalacao do zero" -ForegroundColor Magenta
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# --- PASSO 0: Criar pasta de destino (resolve erro "caminho nao existe") ---
Write-Host "[0/9] Criando pasta $PastaDest ..."
New-Item -ItemType Directory -Path $PastaDest -Force | Out-Null
New-Item -ItemType Directory -Path "$PastaDest\projetos" -Force | Out-Null
Write-Host "      OK — pasta criada" -ForegroundColor Green

# --- PASSO 1: Obter arquivos do projeto ---
$temArquivos = (Test-Path "$PastaOrigem\server.py") -or (Test-Path "$PastaDest\server.py")

if (-not $temArquivos) {
    Write-Host "[1/9] Arquivos nao encontrados — tentando clonar repositorio ..."

    $git = Get-Command git -ErrorAction SilentlyContinue
    if ($git) {
        $cloneDir = Join-Path $env:TEMP "ia-futurista-clone"
        if (Test-Path $cloneDir) { Remove-Item $cloneDir -Recurse -Force }

        try {
            & git clone --depth 1 $RepoUrl $cloneDir 2>&1 | Out-Host
            if (Test-Path "$cloneDir\futurista\server.py") {
                $PastaOrigem = "$cloneDir\futurista"
                $temArquivos = $true
                Write-Host "      Clone OK" -ForegroundColor Green
            } elseif (Test-Path "$cloneDir\server.py") {
                $PastaOrigem = $cloneDir
                $temArquivos = $true
                Write-Host "      Clone OK (raiz)" -ForegroundColor Green
            }
        } catch {
            Write-Host "      Clone falhou: $_" -ForegroundColor Yellow
        }
    }
}

if (-not $temArquivos -and (Test-Path "D:\IA_Futurista.zip")) {
    Write-Host "[1/9] Extraindo D:\IA_Futurista.zip ..."
    Expand-Archive -Path "D:\IA_Futurista.zip" -DestinationPath $PastaDest -Force
    if (Test-Path "$PastaDest\server.py") { $temArquivos = $true; $PastaOrigem = $PastaDest }
}

if (-not $temArquivos) {
    Write-Host ""
    Write-Host "ERRO: Nao foi possivel obter os arquivos do projeto." -ForegroundColor Red
    Write-Host ""
    Write-Host "Opcoes:" -ForegroundColor Yellow
    Write-Host "  1. Clone manualmente:" -ForegroundColor White
    Write-Host "     git clone $RepoUrl D:\IA_Futurista\_repo" -ForegroundColor Gray
    Write-Host "     Copy-Item D:\IA_Futurista\_repo\futurista\* D:\IA_Futurista -Recurse" -ForegroundColor Gray
    Write-Host "  2. Copie a pasta 'futurista' do Cursor Cloud Agent para $PastaDest" -ForegroundColor White
    Write-Host "  3. Extraia IA_Futurista.zip em D:\" -ForegroundColor White
    Write-Host ""
    Write-Host "A pasta $PastaDest ja foi criada — copie os arquivos e execute:" -ForegroundColor Cyan
    Write-Host "  cd $PastaDest" -ForegroundColor White
    Write-Host "  powershell -ExecutionPolicy Bypass -File INSTALAR_TUDO.ps1" -ForegroundColor White
    Write-Host ""
    Read-Host "Pressione Enter para sair"
    exit 1
}

# --- PASSO 2: Copiar arquivos para destino ---
if ($PastaOrigem -ne $PastaDest) {
    Write-Host "[2/9] Copiando arquivos para $PastaDest ..."
    Copy-Item -Path "$PastaOrigem\*" -Destination $PastaDest -Recurse -Force `
        -Exclude @(".venv", "__pycache__", ".git")
    Write-Host "      OK" -ForegroundColor Green
} else {
    Write-Host "[2/9] Arquivos ja estao em $PastaDest" -ForegroundColor Green
}

Set-Location $PastaDest

# --- PASSO 3-9: Executar instalador principal ---
$instalador = Join-Path $PastaDest "INSTALAR_TUDO.ps1"
if (-not (Test-Path $instalador)) {
    Write-Host "ERRO: INSTALAR_TUDO.ps1 nao encontrado em $PastaDest" -ForegroundColor Red
    exit 1
}

Write-Host "[3/9] Executando instalador principal ..." -ForegroundColor Cyan
& powershell -ExecutionPolicy Bypass -File $instalador
