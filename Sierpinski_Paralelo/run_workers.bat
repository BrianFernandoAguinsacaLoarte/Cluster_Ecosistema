@echo off
REM Script para iniciar Workers

echo ============================================================
echo       SIERPINSKI PARALELO - WORKERS
echo ============================================================
echo.
echo Este script abrira 3 ventanas de workers
echo.

set MASTER=http://127.0.0.1:5000

start "Worker 1" python worker.py --master %MASTER% --id worker1
timeout /t 2 /nobreak > nul

start "Worker 2" python worker.py --master %MASTER% --id worker2
timeout /t 2 /nobreak > nul

start "Worker 3" python worker.py --master %MASTER% --id worker3

echo.
echo Todos los workers han sido iniciados!
echo.
pause
