package app.fepdev.ingest_service.messaging;

import app.fepdev.ingest_service.config.AppProperties;
import app.fepdev.ingest_service.domain.Job;
import com.meetscope.events.AudioUploaded;
import com.meetscope.events.ObjectRef;
import java.time.Instant;
import java.util.UUID;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

/**
 * Publica el evento audio.uploaded en Avro. La clave del registro es el job_id,
 * de modo que todos los eventos de un mismo job caen en la misma particion y
 * conservan su orden.
 */
@Component
public class AudioUploadedPublisher {

    private final KafkaTemplate<String, Object> kafkaTemplate;
    private final String topic;

    public AudioUploadedPublisher(KafkaTemplate<String, Object> kafkaTemplate, AppProperties props) {
        this.kafkaTemplate = kafkaTemplate;
        this.topic = props.topics().audioUploaded();
    }

    public void publish(Job job) {
        AudioUploaded event = AudioUploaded.newBuilder()
                .setEventId(UUID.randomUUID())
                .setJobId(job.getJobId())
                .setOccurredAt(Instant.now())
                .setAudio(ObjectRef.newBuilder()
                        .setBucket(job.getAudioBucket())
                        .setKey(job.getAudioKey())
                        .build())
                .setOriginalFilename(job.getOriginalFilename())
                .setContentType(job.getContentType())
                .setSizeBytes(job.getSizeBytes())
                .setLanguageHint(job.getLanguage())
                .build();

        kafkaTemplate.send(topic, job.getJobId().toString(), event);
    }
}
