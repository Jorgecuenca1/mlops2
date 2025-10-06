"""
Configuración centralizada del servicio FastAPI
Carga variables de entorno y configuraciones
"""

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Configuración de la aplicación"""

    # Aplicación
    APP_NAME: str = "MLOps Vision Platform API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    KAFKA_TOPIC_IMAGES: str = "images-input-stream"
    KAFKA_TOPIC_PREDICTIONS: str = "predictions-output-stream"

    # MinIO
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_SECURE: bool = False

    # PostgreSQL
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "mlops"
    POSTGRES_PASSWORD: str = "mlops123"
    POSTGRES_DB: str = "mlops_db"

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # MLflow
    MLFLOW_TRACKING_URI: str = "http://mlflow:5000"

    # Límites
    MAX_IMAGE_SIZE_MB: int = 10
    MAX_BATCH_SIZE: int = 10

    @property
    def database_url(self) -> str:
        """URL de conexión a PostgreSQL"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """
    Singleton de configuración
    Se carga una sola vez y se cachea
    """
    return Settings()

# Instancia global
settings = get_settings()
