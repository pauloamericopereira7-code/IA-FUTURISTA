# -*- coding: utf-8 -*-
# Cria atalho IA Futurista na Area de Trabalho
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$PastaApp   = Split-Path -Parent $MyInvocation.MyCommand.Path
$Desktop    = [Environment]::GetFolderPath("Desktop")
$NomeAtalho = "IA Futurista"
$CaminhoBat = Join-Path $PastaApp "abrir_ia.bat"

# Fallback se rodou de D:\IA_Futurista
if (-not (Test-Path $CaminhoBat)) {
    if (Test-Path "D:\IA_Futurista\abrir_ia.bat") {
        $PastaApp   = "D:\IA_Futurista"
        $CaminhoBat = "D:\IA_Futurista\abrir_ia.bat"
    } elseif (Test-Path "C:\IA_Futurista\abrir_ia.bat") {
        $PastaApp   = "C:\IA_Futurista"
        $CaminhoBat = "C:\IA_Futurista\abrir_ia.bat"
    }
}

$Atalho1 = Join-Path $Desktop "$NomeAtalho.lnk"
$Atalho2 = Join-Path $Desktop "Futuristico.lnk"

$Wsh = New-Object -ComObject WScript.Shell

foreach ($path in @($Atalho1, $Atalho2)) {
    $s = $Wsh.CreateShortcut($path)
    $s.TargetPath       = $CaminhoBat
    $s.WorkingDirectory = $PastaApp
    $s.Description      = "IA Futurista — Agente Cursor local (porta 8742)"
    $s.IconLocation     = "$env:SystemRoot\System32\imageres.dll,109"
    $s.Save()
    Write-Host "Atalho criado: $path" -ForegroundColor Green
}

Write-Host ""
Write-Host "Pronto! Clique duplo em 'IA Futurista' ou 'Futuristico' na Area de Trabalho." -ForegroundColor Cyan
Start-Process $CaminhoBat
