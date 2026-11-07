"""Unit tests for planner.validate() — the deterministic, safety-critical post-processing.
These need NO network; they feed synthetic 'LLM output' dicts through validate().
"""
from vaani.agent.planner import validate


def test_advice_always_refuses_and_drops_plan():
    r = validate({"intent": "advice_request", "confidence": 0.99,
                  "plan": ["resolve_ticker", "fetch_quote", "speak"]})
    assert r.action == "refuse"
    assert r.plan == []                 # tools never run for advice


def test_advice_refuses_even_at_low_confidence():
    r = validate({"intent": "advice_request", "confidence": 0.1})
    assert r.action == "refuse"         # low confidence must NOT downgrade safety


def test_injected_place_order_is_filtered():
    r = validate({"intent": "why_moved", "confidence": 0.9,
                  "plan": ["resolve_ticker", "place_order", "fetch_news", "speak"]})
    assert "place_order" not in r.plan
    assert r.plan == ["resolve_ticker", "fetch_news", "speak"]


def test_out_of_scope_declines():
    r = validate({"intent": "out_of_scope", "confidence": 0.9})
    assert r.action == "decline"


def test_low_confidence_clarifies():
    r = validate({"intent": "price_check", "confidence": 0.3,
                  "plan": ["resolve_ticker", "fetch_quote", "speak"]})
    assert r.action == "clarify"


def test_normal_answer_passes_through():
    r = validate({"intent": "concept", "confidence": 0.95,
                  "plan": ["retrieve", "speak"], "language_in": "te-IN"})
    assert r.action == "answer"
    assert r.plan == ["retrieve", "speak"]


def test_unknown_intent_defaults_safe():
    r = validate({"intent": "launch_nukes", "confidence": 0.9})
    assert r.intent == "out_of_scope"
    assert r.action == "decline"


def test_confidence_clamped():
    assert validate({"intent": "concept", "confidence": 5}).confidence == 1.0
    assert validate({"intent": "concept", "confidence": "x"}).confidence == 0.0
