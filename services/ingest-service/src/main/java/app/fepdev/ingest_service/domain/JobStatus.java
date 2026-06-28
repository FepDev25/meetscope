package app.fepdev.ingest_service.domain;

/**
 * Estado consolidado del job a lo largo del pipeline. El agregador lo avanza a
 * medida que llegan los eventos terminales de cada etapa.
 */
public enum JobStatus {
    UPLOADED,
    TRANSCRIBING,
    TRANSCRIBED
}
