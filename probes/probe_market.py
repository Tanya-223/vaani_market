"""Phase 1 probe: verify every test symbol live on Yahoo Finance.

This is the GATE from the build plan: prove we can fetch a real quote with a
timestamp, record the delay, and confirm each symbol resolves. Tata Motors is
expected to be the 'changed/missing ticker' test, not a demo instrument.
"""
from __future__ import annotations

import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vaani.data import market

SYMBOLS = [
    ("HDFCBANK.NS", "HDFC Bank"),
    ("HDFCLIFE.NS", "HDFC Life"),
    ("HDFCAMC.NS", "HDFC AMC"),
    ("GAIL.NS", "GAIL"),
    ("IOC.NS", "Indian Oil (IOC)"),
    ("GOLDBEES.NS", "GoldBEES (gold ETF)"),
    ("^NSEI", "Nifty 50"),
    ("^BSESN", "Sensex"),
    ("GC=F", "Gold futures (USD/oz) — GoldBEES support"),
    ("INR=X", "USD/INR — GoldBEES support"),
    ("TATAMOTORS.NS", "Tata Motors (changed-ticker test)"),
]


def main() -> int:
    now = datetime.now(timezone.utc)
    print(f"Now (UTC): {now.isoformat()}\n")
    ok = 0
    for sym, name in SYMBOLS:
        try:
            q = market.fetch_quote(sym)
        except Exception as exc:
            print(f"✗ {sym:14} {name}\n    ERROR: {exc}")
            continue
        if not q.ok:
            print(f"✗ {sym:14} {name}  -> NO DATA  {q.note}")
            continue
        ok += 1
        age = ""
        if q.as_of:
            dt = datetime.fromisoformat(q.as_of)
            age = f"  (as-of age ~{(now - dt).total_seconds()/3600:.1f}h)"
        delay = f"{q.delayed_by_seconds}s" if q.delayed_by_seconds is not None else "unknown"
        print(f"✓ {sym:14} {name}")
        print(f"    price={q.price} {q.currency}  prev={q.previous_close}  "
              f"chg={q.change_pct}%  vol={q.volume}  avg10={q.avg_volume_10d}")
        print(f"    as_of={q.as_of}{age}  market={q.market_state}  delay={delay}")
        time.sleep(0.4)  # be gentle with Yahoo to avoid 429
    print(f"\n{ok}/{len(SYMBOLS)} symbols returned data.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
