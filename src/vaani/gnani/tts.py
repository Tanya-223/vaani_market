"""Gnani Timbre v3.0 text-to-speech client.

Success response is RAW AUDIO BYTES (not JSON, not base64). Errors come back as
JSON. We always pass model + language + voice explicitly (per docs/vaani_context.md).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .. import config
from ..http import request_with_retry

# Timbre v3.0 voices that support Telugu (all 13 do; these are a convenient subset).
V3_VOICES = [
    "Avinash", "Chetana", "Devansh", "Kalpana", "Lakshmi", "Prakash",
    "Riyaa", "Shivani", "Shubham", "Tarika", "Vasudha", "Yashraj", "Harshad",
]


class TTSError(RuntimeError):
    def __init__(self, status: int, message: str, body: str):
        super().__init__(f"Timbre {status}: {message}")
        self.status = status
        self.message = message
        self.body = body


@dataclass
class TTSResult:
    audio: bytes
    content_type: str
    wall_seconds: float
    request: dict[str, Any] = field(default_factory=dict)


def synthesize(
    text: str,
    *,
    language: str = "te-IN",
    voice: str = "Kalpana",
    model: str = "timbre-v3.0",
    speed: float = 1.0,  # live API requires a NUMBER (0.85-1.15); the word forms in the docs are rejected
    sample_rate: int = 24000,
    container: str = "wav",
) -> TTSResult:
    if not config.have_gnani():
        raise TTSError(0, "GNANI_API_KEY not set", "")

    body = {
        "text": text,
        "model": model,
        "voice": voice,
        "language": language,          # always explicit, never 'auto'
        "speed": speed,
        "audio_config": {
            "sample_rate": sample_rate,
            "num_channels": 1,
            "sample_width": 2,
            "encoding": "linear_pcm",
            "container": container,
        },
    }
    headers = {config.GNANI_AUTH_HEADER: config.GNANI_API_KEY}

    resp, timing = request_with_retry(
        "POST", config.GNANI_TTS_URL, headers=headers, json=body, timeout=60
    )

    ctype = resp.headers.get("content-type", "")
    if resp.status_code != 200:
        raise TTSError(resp.status_code, _error_message(resp), resp.text[:500])
    if "application/json" in ctype:
        # A 200 that is somehow JSON would be unexpected; surface it.
        raise TTSError(200, "expected audio bytes, got JSON", resp.text[:500])

    return TTSResult(
        audio=resp.content,
        content_type=ctype,
        wall_seconds=timing.wall_seconds,
        request={"voice": voice, "language": language, "model": model, "chars": len(text)},
    )


def _error_message(resp) -> str:
    try:
        j = resp.json()
    except Exception:
        return resp.text[:200]
    if isinstance(j.get("detail"), dict):      # auth / rate-limit shape
        return j["detail"].get("message", str(j))
    return j.get("message", str(j))             # flat validation shape
