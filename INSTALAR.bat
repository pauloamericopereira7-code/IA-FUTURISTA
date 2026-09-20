@echo off
chcp 65001 >nul
echo Instalando IA Futurista...
powershell -ExecutionPolicy Bypass -File "%~dp0instalar_futurista.ps1"
pause
