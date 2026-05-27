@echo off
chcp 65001 >nul
title ControlMetrics - PMD y Cia S.C.A.
cd /d "%~dp0"
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: No se pudo iniciar la aplicacion.
    echo Verifique que Python este instalado y ejecute:
    echo   pip install -r requirements.txt
    pause
)
