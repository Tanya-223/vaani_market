"""Phase 1 probe: Telugu TTS listening test (Timbre v3.0).

Generates several short Telugu clips that stress exactly the things the docs flag
as uncertain: a rupee amount with paise, lakh/crore grouping, a percentage (as
'%' and as 'శాతం'), and the ticker-style names GAIL and IOC. The USER must listen
to probes/out/*.wav and report how numbers and tickers are pronounced; number-to-
words conversion is added ONLY if this test shows it is needed.
"""
from __future__ import annotations

import sys
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vaani import config
from vaani.gnani import tts

OUT = Path(__file__).resolve().parent / "out"

# (id, description of what it tests, Telugu text)
CLIPS = [
    ("rupee_paise", "rupee amount with paise + thousands grouping",
     "ఈ షేర్ ధర ₹2,345.67 ఉంది."),
    ("lakh_crore", "lakh/crore grouping for market cap",
     "ఈ కంపెనీ మార్కెట్ క్యాప్ ₹1,23,456 కోట్లు."),
    ("percent_both", "percentage as % symbol and as the word శాతం",
     "ఈ రోజు షేర్ 3.2% పెరిగింది, వాల్యూమ్ 12 శాతం ఎక్కువ."),
    ("ticker_gail", "the name GAIL in a Telugu sentence",
     "GAIL షేర్ ఈ రోజు ఎలా ఉంది?"),
    ("ticker_ioc", "the name IOC in a Telugu sentence",
     "IOC షేర్ ధర ఎంత ఉంది?"),
    ("answer_shape", "a realistic 'what happened today' answer sentence",
     "GAIL షేర్ ధర ₹185.40, ఈ రోజు 2.3% పెరిగింది."),
]


def wav_duration(path: Path) -> str:
    try:
        with wave.open(str(path), "rb") as w:
            frames, rate, ch, width = w.getnframes(), w.getframerate(), w.getnchannels(), w.getsampwidth()
        return f"{frames / rate:.2f}s @ {rate}Hz, {ch}ch, {width*8}-bit"
    except Exception as exc:  # not a parseable wav
        return f"(not a standard wav: {exc})"


def main() -> int:
    if not config.have_gnani():
        print("GNANI_API_KEY not set — stopping.")
        return 2
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"Voice=Kalpana  model=timbre-v3.0  language=te-IN\n")

    ok = 0
    for cid, desc, text in CLIPS:
        try:
            res = tts.synthesize(text, language="te-IN", voice="Kalpana")
        except tts.TTSError as exc:
            print(f"✗ {cid:14} FAILED  {exc}")
            continue
        path = OUT / f"{cid}.wav"
        path.write_bytes(res.audio)
        ok += 1
        print(f"✓ {cid:14} {len(res.audio):>7} bytes  {res.content_type}  "
              f"{res.wall_seconds:.2f}s wall  {wav_duration(path)}")
        print(f"               tests: {desc}")
        print(f"               text : {text}")
    print(f"\n{ok}/{len(CLIPS)} clips written to {OUT}")
    print("ACTION: listen to each .wav and report how the rupee amount, the percentage,")
    print("and GAIL / IOC are pronounced in Telugu.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
