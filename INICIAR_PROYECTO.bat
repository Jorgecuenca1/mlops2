@echo off
echo ========================================
echo    MLOps Dashboard - Inicio Rapido
echo ========================================
echo.
echo Levantando todos los servicios...
echo.

docker-compose up -d

echo.
echo ========================================
echo    SISTEMA INICIADO CORRECTAMENTE
echo ========================================
echo.
echo Dashboard Django: http://localhost:8000
echo.
echo Esperando que los servicios esten listos...
timeout /t 10 /nobreak >nul

echo.
echo Verificando estado de servicios...
docker ps --format "table {{.Names}}\t{{.Status}}" | findstr "mlops-"

echo.
echo ========================================
echo    LISTO PARA USAR
echo ========================================
echo.
echo Abre tu navegador en:
echo http://localhost:8000
echo.
echo Presiona cualquier tecla para abrir el navegador...
pause >nul

start http://localhost:8000

echo.
echo Dashboard abierto en el navegador.
echo.
pause
