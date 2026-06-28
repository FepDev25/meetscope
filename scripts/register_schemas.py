#!/usr/bin/env python3
"""Registra los esquemas Avro del contrato en Schema Registry.

Idempotente: registrar un esquema identico devuelve el id existente. Fija la
compatibilidad BACKWARD por subject. Sin dependencias externas (solo stdlib).

Uso:
    python scripts/register_schemas.py
    SCHEMA_REGISTRY_URL=http://localhost:8081 python scripts/register_schemas.py

El subject de cada topic sigue TopicNameStrategy: <topic>-value. El topic se
deriva del nombre del archivo (audio-uploaded.avsc -> audio.uploaded).
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

REGISTRY_URL = os.environ.get("SCHEMA_REGISTRY_URL", "http://localhost:8081").rstrip("/")
SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas" / "avro"
COMPATIBILITY = "BACKWARD"
CONTENT_TYPE = "application/vnd.schemaregistry.v1+json"


def _request(method: str, path: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(f"{REGISTRY_URL}{path}", data=data, method=method)
    req.add_header("Content-Type", CONTENT_TYPE)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read() or "{}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        raise SystemExit(f"Error {e.code} en {method} {path}: {detail}")
    except urllib.error.URLError as e:
        raise SystemExit(f"No se pudo contactar Schema Registry en {REGISTRY_URL}: {e.reason}")


def topic_from_filename(path: Path) -> str:
    return path.stem.replace("-", ".")


def register(path: Path) -> None:
    subject = f"{topic_from_filename(path)}-value"
    schema_str = path.read_text(encoding="utf-8")

    # La compatibilidad se fija por subject; el subject se crea con el primer registro.
    result = _request(
        "POST",
        f"/subjects/{subject}/versions",
        {"schemaType": "AVRO", "schema": schema_str},
    )
    _request("PUT", f"/config/{subject}", {"compatibility": COMPATIBILITY})

    print(f"  {subject:<30} id={result.get('id')}  compat={COMPATIBILITY}")


def main() -> None:
    files = sorted(SCHEMAS_DIR.glob("*.avsc"))
    if not files:
        raise SystemExit(f"No se encontraron esquemas en {SCHEMAS_DIR}")

    print(f"Registrando {len(files)} esquemas en {REGISTRY_URL}")
    for path in files:
        register(path)

    subjects = _request("GET", "/subjects")
    print(f"Subjects en el registro: {subjects}")


if __name__ == "__main__":
    sys.exit(main())
