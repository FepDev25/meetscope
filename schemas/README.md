# schemas

Contrato de eventos del pipeline en Avro. Es la fuente de verdad compartida entre los servicios Java y Python; se registra en Schema Registry.

```
schemas/
├── avro/        Definiciones .avsc, una por evento.
└── examples/    Fixtures de ejemplo validados contra los esquemas.
```

## Esquemas

| Archivo                       | Record               | Topic                  |
|-------------------------------|----------------------|------------------------|
| `avro/audio-uploaded.avsc`    | `AudioUploaded`      | `audio.uploaded`       |
| `avro/transcript-created.avsc`| `TranscriptCreated`  | `transcript.created`   |
| `avro/enrichment-completed.avsc`| `EnrichmentCompleted`| `enrichment.completed` |
| `avro/indexing-completed.avsc`| `IndexingCompleted`  | `indexing.completed`   |

Namespace: `com.meetscope.events`. Subject naming `TopicNameStrategy`, compatibilidad `BACKWARD`. Detalle completo de la topologia y las convenciones en `../docs/EVENT-CONTRACT.md`.

## Registrar en Schema Registry

Con la infraestructura levantada, registra (idempotente) los esquemas en sus
subjects `<topic>-value` con compatibilidad `BACKWARD`:

```sh
python scripts/register_schemas.py
```

## Validar los esquemas

```sh
uv run --no-project --with fastavro python -c "
import fastavro, json, glob
for f in sorted(glob.glob('schemas/avro/*.avsc')):
    fastavro.parse_schema(json.load(open(f)))
    print('OK', f)
"
```
