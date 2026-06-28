package app.fepdev.ingest_service.storage;

import app.fepdev.ingest_service.config.AppProperties;
import io.minio.MinioClient;
import io.minio.PutObjectArgs;
import java.io.IOException;
import java.io.InputStream;
import java.util.UUID;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

/**
 * Almacena el binario de audio en el object storage. El pipeline solo mueve
 * referencias (bucket + key); el binario nunca entra a Kafka.
 */
@Service
public class StorageService {

    private final MinioClient minioClient;
    private final String bucket;

    public StorageService(MinioClient minioClient, AppProperties props) {
        this.minioClient = minioClient;
        this.bucket = props.minio().bucket();
    }

    public String bucket() {
        return bucket;
    }

    /**
     * Sube el audio bajo la clave {jobId}/{nombre} y devuelve la clave resultante.
     */
    public String store(UUID jobId, MultipartFile file) {
        String key = jobId + "/" + safeName(file.getOriginalFilename());
        try (InputStream stream = file.getInputStream()) {
            minioClient.putObject(
                    PutObjectArgs.builder()
                            .bucket(bucket)
                            .object(key)
                            .stream(stream, file.getSize(), -1)
                            .contentType(file.getContentType())
                            .build());
        } catch (IOException e) {
            throw new StorageException("No se pudo leer el audio subido", e);
        } catch (Exception e) {
            throw new StorageException("No se pudo almacenar el audio en object storage", e);
        }
        return key;
    }

    private static String safeName(String original) {
        if (original == null || original.isBlank()) {
            return "audio";
        }
        // Conserva solo el nombre base y caracteres seguros para una clave de objeto.
        String base = original.replace("\\", "/");
        base = base.substring(base.lastIndexOf('/') + 1);
        return base.replaceAll("[^A-Za-z0-9._-]", "_");
    }
}
