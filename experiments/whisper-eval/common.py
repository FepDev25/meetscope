"""Utilidades compartidas por los runners de evaluacion de Whisper.

Mantiene identica la forma de las salidas entre motores para que la comparacion
sea directa: mismo audio, mismo modelo, mismas metricas.
"""

from __future__ import annotations

import json
import subprocess
import wave
from dataclasses import asdict, dataclass, field
from pathlib import Path

MODEL = "large-v3-turbo"
LANGUAGE = "es"
DEVICE = "cpu"
COMPUTE_TYPE = "int8"

ROOT = Path(__file__).resolve().parent
AUDIO_PATH = ROOT.parent / "audio.mp3"
RESULTS_DIR = ROOT / "results"


@dataclass
class Segment:
    start: float
    end: float
    text: str
    words: list[dict] = field(default_factory=list)


@dataclass
class Metrics:
    engine: str
    model: str
    device: str
    compute_type: str
    language: str
    audio_seconds: float
    wall_seconds: float
    real_time_factor: float  # wall_seconds / audio_seconds; <1 es mas rapido que tiempo real
    segment_count: int
    has_word_timestamps: bool


def audio_duration_seconds(path: Path) -> float:
    """Duracion del audio via ffprobe; cae a wave si es WAV y no hay ffprobe."""
    try:
        out = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            capture_output=True, text=True, check=True,
        )
        return float(out.stdout.strip())
    except (FileNotFoundError, subprocess.CalledProcessError, ValueError):
        with wave.open(str(path), "rb") as w:
            return w.getnframes() / float(w.getframerate())


def write_outputs(engine: str, segments: list[Segment], metrics: Metrics) -> Path:
    out_dir = RESULTS_DIR / engine
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "transcript.txt").write_text(
        "\n".join(s.text.strip() for s in segments) + "\n", encoding="utf-8"
    )
    (out_dir / "segments.json").write_text(
        json.dumps([asdict(s) for s in segments], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "metrics.json").write_text(
        json.dumps(asdict(metrics), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return out_dir


def print_summary(metrics: Metrics, out_dir: Path) -> None:
    print(f"  motor              : {metrics.engine}")
    print(f"  segmentos          : {metrics.segment_count}")
    print(f"  timestamps palabra : {metrics.has_word_timestamps}")
    print(f"  audio (s)          : {metrics.audio_seconds:.1f}")
    print(f"  wall (s)           : {metrics.wall_seconds:.1f}")
    print(f"  RTF                : {metrics.real_time_factor:.2f}")
    print(f"  salidas            : {out_dir}")
