"""Gnani Prisma v3.0 speech-to-text client.

multipart/form-data upload. Success is JSON with transcript + detected_language_code
+ processing_time. We log the API's processing_time so it can be compared with our
wall-clock time (the difference is network overhead).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .. import config
from ..http import request_with_retry

LANGS = ["bn-IN", "en-IN", "gu-IN", "hi-IN", "kn-IN", "ml-IN", "mr-IN", "pa-IN", "ta-IN", "te-IN"]


class STTError(RuntimeError):
    def __init__(self, status: int, message: str, body: str):
        super().__init__(f"Prisma {status}: {message}")
        self.status = status
        self.message = message
        self.body = body


@dataclass
class STTResult:
    transcript: str
    detected_language_code: str | None
    processing_time: float | None
    wall_seconds: float
    raw: dict[str, Any]


def transcribe(
    audio: bytes | str | Path,
    *,
    language_code: str = "indic-auto",
    model: str = "prisma-v3.0",
    keyterms: list[str] | None = None,
    filename: str = "audio.wav",
) -> STTResult:
    if not config.have_gnani():
        raise STTError(0, "GNANI_API_KEY not set", "")

    if isinstance(audio, (str, Path)):
        filename = Path(audio).name
        audio_bytes = Path(audio).read_bytes()
    else:
        audio_bytes = audio

    data: dict[str, Any] = {"language_code": language_code, "model": model}
    if keyterms:
        # Up to 200 terms; comma-separated string is accepted.
        data["keyterms"] = ",".join(keyterms[:200])

    files = {"audio_file": (filename, audio_bytes, "audio/wav")}
    headers = {config.GNANI_AUTH_HEADER: config.GNANI_API_KEY}

    resp, timing = request_with_retry(
        "POST", config.GNANI_STT_URL, headers=headers, data=data, files=files, timeout=60
    )

    if resp.status_code != 200:
        raise STTError(resp.status_code, _error_message(resp), resp.text[:500])

    j = resp.json()
    if not j.get("success", False):
        err = j.get("error", {})
        raise STTError(200, err.get("message", "transcription failed"), resp.text[:500])

    return STTResult(
        transcript=j.get("transcript", ""),
        detected_language_code=j.get("detected_language_code"),
        processing_time=j.get("processing_time"),
        wall_seconds=timing.wall_seconds,
        raw=j,
    )


def _error_message(resp) -> str:
    try:
        j = resp.json()
    except Exception:
        return resp.text[:200]
    if isinstance(j.get("detail"), dict):
        return j["detail"].get("message", str(j))
    if isinstance(j.get("detail"), list):
        return str(j["detail"])
    if isinstance(j.get("error"), dict):
        return j["error"].get("message", str(j))
    return j.get("message") or j.get("code") or str(j)
