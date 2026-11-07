"""One reused HTTP session + a retry policy that matches Gnani's documented behaviour.

Rules (from docs/vaani_context.md):
  - Retry ONLY on 429 and 5xx. Never retry 400/401/402/403/422.
  - 429 carries no Retry-After header, so we use exponential backoff with jitter.
  - Reuse a single connection (keep-alive) to cut TLS-handshake latency.
"""
from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Any

import requests

_SESSION: requests.Session | None = None

RETRY_STATUS = {429, 500, 502, 503, 504}
NEVER_RETRY_STATUS = {400, 401, 402, 403, 422}


def session() -> requests.Session:
    global _SESSION
    if _SESSION is None:
        _SESSION = requests.Session()
    return _SESSION


@dataclass
class Timing:
    """Wall-clock timing for one call, so we can compare with the API's own
    processing_time later (the difference is network overhead)."""
    wall_seconds: float
    attempts: int


def request_with_retry(
    method: str,
    url: str,
    *,
    max_retries: int = 4,
    base_delay: float = 0.5,
    max_delay: float = 8.0,
    timeout: float = 30.0,
    **kwargs: Any,
) -> tuple[requests.Response, Timing]:
    """Perform a request, retrying only on 429/5xx with exponential backoff + jitter.

    Returns the final Response plus wall-clock timing. Raises on network errors
    after exhausting retries, so callers can fail loudly rather than mask it.
    """
    sess = session()
    start = time.monotonic()
    attempts = 0
    last_exc: Exception | None = None

    for attempt in range(max_retries + 1):
        attempts = attempt + 1
        try:
            resp = sess.request(method, url, timeout=timeout, **kwargs)
        except requests.RequestException as exc:  # connection/timeout errors
            last_exc = exc
            if attempt >= max_retries:
                raise
            _sleep_backoff(attempt, base_delay, max_delay)
            continue

        if resp.status_code in RETRY_STATUS and attempt < max_retries:
            _sleep_backoff(attempt, base_delay, max_delay)
            continue
        return resp, Timing(time.monotonic() - start, attempts)

    # Should not reach here; defensive.
    raise last_exc if last_exc else RuntimeError("request_with_retry exhausted")


def _sleep_backoff(attempt: int, base_delay: float, max_delay: float) -> None:
    delay = min(max_delay, base_delay * (2 ** attempt))
    delay += random.uniform(0, delay * 0.25)  # full-ish jitter
    time.sleep(delay)
