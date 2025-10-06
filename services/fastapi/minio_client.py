"""
MinIO Client - Gestión de almacenamiento de objetos
Similar a AWS S3 pero open source y local
"""

from minio import Minio
from minio.error import S3Error
from config import settings
import logging
from io import BytesIO
from datetime import timedelta

logger = logging.getLogger(__name__)

class MinIOClient:
    """
    Cliente para interactuar con MinIO
    Maneja upload/download de imágenes
    """

    def __init__(self):
        """
        Inicializar cliente de MinIO
        """
        try:
            self.client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE
            )
            logger.info(f"✅ MinIO Client initialized: {settings.MINIO_ENDPOINT}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize MinIO client: {e}")
            raise

    def upload_image(self, bucket: str, object_name: str, data: BytesIO, length: int, content_type: str = "image/jpeg"):
        """
        Subir imagen a MinIO

        Args:
            bucket (str): Nombre del bucket
            object_name (str): Ruta del objeto (ej: "raw-images/2024/01/15/image.jpg")
            data (BytesIO): Datos de la imagen
            length (int): Tamaño en bytes
            content_type (str): Tipo MIME

        Returns:
            str: Path completo del objeto
        """
        try:
            # Crear bucket si no existe
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
                logger.info(f"✅ Bucket created: {bucket}")

            # Subir objeto
            self.client.put_object(
                bucket,
                object_name,
                data,
                length,
                content_type=content_type
            )

            logger.info(f"✅ Uploaded: {bucket}/{object_name} ({length} bytes)")

            return f"{bucket}/{object_name}"

        except S3Error as e:
            logger.error(f"❌ MinIO S3 error: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to upload to MinIO: {e}")
            raise

    def download_image(self, bucket: str, object_name: str) -> bytes:
        """
        Descargar imagen de MinIO

        Args:
            bucket (str): Nombre del bucket
            object_name (str): Ruta del objeto

        Returns:
            bytes: Contenido de la imagen
        """
        try:
            response = self.client.get_object(bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()

            logger.info(f"✅ Downloaded: {bucket}/{object_name} ({len(data)} bytes)")

            return data

        except S3Error as e:
            logger.error(f"❌ MinIO S3 error downloading: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to download from MinIO: {e}")
            raise

    def get_presigned_url(self, bucket: str, object_name: str, expires: int = 3600) -> str:
        """
        Generar URL temporal para acceder a un objeto

        Args:
            bucket (str): Nombre del bucket
            object_name (str): Ruta del objeto
            expires (int): Tiempo de expiración en segundos (default: 1 hora)

        Returns:
            str: URL temporal
        """
        try:
            url = self.client.presigned_get_object(
                bucket,
                object_name,
                expires=timedelta(seconds=expires)
            )

            logger.info(f"✅ Generated presigned URL for {bucket}/{object_name}")

            return url

        except S3Error as e:
            logger.error(f"❌ MinIO S3 error generating URL: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to generate presigned URL: {e}")
            raise

    def list_objects(self, bucket: str, prefix: str = None) -> list:
        """
        Listar objetos en un bucket

        Args:
            bucket (str): Nombre del bucket
            prefix (str): Prefijo para filtrar (ej: "raw-images/2024/01/")

        Returns:
            list: Lista de objetos
        """
        try:
            objects = self.client.list_objects(bucket, prefix=prefix, recursive=True)

            object_list = []
            for obj in objects:
                object_list.append({
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified,
                    "etag": obj.etag
                })

            logger.info(f"✅ Listed {len(object_list)} objects in {bucket}")

            return object_list

        except S3Error as e:
            logger.error(f"❌ MinIO S3 error listing objects: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to list objects: {e}")
            raise

    def delete_object(self, bucket: str, object_name: str):
        """
        Eliminar un objeto

        Args:
            bucket (str): Nombre del bucket
            object_name (str): Ruta del objeto
        """
        try:
            self.client.remove_object(bucket, object_name)
            logger.info(f"✅ Deleted: {bucket}/{object_name}")

        except S3Error as e:
            logger.error(f"❌ MinIO S3 error deleting: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to delete from MinIO: {e}")
            raise

    def check_connection(self) -> bool:
        """
        Verificar conexión con MinIO

        Returns:
            bool: True si está conectado
        """
        try:
            # Listar buckets como prueba de conexión
            buckets = self.client.list_buckets()
            logger.info(f"✅ MinIO connection verified ({len(buckets)} buckets)")
            return True

        except Exception as e:
            logger.error(f"❌ MinIO connection check failed: {e}")
            raise

    def ensure_buckets_exist(self, buckets: list):
        """
        Asegurar que los buckets existen, crearlos si no

        Args:
            buckets (list): Lista de nombres de buckets
        """
        for bucket in buckets:
            try:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
                    logger.info(f"✅ Created bucket: {bucket}")
                else:
                    logger.info(f"✅ Bucket exists: {bucket}")
            except S3Error as e:
                logger.error(f"❌ Error ensuring bucket {bucket}: {e}")


# ============================================
# EJEMPLO DE USO
# ============================================

if __name__ == "__main__":
    """
    Test del cliente MinIO
    """
    from PIL import Image
    import io

    # Crear cliente
    minio_client = MinIOClient()

    # Verificar conexión
    try:
        minio_client.check_connection()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        exit(1)

    # Asegurar que existan los buckets necesarios
    buckets = ["raw-images", "processed-images", "models", "mlflow"]
    minio_client.ensure_buckets_exist(buckets)

    # Crear una imagen de prueba
    img = Image.new('RGB', (224, 224), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)

    # Upload de prueba
    try:
        path = minio_client.upload_image(
            bucket="raw-images",
            object_name="test/test_image.jpg",
            data=img_bytes,
            length=img_bytes.getbuffer().nbytes
        )
        print(f"✅ Test upload successful: {path}")

        # Generar URL temporal
        url = minio_client.get_presigned_url("raw-images", "test/test_image.jpg")
        print(f"✅ Presigned URL: {url}")

        # Listar objetos
        objects = minio_client.list_objects("raw-images", prefix="test/")
        print(f"✅ Found {len(objects)} objects")

    except Exception as e:
        print(f"❌ Test failed: {e}")
