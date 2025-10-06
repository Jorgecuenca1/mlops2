# 🐳 INSTALACIÓN DE DOCKER EN WINDOWS

## 📋 REQUISITOS PREVIOS

Antes de instalar Docker Desktop, verifica que tu sistema cumple:

### Windows 10/11 Requirements:
- ✅ Windows 10 64-bit: Pro, Enterprise o Education (Build 19041 o superior)
- ✅ Windows 11 64-bit: Todas las ediciones
- ✅ WSL 2 (Windows Subsystem for Linux 2)
- ✅ Virtualización habilitada en BIOS
- ✅ Al menos 4 GB de RAM (recomendado 8 GB+)
- ✅ 20 GB de espacio en disco libre

## 🔍 PASO 1: VERIFICAR VIRTUALIZACIÓN

### Opción A: Usando Task Manager
1. Presiona `Ctrl + Shift + Esc` para abrir Task Manager
2. Ve a la pestaña "Performance"
3. Selecciona "CPU"
4. Verifica que "Virtualization" esté **Enabled**

### Opción B: Usando PowerShell
```powershell
# Ejecutar como Administrador
Get-ComputerInfo | Select-Object -Property "Hyper*"
```

**Si la virtualización está DESHABILITADA**:
- Reinicia tu PC
- Entra al BIOS/UEFI (usualmente presionando F2, F10, F12 o Delete al iniciar)
- Busca "Virtualization Technology", "Intel VT-x" o "AMD-V"
- Habilítalo
- Guarda cambios y reinicia

## 🔧 PASO 2: HABILITAR WSL 2

### 2.1 Abrir PowerShell como Administrador

**Click derecho en el menú Start → "Windows PowerShell (Admin)"**

### 2.2 Ejecutar comandos de instalación

```powershell
# Habilitar WSL
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# Habilitar Plataforma de Máquina Virtual
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

### 2.3 Reiniciar Windows

```powershell
Restart-Computer
```

### 2.4 Descargar e instalar el paquete de actualización de WSL 2

**Descarga desde**: https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi

O ejecuta:
```powershell
wsl --install
```

### 2.5 Establecer WSL 2 como versión predeterminada

```powershell
wsl --set-default-version 2
```

### 2.6 Verificar instalación

```powershell
wsl --status
```

Deberías ver:
```
Default Version: 2
```

## 📦 PASO 3: DESCARGAR DOCKER DESKTOP

### Opción A: Descarga Manual
1. Ve a: https://www.docker.com/products/docker-desktop/
2. Click en "Download for Windows"
3. Ejecuta el instalador `Docker Desktop Installer.exe`

### Opción B: Usando winget (Windows Package Manager)

```powershell
# Si tienes winget instalado
winget install -e --id Docker.DockerDesktop
```

### Opción C: Usando Chocolatey

```powershell
# Si tienes Chocolatey
choco install docker-desktop
```

## ⚙️ PASO 4: INSTALAR DOCKER DESKTOP

1. **Ejecuta el instalador descargado**

2. **Durante la instalación**:
   - ✅ Marca "Use WSL 2 instead of Hyper-V"
   - ✅ Marca "Add shortcut to desktop"

3. **Espera a que termine la instalación** (~5-10 minutos)

4. **Reinicia tu computadora cuando te lo pida**

## 🚀 PASO 5: CONFIGURAR DOCKER DESKTOP

### 5.1 Abrir Docker Desktop

1. Busca "Docker Desktop" en el menú Start
2. Ábrelo (puede tardar 1-2 minutos en iniciar la primera vez)

### 5.2 Aceptar Términos y Condiciones

- Acepta los términos de servicio

### 5.3 Configuración Recomendada

1. **Click en el ícono de engranaje (Settings)**

2. **General**:
   - ✅ "Use the WSL 2 based engine"
   - ✅ "Start Docker Desktop when you log in"

3. **Resources** → **WSL Integration**:
   - ✅ Habilita integración con tus distribuciones de Linux instaladas

4. **Resources** → **Advanced**:
   - **CPUs**: 4 (o la mitad de tus cores)
   - **Memory**: 4 GB (ajusta según tu RAM)
   - **Swap**: 1 GB
   - **Disk image size**: 60 GB

5. **Click "Apply & Restart"**

## ✅ PASO 6: VERIFICAR INSTALACIÓN

### Abrir PowerShell o CMD y ejecutar:

```bash
# Verificar versión de Docker
docker --version
```

**Salida esperada**:
```
Docker version 24.0.7, build afdd53b
```

```bash
# Verificar versión de Docker Compose
docker-compose --version
```

**Salida esperada**:
```
Docker Compose version v2.23.0-desktop.1
```

```bash
# Verificar que Docker está corriendo
docker ps
```

**Salida esperada**:
```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

### Test Hello World

```bash
# Ejecutar contenedor de prueba
docker run hello-world
```

**Salida esperada**:
```
Hello from Docker!
This message shows that your installation appears to be working correctly.
...
```

## 🎯 PASO 7: LEVANTAR EL PROYECTO MLOPS

### 7.1 Navega a la carpeta del proyecto

```bash
cd C:\Users\HOME\PycharmProjects\mlops2
```

### 7.2 Verifica que Docker Desktop está corriendo

- Deberías ver el ícono de Docker en la bandeja del sistema (system tray)
- El ícono debe estar **sin un borde rojo** (eso significa que está corriendo)

### 7.3 Levanta todos los servicios

```bash
# Levantar todos los servicios en segundo plano
docker-compose up -d
```

**Primera vez tomará 10-20 minutos** porque debe:
- Descargar imágenes de Docker (~5 GB)
- Construir servicios personalizados
- Inicializar bases de datos

### 7.4 Ver el progreso

```bash
# Ver logs en tiempo real
docker-compose logs -f
```

**Presiona `Ctrl + C` para salir de los logs**

### 7.5 Verificar que todo está corriendo

```bash
# Ver servicios corriendo
docker-compose ps
```

**Deberías ver todos los servicios con STATUS "Up"**:
```
NAME                    IMAGE                          STATUS
mlops-django            mlops2-django                  Up
mlops-fastapi           mlops2-fastapi                 Up
mlops-kafka             confluentinc/cp-kafka:7.5.0    Up
mlops-minio             minio/minio:latest             Up
mlops-postgres          postgres:15-alpine             Up
mlops-redis             redis:7-alpine                 Up
mlops-resnet            mlops2-resnet-service          Up
mlops-mobilenet         mlops2-mobilenet-service       Up
mlops-efficientnet      mlops2-efficientnet-service    Up
mlops-mlflow            mlops2-mlflow                  Up
mlops-airflow-webserver apache/airflow:2.7.3           Up
...
```

## 🌐 PASO 8: ACCEDER A LOS SERVICIOS

Abre tu navegador y ve a:

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Dashboard Django** | http://localhost:8000 | - |
| **FastAPI Docs** | http://localhost:8001/docs | - |
| **GraphQL Playground** | http://localhost:8002/graphql | - |
| **MLflow UI** | http://localhost:5000 | - |
| **Airflow UI** | http://localhost:8080 | admin / admin123 |
| **MinIO Console** | http://localhost:9001 | minioadmin / minioadmin123 |
| **Kafka UI** | http://localhost:8090 | - |
| **Grafana** | http://localhost:3000 | admin / admin123 |
| **Prometheus** | http://localhost:9090 | - |

## 🛠️ COMANDOS ÚTILES

### Ver servicios corriendo
```bash
docker-compose ps
```

### Ver logs de un servicio específico
```bash
docker-compose logs -f django
docker-compose logs -f fastapi
docker-compose logs -f kafka
```

### Reiniciar un servicio
```bash
docker-compose restart django
```

### Detener todos los servicios
```bash
docker-compose down
```

### Detener y eliminar volúmenes (⚠️ CUIDADO: borra datos)
```bash
docker-compose down -v
```

### Reconstruir un servicio
```bash
docker-compose build django
docker-compose up -d django
```

### Ver uso de recursos
```bash
docker stats
```

### Ejecutar comando dentro de un contenedor
```bash
# Ejemplo: Abrir shell en Django
docker-compose exec django bash

# Ejemplo: Ejecutar migrations
docker-compose exec django python manage.py migrate
```

### Limpiar sistema (eliminar imágenes y contenedores no usados)
```bash
docker system prune -a
```

## ❌ SOLUCIÓN DE PROBLEMAS COMUNES

### Error: "WSL 2 installation is incomplete"

**Solución**:
```powershell
wsl --update
wsl --set-default-version 2
```

### Error: "Docker Desktop requires a newer WSL kernel"

**Solución**:
1. Descarga: https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi
2. Instala el paquete
3. Reinicia Docker Desktop

### Error: "Hardware assisted virtualization is not enabled"

**Solución**:
- Entra al BIOS y habilita VT-x (Intel) o AMD-V (AMD)

### Docker Desktop no inicia

**Solución**:
```powershell
# Reiniciar servicio de Docker
net stop com.docker.service
net start com.docker.service
```

### Contenedores no se pueden comunicar

**Solución**:
```bash
# Recrear red de Docker
docker-compose down
docker network prune
docker-compose up -d
```

### Puerto ya está en uso

**Solución**:
```powershell
# Ver qué proceso usa el puerto 8000
netstat -ano | findstr :8000

# Matar proceso (reemplaza PID con el número que viste)
taskkill /PID <PID> /F
```

### Espacio en disco insuficiente

**Solución**:
```bash
# Limpiar imágenes no usadas
docker system prune -a --volumes

# En Docker Desktop: Settings → Resources → Disk image location
# Cambiar a un disco con más espacio
```

## 📚 RECURSOS ADICIONALES

- **Documentación oficial**: https://docs.docker.com/desktop/install/windows-install/
- **WSL 2 Documentation**: https://docs.microsoft.com/en-us/windows/wsl/
- **Docker Compose Reference**: https://docs.docker.com/compose/compose-file/

## 🎓 PRÓXIMOS PASOS

Una vez que Docker esté instalado y funcionando:

1. ✅ Revisa el `README.md` del proyecto
2. ✅ Explora el dashboard en http://localhost:8000
3. ✅ Sube tu primera imagen y ve las predicciones
4. ✅ Revisa los logs con `docker-compose logs -f`
5. ✅ Explora Airflow, MLflow, y las otras herramientas

---

**¿Problemas? Abre un issue en GitHub o revisa `TROUBLESHOOTING.md`**
