@echo off
chcp 65001 >nul
title IA Futurista
cd /d "%~dp0"

REM Sobe Docker se existir docker-compose.yml
where docker >nul 2>&1
if %errorlevel%==0 (
    if exist "%~dp0docker-compose.yml" (
        docker compose -f "%~dp0docker-compose.yml" up -d 2>nul
    )
)

REM Abre no navegador
start "" "http://127.0.0.1:8742"
exit
