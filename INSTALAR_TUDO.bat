@echo off
chcp 65001 >nul
title Instalador IA Futurista — Automatico
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "%~dp0INSTALAR_TUDO.ps1"
