FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Crear directorio para static files
RUN mkdir -p staticfiles

# Exponer puerto
EXPOSE 8000

# Script de inicio
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn mlops_dashboard.wsgi:application --bind 0.0.0.0:8000 --workers 3"]
