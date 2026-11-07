"""Unit tests for the refusal/disclaimer constants and the allowlist (offline)."""
from vaani.agent import refusal, tools


def test_refusal_is_constant_and_mentions_sebi():
    c = refusal.refusal("te-IN")
    assert "SEBI" in c.text
    assert c.reviewed is False          # Telugu must be flagged for review


def test_refusal_falls_back_to_english():
    assert refusal.refusal("xx-YY").text == refusal.REFUSAL["en-IN"].text


def test_disclaimer_present_both_languages():
    assert refusal.disclaimer("te-IN").text
    assert "advice" in refusal.disclaimer("en-IN").text.lower()


def test_telugu_constants_flagged_unreviewed():
    for table in (refusal.REFUSAL, refusal.DECLINE, refusal.DISCLAIMER,
                  refusal.UNKNOWN_CAUSE, refusal.NO_DATA):
        assert table["te-IN"].reviewed is False


def test_allowlist_has_no_order_tool():
    for bad in tools.FORBIDDEN:
        assert bad not in tools.ALLOWLIST


def test_filter_plan_drops_injected_tools():
    plan = ["resolve_ticker", "place_order", "fetch_quote", "speak", "rm_rf"]
    assert tools.filter_plan(plan) == ["resolve_ticker", "fetch_quote", "speak"]


def test_filter_plan_dedupes():
    assert tools.filter_plan(["speak", "speak", "fetch_quote"]) == ["speak", "fetch_quote"]
