"""Tier-1 retrieval: embed the glossary once, answer concept questions by cosine top-k.

Document-aware chunking (report 7.1): one glossary entry = one chunk. The corpus is
small, homogeneous and static — exactly where naive single-vector retrieval is the
right choice. Concept answers are returned from the (human-reviewable) glossary text
directly, so there is no LLM generation step to hallucinate.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from ..llm import adapter
from . import glossary

ANSWER_THRESHOLD = 0.55   # below this, we don't claim a glossary match


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


@dataclass
class Hit:
    entry: glossary.Entry
    score: float


class Tier1Index:
    def __init__(self) -> None:
        self._vectors: list[list[float]] | None = None

    def _doc_text(self, e: glossary.Entry) -> str:
        # Embed English term + Telugu definition so both English and Telugu queries match.
        return f"{e.term_en}. {e.text_te}"

    def build(self) -> None:
        if self._vectors is not None:
            return
        self._vectors = adapter.embed([self._doc_text(e) for e in glossary.GLOSSARY])

    def query(self, text: str, k: int = 5) -> list[Hit]:
        self.build()
        qv = adapter.embed([text])[0]
        scored = [
            Hit(e, cosine(qv, v))
            for e, v in zip(glossary.GLOSSARY, self._vectors or [])
        ]
        scored.sort(key=lambda h: h.score, reverse=True)
        return scored[:k]

    def answer(self, text: str, language: str = "te-IN", threshold: float = ANSWER_THRESHOLD):
        """Return (entry, score) for the best glossary match, or (None, top_score)."""
        hits = self.query(text, k=5)
        if hits and hits[0].score >= threshold:
            return hits[0].entry, hits[0].score
        return None, (hits[0].score if hits else 0.0)


# Module-level singleton (built on first use).
_INDEX = Tier1Index()


def answer(text: str, language: str = "te-IN"):
    return _INDEX.answer(text, language)


def query(text: str, k: int = 5) -> list[Hit]:
    return _INDEX.query(text, k)
