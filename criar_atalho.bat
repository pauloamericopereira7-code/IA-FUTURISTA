@echo off
REM Cria atalho IA Futurista + Futuristico na Area de Trabalho
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "%~dp0criar_atalho.ps1"
pause
