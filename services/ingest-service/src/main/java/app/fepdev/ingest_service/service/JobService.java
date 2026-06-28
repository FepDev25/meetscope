package app.fepdev.ingest_service.service;

import app.fepdev.ingest_service.domain.Job;
import app.fepdev.ingest_service.domain.JobRepository;
import app.fepdev.ingest_service.domain.JobStatus;
import app.fepdev.ingest_service.messaging.AudioUploadedPublisher;
import app.fepdev.ingest_service.storage.StorageService;
import java.util.Optional;
import java.util.UUID;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

@Service
public class JobService {

    private static final String DEFAULT_CONTENT_TYPE = "application/octet-stream";

    private final StorageService storageService;
    private final JobRepository jobRepository;
    private final AudioUploadedPublisher publisher;

    public JobService(StorageService storageService, JobRepository jobRepository,
            AudioUploadedPublisher publisher) {
        this.storageService = storageService;
        this.jobRepository = jobRepository;
        this.publisher = publisher;
    }

    /**
     * Punto de entrada del pipeline: almacena el audio, registra el job y emite
     * audio.uploaded. El binario va a object storage; el evento lleva la referencia.
     */
    @Transactional
    public Job ingest(MultipartFile file, String language) {
        UUID jobId = UUID.randomUUID();
        String key = storageService.store(jobId, file);

        Job job = new Job();
        job.setJobId(jobId);
        job.setStatus(JobStatus.UPLOADED);
        job.setOriginalFilename(file.getOriginalFilename());
        job.setContentType(file.getContentType() != null ? file.getContentType() : DEFAULT_CONTENT_TYPE);
        job.setSizeBytes(file.getSize());
        job.setAudioBucket(storageService.bucket());
        job.setAudioKey(key);
        job.setLanguage(language);
        jobRepository.save(job);

        publisher.publish(job);
        return job;
    }

    @Transactional(readOnly = true)
    public Optional<Job> find(UUID jobId) {
        return jobRepository.findById(jobId);
    }
}
