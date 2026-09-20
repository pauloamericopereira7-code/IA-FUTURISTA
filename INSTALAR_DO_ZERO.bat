@echo off
chcp 65001 >nul
title IA Futurista — Instalacao do zero
powershell -ExecutionPolicy Bypass -File "%~dp0INSTALAR_DO_ZERO.ps1"
pause
