"""
Admin de Django para gestionar los modelos
"""
from django.contrib import admin
from .models import Prediction, Image, ModelMetric, ModelComparison, SystemEvent


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('id', 'model_name', 'prediction_class', 'confidence', 'inference_time_ms', 'created_at')
    list_filter = ('model_name', 'prediction_class', 'created_at')
    search_fields = ('image_id', 'prediction_class')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('image_id', 'original_filename', 'source', 'processing_status', 'upload_timestamp')
    list_filter = ('source', 'processing_status', 'upload_timestamp')
    search_fields = ('image_id', 'original_filename')
    date_hierarchy = 'upload_timestamp'
    ordering = ('-upload_timestamp',)


@admin.register(ModelMetric)
class ModelMetricAdmin(admin.ModelAdmin):
    list_display = ('id', 'model_name', 'metric_name', 'metric_value', 'measured_at')
    list_filter = ('model_name', 'metric_name', 'measured_at')
    search_fields = ('model_name', 'experiment_id')
    date_hierarchy = 'measured_at'
    ordering = ('-measured_at',)


@admin.register(ModelComparison)
class ModelComparisonAdmin(admin.ModelAdmin):
    list_display = ('id', 'image_id', 'consensus_prediction', 'fastest_model', 'most_confident_model', 'comparison_timestamp')
    list_filter = ('fastest_model', 'most_confident_model', 'comparison_timestamp')
    search_fields = ('image_id',)
    date_hierarchy = 'comparison_timestamp'
    ordering = ('-comparison_timestamp',)


@admin.register(SystemEvent)
class SystemEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'event_type', 'severity', 'service_name', 'created_at')
    list_filter = ('severity', 'event_type', 'service_name', 'created_at')
    search_fields = ('event_type', 'service_name')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
