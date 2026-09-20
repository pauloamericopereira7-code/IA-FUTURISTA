@echo off
chcp 65001 >nul
title IA Futurista — Docker
cd /d "%~dp0"
echo.
echo ========================================
echo   IA FUTURISTA — Deploy Docker
echo ========================================
echo.
echo Containers no seu Docker:
echo   cursor-docker  -> porta 9090 (code-server)
echo   open-webui     -> porta 3030
echo   ia-futurista   -> porta 8742 (NOVO)
echo.
docker compose build
docker compose up -d
echo.
echo Aguardando servidor...
timeout /t 5 /nobreak >nul
start "" "http://127.0.0.1:8742"
echo.
echo Pronto! IA Futurista em http://127.0.0.1:8742
echo.
echo IMPORTANTE: Ollama deve estar rodando no Windows:
echo   ollama serve
echo   ollama pull qwen2.5-coder:7b
echo.
pause
