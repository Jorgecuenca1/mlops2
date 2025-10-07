"""
URLs del dashboard
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_home, name='home'),

    # Gestión de imágenes
    path('images/', views.images_list, name='images_list'),
    path('images/upload/', views.image_upload, name='image_upload'),
    path('images/<str:image_id>/', views.image_detail, name='image_detail'),

    # Predicciones
    path('predictions/', views.predictions_list, name='predictions_list'),
    path('predictions/<int:prediction_id>/', views.prediction_detail, name='prediction_detail'),

    # Modelos
    path('models/', views.models_overview, name='models_overview'),
    path('models/compare/', views.models_compare, name='models_compare'),
    path('models/metrics/', views.models_metrics, name='models_metrics'),

    # Monitoreo
    path('monitoring/', views.monitoring_dashboard, name='monitoring'),
    path('monitoring/kafka/', views.kafka_status, name='kafka_status'),
    path('monitoring/services/', views.services_status, name='services_status'),

    # MLflow
    path('mlflow/', views.mlflow_experiments, name='mlflow_experiments'),
    path('mlflow/experiment/<str:experiment_id>/', views.mlflow_experiment_detail, name='mlflow_experiment_detail'),

    # API endpoints (AJAX)
    path('api/stats/', views.api_get_stats, name='api_stats'),
    path('api/recent-predictions/', views.api_recent_predictions, name='api_recent_predictions'),
]
