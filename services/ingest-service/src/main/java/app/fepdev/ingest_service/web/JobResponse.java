package app.fepdev.ingest_service.web;

import app.fepdev.ingest_service.domain.Job;
import app.fepdev.ingest_service.domain.JobStatus;
import java.time.Instant;
import java.util.UUID;

public record JobResponse(
        UUID jobId,
        JobStatus status,
        String originalFilename,
        String language,
        Instant createdAt,
        Instant updatedAt) {

    public static JobResponse from(Job job) {
        return new JobResponse(
                job.getJobId(),
                job.getStatus(),
                job.getOriginalFilename(),
                job.getLanguage(),
                job.getCreatedAt(),
                job.getUpdatedAt());
    }
}
