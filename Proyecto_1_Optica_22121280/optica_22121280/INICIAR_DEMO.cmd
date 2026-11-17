@echo off
setlocal
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Falta preparar Python. Consulta README.md: Inicio rapido en Windows.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" scripts\iniciar_demo.py
if errorlevel 1 pause
