"""Tiny deterministic language detector by Unicode script.

Used before the planner runs (the advice/ambiguous short-circuits need a language for
their constant, but haven't called the planner yet). Script is a reliable signal for
te-IN / hi-IN; everything else defaults to en-IN.
"""
from __future__ import annotations

import re

_TELUGU = re.compile(r"[ఀ-౿]")
_DEVANAGARI = re.compile(r"[ऀ-ॿ]")

SUPPORTED = ("te-IN", "hi-IN", "en-IN")


def detect(text: str) -> str:
    if _TELUGU.search(text or ""):
        return "te-IN"
    if _DEVANAGARI.search(text or ""):
        return "hi-IN"
    return "en-IN"
