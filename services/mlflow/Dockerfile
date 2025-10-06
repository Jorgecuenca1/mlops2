FROM python:3.11-slim

WORKDIR /mlflow

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    mlflow==2.9.2 \
    psycopg2-binary==2.9.9 \
    boto3==1.29.7 \
    pymysql==1.1.0

# Create mlflow directory
RUN mkdir -p /mlflow/artifacts

# Expose port
EXPOSE 5000

# MLflow will be started via docker-compose command
# with proper configuration for PostgreSQL backend and MinIO artifacts
