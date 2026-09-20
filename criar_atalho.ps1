# -*- coding: utf-8 -*-
# Criar atalho na Area de Trabalho para IA Futurista

$Desktop = [Environment]::GetFolderPath("Desktop")
$ScriptPath = Get-Location
$BatchFile = Join-Path $ScriptPath "iniciar_ia_futurista.bat"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Criando Atalho na Area de Trabalho" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se arquivo existe
if (-Not (Test-Path $BatchFile)) {
    Write-Host "[ERRO] Arquivo nao encontrado: $BatchFile" -ForegroundColor Red
    exit 1
}

# Criar COM object para atalho
$WshShell = New-Object -ComObject WScript.Shell
$ShortcutPath = Join-Path $Desktop "IA Futurista.lnk"

Write-Host "[*] Criando atalho..." -ForegroundColor Yellow
Write-Host "    De: $BatchFile"
Write-Host "    Para: $ShortcutPath"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $BatchFile
$Shortcut.WorkingDirectory = $ScriptPath
$Shortcut.Description = "Inicia a IA Futurista localmente"
$Shortcut.IconLocation = "C:\Windows\System32\cmd.exe,0"  # Ícone do cmd
$Shortcut.Save()

Write-Host "[OK] Atalho criado com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "Local: $ShortcutPath" -ForegroundColor Green
Write-Host ""
Write-Host "[+] Para usar:" -ForegroundColor Cyan
Write-Host "    1. Vá à Area de Trabalho"
Write-Host "    2. Clique duplo em 'IA Futurista'"
Write-Host "    3. Espere carregar (1-2 minutos na primeira vez)"
Write-Host "    4. Navegador abre automaticamente"
Write-Host ""

Read-Host "Pressione Enter para sair"
