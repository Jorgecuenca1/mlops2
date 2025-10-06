# 📸 FUENTES DE DATOS - De dónde vienen las imágenes

## 🎯 MÚLTIPLES FUENTES DE IMÁGENES

### 1️⃣ **WEBCAM LOCAL (OpenCV)** - ¡El más visual!

**¿Cómo funciona?**
```python
import cv2

# Captura desde la webcam de tu computadora
cap = cv2.VideoCapture(0)  # 0 = webcam principal
ret, frame = cap.read()

# Envía el frame a Kafka cada X segundos
```

**Características**:
- ✅ **100% en tiempo real**
- ✅ **Super visual para demos**
- ✅ **No requiere internet**
- ✅ **Puedes mover objetos frente a la cámara y ver las predicciones**

**Flujo**:
```
Tu Webcam → OpenCV captura frame →
            → Guarda en MinIO →
            → Publica en Kafka →
            → 3 modelos predicen →
            → Dashboard muestra resultado en <100ms
```

**Implementación**: Servicio `webcam-producer` en Docker

---

### 2️⃣ **UPLOAD MANUAL** - Sube tus propias imágenes

**¿Cómo funciona?**
- Desde el dashboard Django, botón "Subir Imagen"
- Drag & drop de archivos
- Acepta: JPG, PNG, WebP

**Características**:
- ✅ **Control total sobre las imágenes**
- ✅ **Puedes probar con cualquier imagen**
- ✅ **Útil para testing específico**

**Flujo**:
```
Navegador → Django recibe archivo →
           → FastAPI guarda en MinIO →
           → Publica en Kafka →
           → Procesamiento normal
```

---

### 3️⃣ **DATASET CIFAR-10** - Imágenes de entrenamiento

**¿Qué es?**: Dataset público de 60,000 imágenes
**Dónde está**: Se descarga automáticamente de TensorFlow

```python
from tensorflow.keras.datasets import cifar10

# Descarga automática (primera vez ~170 MB)
(x_train, y_train), (x_test, y_test) = cifar10.load_data()
```

**10 Categorías**:
1. ✈️ Avión (airplane)
2. 🚗 Automóvil (automobile)
3. 🐦 Pájaro (bird)
4. 🐱 Gato (cat)
5. 🦌 Venado (deer)
6. 🐕 Perro (dog)
7. 🐸 Rana (frog)
8. 🐴 Caballo (horse)
9. 🚢 Barco (ship)
10. 🚚 Camión (truck)

**Características**:
- ✅ **Descarga automática al primer uso**
- ✅ **Gratuito y legal**
- ✅ **Perfecto para entrenamiento y testing**
- ✅ **Imágenes 32x32 píxeles (ligeras)**

**Uso en el proyecto**:
```python
# Script que simula streaming de CIFAR-10
# Lee imágenes del dataset y las envía a Kafka
# Configurable: X imágenes por segundo
```

---

### 4️⃣ **API PÚBLICA - Unsplash** (Opcional)

**¿Qué es?**: API gratuita de fotos de alta calidad
**URL**: https://unsplash.com/developers

```python
import requests

# API gratuita (50 requests/hora)
response = requests.get(
    'https://api.unsplash.com/photos/random',
    params={'query': 'cat'},
    headers={'Authorization': 'Client-ID TU_KEY'}
)
```

**Características**:
- ✅ **Imágenes reales de alta calidad**
- ✅ **Gratuito (con límites)**
- ✅ **Variedad infinita**

---

### 5️⃣ **SIMULADOR DE CÁMARA IP** (Avanzado)

**¿Qué es?**: Simulamos múltiples "cámaras" leyendo videos

```python
# Lee un video MP4 como si fuera una cámara
video = cv2.VideoCapture('camara_seguridad.mp4')

# Extrae frames y los envía como si fueran en vivo
```

**Características**:
- ✅ **Simula entorno de producción real**
- ✅ **Puedes usar cualquier video**
- ✅ **Ideal para demos profesionales**

---

## 🚀 ARQUITECTURA DE CAPTURA

```
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTORES DE IMÁGENES                   │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Webcam   │  │ Upload   │  │ CIFAR-10 │  │ Unsplash │   │
│  │ Producer │  │ API      │  │ Streamer │  │ API      │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │             │             │           │
│       └─────────────┴─────────────┴─────────────┘           │
│                         │                                    │
└─────────────────────────┼────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                      KAFKA TOPIC                             │
│                   "images-input-stream"                      │
│                                                              │
│  Mensajes:                                                   │
│  {                                                           │
│    "image_id": "uuid",                                      │
│    "source": "webcam|upload|cifar10|unsplash",             │
│    "timestamp": "2024-01-15T10:30:00",                     │
│    "minio_path": "s3://raw-images/img.jpg",                │
│    "metadata": {...}                                        │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
                  [3 Modelos consumen]
```

---

## 📦 SERVICIOS DE CAPTURA

### **Servicio 1: webcam-producer**

```dockerfile
# services/kafka-producer/Dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libopencv-dev \
    python3-opencv

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY webcam_producer.py .

CMD ["python", "webcam_producer.py"]
```

```python
# services/kafka-producer/webcam_producer.py
import cv2
import time
from kafka import KafkaProducer
from minio import Minio
import uuid

# Configuración
KAFKA_BOOTSTRAP = 'kafka:9092'
MINIO_ENDPOINT = 'minio:9000'
FPS = 2  # 2 imágenes por segundo

producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP)
minio_client = Minio(MINIO_ENDPOINT, ...)

# Captura de webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if ret:
        # Guarda en MinIO
        image_id = str(uuid.uuid4())
        path = f"raw-images/{image_id}.jpg"

        # Upload a MinIO
        cv2.imwrite(f"/tmp/{image_id}.jpg", frame)
        minio_client.fput_object('raw-images', path, f"/tmp/{image_id}.jpg")

        # Publica en Kafka
        message = {
            'image_id': image_id,
            'source': 'webcam',
            'minio_path': path
        }
        producer.send('images-input-stream', message)

    time.sleep(1/FPS)
```

---

### **Servicio 2: cifar10-streamer**

```python
# services/kafka-producer/cifar10_streamer.py
from tensorflow.keras.datasets import cifar10
import time

# Descarga CIFAR-10 (solo primera vez)
(x_train, y_train), (x_test, y_test) = cifar10.load_data()

print(f"✅ CIFAR-10 descargado: {len(x_train)} imágenes de entrenamiento")

# Simula streaming
for i, (image, label) in enumerate(zip(x_test, y_test)):
    # Guarda en MinIO
    # Publica en Kafka
    time.sleep(0.5)  # 2 imágenes por segundo
```

---

### **Servicio 3: upload-api** (Ya incluido en FastAPI)

```python
# services/fastapi/main.py
from fastapi import FastAPI, UploadFile

@app.post("/upload")
async def upload_image(file: UploadFile):
    # Guarda en MinIO
    # Publica en Kafka
    return {"image_id": "...", "status": "processing"}
```

---

## 🎮 MODO DEMO INTERACTIVO

### **Opción 1: Dashboard con controles**

```
┌─────────────────────────────────────────┐
│  🎥 Fuentes de Datos                    │
├─────────────────────────────────────────┤
│  [ ] Webcam (2 FPS)          [▶️ START] │
│  [ ] CIFAR-10 Stream (5 FPS) [▶️ START] │
│  [ ] Upload Manual           [📁 OPEN]  │
│  [ ] Unsplash Random         [🔄 FETCH] │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  📊 Stream en Vivo                      │
├─────────────────────────────────────────┤
│  [Video de webcam con overlay]          │
│                                          │
│  ResNet:    🐱 GATO (95%)  - 145ms     │
│  MobileNet: 🐱 GATO (92%)  - 48ms      │
│  Efficient: 🐱 GATO (94%)  - 82ms      │
└─────────────────────────────────────────┘
```

---

## 📝 RESUMEN DE FUENTES

| Fuente | Tipo | Velocidad | Uso | Requiere Internet |
|--------|------|-----------|-----|-------------------|
| **Webcam** | Real-time | 1-30 FPS | Demo visual | ❌ No |
| **Upload** | On-demand | Manual | Testing específico | ❌ No |
| **CIFAR-10** | Dataset | Configurable | Entrenamiento | ⚠️ Solo primera vez |
| **Unsplash** | API | ~1 por segundo | Variedad | ✅ Sí |
| **Video MP4** | Simulado | Configurable | Demo profesional | ❌ No |

---

## 🎯 RECOMENDACIÓN FINAL

**Para tu proyecto, implementaremos**:

1. ✅ **Webcam Producer** - Para el "WOW Factor"
2. ✅ **CIFAR-10 Streamer** - Para datos consistentes
3. ✅ **Upload API** - Para flexibilidad
4. ⚠️ **Unsplash** (Opcional) - Si quieres variedad

**Todo configurable desde el dashboard Django** con botones Start/Stop para cada fuente.

---

## 🔧 CONFIGURACIÓN EN DOCKER-COMPOSE

Ya lo agregué al `docker-compose.yml`:

```yaml
services:
  webcam-producer:
    build: ./services/kafka-producer
    environment:
      SOURCE_TYPE: webcam
      FPS: 2
    devices:
      - /dev/video0:/dev/video0  # Acceso a webcam

  cifar10-producer:
    build: ./services/kafka-producer
    environment:
      SOURCE_TYPE: cifar10
      IMAGES_PER_SECOND: 5
```

**¿Quieres que continúe creando estos servicios?** 🚀
