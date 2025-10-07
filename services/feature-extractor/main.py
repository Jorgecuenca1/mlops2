"""
Feature Extractor Service
Extrae descriptores de imágenes usando un modelo preentrenado (ResNet50 sin la capa final)
y publica vectores de features compactos en lugar de imágenes completas.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing import image
from kafka import KafkaConsumer, KafkaProducer
from minio import Minio
import json
import os
from io import BytesIO
from PIL import Image as PILImage
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# CONFIGURACIÓN
# ============================================

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092").split(",")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin123")

# ============================================
# MODELO DE EXTRACCIÓN DE FEATURES
# ============================================

class FeatureExtractor:
    def __init__(self):
        """
        Carga ResNet50 preentrenado sin la capa de clasificación final
        Output: vector de 2048 features (en lugar de 1000 clases)
        """
        logger.info("🔧 Cargando modelo ResNet50 para extracción de features...")

        # Cargar ResNet50 sin la capa final (include_top=False) + GlobalAveragePooling
        base_model = ResNet50(
            weights='imagenet',
            include_top=False,
            pooling='avg'  # Esto da un vector de 2048 features
        )

        self.model = base_model
        self.model.trainable = False  # No vamos a reentrenar

        logger.info("✅ Modelo cargado. Output shape: 2048 features")

    def extract_features(self, img_array: np.ndarray, num_descriptors: int = 20) -> List[float]:
        """
        Extrae features de una imagen

        Args:
            img_array: Array de numpy con la imagen (224, 224, 3)
            num_descriptors: Número de descriptores a extraer (reducción dimensional)

        Returns:
            Lista de floats con los descriptores más importantes
        """
        # Preprocesar imagen para ResNet50
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        # Extraer features (2048 dimensiones)
        features = self.model.predict(img_array, verbose=0)
        features = features.flatten()

        # Reducir dimensionalidad: tomar los N valores con mayor magnitud
        # Esto es una simplificación; en producción usarías PCA o similar
        top_indices = np.argsort(np.abs(features))[-num_descriptors:]
        descriptors = features[top_indices].tolist()

        logger.info(f"📊 Extraídos {len(descriptors)} descriptores (de 2048 originales)")
        return descriptors

# ============================================
# CLIENTE MINIO
# ============================================

class MinIOClient:
    def __init__(self):
        self.client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False
        )
        logger.info(f"✅ MinIO client conectado a {MINIO_ENDPOINT}")

    def download_image(self, bucket: str, object_name: str) -> PILImage.Image:
        """Descarga imagen desde MinIO"""
        try:
            response = self.client.get_object(bucket, object_name)
            img_data = response.read()
            img = PILImage.open(BytesIO(img_data))
            return img
        except Exception as e:
            logger.error(f"❌ Error descargando imagen de MinIO: {e}")
            raise

    def parse_minio_path(self, path: str):
        """
        Parse path como 'raw-images/2024/01/15/uuid.jpg'
        Retorna bucket y object_name
        """
        parts = path.split("/", 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        else:
            return "raw-images", path

# ============================================
# KAFKA CONSUMER/PRODUCER
# ============================================

class FeatureStreamProcessor:
    def __init__(self):
        self.consumer = KafkaConsumer(
            'images-input-stream',
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='feature-extractor-group'
        )

        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        self.extractor = FeatureExtractor()
        self.minio_client = MinIOClient()

        logger.info("✅ Kafka consumer/producer inicializados")

    def preprocess_image(self, img: PILImage.Image) -> np.ndarray:
        """Preprocesa imagen para el modelo"""
        # Resize a 224x224
        img = img.resize((224, 224))

        # Convertir a RGB si es necesario
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Convertir a array numpy
        img_array = np.array(img)

        return img_array

    def process_message(self, message: dict):
        """
        Procesa un mensaje de Kafka:
        1. Descarga imagen de MinIO
        2. Extrae descriptores
        3. Publica descriptores en nuevo topic
        """
        try:
            image_id = message.get('image_id')
            minio_path = message.get('minio_path')

            logger.info(f"📥 Procesando imagen: {image_id}")

            # Descargar imagen
            bucket, object_name = self.minio_client.parse_minio_path(minio_path)
            img = self.minio_client.download_image(bucket, object_name)

            # Preprocesar
            img_array = self.preprocess_image(img)

            # Extraer features (20 descriptores por defecto)
            descriptors = self.extractor.extract_features(img_array, num_descriptors=20)

            # Crear mensaje con descriptores
            feature_message = {
                'image_id': image_id,
                'descriptors': descriptors,
                'descriptor_count': len(descriptors),
                'minio_path': minio_path,  # Por si se necesita la imagen original
                'timestamp': message.get('timestamp'),
                'metadata': message.get('metadata', {})
            }

            # Publicar en nuevo topic
            self.producer.send('image-features-stream', value=feature_message)
            self.producer.flush()

            logger.info(f"✅ Descriptores publicados para imagen {image_id}")

        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {e}")

    def start(self):
        """Inicia el loop de procesamiento"""
        logger.info("🚀 Iniciando procesamiento de imágenes...")

        try:
            for message in self.consumer:
                self.process_message(message.value)
        except KeyboardInterrupt:
            logger.info("⏹️ Deteniendo procesamiento...")
        finally:
            self.consumer.close()
            self.producer.close()

# ============================================
# FASTAPI (para health checks y testing)
# ============================================

app = FastAPI(
    title="Feature Extractor Service",
    description="Extrae descriptores compactos de imágenes",
    version="1.0.0"
)

# Instancia global del extractor
feature_extractor = FeatureExtractor()

class FeatureExtractionRequest(BaseModel):
    image_id: str
    minio_path: str

class FeatureExtractionResponse(BaseModel):
    image_id: str
    descriptors: List[float]
    descriptor_count: int

@app.get("/")
async def root():
    return {
        "service": "Feature Extractor",
        "version": "1.0.0",
        "status": "running",
        "model": "ResNet50 (feature extraction)",
        "output_dimensions": 20
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": feature_extractor.model is not None
    }

@app.post("/extract", response_model=FeatureExtractionResponse)
async def extract_features_endpoint(request: FeatureExtractionRequest):
    """
    Endpoint para testing manual de extracción de features
    """
    try:
        minio_client = MinIOClient()
        bucket, object_name = minio_client.parse_minio_path(request.minio_path)
        img = minio_client.download_image(bucket, object_name)

        # Preprocesar
        img_array = np.array(img.resize((224, 224)))

        # Extraer features
        descriptors = feature_extractor.extract_features(img_array, num_descriptors=20)

        return FeatureExtractionResponse(
            image_id=request.image_id,
            descriptors=descriptors,
            descriptor_count=len(descriptors)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "stream":
        # Modo consumer: procesa imágenes desde Kafka
        processor = FeatureStreamProcessor()
        processor.start()
    else:
        # Modo API: servidor FastAPI para testing
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
