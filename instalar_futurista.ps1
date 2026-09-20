# -*- coding: utf-8 -*-
# Instalador IA Futurista — atalho na Área de Trabalho + ZIP em D:\
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$NomeIA      = "IA Futurista"
$NomeAtalho  = "Futuristico"
$PastaOrigem = Split-Path -Parent $MyInvocation.MyCommand.Path
$PastaDest   = "D:\IA_Futurista"
$ZipDestino  = "D:\IA_Futurista.zip"
$Desktop     = [Environment]::GetFolderPath("Desktop")
$AtalhoPath  = Join-Path $Desktop "$NomeAtalho.lnk"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INSTALADOR $NomeIA" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Cyan

# Criar pasta D:\IA_Futurista
if (-not (Test-Path "D:\")) {
    Write-Host "AVISO: Unidade D: nao encontrada. Usando C:\IA_Futurista" -ForegroundColor Yellow
    $PastaDest = "C:\IA_Futurista"
    $ZipDestino = "C:\IA_Futurista.zip"
}

Write-Host "[1/4] Copiando arquivos para $PastaDest ..."
New-Item -ItemType Directory -Path $PastaDest -Force | Out-Null
New-Item -ItemType Directory -Path "$PastaDest\projetos" -Force | Out-Null
Copy-Item -Path "$PastaOrigem\*" -Destination $PastaDest -Recurse -Force -Exclude ".venv","__pycache__"

# Ambiente virtual Python
Write-Host "[2/4] Configurando ambiente Python ..."
$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    Set-Location $PastaDest
    if (-not (Test-Path "$PastaDest\.venv")) {
        python -m venv .venv
    }
    & "$PastaDest\.venv\Scripts\pip.exe" install -q -r "$PastaDest\requirements.txt"
}

# Criar ZIP em D:\
Write-Host "[3/4] Criando ZIP em $ZipDestino ..."
if (Test-Path $ZipDestino) { Remove-Item $ZipDestino -Force }
Compress-Archive -Path "$PastaDest\*" -DestinationPath $ZipDestino -Force

# Atalho na Area de Trabalho
Write-Host "[4/4] Criando atalhos na Area de Trabalho ..."
$WshShell = New-Object -ComObject WScript.Shell
foreach ($nome in @("Futuristico", "IA Futurista")) {
    $path = Join-Path $Desktop "$nome.lnk"
    $Atalho = $WshShell.CreateShortcut($path)
    $Atalho.TargetPath       = "$PastaDest\abrir_ia.bat"
    $Atalho.WorkingDirectory = $PastaDest
    $Atalho.Description      = "$NomeIA — Agente Cursor (porta 8742)"
    $Atalho.IconLocation     = "$env:SystemRoot\System32\imageres.dll,109"
    $Atalho.Save()
    Write-Host "  Atalho: $path"
}

Write-Host ""
Write-Host "INSTALACAO CONCLUIDA!" -ForegroundColor Green
Write-Host "  Pasta:   $PastaDest"
Write-Host "  ZIP:     $ZipDestino"
Write-Host "  Atalhos: Futuristico.lnk + IA Futurista.lnk"
Write-Host ""
Write-Host "Clique duplo no atalho 'Futuristico' na Area de Trabalho para abrir a IA."
Write-Host "URL: http://localhost:8742"
Write-Host ""

# Abrir navegador
Start-Process "http://localhost:8742"
Start-Process "$PastaDest\abrir_ia.bat"
