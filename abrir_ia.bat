@echo off
chcp 65001 >nul
title Iris
cd /d "%~dp0"

REM Initialize a local bearer token before mounting it into Docker.
where py >nul 2>&1
if %errorlevel% neq 0 (
    echo Python Launcher (py) nao encontrado.
    pause
    exit /b 1
)
py -3 "%~dp0host_companion.py" --init-token
if %errorlevel% neq 0 (
    echo Nao foi possivel inicializar a ponte do computador.
    pause
    exit /b 1
)

REM Start the Windows-only desktop bridge in a minimized window.
start "Iris Desktop Bridge" /min py -3 "%~dp0host_companion.py"

REM Start the chat container with the authenticated host bridge.
where docker >nul 2>&1
if %errorlevel%==0 (
    if exist "%~dp0docker-compose.yml" (
        docker compose -f "%~dp0docker-compose.yml" up -d --build
    ) else (
        echo docker-compose.yml nao encontrado.
        pause
        exit /b 1
    )
) else (
    echo Docker Desktop nao encontrado.
    pause
    exit /b 1
)

REM Open the local UI.
start "" "http://127.0.0.1:8742"
exit
