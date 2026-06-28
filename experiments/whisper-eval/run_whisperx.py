"""Transcribe el audio de prueba con WhisperX y alinea a nivel de palabra.

WhisperX usa faster-whisper por debajo para la transcripcion, pero anade un paso
de alineacion forzada (wav2vec2) que produce timestamps de palabra precisos. Eso
es lo que la extension de segmentacion temporal por temas necesita.
"""

from __future__ import annotations

import time

import whisperx

from common import (
    AUDIO_PATH,
    COMPUTE_TYPE,
    DEVICE,
    LANGUAGE,
    MODEL,
    Metrics,
    Segment,
    audio_duration_seconds,
    print_summary,
    write_outputs,
)

ENGINE = "whisperx"
BATCH_SIZE = 8  # CPU: lotes pequenos


def main() -> None:
    audio_seconds = audio_duration_seconds(AUDIO_PATH)
    audio = whisperx.load_audio(str(AUDIO_PATH))

    start = time.perf_counter()

    model = whisperx.load_model(
        MODEL, device=DEVICE, compute_type=COMPUTE_TYPE, language=LANGUAGE
    )
    result = model.transcribe(audio, batch_size=BATCH_SIZE, language=LANGUAGE)

    align_model, metadata = whisperx.load_align_model(
        language_code=LANGUAGE, device=DEVICE
    )
    result = whisperx.align(
        result["segments"], align_model, metadata, audio, DEVICE,
        return_char_alignments=False,
    )

    wall_seconds = time.perf_counter() - start

    segments: list[Segment] = []
    has_words = False
    for s in result["segments"]:
        words = []
        for w in s.get("words", []):
            # Tras la alineacion cada palabra trae start/end; algunas pueden faltar
            # si la alineacion no encontro anclaje (p. ej. numeros o simbolos).
            if "start" in w and "end" in w:
                has_words = True
            words.append(
                {
                    "start": w.get("start"),
                    "end": w.get("end"),
                    "word": w.get("word"),
                    "probability": w.get("score"),
                }
            )
        segments.append(
            Segment(start=s["start"], end=s["end"], text=s["text"], words=words)
        )

    metrics = Metrics(
        engine=ENGINE,
        model=MODEL,
        device=DEVICE,
        compute_type=COMPUTE_TYPE,
        language=LANGUAGE,
        audio_seconds=audio_seconds,
        wall_seconds=wall_seconds,
        real_time_factor=wall_seconds / audio_seconds if audio_seconds else 0.0,
        segment_count=len(segments),
        has_word_timestamps=has_words,
    )

    out_dir = write_outputs(ENGINE, segments, metrics)
    print_summary(metrics, out_dir)


if __name__ == "__main__":
    main()
