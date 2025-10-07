"""
FastAPI Service - API REST para el sistema MLOps
Maneja:
- Upload de imágenes
- Publicación en Kafka
- Consultas de predicciones
- Health checks
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
import uuid
import time
import json
from datetime import datetime
from io import BytesIO

# Importaciones propias
from config import settings
from database import get_db, Prediction, Image, ModelComparison
from kafka_producer import KafkaImageProducer
from minio_client import MinIOClient
from utils import process_image, get_image_metadata

# ============================================
# INICIALIZACIÓN
# ============================================

app = FastAPI(
    title="MLOps Vision Platform API",
    description="API REST para sistema de clasificación de imágenes en tiempo real",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS - Permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Clientes
kafka_producer = KafkaImageProducer()
minio_client = MinIOClient()

# ============================================
# MODELOS PYDANTIC
# ============================================

class ImageUploadResponse(BaseModel):
    image_id: str
    filename: str
    file_size: int
    minio_path: str
    status: str
    message: str
    timestamp: str

class PredictionResponse(BaseModel):
    id: int
    image_id: str
    model_name: str
    prediction_class: str
    confidence: float
    inference_time_ms: int
    created_at: str

class ModelComparisonResponse(BaseModel):
    image_id: str
    original_filename: str
    resnet: Optional[dict]
    mobilenet: Optional[dict]
    efficientnet: Optional[dict]
    fastest_model: Optional[str]
    most_confident_model: Optional[str]
    consensus_prediction: Optional[str]

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str
    services: dict

# ============================================
# ENDPOINTS - HEALTH CHECK
# ============================================

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "service": "MLOps Vision Platform API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check completo del sistema
    Verifica conectividad con todos los servicios
    """
    services_status = {}

    # Check Kafka
    try:
        kafka_producer.check_connection()
        services_status["kafka"] = "healthy"
    except Exception as e:
        services_status["kafka"] = f"unhealthy: {str(e)}"

    # Check MinIO
    try:
        minio_client.check_connection()
        services_status["minio"] = "healthy"
    except Exception as e:
        services_status["minio"] = f"unhealthy: {str(e)}"

    # Check PostgreSQL
    try:
        db = next(get_db())
        db.execute("SELECT 1")
        services_status["postgres"] = "healthy"
    except Exception as e:
        services_status["postgres"] = f"unhealthy: {str(e)}"

    # Check Redis (opcional)
    try:
        # TODO: implementar check de Redis
        services_status["redis"] = "not_implemented"
    except Exception as e:
        services_status["redis"] = f"unhealthy: {str(e)}"

    # Determinar estado general
    all_healthy = all(status == "healthy" for status in services_status.values() if status != "not_implemented")
    overall_status = "healthy" if all_healthy else "degraded"

    return HealthCheckResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        services=services_status
    )

# ============================================
# ENDPOINTS - UPLOAD DE IMÁGENES
# ============================================

@app.post("/upload", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Upload de imagen para procesamiento

    Flujo:
    1. Recibe imagen del usuario
    2. Valida formato y tamaño
    3. Guarda en MinIO
    4. Registra en PostgreSQL
    5. Publica mensaje en Kafka
    6. Retorna image_id para tracking
    """

    # Validar tipo de archivo
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido. Permitidos: {allowed_types}"
        )

    # Leer archivo
    contents = await file.read()
    file_size = len(contents)

    # Validar tamaño (máximo 10 MB)
    max_size = 10 * 1024 * 1024  # 10 MB
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"Archivo muy grande. Máximo: {max_size / 1024 / 1024} MB"
        )

    try:
        # Generar ID único
        image_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()

        # Obtener metadata de la imagen
        metadata = get_image_metadata(BytesIO(contents))

        # Guardar en MinIO
        object_name = f"{timestamp.strftime('%Y/%m/%d')}/{image_id}.jpg"
        minio_client.upload_image(
            bucket="raw-images",
            object_name=object_name,
            data=BytesIO(contents),
            length=file_size
        )
        minio_path = f"raw-images/{object_name}"  # Path completo para referencia

        # Registrar en PostgreSQL
        db = next(get_db())
        image_record = Image(
            image_id=image_id,
            original_filename=file.filename,
            minio_path=minio_path,
            upload_timestamp=timestamp,
            file_size_bytes=file_size,
            width=metadata.get("width"),
            height=metadata.get("height"),
            format=metadata.get("format"),
            source="upload",
            processing_status="pending"
        )
        db.add(image_record)
        db.commit()

        # Publicar en Kafka
        kafka_message = {
            "image_id": image_id,
            "minio_bucket": "raw-images",
            "minio_object": object_name,
            "source": "upload",
            "timestamp": timestamp.isoformat(),
            "metadata": metadata
        }
        kafka_producer.send_image(kafka_message)

        return ImageUploadResponse(
            image_id=image_id,
            filename=file.filename,
            file_size=file_size,
            minio_path=minio_path,
            status="queued",
            message="Imagen en cola para procesamiento",
            timestamp=timestamp.isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar imagen: {str(e)}")

@app.post("/upload/batch")
async def upload_batch(files: List[UploadFile] = File(...)):
    """
    Upload de múltiples imágenes
    """
    results = []

    for file in files:
        try:
            result = await upload_image(file)
            results.append(result)
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })

    return {"uploaded": len(results), "results": results}

# ============================================
# ENDPOINTS - CONSULTAS DE PREDICCIONES
# ============================================

@app.get("/predictions/{image_id}", response_model=List[PredictionResponse])
async def get_predictions(image_id: str):
    """
    Obtener todas las predicciones de una imagen
    (de los 3 modelos)
    """
    db = next(get_db())
    predictions = db.query(Prediction).filter(
        Prediction.image_id == image_id
    ).all()

    if not predictions:
        raise HTTPException(status_code=404, detail="No se encontraron predicciones")

    return [
        PredictionResponse(
            id=p.id,
            image_id=p.image_id,
            model_name=p.model_name,
            prediction_class=p.prediction_class,
            confidence=p.confidence,
            inference_time_ms=p.inference_time_ms,
            created_at=p.created_at.isoformat()
        )
        for p in predictions
    ]

@app.get("/predictions/recent/{limit}")
async def get_recent_predictions(limit: int = 50):
    """
    Obtener las últimas N predicciones
    """
    db = next(get_db())
    predictions = db.query(Prediction).order_by(
        Prediction.created_at.desc()
    ).limit(limit).all()

    return [
        PredictionResponse(
            id=p.id,
            image_id=p.image_id,
            model_name=p.model_name,
            prediction_class=p.prediction_class,
            confidence=p.confidence,
            inference_time_ms=p.inference_time_ms,
            created_at=p.created_at.isoformat()
        )
        for p in predictions
    ]

@app.get("/comparisons/{image_id}", response_model=ModelComparisonResponse)
async def get_model_comparison(image_id: str):
    """
    Comparación de los 3 modelos para una imagen
    """
    db = next(get_db())

    # Obtener imagen
    image = db.query(Image).filter(Image.image_id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    # Obtener predicciones de cada modelo
    predictions = db.query(Prediction).filter(
        Prediction.image_id == image_id
    ).all()

    # Organizar por modelo
    model_results = {}
    for p in predictions:
        model_results[p.model_name] = {
            "prediction": p.prediction_class,
            "confidence": p.confidence,
            "time_ms": p.inference_time_ms
        }

    # Calcular estadísticas
    if predictions:
        fastest = min(predictions, key=lambda x: x.inference_time_ms)
        most_confident = max(predictions, key=lambda x: x.confidence)

        # Consenso (predicción más común)
        from collections import Counter
        pred_counts = Counter([p.prediction_class for p in predictions])
        consensus = pred_counts.most_common(1)[0][0]
    else:
        fastest = most_confident = consensus = None

    return ModelComparisonResponse(
        image_id=image_id,
        original_filename=image.original_filename,
        resnet=model_results.get("resnet50"),
        mobilenet=model_results.get("mobilenet_v2"),
        efficientnet=model_results.get("efficientnet_b0"),
        fastest_model=fastest.model_name if fastest else None,
        most_confident_model=most_confident.model_name if most_confident else None,
        consensus_prediction=consensus
    )

# ============================================
# ENDPOINTS - ESTADÍSTICAS
# ============================================

@app.get("/stats/models")
async def get_model_stats():
    """
    Estadísticas agregadas por modelo
    """
    db = next(get_db())

    # Usar la vista creada en PostgreSQL
    result = db.execute("SELECT * FROM model_stats")

    stats = []
    for row in result:
        stats.append({
            "model_name": row[0],
            "total_predictions": row[1],
            "avg_confidence": float(row[2]),
            "avg_time_ms": float(row[3]),
            "min_time_ms": row[4],
            "max_time_ms": row[5],
            "unique_classes": row[6]
        })

    return {"models": stats}

@app.get("/stats/performance")
async def get_performance_stats():
    """
    Performance por hora de cada modelo
    """
    db = next(get_db())
    result = db.execute("SELECT * FROM model_performance_comparison LIMIT 24")

    performance = []
    for row in result:
        performance.append({
            "hour": row[0].isoformat(),
            "model_name": row[1],
            "avg_confidence": float(row[2]),
            "avg_time_ms": float(row[3]),
            "prediction_count": row[4]
        })

    return {"performance": performance}

# ============================================
# ENDPOINTS - ADMINISTRACIÓN
# ============================================

@app.post("/admin/clear-predictions")
async def clear_predictions(confirm: bool = False):
    """
    Limpiar todas las predicciones (solo para desarrollo)
    """
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Debes confirmar esta acción peligrosa"
        )

    db = next(get_db())
    db.execute("TRUNCATE TABLE predictions CASCADE")
    db.commit()

    return {"message": "Predicciones eliminadas", "timestamp": datetime.utcnow().isoformat()}

# ============================================
# STARTUP/SHUTDOWN
# ============================================

@app.on_event("startup")
async def startup_event():
    """
    Inicialización al arrancar el servicio
    """
    print("🚀 FastAPI Service starting...")

    # Verificar conexiones
    try:
        kafka_producer.check_connection()
        print("✅ Kafka connected")
    except Exception as e:
        print(f"❌ Kafka connection failed: {e}")

    try:
        minio_client.check_connection()
        print("✅ MinIO connected")
    except Exception as e:
        print(f"❌ MinIO connection failed: {e}")

    print("🎉 FastAPI Service ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Limpieza al apagar el servicio
    """
    print("👋 FastAPI Service shutting down...")
    kafka_producer.close()
    print("✅ Kafka producer closed")

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
