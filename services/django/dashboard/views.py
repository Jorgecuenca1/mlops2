"""
Vistas del Dashboard Django
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Avg, Max, Min
from django.utils import timezone
from datetime import timedelta
import logging

from .models import Prediction, Image, ModelMetric, ModelComparison, SystemEvent
from .services import FastAPIClient, MinIOClient, KafkaClient, MLflowClient, PrometheusClient

logger = logging.getLogger(__name__)


# ============================================
# DASHBOARD PRINCIPAL
# ============================================

def dashboard_home(request):
    """Dashboard principal con estadísticas generales"""
    # Estadísticas básicas
    total_images = Image.objects.count()
    total_predictions = Prediction.objects.count()

    # Últimas 24 horas
    last_24h = timezone.now() - timedelta(hours=24)
    recent_images = Image.objects.filter(upload_timestamp__gte=last_24h).count()
    recent_predictions = Prediction.objects.filter(created_at__gte=last_24h).count()

    # Predicciones por modelo
    predictions_by_model = Prediction.objects.values('model_name').annotate(
        count=Count('id'),
        avg_confidence=Avg('confidence'),
        avg_time=Avg('inference_time_ms')
    )

    # Predicciones recientes
    recent_predictions_list = Prediction.objects.select_related().order_by('-created_at')[:10]

    # Imágenes recientes
    recent_images_list = Image.objects.order_by('-upload_timestamp')[:6]

    # Eventos del sistema
    recent_events = SystemEvent.objects.order_by('-created_at')[:5]

    context = {
        'total_images': total_images,
        'total_predictions': total_predictions,
        'recent_images_count': recent_images,
        'recent_predictions_count': recent_predictions,
        'predictions_by_model': predictions_by_model,
        'recent_predictions': recent_predictions_list,
        'recent_images': recent_images_list,
        'recent_events': recent_events,
    }

    return render(request, 'dashboard/home.html', context)


# ============================================
# GESTIÓN DE IMÁGENES
# ============================================

def images_list(request):
    """Listado de todas las imágenes"""
    images = Image.objects.all().order_by('-upload_timestamp')

    # Filtros
    status = request.GET.get('status')
    source = request.GET.get('source')

    if status:
        images = images.filter(processing_status=status)
    if source:
        images = images.filter(source=source)

    context = {
        'images': images,
        'status_choices': Image.STATUS_CHOICES,
        'source_choices': Image.SOURCE_CHOICES,
    }

    return render(request, 'dashboard/images_list.html', context)


@require_http_methods(["GET", "POST"])
def image_upload(request):
    """Subir nueva imagen"""
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            image_file = request.FILES['image']

            # Enviar a FastAPI
            result = FastAPIClient.upload_image(image_file)

            if result:
                messages.success(request, f'Imagen subida exitosamente: {result.get("image_id")}')
                return redirect('dashboard:images_list')
            else:
                messages.error(request, 'Error al subir la imagen')

        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            messages.error(request, f'Error: {str(e)}')

    return render(request, 'dashboard/image_upload.html')


def image_detail(request, image_id):
    """Detalle de una imagen específica"""
    image = get_object_or_404(Image, image_id=image_id)

    # Obtener predicciones relacionadas
    predictions = Prediction.objects.filter(image_id=image_id).order_by('-created_at')

    # Comparaciones de modelos
    comparisons = ModelComparison.objects.filter(image_id=image_id).order_by('-comparison_timestamp')

    # URL de MinIO
    minio_client = MinIOClient()
    image_url = None
    if image.minio_path:
        try:
            bucket, object_name = image.minio_path.split('/', 1)
            image_url = minio_client.get_image_url(bucket, object_name)
        except Exception as e:
            logger.error(f"Error getting image URL: {e}")

    context = {
        'image': image,
        'predictions': predictions,
        'comparisons': comparisons,
        'image_url': image_url,
    }

    return render(request, 'dashboard/image_detail.html', context)


# ============================================
# PREDICCIONES
# ============================================

def predictions_list(request):
    """Listado de predicciones"""
    predictions = Prediction.objects.all().order_by('-created_at')

    # Filtros
    model_name = request.GET.get('model')
    prediction_class = request.GET.get('class')

    if model_name:
        predictions = predictions.filter(model_name=model_name)
    if prediction_class:
        predictions = predictions.filter(prediction_class=prediction_class)

    # Estadísticas
    stats = predictions.aggregate(
        avg_confidence=Avg('confidence'),
        avg_time=Avg('inference_time_ms'),
        total=Count('id')
    )

    context = {
        'predictions': predictions[:100],  # Limitar a 100 resultados
        'stats': stats,
        'available_models': Prediction.objects.values_list('model_name', flat=True).distinct(),
        'available_classes': Prediction.objects.values_list('prediction_class', flat=True).distinct(),
    }

    return render(request, 'dashboard/predictions_list.html', context)


def prediction_detail(request, prediction_id):
    """Detalle de una predicción específica"""
    prediction = get_object_or_404(Prediction, id=prediction_id)

    # Otras predicciones para la misma imagen
    related_predictions = Prediction.objects.filter(
        image_id=prediction.image_id
    ).exclude(id=prediction_id).order_by('-created_at')

    context = {
        'prediction': prediction,
        'related_predictions': related_predictions,
    }

    return render(request, 'dashboard/prediction_detail.html', context)


# ============================================
# MODELOS
# ============================================

def models_overview(request):
    """Vista general de modelos"""
    # Métricas por modelo
    model_stats = Prediction.objects.values('model_name').annotate(
        total_predictions=Count('id'),
        avg_confidence=Avg('confidence'),
        avg_inference_time=Avg('inference_time_ms'),
        min_inference_time=Min('inference_time_ms'),
        max_inference_time=Max('inference_time_ms'),
    ).order_by('-total_predictions')

    # Métricas recientes
    recent_metrics = ModelMetric.objects.order_by('-measured_at')[:20]

    context = {
        'model_stats': model_stats,
        'recent_metrics': recent_metrics,
    }

    return render(request, 'dashboard/models_overview.html', context)


def models_compare(request):
    """Comparación entre modelos"""
    # Primero obtener el queryset base
    all_comparisons = ModelComparison.objects.all().order_by('-comparison_timestamp')

    # Calcular estadísticas ANTES de hacer slice
    comparison_stats = {
        'total': all_comparisons.count(),
        'consensus_rate': all_comparisons.exclude(consensus_prediction__isnull=True).count(),
    }

    # Ahora sí hacer el slice para la vista
    comparisons = all_comparisons[:50]

    context = {
        'comparisons': comparisons,
        'stats': comparison_stats,
    }

    return render(request, 'dashboard/models_compare.html', context)


def models_metrics(request):
    """Métricas detalladas de modelos"""
    metrics = ModelMetric.objects.all().order_by('-measured_at')

    # Filtro por modelo
    model_name = request.GET.get('model')
    if model_name:
        metrics = metrics.filter(model_name=model_name)

    context = {
        'metrics': metrics[:100],
        'available_models': ModelMetric.objects.values_list('model_name', flat=True).distinct(),
    }

    return render(request, 'dashboard/models_metrics.html', context)


# ============================================
# MONITOREO
# ============================================

def monitoring_dashboard(request):
    """Dashboard de monitoreo general"""
    # Obtener métricas de Prometheus
    system_metrics = PrometheusClient.get_system_metrics()

    # Eventos del sistema
    recent_events = SystemEvent.objects.order_by('-created_at')[:20]

    # Estadísticas de eventos
    events_by_severity = SystemEvent.objects.values('severity').annotate(count=Count('id'))

    context = {
        'system_metrics': system_metrics,
        'recent_events': recent_events,
        'events_by_severity': events_by_severity,
    }

    return render(request, 'dashboard/monitoring.html', context)


def kafka_status(request):
    """Estado de Kafka"""
    topics = KafkaClient.get_topics()

    context = {
        'topics': topics,
        'kafka_url': 'http://localhost:8090',  # Kafka UI
    }

    return render(request, 'dashboard/kafka_status.html', context)


def services_status(request):
    """Estado de servicios"""
    services = {
        'FastAPI': 'http://localhost:8001',
        'MLflow': 'http://localhost:5000',
        'Kafka UI': 'http://localhost:8090',
        'Grafana': 'http://localhost:3000',
        'Prometheus': 'http://localhost:9090',
        'MinIO': 'http://localhost:9001',
    }

    # Verificar estado de cada servicio
    services_status = {}
    for name, url in services.items():
        try:
            import requests
            response = requests.get(url, timeout=2)
            services_status[name] = {
                'url': url,
                'status': 'online' if response.status_code < 500 else 'error',
                'status_code': response.status_code
            }
        except:
            services_status[name] = {
                'url': url,
                'status': 'offline',
                'status_code': None
            }

    context = {
        'services': services_status,
    }

    return render(request, 'dashboard/services_status.html', context)


# ============================================
# MLFLOW
# ============================================

def mlflow_experiments(request):
    """Lista de experimentos MLflow"""
    experiments = MLflowClient.get_experiments()

    context = {
        'experiments': experiments,
        'mlflow_url': 'http://localhost:5000',
    }

    return render(request, 'dashboard/mlflow_experiments.html', context)


def mlflow_experiment_detail(request, experiment_id):
    """Detalle de experimento MLflow"""
    runs = MLflowClient.get_runs(experiment_id)

    context = {
        'experiment_id': experiment_id,
        'runs': runs,
        'mlflow_url': 'http://localhost:5000',
    }

    return render(request, 'dashboard/mlflow_experiment_detail.html', context)


# ============================================
# API ENDPOINTS (AJAX)
# ============================================

def api_get_stats(request):
    """API: Obtener estadísticas en tiempo real"""
    last_24h = timezone.now() - timedelta(hours=24)

    stats = {
        'total_images': Image.objects.count(),
        'total_predictions': Prediction.objects.count(),
        'recent_images': Image.objects.filter(upload_timestamp__gte=last_24h).count(),
        'recent_predictions': Prediction.objects.filter(created_at__gte=last_24h).count(),
        'models_count': Prediction.objects.values('model_name').distinct().count(),
    }

    return JsonResponse(stats)


def api_recent_predictions(request):
    """API: Predicciones recientes"""
    limit = int(request.GET.get('limit', 10))

    predictions = Prediction.objects.order_by('-created_at')[:limit]

    data = [{
        'id': p.id,
        'image_id': p.image_id,
        'model_name': p.model_name,
        'prediction_class': p.prediction_class,
        'confidence': float(p.confidence),
        'inference_time_ms': p.inference_time_ms,
        'created_at': p.created_at.isoformat(),
    } for p in predictions]

    return JsonResponse({'predictions': data})
