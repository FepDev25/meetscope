-- Esquema inicial del estado del pipeline.
-- Estado consolidado del job e idempotencia del procesamiento por etapa.
-- Los servicios pueden evolucionar este esquema con migraciones propias mas adelante.

-- Estado consolidado de cada job, mantenido por el agregador de ingest-service.
CREATE TABLE IF NOT EXISTS jobs (
    job_id            UUID PRIMARY KEY,
    status            TEXT NOT NULL,
    original_filename TEXT,
    content_type      TEXT,
    size_bytes        BIGINT,
    audio_bucket      TEXT,
    audio_key         TEXT,
    language          TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Dedupe de idempotencia: clave (job_id, stage). Un consumidor registra aqui la
-- combinacion antes (o como parte) de procesar; un evento reprocesado no duplica
-- trabajo porque la insercion choca con la clave primaria.
CREATE TABLE IF NOT EXISTS processed_events (
    job_id       UUID NOT NULL,
    stage        TEXT NOT NULL,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (job_id, stage)
);
