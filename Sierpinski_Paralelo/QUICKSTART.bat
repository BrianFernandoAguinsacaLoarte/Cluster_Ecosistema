@echo off
REM Script de inicio rápido para Sierpinski Paralelo
REM Este script muestra las instrucciones para ejecutar el sistema

echo ============================================================
echo SIERPINSKI PARALELO - GUIA DE INICIO RAPIDO
echo ============================================================
echo.
echo PASO 1: Abre 4 terminales PowerShell
echo.
echo TERMINAL 1 - MAESTRO:
echo   cd %~dp0
echo   python master.py
echo.
echo TERMINAL 2 - WORKER 1:
echo   cd %~dp0
echo   python worker.py --master http://127.0.0.1:5000 --id worker1
echo.
echo TERMINAL 3 - WORKER 2:
echo   cd %~dp0
echo   python worker.py --master http://127.0.0.1:5000 --id worker2
echo.
echo TERMINAL 4 - WORKER 3:
echo   cd %~dp0
echo   python worker.py --master http://127.0.0.1:5000 --id worker3
echo.
echo PASO 2: Abre el navegador en http://127.0.0.1:5000
echo.
echo PASO 3: Haz clic en "Generar Fractal" en el dashboard
echo.
echo ============================================================
echo Presiona Ctrl+C para cerrar esta ventana
pause
