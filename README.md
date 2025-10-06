# 🚀 MLOps Real-Time Vision Platform

## 📖 ¿QUÉ ES ESTE PROYECTO?

**Imagina esto**: Un sistema que recibe imágenes en tiempo real (como de una cámara de seguridad o uploads de usuarios), las procesa con **3 modelos de inteligencia artificial diferentes**, y te muestra en un dashboard cuál modelo es más rápido y preciso.

### 🎯 Caso de Uso Real

Piensa en una empresa que necesita clasificar imágenes automáticamente:
- 📸 **E-commerce**: Clasificar productos subidos por vendedores
- 🏥 **Salud**: Analizar imágenes médicas con múltiples modelos para segunda opinión
- 🚗 **Seguridad**: Detectar objetos en cámaras de vigilancia
- 🏭 **Manufactura**: Control de calidad visual en líneas de producción

## 🏗️ ARQUITECTURA EXPLICADA FÁCIL

```
┌─────────────────────────────────────────────────────────────┐
│  TÚ (Usuario)                                               │
│  ↓                                                           │
│  1. Subes una imagen o activas webcam                       │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────┐
│  DJANGO DASHBOARD (Lo que ves en el navegador)              │
│  - Upload de imágenes                                        │
│  - Ver resultados en tiempo real                            │
│  - Gráficos de comparación de modelos                       │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────┐
│  APIs (FastAPI + GraphQL)                                   │
│  - Reciben tu imagen                                         │
│  - La envían al sistema de streaming                        │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────┐
│  KAFKA (Sistema de Mensajería - El "mensajero")            │
│  - Recibe la imagen                                          │
│  - La pone en una "cola" para procesamiento                 │
│  - Asegura que nada se pierda                               │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────┐
│  3 MODELOS DE IA (Procesando en PARALELO)                  │
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐       │
│  │  ResNet50   │  │  MobileNet   │  │EfficientNet │       │
│  │  (Preciso)  │  │  (Rápido)    │  │ (Balanceado)│       │
│  │  ⏱️ 150ms   │  │  ⏱️ 50ms     │  │  ⏱️ 80ms    │       │
│  └─────────────┘  └──────────────┘  └─────────────┘       │
│                                                              │
│  Cada uno dice: "Esto es un GATO con 95% de confianza"     │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────┐
│  RESULTADOS SE GUARDAN EN:                                  │
│                                                              │
│  📊 PostgreSQL (Metadata: quién, cuándo, qué resultado)    │
│  🖼️ MinIO (Las imágenes originales)                        │
│  📈 MLflow (Tracking: qué modelo funcionó mejor)           │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────┐
│  DASHBOARD te muestra:                                      │
│  ✅ Predicción de cada modelo                              │
│  ✅ Tiempo que tardó cada uno                              │
│  ✅ Gráfico comparativo                                    │
│  ✅ Historial de predicciones                              │
└─────────────────────────────────────────────────────────────┘
```

## 🎓 EXPLICACIÓN DE CADA COMPONENTE

### 1️⃣ **Django Dashboard** (Frontend)
**¿Qué hace?**: Es la página web que ves en tu navegador
**¿Por qué?**: Para que puedas interactuar con el sistema de forma visual
**Funciones**:
- Botón para subir imágenes
- Botón para activar webcam
- Mostrar resultados en tiempo real
- Gráficos bonitos de comparación

### 2️⃣ **FastAPI** (REST API)
**¿Qué hace?**: Recibe peticiones HTTP (como cuando subes una imagen)
**¿Por qué?**: Es súper rápido para Python y fácil de usar
**Ejemplo**: `POST /predict` con una imagen → devuelve predicción

### 3️⃣ **GraphQL** (API Flexible)
**¿Qué hace?**: Permite consultas más complejas y eficientes
**¿Por qué?**: Para que puedas pedir exactamente los datos que necesitas
**Ejemplo**: "Dame las últimas 10 predicciones solo del modelo ResNet"

### 4️⃣ **Kafka** (Sistema de Streaming)
**¿Qué hace?**: Es como una "cinta transportadora" de datos
**¿Por qué?**: Para procesar miles de imágenes sin perder ninguna
**Analogía**: Como una cola en el banco, todos esperan su turno

**Flujo**:
```
Imagen → Topic "images-input" →
         → 3 Consumers (modelos) leen la misma imagen →
         → Cada uno publica resultado en "predictions-output"
```

### 5️⃣ **MinIO** (Almacenamiento de Imágenes)
**¿Qué hace?**: Guarda las imágenes como archivos
**¿Por qué?**: Es como AWS S3 pero gratis y local
**Estructura**:
```
/raw-images/2024/01/15/imagen123.jpg
/processed-images/2024/01/15/imagen123_resized.jpg
```

### 6️⃣ **PostgreSQL** (Base de Datos)
**¿Qué hace?**: Guarda información estructurada
**¿Por qué?**: Para consultas rápidas y relaciones entre datos
**Tablas**:
```sql
predictions:
  - id
  - image_path
  - model_name
  - prediction
  - confidence
  - inference_time_ms
  - created_at
```

### 7️⃣ **MLflow** (Tracking de Experimentos)
**¿Qué hace?**: Registra todo lo que hacen los modelos
**¿Por qué?**: Para saber qué modelo funciona mejor
**Registra**:
- Parámetros del modelo
- Métricas (accuracy, speed)
- Versiones de modelos
- Comparaciones

### 8️⃣ **Airflow** (Orquestador)
**¿Qué hace?**: Programa tareas automáticas
**¿Por qué?**: Para reentrenar modelos automáticamente
**DAGs (tareas programadas)**:
```
Cada semana:
  1. Descargar nuevas imágenes
  2. Reentrenar modelos
  3. Evaluar performance
  4. Desplegar mejor modelo
```

### 9️⃣ **Modelos de IA** (La Magia)

#### **ResNet50**
- **Qué es**: Red neuronal profunda (50 capas)
- **Características**: Muy preciso, pero más lento
- **Cuándo usarlo**: Cuando la precisión es crítica
- **Tiempo**: ~150ms por imagen

#### **MobileNet**
- **Qué es**: Red optimizada para móviles
- **Características**: Super rápido, menos preciso
- **Cuándo usarlo**: Apps móviles, tiempo real
- **Tiempo**: ~50ms por imagen

#### **EfficientNet**
- **Qué es**: Balance entre velocidad y precisión
- **Características**: Lo mejor de ambos mundos
- **Cuándo usarlo**: Producción general
- **Tiempo**: ~80ms por imagen

## 📊 FUENTES DE DATOS

### Dataset Principal: **CIFAR-10**
**¿Qué es?**: 60,000 imágenes de 10 categorías
- ✈️ Aviones
- 🚗 Automóviles
- 🐦 Pájaros
- 🐱 Gatos
- 🦌 Venados
- 🐕 Perros
- 🐸 Ranas
- 🐴 Caballos
- 🚢 Barcos
- 🚚 Camiones

**Descarga**: Automática al iniciar el proyecto (usando TensorFlow)

### Datos en Tiempo Real:
1. **Webcam**: Captura de tu cámara
2. **Uploads**: Imágenes que subas manualmente
3. **API Externa** (opcional): Unsplash API para imágenes random

## 🚀 FLUJO COMPLETO DEL SISTEMA

```
PASO 1: Usuario sube imagen "gato.jpg"
  ↓
PASO 2: Django envía a FastAPI
  ↓
PASO 3: FastAPI guarda imagen en MinIO
  ↓
PASO 4: FastAPI publica mensaje en Kafka topic "images-input"
  Mensaje: {
    "image_id": "123",
    "image_path": "s3://raw-images/gato.jpg",
    "timestamp": "2024-01-15T10:30:00"
  }
  ↓
PASO 5: 3 Servicios (ResNet, MobileNet, EfficientNet) leen el mensaje
  ↓
PASO 6: Cada servicio:
  - Descarga imagen de MinIO
  - Procesa con su modelo
  - Cronometra el tiempo
  - Publica resultado en Kafka topic "predictions-output"

  Ejemplo resultado ResNet:
  {
    "image_id": "123",
    "model": "resnet50",
    "prediction": "gato",
    "confidence": 0.95,
    "inference_time_ms": 145,
    "timestamp": "2024-01-15T10:30:00.500"
  }
  ↓
PASO 7: Consumer de resultados guarda en PostgreSQL
  ↓
PASO 8: Dashboard consulta PostgreSQL y muestra:

  ┌─────────────────────────────────────┐
  │  Imagen: gato.jpg                   │
  │  ────────────────────────────────   │
  │  ResNet50:    GATO (95%) - 145ms   │
  │  MobileNet:   GATO (92%) - 48ms    │
  │  EfficientNet: GATO (94%) - 82ms   │
  │                                      │
  │  🏆 Más rápido: MobileNet           │
  │  🎯 Más preciso: ResNet50           │
  │  ⚖️ Mejor balance: EfficientNet     │
  └─────────────────────────────────────┘
```

## 🎨 VISUALIZACIONES EN EL DASHBOARD

1. **Gráfico de Barras**: Tiempo de inferencia por modelo
2. **Gráfico de Líneas**: Accuracy a lo largo del tiempo
3. **Tabla**: Últimas 50 predicciones
4. **Pie Chart**: Distribución de clases predichas
5. **Heatmap**: Matriz de confusión de cada modelo
6. **Stream en vivo**: Video de webcam con predicciones overlay

## 🐳 DOCKER: TODO CONTENEDORIZADO

Cada servicio corre en su propio contenedor:

```yaml
Servicio              Puerto    Descripción
────────────────────────────────────────────────────
Django               8000      Dashboard web
FastAPI              8001      REST API
GraphQL              8002      GraphQL API
Kafka                9092      Message broker
Zookeeper            2181      Kafka coordination
PostgreSQL           5432      Base de datos
MinIO                9000      Object storage
MinIO Console        9001      UI de MinIO
MLflow               5000      Tracking server
Airflow Webserver    8080      UI de Airflow
Airflow Scheduler    -         Background tasks
ResNet Service       8003      Modelo 1
MobileNet Service    8004      Modelo 2
EfficientNet Service 8005      Modelo 3
Redis                6379      Cache
Prometheus           9090      Métricas
Grafana              3000      Dashboards de infra
```

## 📈 MÉTRICAS QUE VAMOS A MEDIR

### Por Modelo:
- ⏱️ **Latencia promedio** (ms)
- 🎯 **Accuracy** (%)
- 💾 **Memoria usada** (MB)
- 🔄 **Throughput** (imágenes/segundo)
- 📊 **Precision, Recall, F1-Score**

### Por Sistema:
- 📬 **Mensajes en Kafka** (rate)
- 💽 **Espacio en MinIO** (GB)
- 🗄️ **Queries a PostgreSQL** (QPS)
- 🔥 **Errores/Excepciones**

## 🎓 LO QUE VAS A APRENDER

✅ Arquitectura de microservicios
✅ Event-driven architecture (Kafka)
✅ MLOps end-to-end
✅ Docker & Docker Compose
✅ APIs REST y GraphQL
✅ Streaming de datos en tiempo real
✅ Model serving y versionado
✅ Monitoring y observabilidad
✅ CI/CD para ML
✅ Best practices de producción

## 🚀 INICIO RÁPIDO

```bash
# 1. Instalar Docker Desktop (ver INSTALL_DOCKER.md)

# 2. Clonar el proyecto
git clone <repo>
cd mlops2

# 3. Levantar todo (¡un solo comando!)
docker-compose up -d

# 4. Esperar 2-3 minutos mientras se descargan imágenes

# 5. Abrir el dashboard
http://localhost:8000

# 6. ¡Subir tu primera imagen y ver la magia! 🎉
```

## 📚 DOCUMENTACIÓN ADICIONAL

- `ARCHITECTURE.md` - Arquitectura detallada
- `API_DOCS.md` - Documentación de APIs
- `MODELS.md` - Explicación de modelos ML
- `DEPLOYMENT.md` - Deploy a producción
- `TROUBLESHOOTING.md` - Solución de problemas

## 🎯 ROADMAP

### Fase 1: MVP (Minimum Viable Product) ✅
- [x] Arquitectura base
- [ ] Docker Compose
- [ ] 1 Modelo funcionando
- [ ] API básica
- [ ] Dashboard simple

### Fase 2: Múltiples Modelos
- [ ] 3 Modelos en paralelo
- [ ] Kafka streaming
- [ ] Comparación de tiempos
- [ ] Gráficos avanzados

### Fase 3: MLOps Completo
- [ ] MLflow tracking
- [ ] Airflow pipelines
- [ ] Auto-retraining
- [ ] A/B Testing

### Fase 4: Producción
- [ ] Kubernetes deployment
- [ ] Monitoring completo
- [ ] CI/CD pipeline
- [ ] Escalabilidad

## 🤝 CONTRIBUIR

¡Pull requests son bienvenidos! Para cambios grandes, abre un issue primero.

## 📄 LICENCIA

MIT License - Úsalo como quieras, aprende y comparte.

---

**¿Preguntas?** Abre un issue o revisa la documentación en `/docs`
#   m l o p s 2  
 