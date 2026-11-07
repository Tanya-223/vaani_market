"""Phase 2 probe: verify the reasoning LLM (OpenAI-compatible) once .env is filled.

Checks two things the pipeline depends on:
  1. Natural spoken Telugu generation.
  2. Clean JSON output (the planner relies on this).
Prints latency + token usage. Run after adding LLM_BASE_URL/LLM_API_KEY/LLM_MODEL.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vaani import config
from vaani.llm import adapter


def main() -> int:
    if not config.have_llm():
        print("LLM not configured. Add to .env:")
        print("  LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/")
        print("  LLM_API_KEY=<your Gemini key>")
        print("  LLM_MODEL=gemini-3.8-flash")
        return 2

    print(f"Model: {config.LLM_MODEL}  base: {config.LLM_BASE_URL}\n")

    print("1) Telugu generation:")
    try:
        r = adapter.chat(
            [
                {"role": "system", "content": "You reply in natural, spoken Telugu. One short sentence."},
                {"role": "user", "content": "Greet a new user of a stock-market learning app."},
            ],
            max_tokens=80,
        )
        print(f"   {r.text}")
        print(f"   ({r.wall_seconds:.2f}s, usage={r.usage})")
    except adapter.LLMError as exc:
        print(f"   FAILED: {exc}")
        return 1

    print("\n2) JSON planner smoke test:")
    try:
        obj = adapter.chat_json(
            [
                {"role": "system", "content":
                    "Classify the market question. Return JSON only with keys "
                    "intent (one of: concept, price_check, why_moved, advice_request, out_of_scope), "
                    "tickers (array), confidence (0-1). Do not answer the question."},
                {"role": "user", "content": "GAIL ఈ రోజు ఎందుకు పడింది?"},
            ],
            max_tokens=120,
        )
        print(f"   {obj}")
    except adapter.LLMError as exc:
        print(f"   FAILED: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
