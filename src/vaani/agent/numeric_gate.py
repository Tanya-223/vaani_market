"""Numeric provenance gate.

Extracts every number from the drafted answer and checks each against the numbers the
FactSheet allows (currency rounding tolerated). An orphan digit — a number present in
the text but in no tool payload — fails the gate. The orchestrator then regenerates once,
and if it still fails, falls back to a code-built template sentence.

Pure and offline-testable.
"""
from __future__ import annotations

import re

# Matches 1,23,456.78 / 185.40 / 2.3 / -0.11 etc. (commas are Indian or Western grouping)
_NUM_RE = re.compile(r"-?\d[\d,]*(?:\.\d+)?")


def extract_numbers(text: str) -> list[float]:
    out: list[float] = []
    for m in _NUM_RE.finditer(text or ""):
        tok = m.group().replace(",", "")
        try:
            out.append(float(tok))
        except ValueError:
            continue
    return out


def _matches(num: float, allowed: set[float], tol_abs: float, tol_rel: float) -> bool:
    for a in allowed:
        if abs(num - a) <= max(tol_abs, abs(a) * tol_rel):
            return True
    return False


def check(
    draft: str,
    allowed: set[float],
    *,
    tol_abs: float = 0.05,
    tol_rel: float = 0.01,
) -> tuple[bool, list[float]]:
    """Return (ok, orphans). ok is True when every number in the draft traces to
    an allowed value within tolerance (1% relative or 0.05 absolute)."""
    orphans = [n for n in extract_numbers(draft) if not _matches(n, allowed, tol_abs, tol_rel)]
    return (len(orphans) == 0, orphans)
