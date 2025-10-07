@echo off
echo ============================================
echo   MLOps Platform - Inicio Automatico
echo   Arquitectura Optimizada con Descriptores
echo ============================================
echo.

REM Verificar Docker
echo [1/5] Verificando Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker no esta instalado.
    echo Por favor instala Docker Desktop:
    echo https://www.docker.com/products/docker-desktop/
    echo.
    echo O ejecuta: winget install Docker.DockerDesktop --accept-source-agreements --accept-package-agreements
    pause
    exit /b 1
)
echo     Docker instalado correctamente!
echo.

REM Verificar Docker esta corriendo
echo [2/5] Verificando que Docker este corriendo...
docker ps >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker no esta corriendo.
    echo Por favor inicia Docker Desktop y espera a que este listo.
    echo Luego ejecuta este script nuevamente.
    pause
    exit /b 1
)
echo     Docker esta corriendo!
echo.

REM Limpiar contenedores anteriores (opcional)
echo [3/5] Limpiando contenedores anteriores (opcional)...
docker-compose down 2>nul
echo     Listo!
echo.

REM Iniciar servicios
echo [4/5] Iniciando servicios...
echo.
echo     Esto puede tomar 5-10 minutos la primera vez
echo     (descarga imagenes y construye servicios)
echo.

docker-compose up -d

if errorlevel 1 (
    echo.
    echo ERROR: No se pudieron iniciar los servicios.
    echo Revisa los logs con: docker-compose logs
    pause
    exit /b 1
)

echo.
echo [5/5] Esperando que los servicios esten listos...
timeout /t 30 /nobreak >nul

echo.
echo ============================================
echo   SERVICIOS INICIADOS EXITOSAMENTE!
echo ============================================
echo.
echo Puedes acceder a:
echo.
echo   FastAPI:         http://localhost:8001/docs
echo   Kafka UI:        http://localhost:8090
echo   MLflow:          http://localhost:5000
echo   Prometheus:      http://localhost:9090
echo   Grafana:         http://localhost:3000
echo   MinIO Console:   http://localhost:9001
echo.
echo   Classifier Fast:      http://localhost:8003
echo   Classifier Accurate:  http://localhost:8004
echo   Classifier Balanced:  http://localhost:8005
echo.
echo Para ver logs:   docker-compose logs -f [servicio]
echo Para detener:    docker-compose down
echo Para reiniciar:  docker-compose restart
echo.
echo Ver arquitectura optimizada: ARQUITECTURA_OPTIMIZADA.md
echo.
pause
