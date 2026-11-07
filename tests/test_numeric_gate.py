"""Unit tests for the numeric provenance gate + FactSheet allowed_numbers (offline)."""
from vaani.agent import numeric_gate as ng
from vaani.agent.facts import FactSheet
from vaani.data.market import Quote, Series


def test_extract_handles_indian_and_western_grouping():
    nums = ng.extract_numbers("ధర ₹1,23,456.78, 2.3% పెరిగింది, -0.11 కూడా")
    assert 123456.78 in nums
    assert 2.3 in nums
    assert -0.11 in nums


def test_clean_draft_passes():
    allowed = {185.79, 0.11, 30.0}
    ok, orphans = ng.check("ధర 185.79 రూపాయలు, 0.11 శాతం తగ్గింది", allowed)
    assert ok and orphans == []


def test_orphan_number_fails():
    allowed = {185.79, 0.11}
    ok, orphans = ng.check("ధర 185.79 కానీ లక్ష్యం 250 రూపాయలు", allowed)
    assert not ok and 250.0 in orphans


def test_currency_rounding_tolerated():
    ok, _ = ng.check("185.8", {185.79})
    assert ok                       # within rounding
    ok2, _ = ng.check("190", {185.79})
    assert not ok2                  # clearly different


def _fs():
    q = Quote(symbol="GAIL.NS", ok=True, price=185.79, currency="INR",
              previous_close=185.99, change_pct=-0.11, volume=7812989,
              as_of="2026-11-05T18:30:00+00:00")
    s = Series(symbol="GAIL.NS", ok=True, days=30, closes=[180.0, 185.79],
               period_return_pct=3.22, high=190.0, low=175.0,
               latest_volume=7812989, avg_volume=6000000, volume_vs_avg_pct=30.2)
    return FactSheet(symbol="GAIL.NS", name_en="GAIL", name_te="గెయిల్", kind="stock",
                     intent="why_moved", quote=q, series=s)


def test_allowed_numbers_contains_payload_values():
    allowed = _fs().allowed_numbers()
    for v in (185.79, 185.99, 0.11, 3.22, 190.0, 175.0, 30.0):
        assert v in allowed, v


def test_template_fallback_passes_its_own_gate():
    fs = _fs()
    draft = __import__("vaani.agent.explainer", fromlist=["template_answer"]).template_answer(fs, "te-IN")
    ok, orphans = ng.check(draft, fs.allowed_numbers())
    assert ok, (draft, orphans)
