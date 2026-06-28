package app.fepdev.ingest_service.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * Configuracion de la aplicacion: object storage y nombres de topics.
 */
@ConfigurationProperties(prefix = "app")
public record AppProperties(Minio minio, Topics topics) {

    public record Minio(String endpoint, String accessKey, String secretKey, String bucket) {
    }

    public record Topics(String audioUploaded) {
    }
}
