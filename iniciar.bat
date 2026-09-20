@echo off
chcp 65001 >nul
title IA Futurista — Cursor Cloud Agent
cd /d "%~dp0"
set FUTURISTA_RAIZ=%~dp0
set FUTURISTA_PROJETOS=%~dp0projetos
if not exist "%FUTURISTA_PROJETOS%" mkdir "%FUTURISTA_PROJETOS%"
start "" "http://127.0.0.1:8742"
if exist "%FUTURISTA_RAIZ%.venv\Scripts\python.exe" (
    "%FUTURISTA_RAIZ%.venv\Scripts\python.exe" -m uvicorn server:app --host 127.0.0.1 --port 8742
) else (
    python -m uvicorn server:app --host 127.0.0.1 --port 8742
)
