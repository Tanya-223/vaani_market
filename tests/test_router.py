"""Offline tests for the tier timeout/degrade router."""
import time

from vaani.retrieval.router import within_budget, TIER_BUDGET_MS


def test_fast_fn_returns_result():
    out, ok = within_budget(lambda: 42, 1000, default=None)
    assert ok and out == 42


def test_slow_fn_degrades_to_default():
    def slow():
        time.sleep(0.5)
        return "late"
    out, ok = within_budget(slow, 100, default="degraded")
    assert ok is False and out == "degraded"


def test_budgets_present_and_ordered():
    assert set(TIER_BUDGET_MS) == {1, 2, 3}
    assert all(v > 0 for v in TIER_BUDGET_MS.values())
