# 🚀 GUÍA DE INICIO RÁPIDO

## ✅ PRE-REQUISITOS

Antes de empezar, asegúrate de tener:

- [x] **Docker Desktop instalado** (ver `INSTALL_DOCKER.md`)
- [x] **Docker Desktop corriendo** (ícono en system tray sin borde rojo)
- [x] **Al menos 8 GB RAM disponibles**
- [x] **20 GB de espacio en disco libre**
- [x] **Conexión a internet** (primera vez para descargar imágenes)

## 📝 PASO A PASO

### 1️⃣ Verificar Docker

```bash
# Abrir PowerShell o CMD
docker --version
docker-compose --version
docker ps
```

**Salidas esperadas**:
```
Docker version 24.0.7, build afdd53b
Docker Compose version v2.23.0
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

### 2️⃣ Navegar al Proyecto

```bash
cd C:\Users\HOME\PycharmProjects\mlops2
```

### 3️⃣ Verificar Archivos

```bash
dir
```

**Debes ver**:
```
docker-compose.yml
README.md
RESUMEN_PROYECTO.md
services/
config/
scripts/
...
```

### 4️⃣ Levantar Servicios

```bash
# Levantar TODO en segundo plano (-d = detached)
docker-compose up -d
```

**Primera ejecución tomará 10-20 minutos** porque:
- Descarga ~9 GB de imágenes Docker
- Construye servicios personalizados
- Inicializa bases de datos
- Descarga modelos ML

**Verás salida como**:
```
[+] Running 18/18
 ✔ Network mlops-network             Created
 ✔ Container mlops-zookeeper          Started
 ✔ Container mlops-postgres           Started
 ✔ Container mlops-redis              Started
 ✔ Container mlops-minio              Started
 ✔ Container mlops-kafka              Started
 ✔ Container mlops-mlflow             Started
 ✔ Container mlops-fastapi            Started
 ✔ Container mlops-graphql            Started
 ✔ Container mlops-django             Started
 ✔ Container mlops-resnet             Started
 ✔ Container mlops-mobilenet          Started
 ✔ Container mlops-efficientnet       Started
 ✔ Container mlops-airflow-webserver  Started
 ✔ Container mlops-airflow-scheduler  Started
 ✔ Container mlops-kafka-ui           Started
 ✔ Container mlops-prometheus         Started
 ✔ Container mlops-grafana            Started
```

### 5️⃣ Monitorear Progreso

```bash
# Ver logs en tiempo real
docker-compose logs -f
```

**Presiona `Ctrl + C` para salir**

**O ver logs de un servicio específico**:
```bash
docker-compose logs -f django
docker-compose logs -f fastapi
docker-compose logs -f resnet-service
```

### 6️⃣ Verificar que Todo Está Corriendo

```bash
docker-compose ps
```

**Todos los servicios deben mostrar**:
```
NAME                     STATUS
mlops-django             Up
mlops-fastapi            Up
mlops-kafka              Up
mlops-postgres           Up (healthy)
mlops-minio              Up (healthy)
...
```

**Si algún servicio está "Restarting" o "Exited"**:
```bash
# Ver qué pasó
docker-compose logs [nombre-del-servicio]

# Reintentar
docker-compose restart [nombre-del-servicio]
```

### 7️⃣ Acceder a los Servicios

Abre tu navegador favorito (Chrome, Firefox, Edge)

#### Dashboard Principal ⭐
**http://localhost:8000**

Este es tu punto de entrada principal. Aquí podrás:
- Subir imágenes
- Ver predicciones en tiempo real
- Comparar modelos
- Ver gráficos y estadísticas

#### FastAPI Swagger UI (Documentación Interactiva)
**http://localhost:8001/docs**

Interfaz interactiva para probar todos los endpoints:
- POST /upload - Subir imagen
- GET /predictions/{image_id} - Ver predicciones
- GET /health - Estado del sistema

#### MLflow Tracking
**http://localhost:5000**

Ver todos tus experimentos de ML:
- Comparar modelos
- Ver métricas (accuracy, loss)
- Descargar modelos entrenados

#### Airflow (Orquestación)
**http://localhost:8080**
- **Usuario**: admin
- **Contraseña**: admin123

Ver y ejecutar pipelines de datos y ML.

#### MinIO Console (Almacenamiento)
**http://localhost:9001**
- **Usuario**: minioadmin
- **Contraseña**: minioadmin123

Ver todas las imágenes almacenadas.

#### Kafka UI
**http://localhost:8090**

Ver topics, mensajes, y flujo de datos en tiempo real.

#### Prometheus (Métricas)
**http://localhost:9090**

Métricas del sistema.

#### Grafana (Dashboards)
**http://localhost:3000**
- **Usuario**: admin
- **Contraseña**: admin123

Dashboards visuales de todo el sistema.

## 🎯 PRIMEROS PASOS

### ✅ Test 1: Subir tu Primera Imagen

1. **Ve a**: http://localhost:8000

2. **Click en "Subir Imagen"** o "Upload Image"

3. **Selecciona una imagen** de tu computadora
   - Formato: JPG, PNG, WebP
   - Tamaño máximo: 10 MB
   - Sugerencia: Usa una imagen clara de un objeto (gato, perro, auto, etc.)

4. **Espera ~2-3 segundos**

5. **¡Ve los resultados!**
   ```
   ✅ ResNet50:    GATO (95%)  - 145ms
   ✅ MobileNet:   GATO (92%)  - 48ms
   ✅ EfficientNet: GATO (94%) - 82ms
   ```

### ✅ Test 2: Probar la API con Swagger

1. **Ve a**: http://localhost:8001/docs

2. **Expande** `POST /upload`

3. **Click** en "Try it out"

4. **Click** en "Choose File" y selecciona una imagen

5. **Click** en "Execute"

6. **Copia el `image_id`** de la respuesta

7. **Expande** `GET /predictions/{image_id}`

8. **Pega el `image_id`** y click "Execute"

9. **Ve las predicciones** de los 3 modelos

### ✅ Test 3: Ver Datos en MinIO

1. **Ve a**: http://localhost:9001

2. **Login**: minioadmin / minioadmin123

3. **Click en "Buckets"** en el menú izquierdo

4. **Click en "raw-images"**

5. **Ve tus imágenes** organizadas por fecha

### ✅ Test 4: Ver Métricas en MLflow

1. **Ve a**: http://localhost:5000

2. **Click en "Experiments"**

3. **Selecciona un experimento**

4. **Ve las métricas** de cada run

## 🛠️ COMANDOS ÚTILES

### Ver Estado de Servicios
```bash
docker-compose ps
```

### Ver Logs
```bash
# Todos los servicios
docker-compose logs -f

# Un servicio específico
docker-compose logs -f django
docker-compose logs -f fastapi
docker-compose logs -f kafka
```

### Reiniciar un Servicio
```bash
docker-compose restart django
docker-compose restart fastapi
```

### Detener Todo
```bash
docker-compose down
```

### Detener y Eliminar Datos (⚠️ CUIDADO)
```bash
# Elimina contenedores Y volúmenes (bases de datos, imágenes)
docker-compose down -v
```

### Reconstruir un Servicio
```bash
# Si cambiaste código
docker-compose build fastapi
docker-compose up -d fastapi
```

### Ver Uso de Recursos
```bash
docker stats
```

### Ejecutar Comando en Contenedor
```bash
# Abrir shell en Django
docker-compose exec django bash

# Ejecutar migrations
docker-compose exec django python manage.py migrate

# Crear superuser
docker-compose exec django python manage.py createsuperuser
```

## 🐛 TROUBLESHOOTING RÁPIDO

### ❌ Error: "port is already allocated"

**Problema**: El puerto ya está en uso

**Solución**:
```powershell
# Ver qué usa el puerto 8000
netstat -ano | findstr :8000

# Matar proceso (reemplaza PID)
taskkill /PID [PID] /F

# O cambiar puerto en docker-compose.yml
# De: "8000:8000"
# A:  "8001:8000"
```

### ❌ Error: "Cannot connect to the Docker daemon"

**Problema**: Docker Desktop no está corriendo

**Solución**:
1. Abre Docker Desktop
2. Espera que el ícono esté sin borde rojo
3. Reintenta `docker-compose up -d`

### ❌ Servicio en estado "Restarting"

**Problema**: El servicio no arranca

**Solución**:
```bash
# Ver logs del servicio
docker-compose logs [nombre-servicio]

# Reiniciar
docker-compose restart [nombre-servicio]

# Si persiste, reconstruir
docker-compose build [nombre-servicio]
docker-compose up -d [nombre-servicio]
```

### ❌ "Healthy" tarda mucho

**Es normal**. PostgreSQL y MinIO tienen health checks que toman tiempo.

Espera 2-3 minutos. Si después de 5 minutos sigue igual:
```bash
docker-compose logs postgres
docker-compose logs minio
```

### ❌ Imágenes no se procesan

**Verificar**:

1. **Kafka está corriendo**:
   ```bash
   docker-compose logs kafka
   ```

2. **Servicios ML están corriendo**:
   ```bash
   docker-compose ps | grep -E "resnet|mobilenet|efficient"
   ```

3. **Ver logs de servicios ML**:
   ```bash
   docker-compose logs -f resnet-service
   ```

## 📚 PRÓXIMOS PASOS

Una vez que todo esté funcionando:

1. ✅ **Lee** `RESUMEN_PROYECTO.md` - Entiende la arquitectura completa

2. ✅ **Explora** el código en `services/` - Ve cómo funciona cada componente

3. ✅ **Experimenta** con diferentes imágenes - Prueba casos edge

4. ✅ **Modifica** algo pequeño - Cambia un mensaje, color, etc.

5. ✅ **Sube a tu GitHub** - Portfolio profesional

6. ✅ **Documenta** tus aprendizajes - Blog post o README personal

## 🎉 ¡FELICIDADES!

Si llegaste aquí y todo funciona, **tienes un sistema MLOps completo corriendo**.

Esto es lo que las empresas tecnológicas usan en producción para:
- Deployar modelos de ML
- Monitorear performance
- Escalar automáticamente
- Hacer A/B testing

**Es un proyecto portfolio-ready** que demuestra conocimientos avanzados.

---

**¿Dudas?** → Ver `TROUBLESHOOTING.md` o abrir un issue en GitHub

**¿Quieres contribuir?** → Ver `CONTRIBUTING.md`

**¿Listo para producción?** → Ver `DEPLOYMENT.md`
