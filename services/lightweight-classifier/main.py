"""
Lightweight Classifier Service
Consume descriptores (en lugar de imágenes) y realiza clasificación rápida
Usa modelos simples (Random Forest, SVM) entrenados sobre los descriptores
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import numpy as np
from kafka import KafkaConsumer, KafkaProducer
import json
import os
import logging
import time
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import psycopg2
from psycopg2.extras import execute_values

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# CONFIGURACIÓN
# ============================================

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092").split(",")
MODEL_NAME = os.getenv("MODEL_NAME", "random_forest_v1")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_USER = os.getenv("POSTGRES_USER", "mlops")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "mlops123")
POSTGRES_DB = os.getenv("POSTGRES_DB", "mlops_db")

# ============================================
# CLASIFICADOR LIGERO
# ============================================

class LightweightClassifier:
    """
    Clasificador simple que trabaja con descriptores
    Simula 3 modelos diferentes con diferentes características
    """

    def __init__(self, model_variant: str = "balanced"):
        self.model_variant = model_variant
        self.classes = [
            "airplane", "automobile", "bird", "cat", "deer",
            "dog", "frog", "horse", "ship", "truck"
        ]

        # Simular diferentes "modelos" con diferentes configuraciones
        if model_variant == "fast":
            # Modelo rápido pero menos preciso
            self.model_name = "FastClassifier"
            self.base_latency = 15  # ms
            self.confidence_modifier = 0.85
        elif model_variant == "accurate":
            # Modelo preciso pero más lento
            self.model_name = "AccurateClassifier"
            self.base_latency = 45  # ms
            self.confidence_modifier = 0.95
        else:
            # Modelo balanceado
            self.model_name = "BalancedClassifier"
            self.base_latency = 25  # ms
            self.confidence_modifier = 0.90

        logger.info(f"✅ Inicializado {self.model_name} (latencia base: {self.base_latency}ms)")

    def predict(self, descriptors: List[float]) -> Dict:
        """
        Realiza predicción basada en descriptores

        Args:
            descriptors: Lista de 20 floats (features extraídos)

        Returns:
            Dict con predicción, confianza y tiempo
        """
        start_time = time.time()

        # Convertir a numpy array
        features = np.array(descriptors).reshape(1, -1)

        # Simular procesamiento: normalizar
        features_normalized = (features - features.mean()) / (features.std() + 1e-8)

        # Simular predicción: usar la suma de features para determinar clase
        # En producción real, usarías un modelo entrenado
        feature_sum = np.abs(features_normalized).sum()
        class_idx = int(feature_sum * 10) % len(self.classes)

        predicted_class = self.classes[class_idx]

        # Simular confianza: basada en magnitud de features
        base_confidence = min(0.99, max(0.70, feature_sum / 20.0))
        confidence = base_confidence * self.confidence_modifier

        # Simular latencia del modelo
        processing_time = self.base_latency + np.random.randint(-5, 10)

        # Añadir tiempo real de procesamiento
        actual_time = int((time.time() - start_time) * 1000)
        total_time = max(actual_time, processing_time)

        return {
            "prediction_class": predicted_class,
            "confidence": round(float(confidence), 4),
            "inference_time_ms": total_time,
            "model_name": self.model_name
        }

# ============================================
# BASE DE DATOS
# ============================================

class DatabaseClient:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=POSTGRES_HOST,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            dbname=POSTGRES_DB
        )
        logger.info("✅ Conectado a PostgreSQL")

    def save_prediction(self, image_id: str, prediction: Dict):
        """Guarda predicción en la base de datos"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO predictions
                (image_id, model_name, prediction_class, confidence, inference_time_ms)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                image_id,
                prediction['model_name'],
                prediction['prediction_class'],
                prediction['confidence'],
                prediction['inference_time_ms']
            ))
            self.conn.commit()
            cursor.close()
            logger.info(f"💾 Predicción guardada: {image_id} -> {prediction['prediction_class']}")
        except Exception as e:
            logger.error(f"❌ Error guardando predicción: {e}")
            self.conn.rollback()

# ============================================
# KAFKA PROCESSOR
# ============================================

class ClassifierProcessor:
    def __init__(self, model_variant: str = "balanced"):
        self.consumer = KafkaConsumer(
            'image-features-stream',
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=f'classifier-{model_variant}-group'
        )

        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        self.classifier = LightweightClassifier(model_variant)
        self.db_client = DatabaseClient()

        logger.info(f"✅ Processor inicializado: {model_variant}")

    def process_message(self, message: dict):
        """
        Procesa mensaje con descriptores:
        1. Recibe descriptores
        2. Ejecuta clasificación
        3. Guarda en DB
        4. Publica resultado
        """
        try:
            image_id = message.get('image_id')
            descriptors = message.get('descriptors')

            logger.info(f"📥 Clasificando imagen {image_id} con {len(descriptors)} descriptores")

            # Ejecutar predicción
            prediction = self.classifier.predict(descriptors)

            # Agregar metadata
            result = {
                'image_id': image_id,
                'model_name': prediction['model_name'],
                'prediction_class': prediction['prediction_class'],
                'confidence': prediction['confidence'],
                'inference_time_ms': prediction['inference_time_ms'],
                'timestamp': message.get('timestamp')
            }

            # Guardar en base de datos
            self.db_client.save_prediction(image_id, result)

            # Publicar resultado
            self.producer.send('predictions-output', value=result)
            self.producer.flush()

            logger.info(
                f"✅ {prediction['model_name']}: {prediction['prediction_class']} "
                f"({prediction['confidence']:.2%}) en {prediction['inference_time_ms']}ms"
            )

        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {e}")

    def start(self):
        """Inicia el loop de procesamiento"""
        logger.info("🚀 Iniciando clasificación de features...")

        try:
            for message in self.consumer:
                self.process_message(message.value)
        except KeyboardInterrupt:
            logger.info("⏹️ Deteniendo procesamiento...")
        finally:
            self.consumer.close()
            self.producer.close()

# ============================================
# FASTAPI (para health checks)
# ============================================

app = FastAPI(
    title=f"Lightweight Classifier - {MODEL_NAME}",
    description="Clasificador ligero que consume descriptores de imágenes",
    version="1.0.0"
)

# Instancia global
classifier = LightweightClassifier()

class PredictionRequest(BaseModel):
    descriptors: List[float]

class PredictionResponse(BaseModel):
    prediction_class: str
    confidence: float
    inference_time_ms: int
    model_name: str

@app.get("/")
async def root():
    return {
        "service": "Lightweight Classifier",
        "model": classifier.model_name,
        "version": "1.0.0",
        "status": "running",
        "input": "20 descriptors",
        "base_latency_ms": classifier.base_latency
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model": classifier.model_name,
        "classes": len(classifier.classes)
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict_endpoint(request: PredictionRequest):
    """Endpoint para testing manual"""
    try:
        if len(request.descriptors) != 20:
            raise HTTPException(
                status_code=400,
                detail=f"Se esperan 20 descriptores, recibidos {len(request.descriptors)}"
            )

        result = classifier.predict(request.descriptors)
        return PredictionResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "stream":
        # Modo consumer: procesa desde Kafka
        model_variant = os.getenv("MODEL_VARIANT", "balanced")
        processor = ClassifierProcessor(model_variant)
        processor.start()
    else:
        # Modo API: servidor FastAPI para testing
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
