package app.fepdev.ingest_service.web;

import app.fepdev.ingest_service.domain.Job;
import app.fepdev.ingest_service.service.JobService;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.multipart.MultipartFile;

@RestController
public class JobController {

    private final JobService jobService;

    public JobController(JobService jobService) {
        this.jobService = jobService;
    }

    @PostMapping(path = "/jobs", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<JobResponse> create(
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "language", required = false) String language) {

        if (file.isEmpty()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "El archivo de audio esta vacio");
        }
        Job job = jobService.ingest(file, language);
        return ResponseEntity.accepted().body(JobResponse.from(job));
    }

    @GetMapping("/jobs/{id}")
    public ResponseEntity<JobResponse> get(@PathVariable("id") UUID id) {
        return jobService.find(id)
                .map(JobResponse::from)
                .map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }
}
