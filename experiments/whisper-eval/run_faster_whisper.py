"""Transcribe el audio de prueba con faster-whisper (CTranslate2, sin torch).

Pide word_timestamps=True para ver tambien la granularidad de palabra que ofrece
este motor, y poder compararla contra WhisperX.
"""

from __future__ import annotations

import time

from faster_whisper import WhisperModel

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

ENGINE = "faster-whisper"


def main() -> None:
    audio_seconds = audio_duration_seconds(AUDIO_PATH)

    model = WhisperModel(MODEL, device=DEVICE, compute_type=COMPUTE_TYPE)

    start = time.perf_counter()
    seg_iter, _info = model.transcribe(
        str(AUDIO_PATH),
        language=LANGUAGE,
        word_timestamps=True,
    )

    segments: list[Segment] = []
    has_words = False
    for s in seg_iter:  # el motor transcribe perezosamente al iterar
        words = []
        if s.words:
            has_words = True
            words = [
                {"start": w.start, "end": w.end, "word": w.word, "probability": w.probability}
                for w in s.words
            ]
        segments.append(Segment(start=s.start, end=s.end, text=s.text, words=words))
    wall_seconds = time.perf_counter() - start

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
