"""Phase 3 live demo: Tier-1 glossary retrieval for beginner concept questions.

Shows the top matched glossary entry + cosine score for each question (including a
paraphrase that doesn't lexically match), then the full routed answer.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vaani import config
from vaani.agent import orchestrate
from vaani.retrieval import tier1

CASES = [
    "స్టాక్ అంటే ఏమిటి?",
    "షేర్ మార్కెట్ అంటే ఏమిటి?",
    "NSE, BSE మధ్య తేడా ఏమిటి?",
    "క్యాండిల్ చార్ట్ అంటే ఏమిటి? ఎలా చదవాలి?",
    "P/E రేషియో అంటే ఏమిటి?",
    "కంపెనీ మొత్తం విలువ ఎలా లెక్కిస్తారు?",   # paraphrase -> should hit market_cap
    "డివిడెండ్ అంటే ఏంటి?",
]


def main() -> int:
    if not config.have_llm():
        print("LLM not configured — add Gemini creds to .env.")
        return 2

    print("Top-3 retrieval per question:\n")
    for q in CASES:
        hits = tier1.query(q, k=3)
        tops = ", ".join(f"{h.entry.id}={h.score:.3f}" for h in hits)
        print(f"Q: {q}\n   {tops}")

    print("\nFull routed answers:\n")
    for q in CASES[:5]:
        a = orchestrate.handle(q)
        vis = a.display.get("visual")
        print(f"Q: {q}")
        print(f"   routing={a.routing} concept={a.display.get('concept')} "
              f"score={a.display.get('retrieval_score')} visual={vis} reviewed={a.display.get('reviewed')}")
        print(f"   A: {a.text[:160]}{'…' if len(a.text) > 160 else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
