"""Phase 6 live demo: session memory — follow-ups reuse the last ticker.

Turn 2 and 4 mention NO company; the agent carries the ticker from the previous turn.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vaani import config
from vaani.agent import memory, orchestrate

TURNS = [
    "GAIL ఈ రోజు ఎలా ఉంది?",       # -> GAIL.NS
    "దాని ట్రెండ్ ఎలా ఉంది?",       # no ticker -> carry GAIL.NS
    "మరి IOC ఎలా ఉంది?",           # switch -> IOC.NS
    "దాని 30 రోజుల ట్రెండ్ చెప్పు",  # no ticker -> carry IOC.NS
]


def main() -> int:
    if not config.have_llm():
        print("LLM not configured."); return 2
    session = memory.SessionMemory()
    for i, q in enumerate(TURNS, 1):
        a = orchestrate.handle(q, session=session)
        sym = a.display.get("symbol", "—")
        print(f"Turn {i}: {q}")
        print(f"   routing={a.routing}  resolved={sym}  intent={a.intent}")
        print(f"   A: {a.text[:120]}")
        print(f"   [session last_symbol now = {session.last_symbol()}]\n")
        time.sleep(4)   # gentle on free-tier quota
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
