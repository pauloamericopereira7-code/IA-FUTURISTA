@echo off
REM IA Futurista - Startup Script
REM ==============================

echo.
echo ╔════════════════════════════════════════════════════╗
echo ║  🤖 IA FUTURISTA - INICIANDO                      ║
echo ╚════════════════════════════════════════════════════╝
echo.

cd /d "C:\Users\Administrador\Downloads\IA_Futurista\futurista"

REM Verificar se Docker está rodando
docker ps >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker não está rodando!
    echo Inicie o Docker Desktop e tente novamente.
    pause
    exit /b 1
)

echo ✅ Docker OK
echo.
echo 🚀 Iniciando containers...
docker compose up -d

echo.
echo ⏳ Aguardando servidor inicializar (10 segundos)...
timeout /t 10 /nobreak

echo.
echo 🌐 Abrindo navegador...
start http://localhost:8742

echo.
echo ✅ IA Futurista online em http://localhost:8742
echo.
