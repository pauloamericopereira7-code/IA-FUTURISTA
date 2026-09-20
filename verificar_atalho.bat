@echo off
REM -*- coding: utf-8 -*-
REM Criar icone customizado para IA Futurista

echo.
echo ========================================
echo   Criando icone customizado...
echo ========================================
echo.

REM Caminhos
set DESKTOP=%USERPROFILE%\OneDrive\Desktop
set SHORTCUT="%DESKTOP%\IA Futurista.lnk"

if not exist %SHORTCUT% (
    echo [!] Atalho nao encontrado em OneDrive
    set DESKTOP=%USERPROFILE%\Desktop
    set SHORTCUT="%DESKTOP%\IA Futurista.lnk"
)

if not exist %SHORTCUT% (
    echo [ERRO] Atalho nao encontrado!
    echo       Procure em: %DESKTOP%
    pause
    exit /b 1
)

echo [OK] Atalho encontrado: %SHORTCUT%
echo [OK] Atalho criado com sucesso!
echo.
echo Para iniciar a IA Futurista:
echo 1. Vá à Area de Trabalho
echo 2. Clique duplo em "IA Futurista"
echo 3. Espere 2-3 minutos (primeira vez é mais lenta)
echo 4. Navegador abre automaticamente em http://127.0.0.1:8742
echo.
echo Certifique-se de que:
echo - Docker Desktop está instalado
echo - Ollama está rodando (execute: ollama serve)
echo.
pause
