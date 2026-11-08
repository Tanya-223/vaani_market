"""Phase 3 (Tier-2) live demo: hybrid BM25+dense+RRF retrieval over company notes.

Shows the fused ranking for each query (keyword + semantic), including a Telugu query that
has no lexical overlap with the English note.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vaani import config
from vaani.retrieval import tier2

QUERIES = [
    "GAIL ఈ రోజు ఎందుకు పడింది?",
    "IOC refining margin",
    "GoldBEES దేనిని అనుసరిస్తుంది?",
    "HDFC బ్యాంక్ ఏం చేస్తుంది?",
]


def main() -> int:
    if not config.have_llm():
        print("LLM not configured."); return 2
    for q in QUERIES:
        hits = tier2.query(q, k=3)
        print(f"Q: {q}")
        for h in hits:
            print(f"   {h.rrf_rank}. {h.doc.id}  [{h.doc.ticker} · {h.doc.sector}]")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
