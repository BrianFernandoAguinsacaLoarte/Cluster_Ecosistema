@echo off
echo ============================================================
echo SIERPINSKI PARALELO - TEST DE CORRECCIONES
echo ============================================================
echo.
echo Este script te guiara para probar que los problemas estan corregidos:
echo.
echo PROBLEMA 1 CORREGIDO: Canvas no se limpiaba al desconectar worker
echo PROBLEMA 2 CORREGIDO: Worker1 generaba todo el triangulo
echo PROBLEMA 3 CORREGIDO: Regiones no desaparecian
echo.
echo ============================================================
echo INSTRUCCIONES DE PRUEBA:
echo ============================================================
echo.
echo TERMINAL 1 - Ejecuta esto primero:
echo    python master.py
echo.
echo TERMINAL 2 - Luego ejecuta SOLO worker1:
echo    python worker.py --master http://127.0.0.1:5000 --id worker1
echo.
echo EN EL NAVEGADOR (http://127.0.0.1:5000):
echo    - Verifica que solo aparece 1 worker
echo    - Genera fractal
echo    - DEBE verse SOLO la region superior (no todo el triangulo)
echo.
echo TERMINAL 3 - Agrega worker2:
echo    python worker.py --master http://127.0.0.1:5000 --id worker2
echo.
echo    - Genera fractal de nuevo
echo    - DEBEN verse 2 regiones (superior + derecha)
echo.
echo TERMINAL 4 - Agrega worker3:
echo    python worker.py --master http://127.0.0.1:5000 --id worker3
echo.
echo    - Genera fractal de nuevo
echo    - DEBE verse el fractal completo (3 regiones)
echo.
echo PRUEBA FINAL - Desconectar worker2:
echo    - Ve a Terminal 3 y presiona Ctrl+C
echo    - Espera 10-15 segundos
echo    - La region derecha DEBE DESAPARECER del canvas
echo.
echo ============================================================
echo Lee PRUEBAS.md para instrucciones detalladas
echo ============================================================
pause
