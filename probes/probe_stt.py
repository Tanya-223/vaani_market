"""Phase 1 probe: Prisma v3.0 STT, verified by loopback.

We reuse the Telugu clips made by probe_tts.py and send them back through STT.
This is self-contained (no human recording needed) and confirms:
  - STT accepts Timbre's WAV,
  - returns a Telugu transcript,
  - reports detected_language_code = te-IN (both with te-IN and with indic-auto),
  - reports processing_time (compared against our wall-clock time).

NOTE: this is a SYNTHETIC check of the plumbing, NOT a word-error-rate result.
Real WER needs human-recorded clips (eval harness, Phase 7).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vaani import config
from vaani.gnani import stt

OUT = Path(__file__).resolve().parent / "out"

MARKET_KEYTERMS = ["GAIL", "IOC", "HDFC", "GoldBEES", "Nifty", "Sensex", "షేర్", "మార్కెట్"]


def run(clip: str, language_code: str) -> None:
    path = OUT / clip
    if not path.exists():
        print(f"  (missing {clip} — run probe_tts.py first)")
        return
    try:
        r = stt.transcribe(path, language_code=language_code, keyterms=MARKET_KEYTERMS)
    except stt.STTError as exc:
        print(f"  ✗ {clip} [{language_code}] FAILED: {exc}")
        return
    net = r.wall_seconds - (r.processing_time or 0)
    print(f"  ✓ {clip} [{language_code}]")
    print(f"      transcript : {r.transcript}")
    print(f"      detected   : {r.detected_language_code}")
    print(f"      timing     : wall {r.wall_seconds:.2f}s | api processing {r.processing_time}s "
          f"| network ~{net:.2f}s")


def main() -> int:
    if not config.have_gnani():
        print("GNANI_API_KEY not set — stopping.")
        return 2
    print("Prisma v3.0 loopback (synthetic Telugu audio):\n")
    run("answer_shape.wav", "te-IN")
    run("answer_shape.wav", "indic-auto")
    run("ticker_gail.wav", "te-IN")
    run("ticker_ioc.wav", "indic-auto")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
