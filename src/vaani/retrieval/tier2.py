"""Tier-2 retrieval: hybrid (BM25 + dense) fused with Reciprocal Rank Fusion, with metadata
filtering and query rewriting, over the company-notes corpus (+ optional live news).

Why hybrid for Indian tickers (report 7.2): names like "GAIL"/"IOC"/"HDFC" are exact-token
problems that dense embeddings blur; BM25 catches the exact match while dense catches the
Telugu paraphrase. RRF fuses the two rank lists (ignoring incomparable raw scores).

The cross-encoder RERANKER is intentionally NOT built (first item in the report's cut order);
RRF fusion is the ranker. Retrieved text is DATA, surfaced to the explainer inside a
delimited block — never instructions, and it carries no gate-relevant numbers.
"""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass

from rank_bm25 import BM25Okapi

from ..agent import ticker_resolver
from ..llm import adapter
from . import corpus
from .tier1 import cosine

_FILLER = {"the", "is", "a", "of", "what", "how", "today", "why", "ఈ", "రోజు", "ఈరోజు",
           "ఎలా", "ఉంది", "ఎందుకు", "షేర్", "ధర", "అంటే", "ఏమిటి", "గురించి", "చెప్పు"}


def _tok(s: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", s.lower()) if t not in _FILLER]


def _rewrite(text: str) -> tuple[str, str | None]:
    """Expand the query: strip filler, append the resolved ticker's name + aliases."""
    res = ticker_resolver.resolve(text)
    symbol = res.symbol if res.status == "resolved" else None
    extra = ""
    if symbol:
        inst = ticker_resolver._BY_SYMBOL[symbol]
        extra = " " + " ".join([inst.name_en, *inst.aliases])
    return (text + extra).strip(), symbol


def _rrf(rankings: list[list[str]], k0: int = 60) -> list[str]:
    scores: dict[str, float] = defaultdict(float)
    for ranking in rankings:
        for rank, did in enumerate(ranking):
            scores[did] += 1.0 / (k0 + rank + 1)
    return sorted(scores, key=lambda d: scores[d], reverse=True)


@dataclass
class Hit:
    doc: corpus.Doc
    rrf_rank: int


class Tier2Index:
    def __init__(self) -> None:
        self._docs: list[corpus.Doc] = list(corpus.NOTES)
        self._vectors: list[list[float]] | None = None
        self._bm25: BM25Okapi | None = None

    def build(self) -> None:
        if self._vectors is not None:
            return
        self._vectors = adapter.embed([d.text for d in self._docs])
        self._bm25 = BM25Okapi([_tok(d.text) for d in self._docs])

    def query(self, text: str, k: int = 5) -> list[Hit]:
        self.build()
        qrw, symbol = _rewrite(text)

        # dense ranking
        qv = adapter.embed([qrw])[0]
        dense = sorted(range(len(self._docs)),
                       key=lambda i: cosine(qv, self._vectors[i]), reverse=True)
        # sparse ranking
        bm = self._bm25.get_scores(_tok(qrw))  # type: ignore[union-attr]
        sparse = sorted(range(len(self._docs)), key=lambda i: bm[i], reverse=True)

        ids = [self._docs[i].id for i in dense], [self._docs[i].id for i in sparse]
        fused = _rrf([ids[0], ids[1]])

        # metadata filter: if we know the ticker, keep only its docs (+ index context).
        if symbol:
            fused = [d for d in fused
                     if corpus.BY_ID[d].ticker == symbol or corpus.BY_ID[d].sector == "index"] \
                     or fused
        return [Hit(corpus.BY_ID[d], r + 1) for r, d in enumerate(fused[:k])]

    def note_for(self, symbol: str) -> str | None:
        """The background note for a resolved ticker (used to enrich why-moved answers)."""
        for d in self._docs:
            if d.ticker == symbol and d.doc_type in ("company_note", "etf_note"):
                return d.text
        return None


_INDEX = Tier2Index()


def query(text: str, k: int = 5) -> list[Hit]:
    return _INDEX.query(text, k)


def note_for(symbol: str) -> str | None:
    return _INDEX.note_for(symbol)
