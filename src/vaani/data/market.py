"""Market data tool (Yahoo Finance via yfinance).

Every quote is a PAYLOAD: value + unit + source + as-of timestamp + delay flag.
Numbers are computed here in code, never by the model. Yahoo data is delayed and
unofficial; we surface that rather than hide it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import yfinance as yf


@dataclass
class Quote:
    symbol: str
    ok: bool
    price: float | None = None
    currency: str | None = None
    previous_close: float | None = None
    change_pct: float | None = None
    volume: int | None = None
    avg_volume_10d: int | None = None
    as_of: str | None = None          # ISO8601 of the latest data point
    market_state: str | None = None
    delayed_by_seconds: int | None = None   # None = unknown
    source: str = "Yahoo Finance (delayed, unofficial)"
    note: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


def fetch_quote(symbol: str) -> Quote:
    """Fetch a single quote. Raises nothing for a 'missing' symbol — returns
    ok=False so the agent can say 'no data' honestly."""
    t = yf.Ticker(symbol)

    price = prev = vol = avg10 = None
    currency = state = None
    delay = None
    as_of = None
    note = ""

    # fast_info is the cheap, reliable path.
    try:
        fi = t.fast_info
        price = _f(fi.get("last_price"))
        prev = _f(fi.get("previous_close"))
        vol = _i(fi.get("last_volume"))
        avg10 = _i(fi.get("ten_day_average_volume"))
        currency = fi.get("currency")
    except Exception as exc:
        note = f"fast_info failed: {exc}; "

    # Latest timestamp + a fallback price from recent history.
    try:
        hist = t.history(period="5d", interval="1d")
        if not hist.empty:
            last_ts = hist.index[-1].to_pydatetime()
            as_of = last_ts.astimezone(timezone.utc).isoformat()
            if price is None:
                price = _f(hist["Close"].iloc[-1])
            if prev is None and len(hist) >= 2:
                prev = _f(hist["Close"].iloc[-2])
            if vol is None:
                vol = _i(hist["Volume"].iloc[-1])
    except Exception as exc:
        note += f"history failed: {exc}; "

    # Delay + market state live in .get_info(), which is heavier and flakier.
    try:
        info = t.get_info()
        delay = info.get("exchangeDataDelayedBy")
        state = info.get("marketState")
        if currency is None:
            currency = info.get("currency")
    except Exception:
        pass  # non-fatal; delay stays unknown

    ok = price is not None
    change_pct = None
    if price is not None and prev not in (None, 0):
        change_pct = round((price - prev) / prev * 100, 2)

    return Quote(
        symbol=symbol, ok=ok, price=price, currency=currency,
        previous_close=prev, change_pct=change_pct, volume=vol,
        avg_volume_10d=avg10, as_of=as_of, market_state=state,
        delayed_by_seconds=delay, note=note.strip(),
    )


def _f(x):
    try:
        return None if x is None else round(float(x), 2)
    except Exception:
        return None


def _i(x):
    try:
        return None if x is None else int(x)
    except Exception:
        return None


@dataclass
class Series:
    symbol: str
    ok: bool
    days: int = 30
    closes: list[float] = field(default_factory=list)
    start_date: str | None = None
    end_date: str | None = None
    period_return_pct: float | None = None
    high: float | None = None
    low: float | None = None
    latest_volume: int | None = None
    avg_volume: int | None = None
    volume_vs_avg_pct: float | None = None
    source: str = "Yahoo Finance (delayed, unofficial)"


def fetch_series(symbol: str, days: int = 30) -> Series:
    """Trailing `days` daily closes + returns + volume-vs-average, all computed here."""
    t = yf.Ticker(symbol)
    try:
        hist = t.history(period=f"{days + 12}d", interval="1d")
    except Exception:
        return Series(symbol, ok=False, days=days)
    if hist is None or hist.empty:
        return Series(symbol, ok=False, days=days)

    hist = hist.tail(days)
    closes = [round(float(c), 2) for c in hist["Close"].tolist() if c == c]
    vols = [int(v) for v in hist["Volume"].tolist() if v == v]
    if not closes:
        return Series(symbol, ok=False, days=days)

    ret = round((closes[-1] - closes[0]) / closes[0] * 100, 2) if closes[0] else None
    latest_vol = vols[-1] if vols else None
    avg_vol = int(sum(vols) / len(vols)) if vols else None
    vol_vs = round((latest_vol - avg_vol) / avg_vol * 100, 2) if (latest_vol and avg_vol) else None

    return Series(
        symbol=symbol, ok=True, days=len(closes), closes=closes,
        start_date=hist.index[0].astimezone(timezone.utc).isoformat(),
        end_date=hist.index[-1].astimezone(timezone.utc).isoformat(),
        period_return_pct=ret,
        high=round(float(hist["High"].max()), 2),
        low=round(float(hist["Low"].min()), 2),
        latest_volume=latest_vol, avg_volume=avg_vol, volume_vs_avg_pct=vol_vs,
    )


@dataclass
class Headline:
    title: str
    publisher: str
    published_at: str | None
    link: str | None = None


def fetch_news(symbol: str, limit: int = 5) -> list[Headline]:
    """Recent headlines with timestamps. yfinance's schema varies, so we read both
    the old flat shape and the new nested 'content' shape. Empty list is a valid,
    honest result (the explainer then says the cause is unconfirmed)."""
    try:
        raw = yf.Ticker(symbol).news or []
    except Exception:
        return []

    out: list[Headline] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        c = item.get("content")
        if isinstance(c, dict):  # new nested schema
            title = c.get("title")
            pub = ((c.get("provider") or {}) or {}).get("displayName", "")
            published = c.get("pubDate") or c.get("displayTime")
            link = ((c.get("canonicalUrl") or {}) or {}).get("url")
        else:                     # old flat schema
            title = item.get("title")
            pub = item.get("publisher", "")
            epoch = item.get("providerPublishTime")
            published = (
                datetime.fromtimestamp(epoch, timezone.utc).isoformat() if epoch else None
            )
            link = item.get("link")
        if title:
            out.append(Headline(title.strip(), pub or "", published, link))
        if len(out) >= limit:
            break
    return out
