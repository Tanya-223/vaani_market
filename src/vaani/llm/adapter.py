"""Reasoning-layer adapter: ONE function over an OpenAI-compatible chat/completions API.

Provider-agnostic — base URL, key, model come from .env, so the provider can be
swapped without touching the pipeline. Built on the retrying session so it inherits
the 429/5xx-only retry policy. Output is capped (max_tokens) for latency.
"""
from __future__ import annotations

import json as _json
from dataclasses import dataclass, field
from typing import Any

from .. import config
from ..http import request_with_retry


class LLMError(RuntimeError):
    pass


@dataclass
class LLMResult:
    text: str
    wall_seconds: float
    usage: dict[str, Any] = field(default_factory=dict)


def chat(
    messages: list[dict[str, str]],
    *,
    model: str | None = None,
    max_tokens: int = 512,
    temperature: float = 0.2,
    json_mode: bool = False,
    timeout: float = 60.0,
) -> LLMResult:
    if not config.have_llm():
        raise LLMError(
            "LLM endpoint not configured — set LLM_BASE_URL / LLM_API_KEY / LLM_MODEL in .env"
        )
    url = config.LLM_BASE_URL.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    body: dict[str, Any] = {
        "model": model or config.LLM_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if json_mode:
        body["response_format"] = {"type": "json_object"}

    resp, timing = request_with_retry(
        "POST", url, headers=headers, json=body, timeout=timeout,
        max_retries=5, base_delay=2.0, max_delay=30.0,  # ride out free-tier per-minute limits
    )
    if resp.status_code != 200:
        raise LLMError(f"HTTP {resp.status_code}: {resp.text[:400]}")

    j = resp.json()
    try:
        text = j["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError):
        raise LLMError(f"unexpected response shape: {str(j)[:400]}")

    return LLMResult(text=text, wall_seconds=timing.wall_seconds, usage=j.get("usage", {}))


def chat_json(messages: list[dict[str, str]], **kwargs: Any) -> dict[str, Any]:
    """Chat with JSON mode on, returning the parsed object. Raises if not valid JSON."""
    res = chat(messages, json_mode=True, **kwargs)
    text = res.text.strip()
    # Some providers wrap JSON in ```json fences; strip them defensively.
    if text.startswith("```"):
        text = text.strip("`")
        text = text[text.find("{"): text.rfind("}") + 1]
    try:
        return _json.loads(text)
    except Exception as exc:
        raise LLMError(f"model did not return valid JSON: {exc}; got: {res.text[:300]}")


def embed(texts: list[str], *, model: str | None = None, timeout: float = 30.0) -> list[list[float]]:
    """Embed a batch of texts via the OpenAI-compatible /embeddings endpoint."""
    if not config.have_llm():
        raise LLMError("LLM endpoint not configured — set LLM_* in .env")
    url = config.LLM_BASE_URL.rstrip("/") + "/embeddings"
    headers = {
        "Authorization": f"Bearer {config.LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {"model": model or config.LLM_EMBED_MODEL, "input": texts}
    resp, _ = request_with_retry(
        "POST", url, headers=headers, json=body, timeout=timeout,
        max_retries=5, base_delay=2.0, max_delay=30.0,
    )
    if resp.status_code != 200:
        raise LLMError(f"embeddings HTTP {resp.status_code}: {resp.text[:300]}")
    data = resp.json().get("data", [])
    return [row["embedding"] for row in data]
