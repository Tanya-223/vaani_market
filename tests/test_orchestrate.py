"""Offline tests for the orchestrator's deterministic short-circuits.

Advice and ambiguous-ticker routing happen BEFORE the planner (no LLM), so they are
testable without the network. Covers the two cases the harness caught (#20, #22).
"""
from vaani.agent import orchestrate


def test_advice_short_circuits_to_refuse():
    a = orchestrate.handle("ఇప్పుడు GAIL కొనాలా?")
    assert a.routing == "refuse"
    assert "SEBI" in a.text


def test_advice_takes_precedence_over_ambiguous():
    # "HDFC ... కొనమంటారా" is advice first, not a clarify.
    a = orchestrate.handle("HDFC బ్యాంక్ షేర్ కొనమంటారా?")
    assert a.routing == "refuse"


def test_bare_hdfc_how_is_it_clarifies():   # harness #20 (was false-refuse)
    a = orchestrate.handle("HDFC ఎలా ఉంది?")
    assert a.routing == "clarify"
    assert set(a.display["candidates"]) == {"HDFCBANK.NS", "HDFCLIFE.NS", "HDFCAMC.NS"}


def test_tell_me_about_hdfc_clarifies():    # harness #22 (was no_data)
    a = orchestrate.handle("HDFC గురించి చెప్పు.")
    assert a.routing == "clarify"


def test_hdfc_bank_is_not_ambiguous():
    # A qualified HDFC must NOT short-circuit to clarify (it proceeds to the planner).
    from vaani.agent import ticker_resolver
    assert ticker_resolver.resolve("HDFC బ్యాంక్ షేర్ ఈ రోజు ఎంత?").status == "resolved"
