"""Advice / prediction classifier — the belt-and-suspenders guard.

Runs on BOTH the input (backstop to the planner) and the drafted OUTPUT (so a
leaked recommendation — e.g. from a prompt injection — still cannot ship). Pure,
deterministic keyword/pattern matching in Telugu + English; no LLM, fully testable.

The planner already routes obvious advice to the refusal node; this catches anything
that slips through, and rejects forward-looking predictions in the drafted answer.
"""
from __future__ import annotations

import re

# Phrases that indicate the USER is asking for advice (checked on input).
_ADVICE_INPUT = [
    # Telugu — direct
    "కొనమంటారా", "కొనాలా", "కొనవచ్చా", "కొనడం మంచి", "అమ్మమంటారా", "అమ్మాలా", "అమ్మవచ్చా",
    "ఏ షేర్ కొన", "ఏది కొన", "ఏవి కొన",
    # Telugu — indirect / roleplay / where-to-invest
    "పెట్టుబడి పెట్టాలా", "పెట్టడం మంచి", "మంచి సమయమా", "మంచిదా", "మంచిదేనా", "లాభమా",
    "ఎక్కడ పెట్టాలి", "దిగడానికి", "దీర్ఘకాలానికి మంచి", "బ్రోకర్ అనుకో", "సలహా ఇవ్వు",
    "నిపుణుడివి అనుకో", "ఏది కొనాలి", "ఏ షేర్ కొనాలి", "కొంటే లాభ",
    # English
    "should i buy", "should i sell", "should i invest", "buy or sell", "worth buying",
    "good time to", "which stock", "recommend", "pretend you", "act as my broker",
    "tell me what to buy", "where should i invest", "is it a good",
]

# Phrases that indicate advice LEAKING INTO the answer (checked on output).
_ADVICE_OUTPUT = [
    # Telugu imperatives / recommendations
    "కొనండి", "అమ్మండి", "కొనవచ్చు", "అమ్మవచ్చు", "కొనడం మంచిది", "సిఫార్సు", "మంచి పెట్టుబడి",
    "ఇప్పుడు కొన", "హోల్డ్ చేయండి",
    # English
    "you should buy", "you should sell", "i recommend", "a good buy", "worth buying",
    "good investment", "hold it", "buy now", "sell now",
]

# Forward-looking prediction phrases (rejected in the draft).
_PREDICTION = [
    # Telugu
    "రేపు పెరుగు", "రేపు తగ్గు", "పెరుగుతుంది", "తగ్గుతుంది", "పెరగవచ్చు", "తగ్గవచ్చు",
    "భవిష్యత్తులో", "రాబోయే",
    # English
    "will rise", "will fall", "will go up", "will go down", "expected to rise",
    "expected to fall", "tomorrow it will", "next week", "forecast", "predict",
]


def _hit(text: str, patterns: list[str]) -> bool:
    low = (text or "").lower()
    return any(p.lower() in low for p in patterns)


def is_advice_request(text: str) -> bool:
    """True if the INPUT is asking for a buy/sell/hold recommendation."""
    return _hit(text, _ADVICE_INPUT)


def output_contains_advice(text: str) -> bool:
    """True if the drafted ANSWER contains a recommendation (must not ship)."""
    return _hit(text, _ADVICE_OUTPUT)


def output_contains_prediction(text: str) -> bool:
    """True if the drafted ANSWER makes a forward-looking prediction."""
    return _hit(text, _PREDICTION)


def output_is_unsafe(text: str) -> bool:
    return output_contains_advice(text) or output_contains_prediction(text)
