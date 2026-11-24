@echo off
setlocal
rem Use the shared course repository, including in this PC's legacy checkout.
if not exist "%~dp0..\..\.git" (
  echo No se encontro el repositorio principal. Usa la carpeta Topicos-Web-y-Movil-2026.
  exit /b 1
)
git -C "%~dp0..\.." %*
