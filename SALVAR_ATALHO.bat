@echo off
chcp 65001 >nul
title Salvar Atalho — IA Futurista
cd /d "%~dp0"
echo.
echo Criando atalho na Area de Trabalho...
powershell -ExecutionPolicy Bypass -File "%~dp0criar_atalho.ps1"
echo.
pause
