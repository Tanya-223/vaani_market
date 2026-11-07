"""Phase 2 live demo: full text -> grounded Telugu answer (what-happened-today flow).

Runs the orchestrator on real questions, showing the spoken Telugu answer, whether the
numeric provenance gate passed, and the key grounded numbers. Synthesizes one answer to
audio to prove voice-out end to end.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vaani import config
from vaani.agent import orchestrate
from vaani.gnani import tts

OUT = Path(__file__).resolve().parent / "out"

CASES = [
    ("price_check", "HDFC బ్యాంక్ షేర్ ఈ రోజు ఎంత ఉంది?"),
    ("why_moved",   "GAIL షేర్ ఈ రోజు ఎందుకు పడింది?"),
    ("trend",       "IOC షేర్ ఈ నెలలో ఎలా ఉంది?"),
    ("etf/gold",    "GoldBEES ఈ రోజు ఎంత మారింది?"),
    ("overview",    "Nifty ఈ రోజు ఎలా ఉంది?"),
]


def main() -> int:
    if not config.have_llm():
        print("LLM not configured — add Gemini creds to .env.")
        return 2

    synth_text = None
    for label, q in CASES:
        print(f"\n=== {label}: {q}")
        a = orchestrate.handle(q)
        d = a.display
        print(f"  routing={a.routing}  gate_ok={a.gate_ok}  template={a.used_template}")
        if d:
            delay = d.get("delayed_by_seconds")
            print(f"  data: {d.get('name_en')} price={d.get('price')} {d.get('currency')} "
                  f"chg={d.get('change_pct')}%  as_of={d.get('as_of')}  delay={delay}s")
            if "series" in d:
                s = d["series"]
                print(f"  30d: return={s['return_pct']}%  high={s['high']} low={s['low']} "
                      f"vol_vs_avg={s['volume_vs_avg_pct']}%")
            if "gold" in d:
                print(f"  gold support: {d['gold']}")
            if "headlines" in d:
                print(f"  headlines: {len(d['headlines'])} found")
        print(f"  ANSWER (te): {a.text}")
        print(f"  disclaimer : {a.disclaimer}")
        if label == "why_moved" and a.routing == "answer":
            synth_text = a.text

    # Prove voice-out on one answer.
    if synth_text:
        try:
            res = tts.synthesize(synth_text, language="te-IN", voice="Kalpana")
            (OUT / "answer_gail.wav").write_bytes(res.audio)
            print(f"\nSynthesized GAIL answer -> {OUT/'answer_gail.wav'} "
                  f"({len(res.audio)} bytes, {res.wall_seconds:.2f}s)")
        except tts.TTSError as exc:
            print(f"\nTTS failed: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
