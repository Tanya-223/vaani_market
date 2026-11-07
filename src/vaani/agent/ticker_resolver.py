"""Ticker resolver: spoken name -> canonical exchange symbol.

The hardest component (report 6.2 / 12.3). Indian names are spoken with heavy
code-mixing and several share a prefix (HDFC Bank / Life / AMC). Strategy:
  1. Alias table (Latin + Telugu-script variants) for exact hits.
  2. Ambiguous-prefix guard: a bare "HDFC" must ask which one, never guess.
  3. Fuzzy (difflib) + a light phonetic key for Latin transcription errors.
When the top candidates are too close, we return AMBIGUOUS so the agent asks a
clarifying question instead of guessing.

No network, no LLM — pure code, fully unit-testable.
"""
from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field

# --- thresholds (tunable) ---
MIN_SCORE = 0.60       # below this -> no match
RESOLVE_MIN = 0.72     # a candidate must beat this to count as "strong"
GAP = 0.12             # if 2+ strong candidates within this gap -> ambiguous

# Filler/market words stripped before matching (acts as light query rewriting).
STOP = {
    # English
    "share", "shares", "stock", "stocks", "price", "the", "a", "of", "what", "is",
    "how", "today", "now", "much",
    # Telugu
    "షేర్", "ధర", "ఎంత", "ఎలా", "ఉంది", "ఈ", "రోజు", "ఈరోజు", "ఇవాళ", "అంటే", "ఏమిటి",
    "ఎందుకు", "మార్కెట్",
}


@dataclass
class Instrument:
    symbol: str
    name_en: str
    name_te: str
    kind: str                 # stock | etf | index
    aliases: list[str] = field(default_factory=list)


INSTRUMENTS: list[Instrument] = [
    Instrument("HDFCBANK.NS", "HDFC Bank", "హెచ్‌డిఎఫ్‌సి బ్యాంక్", "stock",
               ["hdfc bank", "hdfcbank", "hdfc bank ltd", "హెచ్‌డిఎఫ్‌సి బ్యాంక్", "హెచ్‌డిఎఫ్‌సి బ్యాంకు"]),
    Instrument("HDFCLIFE.NS", "HDFC Life", "హెచ్‌డిఎఫ్‌సి లైఫ్", "stock",
               ["hdfc life", "hdfclife", "hdfc life insurance", "హెచ్‌డిఎఫ్‌సి లైఫ్"]),
    Instrument("HDFCAMC.NS", "HDFC AMC", "హెచ్‌డిఎఫ్‌సి ఎఎంసి", "stock",
               ["hdfc amc", "hdfcamc", "hdfc asset management", "hdfc mutual fund", "హెచ్‌డిఎఫ్‌సి ఎఎంసి"]),
    Instrument("GAIL.NS", "GAIL", "గెయిల్", "stock",
               ["gail", "gail india", "గెయిల్", "గేల్", "గేయిల్"]),
    Instrument("IOC.NS", "Indian Oil (IOC)", "ఇండియన్ ఆయిల్", "stock",
               ["ioc", "indian oil", "indianoil", "indian oil corporation", "ఐఓసి", "ఇండియన్ ఆయిల్"]),
    Instrument("GOLDBEES.NS", "GoldBEES", "గోల్డ్ బీస్", "etf",
               ["goldbees", "gold bees", "gold bees etf", "gold etf", "గోల్డ్ బీస్", "గోల్డ్‌బీస్"]),
    Instrument("^NSEI", "Nifty 50", "నిఫ్టీ 50", "index",
               ["nifty", "nifty 50", "nifty fifty", "నిఫ్టీ", "నిఫ్టీ 50", "నిఫ్టి"]),
    Instrument("^BSESN", "Sensex", "సెన్సెక్స్", "index",
               ["sensex", "bse sensex", "సెన్సెక్స్"]),
]

# Shared prefixes that are ambiguous on their own. Present -> only resolve if a
# distinguishing word pins exactly one family member; otherwise ask.
AMBIGUOUS_PREFIXES: dict[str, list[str]] = {
    "hdfc": ["HDFCBANK.NS", "HDFCLIFE.NS", "HDFCAMC.NS"],
    "హెచ్‌డిఎఫ్‌సి": ["HDFCBANK.NS", "HDFCLIFE.NS", "HDFCAMC.NS"],
}

# Words that pin one HDFC member (substring-matched against the normalized query).
DISTINGUISHERS: dict[str, list[str]] = {
    "HDFCBANK.NS": ["bank", "బ్యాంక్", "బ్యాంకు"],
    "HDFCLIFE.NS": ["life", "insurance", "లైఫ్"],
    "HDFCAMC.NS": ["amc", "asset", "mutual", "ఎఎంసి", "ఎఎమ్‌సి"],
}

_BY_SYMBOL = {i.symbol: i for i in INSTRUMENTS}


@dataclass
class Candidate:
    symbol: str
    name_en: str
    name_te: str
    score: float


@dataclass
class Resolution:
    status: str                      # "resolved" | "ambiguous" | "none"
    candidates: list[Candidate] = field(default_factory=list)

    @property
    def symbol(self) -> str | None:
        return self.candidates[0].symbol if (self.status == "resolved" and self.candidates) else None


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[?.!,;:₹%\"'()]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _content_tokens(norm: str) -> list[str]:
    return [t for t in norm.split() if t not in STOP]


def _phonetic(s: str) -> str:
    """Consonant-skeleton of the Latin part only (helps gail/gale/gayil)."""
    s = re.sub(r"[^a-z]", "", s.lower())
    if not s:
        return ""
    s = s.replace("ph", "f").replace("ck", "k")
    out = [s[0]]
    for ch in s[1:]:
        if ch in "aeiou":
            continue
        if ch == out[-1]:
            continue
        out.append(ch)
    return "".join(out)


def _alias_score(query: str, alias: str) -> float:
    if query == alias:
        return 1.0
    r = difflib.SequenceMatcher(None, query, alias).ratio()
    qp, ap = _phonetic(query), _phonetic(alias)
    if qp and qp == ap:
        r = max(r, 0.88)
    return r


def _best_score(query: str, inst: Instrument) -> float:
    pool = inst.aliases + [inst.name_en.lower(), inst.name_te]
    return max(_alias_score(query, normalize(a)) for a in pool)


def resolve(text: str, language: str = "te-IN") -> Resolution:
    norm = normalize(text)
    content = _content_tokens(norm)
    query = " ".join(content) if content else norm

    # 1. Ambiguous-prefix guard (HDFC family). If the prefix is present, resolve
    #    ONLY when a distinguishing word pins exactly one member; else ask.
    prefix = _find_prefix(norm)
    if prefix:
        members = AMBIGUOUS_PREFIXES[prefix]
        matched = [sym for sym in members if _has_distinguisher(norm, sym)]
        if len(matched) == 1:
            return Resolution("resolved", [_cand(matched[0], 0.95)])
        return Resolution("ambiguous", [_cand(sym, 1.0) for sym in members])

    # 2. Score every (non-prefix) instrument.
    scored = sorted(
        ((inst, _best_score(query, inst)) for inst in INSTRUMENTS),
        key=lambda p: p[1],
        reverse=True,
    )
    top_inst, top_score = scored[0]
    if top_score < MIN_SCORE:
        return Resolution("none", [])

    strong = [(i, s) for i, s in scored if s >= RESOLVE_MIN and s >= top_score - GAP]
    if len({i.symbol for i, _ in strong}) >= 2:
        return Resolution("ambiguous", [_cand(i.symbol, s) for i, s in strong])

    return Resolution("resolved", [_cand(top_inst.symbol, top_score)])


def _find_prefix(norm: str) -> str | None:
    for p in AMBIGUOUS_PREFIXES:
        if p in norm.split() or p in norm:
            return p
    return None


def _has_distinguisher(norm: str, symbol: str) -> bool:
    return any(w in norm for w in DISTINGUISHERS.get(symbol, []))


def _cand(symbol: str, score: float) -> Candidate:
    i = _BY_SYMBOL[symbol]
    return Candidate(i.symbol, i.name_en, i.name_te, round(score, 3))


# Telugu clarifying question (DRAFT — needs native-speaker review).
def clarifying_question_te(res: Resolution) -> str:
    names = " లేదా ".join(c.name_te for c in res.candidates)
    return f"మీరు {names} గురించి అడుగుతున్నారా?"  # "Are you asking about X or Y?"


def keyterms() -> list[str]:
    """Names to bias Prisma STT (keyterms). Capped at 200 upstream."""
    terms: list[str] = []
    for i in INSTRUMENTS:
        terms.extend([i.name_en, i.name_te, *i.aliases])
    # de-dup, preserve order
    seen: set[str] = set()
    out: list[str] = []
    for t in terms:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out
