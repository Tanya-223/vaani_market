"""Offline tests for the memory tiers (no network)."""
import tempfile
from pathlib import Path

from vaani.agent import memory


def test_session_records_and_window():
    s = memory.SessionMemory(maxlen=5)
    for i in range(7):
        s.record(f"q{i}", "why_moved", f"SYM{i}.NS", "te-IN")
    assert len(s.as_list()) == 5                      # oldest dropped
    assert s.as_list()[0].text == "q2"


def test_last_symbol_skips_none():
    s = memory.SessionMemory()
    s.record("GAIL ఎలా ఉంది?", "why_moved", "GAIL.NS", "te-IN")
    s.record("స్టాక్ అంటే ఏమిటి?", "concept", None, "te-IN")   # concept has no ticker
    assert s.last_symbol() == "GAIL.NS"              # carries over the last real ticker


def test_longterm_defaults_and_watchlist_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "prefs.json"
        lt = memory.LongTermMemory.load(p)
        assert lt.preferred_language == "te-IN" and lt.preferred_voice == "Kalpana"
        lt.add_watch("GAIL.NS")
        lt.add_watch("GAIL.NS")                       # dedup
        lt.add_watch("IOC.NS")
        lt2 = memory.LongTermMemory.load(p)           # persisted
        assert lt2.watchlist == ["GAIL.NS", "IOC.NS"]
        lt2.remove_watch("GAIL.NS")
        assert memory.LongTermMemory.load(p).watchlist == ["IOC.NS"]


def test_no_financial_profile_fields():
    lt = memory.LongTermMemory()
    for banned in memory.FORBIDDEN:
        assert not hasattr(lt, banned), banned
