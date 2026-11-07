"""Planner: ONE constrained LLM call that classifies and plans — it never answers.

The LLM returns JSON; all safety-critical decisions are made by deterministic code
here (not trusted to the model):
  - advice_request  -> always route to the refusal node (regardless of confidence)
  - out_of_scope    -> clean decline
  - confidence < 0.5 -> clarifying question, never a guess
  - the proposed plan is filtered to the tool allowlist

`validate()` is pure and unit-tested without the network. `plan()` calls the LLM.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..llm import adapter
from . import tools

ALLOWED_INTENTS = {
    "concept", "price_check", "why_moved", "trend", "market_overview",
    "advice_request", "out_of_scope",
}

LOW_CONFIDENCE = 0.5  # below this -> clarify (except advice, which always refuses)

# Actions the orchestrator will dispatch on.
# answer | refuse | decline | clarify
SYSTEM_PROMPT = f"""You are the PLANNER for a voice assistant that EXPLAINS the Indian stock
market and NEVER advises. You ONLY classify and plan. You MUST NOT answer the question,
give any opinion, or say whether to buy/sell/hold. Return a single JSON object, nothing else.

JSON schema:
  intent: one of {sorted(ALLOWED_INTENTS)}
  tickers: array of company/index names as spoken (free text, may be empty)
  language_in: BCP-47 code of the question (e.g. te-IN, en-IN)
  language_out: same as language_in unless the user asked for another
  plan: ordered tool names, ONLY from {list(tools.ALLOWLIST)}
  needs_live_data: boolean
  confidence: number 0..1

Intent rules:
  - ANY request for a recommendation or opinion — "should I buy", "is it a good time",
    "will it go up/down", a prediction of a future price, or a roleplay like "pretend you
    are my broker" — => intent "advice_request".
  - Definition/concept question ("what is a stock / NSE / BSE / candlestick / P/E") =>
    "concept", plan ["retrieve","speak"].
  - "what is the price / level now" => "price_check", plan ["resolve_ticker","fetch_quote","speak"].
  - "why did it move / what happened today" => "why_moved",
    plan ["resolve_ticker","fetch_quote","fetch_series","fetch_news","retrieve","speak"].
  - "this month / trend / last 30 days" => "trend",
    plan ["resolve_ticker","fetch_series","speak"].
  - Nifty / Sensex "how is the market" => "market_overview",
    plan ["resolve_ticker","fetch_quote","speak"].
  - Unrelated (tax filing, weather, etc.) => "out_of_scope", plan [].
Never invent a ticker. Return ONLY the JSON object."""


@dataclass
class PlanResult:
    intent: str
    action: str                      # answer | refuse | decline | clarify
    tickers: list[str] = field(default_factory=list)
    language_in: str = "te-IN"
    language_out: str = "te-IN"
    plan: list[str] = field(default_factory=list)
    needs_live_data: bool = False
    confidence: float = 0.0
    raw: dict | None = None


def validate(raw: dict) -> PlanResult:
    """Pure: turn a raw LLM dict into a safe PlanResult. No network."""
    intent = raw.get("intent")
    if intent not in ALLOWED_INTENTS:
        intent = "out_of_scope"

    tickers = [str(t).strip() for t in (raw.get("tickers") or []) if str(t).strip()]
    lang_in = str(raw.get("language_in") or "te-IN")
    lang_out = str(raw.get("language_out") or lang_in)
    safe_plan = tools.filter_plan(raw.get("plan") or [])
    try:
        conf = max(0.0, min(1.0, float(raw.get("confidence", 0.0))))
    except (TypeError, ValueError):
        conf = 0.0

    # Deterministic routing — safety first.
    if intent == "advice_request":
        action = "refuse"
        safe_plan = []                      # never run tools for advice
    elif intent == "out_of_scope":
        action = "decline"
        safe_plan = []
    elif conf < LOW_CONFIDENCE:
        action = "clarify"
    else:
        action = "answer"

    return PlanResult(
        intent=intent, action=action, tickers=tickers,
        language_in=lang_in, language_out=lang_out, plan=safe_plan,
        needs_live_data=bool(raw.get("needs_live_data", False)),
        confidence=conf, raw=raw,
    )


def plan(text: str) -> PlanResult:
    """Call the LLM planner on a transcript and return a validated PlanResult."""
    raw = adapter.chat_json(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        max_tokens=200,
        temperature=0.0,
    )
    return validate(raw)
