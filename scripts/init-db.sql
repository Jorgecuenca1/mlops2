-- ============================================
-- MLOPS DATABASE INITIALIZATION
-- ============================================

-- Tabla de predicciones
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    image_id VARCHAR(255) NOT NULL,
    image_path TEXT NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    prediction_class VARCHAR(100) NOT NULL,
    confidence FLOAT NOT NULL,
    inference_time_ms INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Metadata adicional
    image_size_bytes INTEGER,
    image_width INTEGER,
    image_height INTEGER,

    -- Índices para búsquedas rápidas
    CONSTRAINT predictions_confidence_check CHECK (confidence >= 0 AND confidence <= 1)
);

-- Tabla de métricas por modelo
CREATE TABLE IF NOT EXISTS model_metrics (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Metadata del experimento
    experiment_id VARCHAR(255),
    run_id VARCHAR(255),

    UNIQUE(model_name, metric_name, measured_at)
);

-- Tabla de imágenes procesadas
CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
    image_id VARCHAR(255) UNIQUE NOT NULL,
    original_filename VARCHAR(500),
    minio_path TEXT NOT NULL,
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_size_bytes INTEGER,
    width INTEGER,
    height INTEGER,
    format VARCHAR(50),
    source VARCHAR(100), -- 'upload', 'webcam', 'api'

    -- Estado de procesamiento
    processing_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    processed_at TIMESTAMP,

    -- Metadata JSON para campos adicionales
    metadata JSONB
);

-- Tabla de comparaciones de modelos
CREATE TABLE IF NOT EXISTS model_comparisons (
    id SERIAL PRIMARY KEY,
    image_id VARCHAR(255) NOT NULL,
    comparison_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Resultados de cada modelo
    resnet_prediction VARCHAR(100),
    resnet_confidence FLOAT,
    resnet_time_ms INTEGER,

    mobilenet_prediction VARCHAR(100),
    mobilenet_confidence FLOAT,
    mobilenet_time_ms INTEGER,

    efficientnet_prediction VARCHAR(100),
    efficientnet_confidence FLOAT,
    efficientnet_time_ms INTEGER,

    -- Análisis
    consensus_prediction VARCHAR(100), -- La predicción más común
    fastest_model VARCHAR(100),
    most_confident_model VARCHAR(100),

    FOREIGN KEY (image_id) REFERENCES images(image_id)
);

-- Tabla de eventos del sistema (audit log)
CREATE TABLE IF NOT EXISTS system_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    severity VARCHAR(20) DEFAULT 'info', -- 'debug', 'info', 'warning', 'error'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    service_name VARCHAR(100)
);

-- Índices para mejorar performance
CREATE INDEX idx_predictions_model ON predictions(model_name);
CREATE INDEX idx_predictions_created ON predictions(created_at DESC);
CREATE INDEX idx_predictions_image_id ON predictions(image_id);
CREATE INDEX idx_predictions_class ON predictions(prediction_class);

CREATE INDEX idx_images_status ON images(processing_status);
CREATE INDEX idx_images_upload ON images(upload_timestamp DESC);
CREATE INDEX idx_images_source ON images(source);

CREATE INDEX idx_model_metrics_name ON model_metrics(model_name);
CREATE INDEX idx_model_metrics_measured ON model_metrics(measured_at DESC);

CREATE INDEX idx_comparisons_image ON model_comparisons(image_id);
CREATE INDEX idx_comparisons_timestamp ON model_comparisons(comparison_timestamp DESC);

CREATE INDEX idx_events_type ON system_events(event_type);
CREATE INDEX idx_events_created ON system_events(created_at DESC);
CREATE INDEX idx_events_severity ON system_events(severity);

-- Vista para estadísticas rápidas por modelo
CREATE OR REPLACE VIEW model_stats AS
SELECT
    model_name,
    COUNT(*) as total_predictions,
    AVG(confidence) as avg_confidence,
    AVG(inference_time_ms) as avg_time_ms,
    MIN(inference_time_ms) as min_time_ms,
    MAX(inference_time_ms) as max_time_ms,
    COUNT(DISTINCT prediction_class) as unique_classes
FROM predictions
GROUP BY model_name;

-- Vista para las últimas predicciones con información de imagen
CREATE OR REPLACE VIEW recent_predictions AS
SELECT
    p.id,
    p.image_id,
    i.original_filename,
    p.model_name,
    p.prediction_class,
    p.confidence,
    p.inference_time_ms,
    p.created_at,
    i.source
FROM predictions p
JOIN images i ON p.image_id = i.image_id
ORDER BY p.created_at DESC;

-- Vista para comparaciones de rendimiento
CREATE OR REPLACE VIEW model_performance_comparison AS
SELECT
    DATE_TRUNC('hour', created_at) as hour,
    model_name,
    AVG(confidence) as avg_confidence,
    AVG(inference_time_ms) as avg_time_ms,
    COUNT(*) as prediction_count
FROM predictions
GROUP BY DATE_TRUNC('hour', created_at), model_name
ORDER BY hour DESC;

-- Función para insertar evento del sistema
CREATE OR REPLACE FUNCTION log_system_event(
    p_event_type VARCHAR,
    p_event_data JSONB,
    p_severity VARCHAR DEFAULT 'info',
    p_service_name VARCHAR DEFAULT 'unknown'
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO system_events (event_type, event_data, severity, service_name)
    VALUES (p_event_type, p_event_data, p_severity, p_service_name);
END;
$$ LANGUAGE plpgsql;

-- Insertar datos de ejemplo para testing
INSERT INTO system_events (event_type, event_data, severity, service_name)
VALUES
    ('database_initialized', '{"version": "1.0"}', 'info', 'postgres'),
    ('tables_created', '{"tables": ["predictions", "images", "model_metrics", "model_comparisons", "system_events"]}', 'info', 'postgres');

-- Configuración adicional de PostgreSQL para mejor performance
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET work_mem = '4MB';
ALTER SYSTEM SET min_wal_size = '1GB';
ALTER SYSTEM SET max_wal_size = '4GB';

COMMIT;
