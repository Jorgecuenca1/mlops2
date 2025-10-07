# 🎯 Guía de Uso - Django MLOps Dashboard

## ✅ Sistema Completamente Configurado

**Django Dashboard ya está corriendo en:** http://localhost:8000

---

## 📊 ACCESO AL DASHBOARD

### Dashboard Principal
**URL:** http://localhost:8000

El dashboard Django es la **interfaz unificada** para gestionar todo el sistema MLOps:

✅ **Gestión de Imágenes**
✅ **Visualización de Predicciones**
✅ **Monitoreo de Modelos**
✅ **Estado de Servicios**
✅ **Integración con Kafka, MLflow y Prometheus**

---

## 🚀 PASO A PASO PARA USAR EL PROYECTO

### **PASO 1: Acceder al Dashboard**
```
http://localhost:8000
```

Verás el dashboard principal con:
- Estadísticas generales del sistema
- Imágenes recientes
- Predicciones recientes
- Eventos del sistema

---

### **PASO 2: Subir una Imagen**

1. Click en **"Subir Imagen"** en el menú lateral
2. O navega a: http://localhost:8000/images/upload/
3. Selecciona una imagen (JPG, PNG, GIF)
4. Click en **"Subir y Clasificar"**

**¿Qué sucede automáticamente?**
- ✅ La imagen se sube a MinIO
- ✅ Se envía mensaje a Kafka
- ✅ Feature-extractor procesa la imagen
- ✅ 3 clasificadores predicen en paralelo:
  - **Fast Classifier** (~15ms)
  - **Balanced Classifier** (~25ms)
  - **Accurate Classifier** (~45ms)
- ✅ Resultados se guardan en PostgreSQL
- ✅ Puedes ver los resultados en el dashboard

---

### **PASO 3: Ver Predicciones**

**URL:** http://localhost:8000/predictions/

Aquí puedes:
- Ver todas las predicciones realizadas
- Filtrar por modelo
- Filtrar por clase predicha
- Ver estadísticas de confianza y tiempo

---

### **PASO 4: Comparar Modelos**

**URL:** http://localhost:8000/models/

- Ver rendimiento de cada modelo
- Comparar tiempos de inferencia
- Ver precisión promedio
- Análisis de consenso entre modelos

---

### **PASO 5: Monitorear el Sistema**

#### **Estado de Servicios**
**URL:** http://localhost:8000/monitoring/services/

Muestra el estado de todos los servicios:
- FastAPI
- MLflow
- Kafka UI
- Grafana
- Prometheus
- MinIO

#### **Kafka Status**
**URL:** http://localhost:8000/monitoring/kafka/

Monitorea los topics de Kafka y mensajes en tiempo real

---

### **PASO 6: Experimentos MLflow**

**URL:** http://localhost:8000/mlflow/

- Ver experimentos de machine learning
- Tracking de modelos
- Métricas de entrenamiento
- Enlace directo a MLflow UI

---

## 🎨 CARACTERÍSTICAS DEL DASHBOARD

### ✨ Interfaz Moderna
- **Bootstrap 5** - Diseño responsive
- **Sidebar navegable** con todos los servicios
- **Gráficos en tiempo real** con Chart.js
- **Auto-refresh** de estadísticas cada 30 segundos

### 🔄 Funcionalidades Principales

1. **Gestión de Imágenes**
   - Subir imágenes
   - Ver historial
   - Filtrar por estado/fuente
   - Ver detalles de cada imagen

2. **Predicciones**
   - Listado completo
   - Filtros avanzados
   - Estadísticas agregadas
   - Barras de progreso de confianza

3. **Modelos ML**
   - Comparación de rendimiento
   - Métricas detalladas
   - Análisis de consenso
   - Tiempos de inferencia

4. **Monitoreo**
   - Estado de servicios en tiempo real
   - Kafka topics
   - Eventos del sistema
   - Integración con Prometheus

---

## 🌐 TODOS LOS SERVICIOS DISPONIBLES

| Servicio | Puerto | URL | Descripción |
|----------|--------|-----|-------------|
| **Django Dashboard** | 8000 | http://localhost:8000 | **Dashboard principal (USAR ESTE)** |
| FastAPI | 8001 | http://localhost:8001/docs | API de predicciones |
| Classifier Fast | 8003 | http://localhost:8003 | Clasificador rápido |
| Classifier Accurate | 8004 | http://localhost:8004 | Clasificador preciso |
| Classifier Balanced | 8005 | http://localhost:8005 | Clasificador balanceado |
| MLflow | 5000 | http://localhost:5000 | Tracking experimentos |
| Kafka UI | 8090 | http://localhost:8090 | Mensajería |
| Grafana | 3000 | http://localhost:3000 | Métricas visuales |
| Prometheus | 9090 | http://localhost:9090 | Sistema de métricas |
| MinIO Console | 9001 | http://localhost:9001 | Almacenamiento |

---

## 🔑 CREDENCIALES

### Django Admin (opcional)
Primero crear superusuario:
```bash
docker exec -it mlops-django python manage.py createsuperuser
```
Luego acceder a: http://localhost:8000/admin

### Grafana
- Usuario: `admin`
- Contraseña: `admin123`

### MinIO Console
- Usuario: `minioadmin`
- Contraseña: `minioadmin123`

---

## 📱 EJEMPLO DE FLUJO COMPLETO

1. **Abrir Dashboard:** http://localhost:8000
2. **Ir a "Subir Imagen"** (menú lateral)
3. **Seleccionar una imagen** de tu PC
4. **Click "Subir y Clasificar"**
5. **Ir a "Predicciones"** para ver resultados
6. **Ver "Modelos"** para comparar rendimiento
7. **Revisar "Monitoreo"** para estado del sistema

---

## 🛠️ COMANDOS ÚTILES

### Ver logs de Django
```bash
docker logs mlops-django -f
```

### Ver todos los contenedores
```bash
docker ps
```

### Reiniciar Django
```bash
docker-compose restart django
```

### Detener todo
```bash
docker-compose down
```

### Iniciar todo
```bash
docker-compose up -d
```

### Reconstruir Django (si cambias código)
```bash
docker-compose up -d --build django
```

---

## 🎯 VENTAJAS DEL DASHBOARD DJANGO

✅ **Una sola interfaz** para todo el sistema
✅ **No necesitas abrir múltiples URLs**
✅ **Gestión visual** de imágenes y predicciones
✅ **Monitoreo integrado** de todos los servicios
✅ **Historial completo** en base de datos
✅ **Filtros y búsquedas** avanzadas
✅ **Auto-refresh** de datos en tiempo real
✅ **Enlaces directos** a Grafana, MLflow, Kafka UI
✅ **Diseño moderno** y responsive
✅ **Fácil de usar** - sin necesidad de conocer APIs

---

## 📊 ARQUITECTURA DEL SISTEMA

```
Usuario → Django Dashboard (puerto 8000)
              ↓
              ├→ FastAPI (subida de imágenes)
              ├→ PostgreSQL (lectura/escritura de datos)
              ├→ Redis (caché)
              ├→ MinIO (visualización de imágenes)
              ├→ Kafka (monitoreo de mensajes)
              ├→ MLflow (experimentos)
              ├→ Prometheus (métricas)
              └→ Grafana (dashboards)
```

---

## ✨ ¡TODO FUNCIONA DESDE EL DASHBOARD!

**Ya no necesitas usar FastAPI directamente.**
**Todo se gestiona desde Django en http://localhost:8000**

El usuario puede:
- Subir imágenes
- Ver predicciones
- Comparar modelos
- Monitorear el sistema
- Ver experimentos MLflow
- Revisar estado de Kafka
- Todo desde una sola interfaz bonita y fácil de usar

---

## 🎉 ¡LISTO PARA USAR!

Abre tu navegador en:
# http://localhost:8000

Y empieza a usar el sistema completo de MLOps con una interfaz amigable.
