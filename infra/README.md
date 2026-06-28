# infra

Infraestructura local del pipeline, orquestada con `docker-compose.yml` en la raiz del repositorio.

## Componentes

| Servicio        | Host                  | Notas                                       |
|-----------------|-----------------------|---------------------------------------------|
| Kafka           | `localhost:9092`      | Modo KRaft, sin Zookeeper. Single node.     |
| Schema Registry | `localhost:8081`      | Compatibilidad por defecto `BACKWARD`.      |
| Kafka UI        | `localhost:8080`      | Inspeccion de topics, mensajes y esquemas.  |
| MinIO API       | `localhost:9000`      | Object storage S3. Bucket `meetscope-audio`.|
| MinIO consola   | `localhost:9001`      | Usuario/clave `minioadmin` / `minioadmin`.  |
| Postgres        | `localhost:5433`      | DB/usuario/clave `meetscope`. Estado y dedupe. |

Postgres se publica en el host en `5433` (el `5432` suele estar ocupado).

## Uso

```sh
docker compose up -d        # levantar
docker compose ps           # estado
docker compose down         # parar (conserva volumenes)
docker compose down -v      # parar y borrar datos
```

Al arrancar, dos jobs efimeros provisionan el entorno y terminan: `kafka-topics-init` crea los topics del contrato y `minio-init` crea el bucket.

## Esquema de Postgres

`infra/postgres/init.sql` (se ejecuta solo en la primera creacion del volumen):

- `jobs`: estado consolidado de cada job.
- `processed_events`: dedupe de idempotencia, clave `(job_id, stage)`.
