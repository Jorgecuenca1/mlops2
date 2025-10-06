"""
Funciones de utilidad
"""

from PIL import Image
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

def get_image_metadata(image_data: BytesIO) -> dict:
    """
    Extraer metadata de una imagen

    Args:
        image_data (BytesIO): Datos de la imagen

    Returns:
        dict: Metadata de la imagen
    """
    try:
        img = Image.open(image_data)

        metadata = {
            "width": img.width,
            "height": img.height,
            "format": img.format,
            "mode": img.mode,
            "size_bytes": image_data.getbuffer().nbytes
        }

        # Resetear puntero
        image_data.seek(0)

        return metadata

    except Exception as e:
        logger.error(f"Error extracting image metadata: {e}")
        return {}

def process_image(image_data: BytesIO, target_size: tuple = (224, 224)) -> BytesIO:
    """
    Procesar imagen: redimensionar y normalizar

    Args:
        image_data (BytesIO): Imagen original
        target_size (tuple): Tamaño objetivo (width, height)

    Returns:
        BytesIO: Imagen procesada
    """
    try:
        img = Image.open(image_data)

        # Convertir a RGB si es necesario
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Redimensionar
        img = img.resize(target_size, Image.Resampling.LANCZOS)

        # Guardar en BytesIO
        output = BytesIO()
        img.save(output, format='JPEG', quality=95)
        output.seek(0)

        return output

    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise
