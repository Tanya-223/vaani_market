"""FactSheet: the single grounded payload for one answer.

Code fetches and computes every number; the explainer may ONLY quote from here, and
the numeric gate checks the drafted answer against `allowed_numbers()`. Retrieved
text and headlines are DATA, never instructions.

GoldBEES is a gold ETF, not a company: no P/E or earnings are ever fetched; gold
(GC=F) and USD/INR (INR=X) are attached as supporting context instead.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..data import market
from . import ticker_resolver

GOLD_SYMBOL = "GOLDBEES.NS"


@dataclass
class FactSheet:
    symbol: str
    name_en: str
    name_te: str
    kind: str
    intent: str
    quote: market.Quote
    series: market.Series | None = None
    news: list[market.Headline] = field(default_factory=list)
    gold: dict | None = None            # for GoldBEES only
    as_of: str | None = None

    # ---- the two things the rest of the pipeline consumes ----
    def to_prompt_block(self) -> str:
        q = self.quote
        lines = [
            f'name: {self.name_en} ({self.name_te})',
            f'kind: {self.kind}',
            f'as of: {self.as_of or q.as_of} (source: {q.source})',
        ]
        if q.price is not None:
            lines.append(f'latest price: {q.price} {q.currency or ""}'.strip())
        if q.previous_close is not None:
            lines.append(f'previous close: {q.previous_close}')
        if q.change_pct is not None:
            lines.append(f'change from previous close (percent): {q.change_pct}')
        s = self.series
        if s and s.ok:
            if s.volume_vs_avg_pct is not None:
                lines.append(f'volume vs {s.days}-day average (percent): {s.volume_vs_avg_pct}')
            if s.period_return_pct is not None:
                lines.append(f'return over {s.days} days (percent): {s.period_return_pct}')
            if s.high is not None and s.low is not None:
                lines.append(f'{s.days}-day high: {s.high}; {s.days}-day low: {s.low}')
        if self.gold:
            lines.append(f'gold price (USD per ounce): {self.gold.get("gold_usd")}')
            lines.append(f'USD to INR rate: {self.gold.get("usd_inr")}')
        if self.news:
            lines.append("headlines:")
            for h in self.news:
                when = (h.published_at or "")[:10]
                lines.append(f'  - "{h.title}" ({h.publisher}, {when})')
        else:
            lines.append("headlines: none available")
        return "<FACTS>\n" + "\n".join(lines) + "\n</FACTS>"

    def allowed_numbers(self) -> set[float]:
        vals: set[float] = {float(self.series.days)} if (self.series and self.series.ok) else {30.0}
        q = self.quote
        for v in (q.price, q.previous_close, q.change_pct, q.volume):
            _add(vals, v)
        s = self.series
        if s and s.ok:
            for v in (s.avg_volume, s.latest_volume, s.volume_vs_avg_pct,
                      s.period_return_pct, s.high, s.low):
                _add(vals, v)
        if self.gold:
            _add(vals, self.gold.get("gold_usd"))
            _add(vals, self.gold.get("usd_inr"))
        # date components of as_of (so a spoken date isn't flagged as an orphan)
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})", self.as_of or q.as_of or "")
        if m:
            for part in m.groups():
                _add(vals, int(part))
                _add(vals, int(part.lstrip("0") or "0"))
        # numbers that are part of the instrument name itself (e.g. "Nifty 50")
        for tok in re.findall(r"\d+(?:\.\d+)?", f"{self.name_en} {self.name_te}"):
            _add(vals, float(tok))
        return vals

    @property
    def has_cause_evidence(self) -> bool:
        return bool(self.news)


def _add(s: set[float], v) -> None:
    if v is None:
        return
    try:
        f = round(float(v), 2)
    except (TypeError, ValueError):
        return
    s.add(f)
    s.add(abs(f))


def build(symbol: str, intent: str, language: str = "te-IN") -> FactSheet | None:
    """Assemble the FactSheet for a resolved symbol. Returns None if there's no data."""
    inst = ticker_resolver._BY_SYMBOL.get(symbol)
    name_en = inst.name_en if inst else symbol
    name_te = inst.name_te if inst else symbol
    kind = inst.kind if inst else "stock"

    quote = market.fetch_quote(symbol)
    if not quote.ok:
        return None

    series = None
    if intent in ("why_moved", "trend"):
        series = market.fetch_series(symbol, days=30)

    news: list[market.Headline] = []
    if intent == "why_moved":
        news = market.fetch_news(symbol, limit=4)

    gold = None
    if symbol == GOLD_SYMBOL:
        g = market.fetch_quote("GC=F")
        fx = market.fetch_quote("INR=X")
        gold = {
            "gold_usd": g.price if g.ok else None,
            "usd_inr": fx.price if fx.ok else None,
        }

    return FactSheet(
        symbol=symbol, name_en=name_en, name_te=name_te, kind=kind, intent=intent,
        quote=quote, series=series, news=news, gold=gold, as_of=quote.as_of,
    )
