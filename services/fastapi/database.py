"""
Modelos de base de datos con SQLAlchemy
Define las tablas y relaciones
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import settings

# ============================================
# CONFIGURACIÓN DE SQLALCHEMY
# ============================================

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# ============================================
# MODELOS
# ============================================

class Prediction(Base):
    """Tabla de predicciones individuales"""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(String(255), nullable=False, index=True)
    image_path = Column(Text, nullable=False)
    model_name = Column(String(100), nullable=False, index=True)
    prediction_class = Column(String(100), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    inference_time_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Metadata adicional
    image_size_bytes = Column(Integer)
    image_width = Column(Integer)
    image_height = Column(Integer)

class Image(Base):
    """Tabla de imágenes procesadas"""
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(String(255), unique=True, nullable=False, index=True)
    original_filename = Column(String(500))
    minio_path = Column(Text, nullable=False)
    upload_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    file_size_bytes = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    format = Column(String(50))
    source = Column(String(100), index=True)  # 'upload', 'webcam', 'cifar10'

    # Estado de procesamiento
    processing_status = Column(String(50), default='pending', index=True)
    processed_at = Column(DateTime)

    # Metadata JSON
    image_metadata = Column(JSON)

class ModelMetric(Base):
    """Tabla de métricas por modelo"""
    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    measured_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Metadata del experimento
    experiment_id = Column(String(255))
    run_id = Column(String(255))

class ModelComparison(Base):
    """Tabla de comparaciones entre modelos"""
    __tablename__ = "model_comparisons"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(String(255), nullable=False, index=True)
    comparison_timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Resultados de ResNet
    resnet_prediction = Column(String(100))
    resnet_confidence = Column(Float)
    resnet_time_ms = Column(Integer)

    # Resultados de MobileNet
    mobilenet_prediction = Column(String(100))
    mobilenet_confidence = Column(Float)
    mobilenet_time_ms = Column(Integer)

    # Resultados de EfficientNet
    efficientnet_prediction = Column(String(100))
    efficientnet_confidence = Column(Float)
    efficientnet_time_ms = Column(Integer)

    # Análisis
    consensus_prediction = Column(String(100))
    fastest_model = Column(String(100))
    most_confident_model = Column(String(100))

class SystemEvent(Base):
    """Tabla de eventos del sistema (audit log)"""
    __tablename__ = "system_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    event_data = Column(JSON)
    severity = Column(String(20), default='info', index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    service_name = Column(String(100))

# ============================================
# FUNCIONES DE UTILIDAD
# ============================================

def get_db():
    """
    Generador de sesiones de base de datos
    Uso en FastAPI con Depends()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Inicializar la base de datos
    Crear todas las tablas si no existen
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

if __name__ == "__main__":
    # Ejecutar para crear tablas manualmente
    init_db()
