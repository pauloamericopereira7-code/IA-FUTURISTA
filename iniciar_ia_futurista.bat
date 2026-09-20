@echo off
REM -*- coding: utf-8 -*-
REM Iniciar IA Futurista - Script de Startup

echo.
echo ========================================
echo   IA FUTURISTA - Iniciando...
echo ========================================
echo.

REM Get the directory where this script is located
for %%i in ("%~dp0") do set SCRIPT_DIR=%%~fi

REM Navigate to the project directory
cd /d "%SCRIPT_DIR%\futurista"

echo [*] Diretorio: %cd%
echo [*] Verificando Docker...

REM Check if Docker is running
docker ps >nul 2>&1
if errorlevel 1 (
    echo [!] Docker nao esta rodando! Iniciando Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker.exe"
    timeout /t 10 /nobreak
)

echo [*] Iniciando IA Futurista via Docker...
docker compose up -d

echo [*] Aguardando container ficar saudavel...
timeout /t 5 /nobreak

REM Wait for container to be healthy
for /L %%i in (1,1,30) do (
    docker ps | find "ia-futurista" | find "healthy" >nul 2>&1
    if not errorlevel 1 (
        echo [OK] Container esta saudavel!
        goto :healthy
    )
    timeout /t 1 /nobreak
)

:healthy
echo.
echo ========================================
echo   IA FUTURISTA ONLINE
echo ========================================
echo.
echo [*] Abrindo navegador em 3 segundos...
timeout /t 3 /nobreak

REM Open browser
start "" "http://127.0.0.1:8742"

echo [OK] Abra http://127.0.0.1:8742 em seu navegador
echo.
echo Pressione qualquer tecla para fechar esta janela...
pause >nul
