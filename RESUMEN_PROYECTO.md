# 📊 RESUMEN EJECUTIVO DEL PROYECTO

## 🎯 ¿QUÉ ES ESTE PROYECTO?

**Nombre**: MLOps Real-Time Vision Platform

**Descripción**: Sistema completo de clasificación de imágenes en tiempo real que compara 3 modelos de inteligencia artificial (ResNet50, MobileNet, EfficientNet) mostrando cuál es más rápido y preciso.

**Analogía Simple**:
Imagina una fábrica donde 3 trabajadores diferentes (modelos AI) clasifican productos (imágenes). El sistema mide quién es más rápido, quién es más preciso, y te lo muestra en tiempo real en un dashboard.

---

## 🏗️ ARQUITECTURA SIMPLIFICADA

```
TÚ subes imagen
    ↓
DJANGO (Dashboard visual)
    ↓
FASTAPI (recibe y procesa)
    ↓
KAFKA (distribuye a 3 modelos)
    ↓
┌────────────────┬────────────────┬─────────────────┐
│   ResNet50     │   MobileNet    │  EfficientNet   │
│  (Muy preciso) │  (Muy rápido)  │   (Balanceado)  │
│    145ms       │     48ms       │      82ms       │
└────────────────┴────────────────┴─────────────────┘
    ↓
PostgreSQL (guarda resultados)
    ↓
DASHBOARD muestra:
- Predicción de cada modelo
- Tiempo de cada uno
- Cuál ganó en velocidad
- Cuál ganó en precisión
```

---

## 📦 SERVICIOS DOCKERIZADOS (16 Contenedores)

| # | Servicio | Puerto | Función | Tamaño Aprox |
|---|----------|--------|---------|--------------|
| 1 | **Django** | 8000 | Dashboard web con visualizaciones | ~500 MB |
| 2 | **FastAPI** | 8001 | API REST para subir imágenes | ~400 MB |
| 3 | **GraphQL** | 8002 | API avanzada para consultas flexibles | ~400 MB |
| 4 | **Kafka** | 9092 | Sistema de mensajería (streaming) | ~800 MB |
| 5 | **Zookeeper** | 2181 | Coordinador de Kafka | ~200 MB |
| 6 | **Kafka UI** | 8090 | Interfaz visual para Kafka | ~150 MB |
| 7 | **PostgreSQL** | 5432 | Base de datos principal | ~200 MB |
| 8 | **MinIO** | 9000 | Almacenamiento de imágenes (como S3) | ~100 MB |
| 9 | **MinIO Console** | 9001 | Interfaz web de MinIO | Incluido |
| 10 | **Redis** | 6379 | Cache rápido | ~50 MB |
| 11 | **MLflow** | 5000 | Tracking de experimentos ML | ~600 MB |
| 12 | **Airflow Web** | 8080 | Orquestador de pipelines | ~1.5 GB |
| 13 | **Airflow Scheduler** | - | Ejecutor de tareas programadas | Incluido |
| 14 | **ResNet Service** | 8003 | Modelo 1 (Preciso pero lento) | ~2 GB |
| 15 | **MobileNet Service** | 8004 | Modelo 2 (Rápido pero menos preciso) | ~800 MB |
| 16 | **EfficientNet Service** | 8005 | Modelo 3 (Balance) | ~1.2 GB |
| 17 | **Prometheus** | 9090 | Recolección de métricas | ~150 MB |
| 18 | **Grafana** | 3000 | Visualización de métricas | ~300 MB |

**TOTAL**: ~9-10 GB de imágenes Docker (descarga inicial)

---

## 📸 FUENTES DE DATOS - De dónde vienen las imágenes

### 1. **Webcam en Tiempo Real** (Lo más visual!)
```python
# Servicio que captura de tu cámara
OpenCV → captura frame cada 0.5 segundos → Kafka → 3 modelos procesan
```
**Efecto**: Mueves un objeto frente a la cámara y ves las predicciones en <1 segundo

### 2. **Dataset CIFAR-10** (60,000 imágenes)
- Se descarga automáticamente de TensorFlow
- 10 categorías: aviones, autos, pájaros, gatos, perros, etc.
- Ligero: 32x32 píxeles
- Perfecto para entrenamiento y testing

### 3. **Upload Manual**
- Desde el dashboard: botón "Subir Imagen"
- Arrastra y suelta archivos
- Acepta JPG, PNG, WebP

### 4. **API Pública (Opcional)**
- Unsplash API para imágenes aleatorias de alta calidad
- 50 requests/hora gratis

---

## 🔄 FLUJO COMPLETO (Paso a Paso)

### CASO DE USO: Usuario sube imagen de un GATO

```
PASO 1: Usuario abre http://localhost:8000
    ↓
PASO 2: Click en "Subir Imagen" → selecciona "gato.jpg"
    ↓
PASO 3: Django envía imagen a FastAPI (POST /upload)
    ↓
PASO 4: FastAPI hace:
    - Valida formato (JPG/PNG)
    - Valida tamaño (<10 MB)
    - Genera ID único: "550e8400-e29b-41d4-a716-446655440000"
    - Guarda en MinIO: "raw-images/2024/01/15/550e8400.jpg"
    - Registra en PostgreSQL: tabla "images"
    ↓
PASO 5: FastAPI publica mensaje en Kafka topic "images-input-stream":
    {
      "image_id": "550e8400-e29b-41d4-a716-446655440000",
      "minio_path": "raw-images/2024/01/15/550e8400.jpg",
      "timestamp": "2024-01-15T10:30:00Z"
    }
    ↓
PASO 6: 3 Servicios ML leen el mensaje AL MISMO TIEMPO:

    ResNet Service:
    ├─ Descarga imagen de MinIO
    ├─ Preprocesa (resize 224x224, normaliza)
    ├─ Ejecuta inferencia con ResNet50
    ├─ Resultado: "GATO" (95% confianza) en 145ms
    └─ Publica en Kafka topic "predictions-output"

    MobileNet Service:
    ├─ Descarga imagen de MinIO
    ├─ Preprocesa (resize 224x224)
    ├─ Ejecuta inferencia con MobileNet
    ├─ Resultado: "GATO" (92% confianza) en 48ms
    └─ Publica en Kafka topic "predictions-output"

    EfficientNet Service:
    ├─ Descarga imagen de MinIO
    ├─ Preprocesa
    ├─ Ejecuta inferencia
    ├─ Resultado: "GATO" (94% confianza) en 82ms
    └─ Publica en Kafka topic "predictions-output"
    ↓
PASO 7: Consumer de resultados guarda en PostgreSQL:

    Tabla "predictions":
    ┌────┬──────────┬──────────┬────────────┬───────────┬──────┐
    │ ID │ image_id │  model   │ prediction │ confidence│ time │
    ├────┼──────────┼──────────┼────────────┼───────────┼──────┤
    │ 1  │ 550e8400 │ resnet50 │    GATO    │   0.95    │ 145ms│
    │ 2  │ 550e8400 │mobilenet │    GATO    │   0.92    │ 48ms │
    │ 3  │ 550e8400 │efficient │    GATO    │   0.94    │ 82ms │
    └────┴──────────┴──────────┴────────────┴───────────┴──────┘
    ↓
PASO 8: Dashboard (Django) hace polling cada 2 segundos:
    - GET http://localhost:8001/predictions/550e8400
    - Recibe las 3 predicciones
    - Actualiza interfaz en tiempo real
    ↓
PASO 9: Usuario VE en pantalla:

    ┌─────────────────────────────────────────┐
    │  📸 Imagen: gato.jpg                    │
    │  ─────────────────────────────────────  │
    │                                          │
    │  🔴 ResNet50:    🐱 GATO (95%) - 145ms  │
    │  🟢 MobileNet:   🐱 GATO (92%) - 48ms   │
    │  🟡 EfficientNet: 🐱 GATO (94%) - 82ms  │
    │                                          │
    │  🏆 MÁS RÁPIDO: MobileNet (48ms)        │
    │  🎯 MÁS PRECISO: ResNet50 (95%)         │
    │  ⚖️ CONSENSO: GATO (100% acuerdo)       │
    │                                          │
    │  [Gráfico de Barras comparando tiempos] │
    └─────────────────────────────────────────┘
```

**TIEMPO TOTAL**: ~200ms desde upload hasta ver resultados

---

## 🎨 TECNOLOGÍAS USADAS

### Backend
- **Python 3.11** - Lenguaje principal
- **FastAPI** - API REST (súper rápido)
- **Django** - Framework web para dashboard
- **Strawberry** - GraphQL para Python

### Streaming & Mensajería
- **Apache Kafka** - Event streaming
- **Zookeeper** - Coordinación de Kafka

### Bases de Datos
- **PostgreSQL** - Base de datos relacional
- **Redis** - Cache en memoria
- **MinIO** - Object storage (imágenes)

### Machine Learning
- **TensorFlow/Keras** - Framework ML
- **MLflow** - Tracking de experimentos
- **NumPy** - Operaciones numéricas
- **Pillow** - Procesamiento de imágenes
- **OpenCV** - Captura de webcam

### Orquestación
- **Apache Airflow** - Pipelines programados
- **Docker & Docker Compose** - Contenedores

### Monitoring
- **Prometheus** - Recolección de métricas
- **Grafana** - Visualización de métricas

---

## 🚀 INICIO RÁPIDO (3 Comandos)

```bash
# 1. Instalar Docker Desktop (ver INSTALL_DOCKER.md)

# 2. Clonar y entrar al proyecto
cd C:\Users\HOME\PycharmProjects\mlops2

# 3. Levantar TODO (un solo comando!)
docker-compose up -d

# Esperar 5-10 minutos la primera vez
# (descarga imágenes y construye servicios)

# 4. Abrir en navegador
http://localhost:8000
```

---

## 📊 CASOS DE USO REALES

### 1. **E-Commerce - Clasificación de Productos**
- Vendedores suben fotos de productos
- Sistema clasifica automáticamente: ropa, electrónica, etc.
- Ahorra tiempo en categorización manual

### 2. **Salud - Detección de Enfermedades**
- Rayos X o resonancias → 3 modelos analizan
- Segunda, tercera opinión automática
- Comparación de confianza entre modelos

### 3. **Manufactura - Control de Calidad**
- Cámara en línea de producción
- Detecta defectos en tiempo real
- Alertas si algún modelo difiere (incertidumbre)

### 4. **Seguridad - Videovigilancia**
- Múltiples cámaras streaming
- Detección de objetos/personas
- Comparación de modelos para reducir falsos positivos

---

## 📈 MÉTRICAS QUE SE MIDEN

### Por Modelo
```python
{
  "model_name": "resnet50",
  "avg_latency_ms": 145,
  "avg_confidence": 0.93,
  "accuracy": 0.89,
  "throughput_imgs_per_sec": 6.9,
  "total_predictions": 1532
}
```

### Por Sistema
- **Mensajes en Kafka**: 150 msg/s
- **Espacio en MinIO**: 2.3 GB
- **Queries PostgreSQL**: 45 QPS
- **Uptime**: 99.8%

---

## 🎓 LO QUE VAS A APRENDER CON ESTE PROYECTO

### Nivel Técnico
✅ Arquitectura de microservicios
✅ Event-driven architecture
✅ Docker & containerización
✅ API design (REST & GraphQL)
✅ Streaming de datos en tiempo real
✅ Machine Learning en producción
✅ MLOps end-to-end

### Nivel Conceptual
✅ Cómo escalar sistemas ML
✅ Monitoreo y observabilidad
✅ Trade-offs: velocidad vs. precisión
✅ Ensemble de modelos
✅ CI/CD para ML

### Herramientas
✅ Kafka para streaming
✅ MLflow para experimentos
✅ Airflow para orquestación
✅ Prometheus + Grafana para monitoring
✅ MinIO como data lake

---

## 🗂️ ESTRUCTURA DE ARCHIVOS (Simplificada)

```
mlops2/
│
├── docker-compose.yml          ← Configuración de todos los servicios
│
├── services/
│   ├── fastapi/                ← API REST
│   │   ├── main.py            ← Endpoints
│   │   ├── kafka_producer.py  ← Envío a Kafka
│   │   └── minio_client.py    ← Gestión de imágenes
│   │
│   ├── django-dashboard/       ← Dashboard web
│   │   ├── views.py
│   │   └── templates/
│   │
│   ├── ml-models/
│   │   ├── resnet/            ← Modelo 1
│   │   ├── mobilenet/         ← Modelo 2
│   │   └── efficientnet/      ← Modelo 3
│   │
│   ├── kafka-producer/        ← Productores de imágenes
│   │   ├── webcam_producer.py
│   │   └── cifar10_streamer.py
│   │
│   ├── mlflow/                ← Tracking ML
│   ├── airflow/               ← Orquestación
│   └── graphql/               ← API GraphQL
│
├── scripts/
│   └── init-db.sql            ← Inicialización de PostgreSQL
│
├── config/
│   ├── prometheus.yml         ← Config de Prometheus
│   └── grafana/               ← Dashboards de Grafana
│
├── data/
│   ├── raw/                   ← Datos sin procesar
│   ├── processed/             ← Datos procesados
│   └── models/                ← Modelos entrenados
│
└── docs/
    ├── README.md              ← Documentación principal
    ├── INSTALL_DOCKER.md      ← Guía de instalación
    ├── FUENTES_DE_DATOS.md    ← Explicación de datos
    └── ARCHITECTURE.md        ← Arquitectura detallada
```

---

## 🎯 ROADMAP DE DESARROLLO

### ✅ Fase 1: Infraestructura (COMPLETADO)
- [x] Docker Compose con todos los servicios
- [x] PostgreSQL + MinIO + Kafka + Redis
- [x] Networking entre servicios

### 🔄 Fase 2: MVP (EN PROGRESO)
- [x] FastAPI con upload de imágenes
- [x] Kafka producer funcional
- [ ] 1 modelo funcionando (ResNet)
- [ ] Dashboard básico con resultados

### ⏳ Fase 3: Múltiples Modelos
- [ ] 3 modelos en paralelo
- [ ] Comparación visual de resultados
- [ ] Gráficos de tiempo/confianza
- [ ] Webcam streaming

### ⏳ Fase 4: MLOps Completo
- [ ] MLflow tracking integrado
- [ ] Airflow DAG para reentrenamiento
- [ ] A/B testing de modelos
- [ ] Auto-scaling basado en carga

### ⏳ Fase 5: Producción
- [ ] Kubernetes deployment
- [ ] CI/CD con GitHub Actions
- [ ] Monitoring completo con alertas
- [ ] Documentación API completa

---

## 💡 CONCEPTOS CLAVE EXPLICADOS

### ¿Qué es Kafka y por qué lo usamos?
**Analogía**: Kafka es como una cinta transportadora en una fábrica.

- Sin Kafka: Cada modelo tendría que preguntar "¿hay imágenes nuevas?" constantemente
- Con Kafka: Las imágenes se ponen en la cinta, los modelos toman lo que necesitan

**Ventajas**:
- Si un modelo se cae, no pierde mensajes
- Múltiples modelos pueden procesar la misma imagen
- Escala a millones de mensajes por segundo

### ¿Por qué 3 modelos diferentes?
**En producción real**, diferentes modelos tienen diferentes características:

| Modelo | Precisión | Velocidad | Uso de Memoria | Mejor para |
|--------|-----------|-----------|----------------|------------|
| **ResNet50** | ⭐⭐⭐⭐⭐ | ⭐⭐ | Alta | Medicina, seguridad crítica |
| **MobileNet** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Baja | Apps móviles, IoT |
| **EfficientNet** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Media | Producción general |

**Estrategias**:
- **Ensemble**: Combinar predicciones de los 3 → mejor accuracy
- **Cascade**: ResNet solo si MobileNet tiene baja confianza
- **A/B Testing**: Ver cuál funciona mejor con usuarios reales

### ¿Qué es MLflow?
**MLflow registra TODO sobre tus experimentos**:

```python
with mlflow.start_run():
    # Registra parámetros
    mlflow.log_param("learning_rate", 0.001)
    mlflow.log_param("epochs", 10)

    # Entrena modelo
    model.fit(X_train, y_train)

    # Registra métricas
    accuracy = model.score(X_test, y_test)
    mlflow.log_metric("accuracy", accuracy)

    # Guarda modelo
    mlflow.keras.log_model(model, "model")
```

Luego puedes:
- Comparar 100 experimentos en una tabla
- Ver cuál combinación de parámetros dio mejor resultado
- Volver a cualquier versión del modelo

---

## 🔐 SEGURIDAD (Para Producción)

Este proyecto es para **desarrollo/aprendizaje**. Para producción:

❌ **NO uses** contraseñas hardcodeadas (como "mlops123")
❌ **NO expongas** todos los puertos al internet
❌ **NO uses** `allow_origins=["*"]` en CORS

✅ **SÍ usa** variables de entorno para credenciales
✅ **SÍ implementa** autenticación JWT
✅ **SÍ usa** HTTPS con certificados SSL
✅ **SÍ configura** firewall y VPN

---

## 📞 SOPORTE

- **Documentación completa**: Ver carpeta `/docs`
- **Issues técnicos**: Abrir issue en GitHub
- **Preguntas**: Ver `TROUBLESHOOTING.md`

---

## 🎉 CONCLUSIÓN

Este proyecto es una **plataforma completa de MLOps** que te enseña:
- Arquitectura moderna de microservicios
- Machine Learning en producción
- Streaming de datos en tiempo real
- Mejores prácticas de DevOps/MLOps

**Es portfolio-ready**: Demuestra conocimientos avanzados en múltiples áreas.

**¿Listo para empezar?** → Sigue `INSTALL_DOCKER.md` y luego `README.md`

---

**Made with ❤️ for learning MLOps**
