"""Offline tests for Tier-2 fusion, tokenizer, metadata notes (no network)."""
from vaani.retrieval import corpus, tier2


def test_rrf_rewards_agreement():
    # A doc ranked high by BOTH lists should beat one ranked high by only one.
    fused = tier2._rrf([["a", "b", "c"], ["a", "c", "b"]])
    assert fused[0] == "a"


def test_tokenizer_strips_filler_and_keeps_tickers():
    toks = tier2._tok("GAIL ఈ రోజు ఎందుకు పడింది?")
    assert "gail" in toks
    assert "ఈ" not in toks and "రోజు" not in toks   # Telugu filler removed


def test_note_for_resolved_symbol():
    assert "natural-gas" in tier2.note_for("GAIL.NS").lower()
    assert "exchange-traded fund" in tier2.note_for("GOLDBEES.NS").lower()


def test_goldbees_note_says_no_earnings():
    note = tier2.note_for("GOLDBEES.NS").lower()
    assert "no earnings" in note or "not a company" in note


def test_corpus_covers_all_instruments():
    tickers = {d.ticker for d in corpus.NOTES}
    for t in ["HDFCBANK.NS", "GAIL.NS", "IOC.NS", "GOLDBEES.NS", "^NSEI", "^BSESN"]:
        assert t in tickers, t
