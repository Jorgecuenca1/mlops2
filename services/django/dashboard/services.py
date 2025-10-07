"""
Servicios para conectar con otros componentes del sistema
"""
import requests
from django.conf import settings
from minio import Minio
from kafka import KafkaProducer, KafkaConsumer
import json
import logging

logger = logging.getLogger(__name__)


class FastAPIClient:
    """Cliente para interactuar con FastAPI"""

    @staticmethod
    def upload_image(image_file):
        """Subir imagen a través de FastAPI"""
        try:
            # Leer el archivo y preparar para envío
            image_file.seek(0)  # Asegurar que estamos al inicio del archivo
            files = {
                'file': (
                    image_file.name,
                    image_file.read(),
                    image_file.content_type
                )
            }
            response = requests.post(
                f"{settings.FASTAPI_URL}/upload",
                files=files,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error uploading image to FastAPI: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error uploading image to FastAPI: {e}")
            return None

    @staticmethod
    def get_predictions(limit=100):
        """Obtener predicciones recientes"""
        try:
            response = requests.get(
                f"{settings.FASTAPI_URL}/predictions",
                params={'limit': limit},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching predictions: {e}")
            return []

    @staticmethod
    def get_metrics():
        """Obtener métricas del sistema"""
        try:
            response = requests.get(
                f"{settings.FASTAPI_URL}/metrics",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching metrics: {e}")
            return {}


class MinIOClient:
    """Cliente para interactuar con MinIO"""

    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )

    def get_image_url(self, bucket, object_name, expires=3600):
        """Obtener URL temporal para imagen"""
        try:
            return self.client.presigned_get_object(bucket, object_name, expires=expires)
        except Exception as e:
            logger.error(f"Error getting presigned URL: {e}")
            return None

    def list_images(self, bucket='processed-images', limit=100):
        """Listar imágenes en bucket"""
        try:
            objects = self.client.list_objects(bucket, recursive=True)
            return [obj.object_name for obj in list(objects)[:limit]]
        except Exception as e:
            logger.error(f"Error listing images: {e}")
            return []


class KafkaClient:
    """Cliente para interactuar con Kafka"""

    @staticmethod
    def send_message(topic, message):
        """Enviar mensaje a Kafka"""
        try:
            producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            producer.send(topic, message)
            producer.flush()
            producer.close()
            return True
        except Exception as e:
            logger.error(f"Error sending Kafka message: {e}")
            return False

    @staticmethod
    def get_topics():
        """Obtener lista de topics"""
        try:
            consumer = KafkaConsumer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                consumer_timeout_ms=1000
            )
            topics = consumer.topics()
            consumer.close()
            return list(topics)
        except Exception as e:
            logger.error(f"Error fetching Kafka topics: {e}")
            return []


class MLflowClient:
    """Cliente para interactuar con MLflow"""

    @staticmethod
    def get_experiments():
        """Obtener experimentos de MLflow"""
        try:
            response = requests.get(
                f"{settings.MLFLOW_URL}/api/2.0/mlflow/experiments/search",
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('experiments', [])
        except Exception as e:
            logger.error(f"Error fetching MLflow experiments: {e}")
            return []

    @staticmethod
    def get_runs(experiment_id):
        """Obtener runs de un experimento"""
        try:
            response = requests.post(
                f"{settings.MLFLOW_URL}/api/2.0/mlflow/runs/search",
                json={'experiment_ids': [experiment_id]},
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('runs', [])
        except Exception as e:
            logger.error(f"Error fetching MLflow runs: {e}")
            return []


class PrometheusClient:
    """Cliente para interactuar con Prometheus"""

    @staticmethod
    def query(query_string):
        """Ejecutar query en Prometheus"""
        try:
            response = requests.get(
                f"{settings.PROMETHEUS_URL}/api/v1/query",
                params={'query': query_string},
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('data', {}).get('result', [])
        except Exception as e:
            logger.error(f"Error querying Prometheus: {e}")
            return []

    @staticmethod
    def get_system_metrics():
        """Obtener métricas básicas del sistema"""
        metrics = {}
        queries = {
            'cpu_usage': 'rate(process_cpu_seconds_total[1m])',
            'memory_usage': 'process_resident_memory_bytes',
            'http_requests_total': 'http_requests_total',
        }

        for metric_name, query in queries.items():
            result = PrometheusClient.query(query)
            metrics[metric_name] = result

        return metrics
