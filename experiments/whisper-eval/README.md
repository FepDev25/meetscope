# whisper-eval

Banco de pruebas de la Fase 1: validar Whisper sobre audio real en espanol y decidir la libreria de transcripcion (`faster-whisper` vs `WhisperX`). Queda en el repositorio como evidencia de la decision, no es codigo desechable.

Ambos motores corren el mismo modelo (`large-v3-turbo`) en CPU con `compute_type=int8`, sobre el mismo audio (`../audio.mp3`), y vuelcan salidas con la misma forma para comparar.

## Que compara

- Calidad del texto transcrito (`results/<motor>/transcript.txt`).
- Granularidad de timestamps: por segmento vs por palabra (`results/<motor>/segments.json`). WhisperX anade alineacion forzada para timestamps de palabra precisos; faster-whisper los aproxima.
- Velocidad en CPU: wall time y RTF (`results/<motor>/metrics.json`).

El criterio que pesa la decision: la extension de segmentacion temporal por temas necesita timestamps fiables a nivel de palabra.

## Requisitos

- `uv` y `ffmpeg` (para `ffprobe` y la decodificacion de audio).
- Primera ejecucion descarga el modelo y, en WhisperX, el modelo de alineacion.

## Uso

```sh
cd experiments/whisper-eval
uv run run_faster_whisper.py
uv run run_whisperx.py
```

Las salidas quedan en `results/faster-whisper/` y `results/whisperx/`.
