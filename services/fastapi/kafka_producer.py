"""
Kafka Producer - Publicación de mensajes
Envía imágenes a Kafka para procesamiento
"""

import json
from kafka import KafkaProducer
from kafka.errors import KafkaError
from config import settings
import logging

logger = logging.getLogger(__name__)

class KafkaImageProducer:
    """
    Producer de Kafka para enviar imágenes a procesar
    """

    def __init__(self):
        """
        Inicializar el producer de Kafka
        """
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',  # Esperar confirmación de todos los brokers
                retries=3,
                max_in_flight_requests_per_connection=1,  # Garantizar orden
                compression_type='gzip'  # Comprimir mensajes
            )
            logger.info(f"✅ Kafka Producer initialized: {settings.KAFKA_BOOTSTRAP_SERVERS}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Kafka Producer: {e}")
            raise

    def send_image(self, message: dict, topic: str = None):
        """
        Enviar mensaje de imagen a Kafka

        Args:
            message (dict): Mensaje con información de la imagen
                {
                    "image_id": "uuid",
                    "minio_path": "s3://...",
                    "source": "upload|webcam|cifar10",
                    "timestamp": "2024-01-15T10:30:00",
                    "metadata": {...}
                }
            topic (str): Topic de Kafka (default: images-input-stream)

        Returns:
            RecordMetadata: Metadata del mensaje enviado
        """
        if topic is None:
            topic = settings.KAFKA_TOPIC_IMAGES

        try:
            # Enviar mensaje asíncronamente
            future = self.producer.send(topic, value=message)

            # Esperar confirmación (bloquea hasta 60s)
            record_metadata = future.get(timeout=60)

            logger.info(
                f"✅ Message sent to {topic}: "
                f"partition={record_metadata.partition}, "
                f"offset={record_metadata.offset}, "
                f"image_id={message.get('image_id')}"
            )

            return record_metadata

        except KafkaError as e:
            logger.error(f"❌ Failed to send message to Kafka: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error sending to Kafka: {e}")
            raise

    def send_batch(self, messages: list, topic: str = None):
        """
        Enviar múltiples mensajes en batch

        Args:
            messages (list): Lista de diccionarios con mensajes
            topic (str): Topic de Kafka

        Returns:
            list: Lista de RecordMetadata
        """
        if topic is None:
            topic = settings.KAFKA_TOPIC_IMAGES

        results = []
        for message in messages:
            try:
                result = self.send_image(message, topic)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to send message in batch: {e}")
                results.append(None)

        return results

    def check_connection(self):
        """
        Verificar conexión con Kafka
        Lanza excepción si no hay conexión

        Returns:
            bool: True si está conectado
        """
        try:
            # Obtener metadata de Kafka (prueba de conexión)
            metadata = self.producer.bootstrap_connected()
            if metadata:
                logger.info("✅ Kafka connection verified")
                return True
            else:
                raise Exception("Kafka not connected")
        except Exception as e:
            logger.error(f"❌ Kafka connection check failed: {e}")
            raise

    def flush(self):
        """
        Forzar envío de todos los mensajes pendientes
        """
        self.producer.flush()
        logger.info("✅ Kafka producer flushed")

    def close(self):
        """
        Cerrar el producer de Kafka
        """
        try:
            self.producer.flush()
            self.producer.close()
            logger.info("✅ Kafka producer closed")
        except Exception as e:
            logger.error(f"❌ Error closing Kafka producer: {e}")

    def __del__(self):
        """
        Destructor - cerrar conexión al eliminar objeto
        """
        try:
            self.close()
        except:
            pass


# ============================================
# EJEMPLO DE USO
# ============================================

if __name__ == "__main__":
    """
    Test del producer
    """
    import uuid
    from datetime import datetime

    # Crear producer
    producer = KafkaImageProducer()

    # Mensaje de ejemplo
    test_message = {
        "image_id": str(uuid.uuid4()),
        "minio_path": "raw-images/2024/01/15/test.jpg",
        "source": "test",
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {
            "width": 224,
            "height": 224,
            "format": "JPEG"
        }
    }

    # Enviar mensaje
    try:
        result = producer.send_image(test_message)
        print(f"✅ Test message sent successfully: {result}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        producer.close()
