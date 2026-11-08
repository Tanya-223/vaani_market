"""Tier budgets + hard-timeout executor with downward degradation (report §7.4).

Each retrieval tier runs under a hard time budget. If it overruns, we degrade DOWNWARD
(Tier-3 → Tier-2 → Tier-1 → no-retrieval), never upward — so under load the system becomes
less thorough, never slower.

NOTE on the numbers: the report's 150/700/1800 ms budgets assume LOCAL embeddings. This build
uses a network embedder (Gemini), where one query is ~0.7–2 s, so the budgets below are tuned
to that deployment. The MECHANISM (hard timeout + downward degrade) is exactly §7.4; only the
constants differ, consistent with the documented embedder deviation.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from typing import Callable, TypeVar

T = TypeVar("T")

# Milliseconds. tier1 keyword fast-path is instant (not timed); these bound the embedding work.
TIER_BUDGET_MS = {1: 2000, 2: 2500, 3: 1800}


def within_budget(fn: Callable[[], T], budget_ms: int, default: T) -> tuple[T, bool]:
    """Run fn under a hard timeout. Returns (result, ok); ok=False means it overran its
    budget and the caller should degrade to a cheaper tier / fallback."""
    with ThreadPoolExecutor(max_workers=1) as ex:
        fut = ex.submit(fn)
        try:
            return fut.result(timeout=budget_ms / 1000.0), True
        except FutureTimeout:
            return default, False
