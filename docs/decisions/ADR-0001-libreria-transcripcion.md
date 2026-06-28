# ADR-0001: Libreria de transcripcion (faster-whisper vs WhisperX)

- Fecha: 2026-06-28
- Contexto del experimento: `experiments/whisper-eval/`

## Contexto

Se valido sobre audio real en espanol (`experiments/audio.mp3`, ~80 s), ambos motores con el mismo modelo `large-v3-turbo`, en CPU, `compute_type=int8`.

## Resultados medidos

| Criterio                  | faster-whisper          | WhisperX                          |
|---------------------------|-------------------------|-----------------------------------|
| Palabras transcritas      | 185                     | 185 (identico)                    |
| Calidad de texto          | Correcta                | Correcta (1 diferencia menor)     |
| Timestamps de palabra     | Si (185)                | Si (185, 0 sin alinear)           |
| Naturaleza timestamps     | Aproximados (DTW/atten) | Precisos (alineacion forzada w2v2)|
| Segmentacion              | 19 segmentos largos     | 22 segmentos cortos (VAD)         |
| RTF (CPU)                 | 0.34                    | ~0.71 computo (1.52 con descarga) |
| Dependencias              | CTranslate2, sin torch  | torch + modelo w2v2 (360 MB)      |

Evidencia versionada en `experiments/whisper-eval/results/`.

## Hallazgo clave

La hipotesis de partida resulto falsa: `faster-whisper` tambien entrega timestamps a nivel de palabra (`word_timestamps=True`), con las mismas 185 palabras. La diferencia real no es disponer o no de ellos, sino la precision acustica: WhisperX los ancla con alineacion forzada (mas exactos), faster-whisper los deriva del propio modelo (suficientes para agrupar segmentos por tema).

## Decision

Se usará **faster-whisper** en el `transcription-worker`.

- Mas del doble de rapido en CPU, justo en la etapa que es el cuello de botella.
- Sin dependencia de torch: el worker queda liviano (solo CTranslate2), sin arrastrar el stack CUDA.
- Ya entrega timestamps de palabra, suficientes para la segmentacion temporal por temas, que ancla a los tiempos de Whisper y nunca los pide al LLM.

Modelo: `large-v3-turbo`. Lengua fijada a espanol. `compute_type=int8` en CPU; GPU queda como optimizacion posterior.
