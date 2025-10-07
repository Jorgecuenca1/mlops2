"""
Modelos Django - Sincronizados con las tablas de FastAPI
Usa la misma base de datos PostgreSQL
"""
from django.db import models
from django.utils import timezone


class Prediction(models.Model):
    """Predicciones individuales de modelos"""
    image_id = models.CharField(max_length=255, db_index=True)
    image_path = models.TextField()
    model_name = models.CharField(max_length=100, db_index=True)
    prediction_class = models.CharField(max_length=100, db_index=True)
    confidence = models.FloatField()
    inference_time_ms = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    # Metadata adicional
    image_size_bytes = models.IntegerField(null=True, blank=True)
    image_width = models.IntegerField(null=True, blank=True)
    image_height = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'predictions'
        managed = False  # No dejar que Django gestione esta tabla
        ordering = ['-created_at']
        verbose_name = 'Predicción'
        verbose_name_plural = 'Predicciones'

    def __str__(self):
        return f"{self.model_name}: {self.prediction_class} ({self.confidence:.2%})"


class Image(models.Model):
    """Imágenes procesadas"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
    ]

    SOURCE_CHOICES = [
        ('upload', 'Subida'),
        ('webcam', 'Webcam'),
        ('cifar10', 'CIFAR-10'),
    ]

    image_id = models.CharField(max_length=255, unique=True, db_index=True)
    original_filename = models.CharField(max_length=500, null=True, blank=True)
    minio_path = models.TextField()
    upload_timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    file_size_bytes = models.IntegerField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    format = models.CharField(max_length=50, null=True, blank=True)
    source = models.CharField(max_length=100, choices=SOURCE_CHOICES, db_index=True)

    # Estado de procesamiento
    processing_status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    processed_at = models.DateTimeField(null=True, blank=True)

    # Metadata JSON - usar el nombre de columna existente 'metadata' de FastAPI
    image_metadata = models.JSONField(null=True, blank=True, db_column='metadata')

    class Meta:
        db_table = 'images'
        managed = False  # No dejar que Django gestione esta tabla
        ordering = ['-upload_timestamp']
        verbose_name = 'Imagen'
        verbose_name_plural = 'Imágenes'

    def __str__(self):
        return f"{self.image_id} - {self.original_filename}"


class ModelMetric(models.Model):
    """Métricas por modelo"""
    model_name = models.CharField(max_length=100, db_index=True)
    metric_name = models.CharField(max_length=100)
    metric_value = models.FloatField()
    measured_at = models.DateTimeField(default=timezone.now, db_index=True)

    # Metadata del experimento
    experiment_id = models.CharField(max_length=255, null=True, blank=True)
    run_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'model_metrics'
        managed = False
        ordering = ['-measured_at']
        verbose_name = 'Métrica de Modelo'
        verbose_name_plural = 'Métricas de Modelos'

    def __str__(self):
        return f"{self.model_name} - {self.metric_name}: {self.metric_value}"


class ModelComparison(models.Model):
    """Comparaciones entre modelos"""
    image_id = models.CharField(max_length=255, db_index=True)
    comparison_timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    # Resultados de ResNet
    resnet_prediction = models.CharField(max_length=100, null=True, blank=True)
    resnet_confidence = models.FloatField(null=True, blank=True)
    resnet_time_ms = models.IntegerField(null=True, blank=True)

    # Resultados de MobileNet
    mobilenet_prediction = models.CharField(max_length=100, null=True, blank=True)
    mobilenet_confidence = models.FloatField(null=True, blank=True)
    mobilenet_time_ms = models.IntegerField(null=True, blank=True)

    # Resultados de EfficientNet
    efficientnet_prediction = models.CharField(max_length=100, null=True, blank=True)
    efficientnet_confidence = models.FloatField(null=True, blank=True)
    efficientnet_time_ms = models.IntegerField(null=True, blank=True)

    # Análisis
    consensus_prediction = models.CharField(max_length=100, null=True, blank=True)
    fastest_model = models.CharField(max_length=100, null=True, blank=True)
    most_confident_model = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'model_comparisons'
        managed = False
        ordering = ['-comparison_timestamp']
        verbose_name = 'Comparación de Modelos'
        verbose_name_plural = 'Comparaciones de Modelos'

    def __str__(self):
        return f"Comparación {self.image_id} - {self.comparison_timestamp}"


class SystemEvent(models.Model):
    """Eventos del sistema (audit log)"""
    SEVERITY_CHOICES = [
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]

    event_type = models.CharField(max_length=100, db_index=True)
    event_data = models.JSONField(null=True, blank=True)
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='info',
        db_index=True
    )
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    service_name = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'system_events'
        managed = False
        ordering = ['-created_at']
        verbose_name = 'Evento del Sistema'
        verbose_name_plural = 'Eventos del Sistema'

    def __str__(self):
        return f"[{self.severity.upper()}] {self.event_type} - {self.created_at}"
