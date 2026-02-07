@echo off
REM Script completo de demostración

echo ============================================================
echo    DEMO COMPLETA - SIERPINSKI PARALELO
echo ============================================================
echo.
echo Este script:
echo 1. Iniciara el maestro
echo 2. Iniciara 3 workers
echo 3. Abrira el navegador
echo.
echo Presiona cualquier tecla para continuar...
pause > nul
echo.

REM Iniciar maestro en background
echo [1/3] Iniciando nodo maestro...
start "Maestro" /MIN python master.py
timeout /t 3 /nobreak > nul

REM Iniciar workers
echo [2/3] Iniciando workers...
set MASTER=http://127.0.0.1:5000

start "Worker 1" python worker.py --master %MASTER% --id worker1
timeout /t 1 /nobreak > nul

start "Worker 2" python worker.py --master %MASTER% --id worker2
timeout /t 1 /nobreak > nul

start "Worker 3" python worker.py --master %MASTER% --id worker3
timeout /t 2 /nobreak > nul

REM Abrir navegador
echo [3/3] Abriendo dashboard...
start http://127.0.0.1:5000

echo.
echo ============================================================
echo Sistema iniciado!
echo.
echo Dashboard: http://127.0.0.1:5000
echo.
echo Para detener:
echo   1. Cierra las ventanas de workers (Ctrl+C)
echo   2. Cierra la ventana del maestro (Ctrl+C)
echo ============================================================
echo.
pause
