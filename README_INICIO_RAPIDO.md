# 🚀 Inicio Rápido - MLOps Dashboard

## ⚡ TLDR - Empezar en 3 pasos

```bash
# 1. Levantar todo el sistema
docker-compose up -d

# 2. Abrir el dashboard
# http://localhost:8000

# 3. ¡Listo! Empieza a subir imágenes y ver predicciones
```

---

## 📋 ¿Qué tengo corriendo?

**15 contenedores** trabajando juntos:

### 🎨 Interfaz Principal
- **Django Dashboard** (puerto 8000) ← **EMPIEZA AQUÍ**

### 🤖 Machine Learning
- FastAPI (puerto 8001)
- 3 Clasificadores (puertos 8003, 8004, 8005)
- Feature Extractor
- MLflow (puerto 5000)

### 💾 Bases de Datos
- PostgreSQL (puerto 5432)
- Redis (puerto 6379)
- MinIO (puertos 9000, 9001)

### 📡 Mensajería
- Kafka (puerto 9092)
- Zookeeper (puerto 2181)
- Kafka UI (puerto 8090)

### 📊 Monitoreo
- Prometheus (puerto 9090)
- Grafana (puerto 3000)

---

## 🎯 ¿Cómo lo uso?

### Opción 1: Dashboard Django (RECOMENDADO)
```
http://localhost:8000
```
**Todo en una sola interfaz:**
- Sube imágenes con drag & drop
- Ve predicciones en tiempo real
- Compara modelos ML
- Monitorea todos los servicios
- ¡Todo visual y fácil de usar!

### Opción 2: FastAPI (para desarrolladores)
```
http://localhost:8001/docs
```

---

## 📸 Ejemplo de Uso

1. Abre: http://localhost:8000
2. Click en **"Subir Imagen"**
3. Selecciona una imagen de tu PC
4. ¡Automáticamente se procesa!
5. Ve los resultados en **"Predicciones"**

**El sistema hace:**
- ✅ Sube a MinIO
- ✅ Envía a Kafka
- ✅ Extrae características
- ✅ 3 modelos predicen en paralelo
- ✅ Guarda en PostgreSQL
- ✅ Muestra resultados en el dashboard

---

## 🛠️ Comandos Básicos

```bash
# Ver todos los contenedores
docker ps

# Ver logs de Django
docker logs mlops-django -f

# Reiniciar todo
docker-compose restart

# Detener todo
docker-compose down

# Levantar todo de nuevo
docker-compose up -d
```

---

## 🌐 URLs Importantes

| Servicio | URL |
|----------|-----|
| **Dashboard Django** | http://localhost:8000 |
| FastAPI Docs | http://localhost:8001/docs |
| Grafana | http://localhost:3000 |
| MLflow | http://localhost:5000 |
| Kafka UI | http://localhost:8090 |
| MinIO | http://localhost:9001 |

---

## 🎉 ¡Eso es todo!

Abre http://localhost:8000 y empieza a usar el sistema completo de MLOps.

Para más detalles, lee: `GUIA_DJANGO_DASHBOARD.md`
