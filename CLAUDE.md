# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**MLOps Real-Time Vision Platform** - A complete end-to-end MLOps system for real-time image classification with model comparison.

This is a production-ready microservices architecture that:
- Processes images in real-time via Kafka streaming
- Runs 3 ML models in parallel (ResNet50, MobileNet, EfficientNet)
- Compares inference time and accuracy across models
- Provides REST and GraphQL APIs
- Includes full MLOps stack (MLflow, Airflow, monitoring)
- All services dockerized with docker-compose

## Quick Start Commands

### Development Workflow

```bash
# Start all services
docker-compose up -d

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f fastapi
docker-compose logs -f django
docker-compose logs -f resnet-service

# Stop all services
docker-compose down

# Rebuild a service after code changes
docker-compose build <service-name>
docker-compose up -d <service-name>

# Execute command in container
docker-compose exec <service> bash
docker-compose exec django python manage.py migrate
docker-compose exec postgres psql -U mlops -d mlops_db

# View service status
docker-compose ps

# View resource usage
docker stats
```

### Testing

```bash
# Test FastAPI upload endpoint
curl -X POST "http://localhost:8001/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/image.jpg"

# Test health check
curl http://localhost:8001/health

# Test predictions endpoint
curl http://localhost:8001/predictions/{image_id}
```

## Architecture

### High-Level Flow

```
User Upload → Django/FastAPI → MinIO (storage) → Kafka Topic
    ↓
3 ML Services consume from Kafka in parallel
    ↓
Each service:
  1. Downloads image from MinIO
  2. Runs inference
  3. Times execution
  4. Publishes results to Kafka
    ↓
Results Consumer → PostgreSQL
    ↓
Dashboard displays comparison
```

### Services Architecture

**Frontend Layer**:
- `django-dashboard` (port 8000) - Web UI for visualizations
- `fastapi` (port 8001) - REST API for image uploads and queries
- `graphql` (port 8002) - GraphQL API for flexible queries

**Streaming Layer**:
- `kafka` (port 9092) - Message broker for event streaming
- `zookeeper` (port 2181) - Kafka coordination
- `kafka-ui` (port 8090) - Kafka visualization

**ML Inference Layer**:
- `resnet-service` (port 8003) - ResNet50 model (high accuracy, slower)
- `mobilenet-service` (port 8004) - MobileNetV2 (fast, lower accuracy)
- `efficientnet-service` (port 8005) - EfficientNetB0 (balanced)

**Data Layer**:
- `postgres` (port 5432) - Relational database for metadata
- `minio` (port 9000/9001) - Object storage for images (S3-compatible)
- `redis` (port 6379) - Cache and session storage

**MLOps Layer**:
- `mlflow` (port 5000) - Experiment tracking and model registry
- `airflow-webserver` (port 8080) - Pipeline orchestration UI
- `airflow-scheduler` - Background task executor

**Monitoring Layer**:
- `prometheus` (port 9090) - Metrics collection
- `grafana` (port 3000) - Metrics visualization

### Data Flow

**Kafka Topics**:
- `images-input-stream` - New images to process
- `predictions-output-stream` - Model predictions

**Message Format** (images-input-stream):
```json
{
  "image_id": "uuid",
  "minio_path": "raw-images/2024/01/15/uuid.jpg",
  "source": "upload|webcam|cifar10",
  "timestamp": "2024-01-15T10:30:00Z",
  "metadata": {
    "width": 224,
    "height": 224,
    "format": "JPEG"
  }
}
```

**Message Format** (predictions-output-stream):
```json
{
  "image_id": "uuid",
  "model_name": "resnet50",
  "prediction_class": "cat",
  "confidence": 0.95,
  "inference_time_ms": 145,
  "timestamp": "2024-01-15T10:30:00.500Z"
}
```

### Database Schema

**Key Tables** (see scripts/init-db.sql for full schema):

- `images` - Uploaded/captured images metadata
- `predictions` - Individual model predictions
- `model_comparisons` - Side-by-side model results
- `model_metrics` - Aggregated performance metrics
- `system_events` - Audit log

**Important Views**:
- `model_stats` - Aggregated statistics per model
- `recent_predictions` - Latest predictions with image info
- `model_performance_comparison` - Hourly performance metrics

## Code Organization

### Service Structure

```
services/
├── fastapi/
│   ├── main.py              # FastAPI app with endpoints
│   ├── config.py            # Environment configuration
│   ├── database.py          # SQLAlchemy models
│   ├── kafka_producer.py    # Kafka message publishing
│   ├── minio_client.py      # MinIO file operations
│   └── utils.py             # Image processing utilities
│
├── ml-models/
│   ├── resnet/
│   │   ├── model.py         # ResNet50 inference
│   │   ├── consumer.py      # Kafka consumer
│   │   └── Dockerfile
│   ├── mobilenet/           # Same structure
│   └── efficientnet/        # Same structure
│
├── django-dashboard/
│   ├── views.py             # Django views
│   ├── templates/           # HTML templates
│   └── static/              # CSS/JS
│
├── kafka-producer/
│   ├── webcam_producer.py   # Webcam streaming
│   └── cifar10_streamer.py  # Dataset streaming
│
└── airflow/
    └── dags/                # Airflow DAG definitions
```

## Development Guidelines

### Adding a New ML Model

1. Create new directory in `services/ml-models/<model-name>/`
2. Implement model loading and inference in `model.py`
3. Implement Kafka consumer in `consumer.py`
4. Create Dockerfile
5. Add service to `docker-compose.yml`
6. Update dashboard to display new model results

### Adding a New API Endpoint (FastAPI)

1. Add endpoint function to `services/fastapi/main.py`
2. Define Pydantic models for request/response
3. Update `services/fastapi/database.py` if new DB tables needed
4. Test with Swagger UI at http://localhost:8001/docs

### Modifying Kafka Topics

1. Update topic names in `services/fastapi/config.py`
2. Update producers in `services/fastapi/kafka_producer.py`
3. Update consumers in each ML service
4. Restart all services: `docker-compose restart`

### Database Migrations

```bash
# Create migration
docker-compose exec django python manage.py makemigrations

# Apply migrations
docker-compose exec django python manage.py migrate

# Or update scripts/init-db.sql for new deployments
```

## Important Environment Variables

Set these in docker-compose.yml or .env file:

**Kafka**:
- `KAFKA_BOOTSTRAP_SERVERS` - Kafka broker address
- `KAFKA_TOPIC_IMAGES` - Input images topic
- `KAFKA_TOPIC_PREDICTIONS` - Output predictions topic

**PostgreSQL**:
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`

**MinIO**:
- `MINIO_ENDPOINT` - MinIO server address
- `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY` - Credentials

**MLflow**:
- `MLFLOW_TRACKING_URI` - MLflow server URL
- `MLFLOW_S3_ENDPOINT_URL` - MinIO endpoint for artifacts

## Common Tasks

### Reset Database
```bash
docker-compose down -v  # Removes volumes
docker-compose up -d postgres
# Wait for initialization
docker-compose up -d
```

### View Kafka Messages
```bash
# Use Kafka UI at http://localhost:8090
# Or CLI:
docker-compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic images-input-stream \
  --from-beginning
```

### Debug ML Service
```bash
# View logs
docker-compose logs -f resnet-service

# Enter container
docker-compose exec resnet-service bash

# Test model directly
docker-compose exec resnet-service python model.py
```

### Monitor Performance
- Grafana dashboards: http://localhost:3000
- Prometheus metrics: http://localhost:9090
- MLflow experiments: http://localhost:5000

## Data Sources

### CIFAR-10 Dataset
- Automatically downloaded via TensorFlow on first run
- 60,000 images in 10 classes
- Used for training and testing
- Location: Downloaded to container on first use

### Webcam Streaming
- Implemented in `services/kafka-producer/webcam_producer.py`
- Captures frames via OpenCV
- Configurable FPS (default: 2)
- Requires webcam access in Docker (platform-dependent)

### Manual Upload
- Via Django dashboard (http://localhost:8000)
- Via FastAPI endpoint (POST /upload)
- Supported formats: JPG, PNG, WebP
- Max size: 10 MB (configurable in config.py)

## Monitoring and Debugging

### Health Checks
```bash
# System health
curl http://localhost:8001/health

# Individual services
docker-compose ps
```

### Logs
```bash
# All services
docker-compose logs -f

# Specific service with timestamps
docker-compose logs -f --timestamps fastapi

# Last 100 lines
docker-compose logs --tail=100 kafka
```

### Metrics
- Service-level metrics: Exposed at `<service>:8000/metrics`
- Aggregated in Prometheus: http://localhost:9090
- Visualized in Grafana: http://localhost:3000

## Deployment Notes

### For Production
- Change all default passwords in docker-compose.yml
- Use environment variables for sensitive data
- Enable HTTPS/SSL certificates
- Configure proper firewall rules
- Use managed services for PostgreSQL, Kafka in cloud
- Implement proper authentication/authorization
- Add rate limiting to APIs
- Enable backup strategies for databases

### Scaling
- Kafka partitions can be increased for parallel processing
- ML services can be replicated: `docker-compose up -d --scale resnet-service=3`
- PostgreSQL can be replaced with managed RDS
- MinIO can be replaced with AWS S3
- Consider Kubernetes for orchestration at scale

## Troubleshooting

### Service Won't Start
1. Check logs: `docker-compose logs <service>`
2. Check dependencies are running: `docker-compose ps`
3. Rebuild if code changed: `docker-compose build <service>`
4. Check port conflicts: `netstat -ano | findstr :<port>`

### Kafka Messages Not Processing
1. Check Kafka is running: `docker-compose logs kafka`
2. Verify topic exists: Visit http://localhost:8090
3. Check consumers are running: `docker-compose logs <model>-service`
4. Verify network connectivity: `docker-compose exec <service> ping kafka`

### Database Connection Issues
1. Check PostgreSQL is healthy: `docker-compose ps postgres`
2. Verify credentials in config
3. Check network: `docker-compose exec fastapi ping postgres`
4. Reset database: `docker-compose down -v && docker-compose up -d`

## Resources

- Docker Compose docs: https://docs.docker.com/compose/
- Kafka documentation: https://kafka.apache.org/documentation/
- MLflow documentation: https://mlflow.org/docs/latest/
- FastAPI documentation: https://fastapi.tiangolo.com/
- Project README: `README.md`
- Quick start guide: `START.md`
- Installation guide: `INSTALL_DOCKER.md`
- Project summary: `RESUMEN_PROYECTO.md`
