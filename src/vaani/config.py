"""Central configuration. Reads .env once; never logs secret values.

Nothing here prints the key. `masked()` exists so we can show *that* a key is
loaded without revealing it.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_ROOT / ".env")

# --- Gnani Speech APIs (one key, header X-API-Key-ID, for both STT and TTS) ---
GNANI_API_KEY = os.getenv("GNANI_API_KEY", "").strip()
GNANI_STT_URL = os.getenv("GNANI_STT_URL", "https://api.vachana.ai/stt/v3").strip()
GNANI_TTS_URL = os.getenv("GNANI_TTS_URL", "https://api.vachana.ai/api/v1/tts/inference").strip()

# --- Reasoning layer (OpenAI-compatible), optional until provided ---
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "").strip()
LLM_API_KEY = os.getenv("LLM_API_KEY", "").strip()
LLM_MODEL = os.getenv("LLM_MODEL", "").strip()
LLM_EMBED_MODEL = os.getenv("LLM_EMBED_MODEL", "gemini-embedding-001").strip()

# The header name is a Gnani-specific fact from docs/vaani_context.md.
# Phase 1 confirms it empirically before anything depends on it.
GNANI_AUTH_HEADER = "X-API-Key-ID"


def have_gnani() -> bool:
    return bool(GNANI_API_KEY)


def have_llm() -> bool:
    return bool(LLM_BASE_URL and LLM_API_KEY and LLM_MODEL)


def masked(secret: str) -> str:
    """Show only enough to confirm identity in logs, never the whole key."""
    if not secret:
        return "<empty>"
    if len(secret) <= 10:
        return "*" * len(secret)
    return f"{secret[:6]}…{secret[-4:]} (len={len(secret)})"
