"""Three memory tiers (report 4.4).

  Working    — current turn only (transcript, plan, payloads). Lives in the orchestrator
               call; nothing to persist.
  Session    — last 5 turns (resolved ticker, language, intent). Enables follow-ups like
               "దాని ట్రెండ్?" ("its trend?") without repeating the company.
  Long-term  — preferred language, preferred voice, watchlist ONLY. User-controlled, persisted.

HARD PRIVACY RULE: we never store holdings, orders, PAN, Aadhaar, or any inferred financial
profile. `LongTermMemory` has no field for them, and a test asserts it.
"""
from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

# Fields that must NEVER exist on any memory object (asserted by tests).
FORBIDDEN = {"holdings", "portfolio", "orders", "order_history", "pan", "aadhaar",
             "income", "net_worth", "networth", "financial_profile", "profile"}

DATA_INTENTS = {"price_check", "why_moved", "trend", "market_overview"}


@dataclass
class Turn:
    text: str
    intent: str
    symbol: str | None
    language: str


class SessionMemory:
    """Rolling window of the last N turns (default 5)."""
    def __init__(self, maxlen: int = 5) -> None:
        self.turns: deque[Turn] = deque(maxlen=maxlen)

    def record(self, text: str, intent: str, symbol: str | None, language: str) -> None:
        self.turns.append(Turn(text, intent, symbol, language))

    def last_symbol(self) -> str | None:
        for t in reversed(self.turns):
            if t.symbol:
                return t.symbol
        return None

    def last_language(self) -> str | None:
        return self.turns[-1].language if self.turns else None

    def as_list(self) -> list[Turn]:
        return list(self.turns)


@dataclass
class LongTermMemory:
    """User-controlled preferences. Deliberately NO financial-position fields."""
    preferred_language: str = "te-IN"
    preferred_voice: str = "Kalpana"
    watchlist: list[str] = field(default_factory=list)
    _path: Path | None = None

    @classmethod
    def load(cls, path: str | Path) -> "LongTermMemory":
        p = Path(path)
        if p.is_file():
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                return cls(
                    preferred_language=d.get("preferred_language", "te-IN"),
                    preferred_voice=d.get("preferred_voice", "Kalpana"),
                    watchlist=list(d.get("watchlist", [])),
                    _path=p,
                )
            except (ValueError, OSError):
                pass
        return cls(_path=p)

    def save(self) -> None:
        if not self._path:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps({
            "preferred_language": self.preferred_language,
            "preferred_voice": self.preferred_voice,
            "watchlist": self.watchlist,
        }, ensure_ascii=False, indent=2), encoding="utf-8")

    def add_watch(self, symbol: str) -> None:
        if symbol and symbol not in self.watchlist:
            self.watchlist.append(symbol)
            self.save()

    def remove_watch(self, symbol: str) -> None:
        if symbol in self.watchlist:
            self.watchlist.remove(symbol)
            self.save()
