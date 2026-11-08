"""Tier-1 retrieval: embed the glossary once, answer concept questions by cosine top-k.

Document-aware chunking (report 7.1): one glossary entry = one chunk. The corpus is
small, homogeneous and static — exactly where naive single-vector retrieval is the
right choice. Concept answers are returned from the (human-reviewable) glossary text
directly, so there is no LLM generation step to hallucinate.
"""
from __future__ import annotations

import math
import unicodedata
from dataclasses import dataclass

from ..llm import adapter
from . import glossary

ANSWER_THRESHOLD = 0.55   # below this, we don't claim a glossary match

# Fast-path: obvious term keywords -> entry id, checked in order (specific first). Lets
# common beginner questions answer INSTANTLY with no embedding call (big latency win), and
# resolves the "share market" vs "share" tie deterministically.
_KEYWORDS: list[tuple[str, str]] = [
    ("క్యాండిల్", "candlestick"), ("candle", "candlestick"),
    ("p/e", "pe_ratio"), ("పి/ఈ", "pe_ratio"), ("పిఈ", "pe_ratio"), ("రేషియో", "pe_ratio"),
    ("market cap", "market_cap"), ("మార్కెట్ క్యాప్", "market_cap"), ("మొత్తం విలువ", "market_cap"),
    ("circuit", "circuit_limit"), ("సర్క్యూట్", "circuit_limit"),
    ("demat", "demat_account"), ("డీమ్యాట్", "demat_account"),
    ("dividend", "dividend"), ("డివిడెండ్", "dividend"),
    ("volume", "volume"), ("వాల్యూమ్", "volume"),
    ("goldbees", "etf"), ("గోల్డ్ బీస్", "etf"), ("etf", "etf"), ("ఇటిఎఫ్", "etf"),
    ("nse", "nse_bse"), ("bse", "nse_bse"),
    ("sensex", "nifty_sensex"), ("సెన్సెక్స్", "nifty_sensex"),
    ("nifty", "nifty_sensex"), ("నిఫ్టీ", "nifty_sensex"),
    ("share market", "stock_market"), ("stock market", "stock_market"),
    ("షేర్ మార్కెట్", "stock_market"), ("స్టాక్ మార్కెట్", "stock_market"), ("మార్కెట్", "stock_market"),
    ("స్టాక్", "stock_share"), ("షేర్", "stock_share"), ("stock", "stock_share"), ("share", "stock_share"),
]


def _norm(s: str) -> str:
    # NFC + strip zero-width joiners so Telugu keyword matching is robust.
    return unicodedata.normalize("NFC", s.lower()).replace("‌", "").replace("‍", "")


def keyword_hit(text: str) -> str | None:
    t = _norm(text)
    for kw, eid in _KEYWORDS:
        if _norm(kw) in t:
            return eid
    return None


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
        """Return (entry, score) for the best glossary match, or (None, top_score).
        Tries the instant keyword fast-path first; falls back to embedding retrieval."""
        eid = keyword_hit(text)
        if eid and eid in glossary.BY_ID:
            return glossary.BY_ID[eid], 1.0
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
