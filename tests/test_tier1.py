"""Offline tests for Tier-1 cosine + glossary metadata (no network)."""
import math

from vaani.retrieval import glossary
from vaani.retrieval.tier1 import cosine


def test_cosine_identity_and_orthogonal():
    assert abs(cosine([1, 0, 0], [1, 0, 0]) - 1.0) < 1e-9
    assert abs(cosine([1, 0, 0], [0, 1, 0])) < 1e-9


def test_cosine_ranks_closer_vector_higher():
    q = [1, 1, 0]
    near = cosine(q, [1, 0.9, 0])
    far = cosine(q, [0, 0, 1])
    assert near > far


def test_cosine_handles_zero_vector():
    assert cosine([0, 0, 0], [1, 2, 3]) == 0.0


def test_glossary_all_telugu_unreviewed():
    assert glossary.unreviewed_count() == len(glossary.GLOSSARY)
    for e in glossary.GLOSSARY:
        assert e.reviewed is False
        assert e.text_te and e.text_en


def test_candlestick_has_visual():
    assert glossary.BY_ID["candlestick"].visual == "candlestick"


def test_keyword_fastpath_routes_and_resolves_share_market_tie():
    from vaani.retrieval.tier1 import keyword_hit
    assert keyword_hit("షేర్ మార్కెట్ అంటే ఏమిటి?") == "stock_market"   # the tie, fixed
    assert keyword_hit("స్టాక్ అంటే ఏమిటి?") == "stock_share"
    assert keyword_hit("క్యాండిల్ చార్ట్ అంటే ఏమిటి?") == "candlestick"
    assert keyword_hit("P/E రేషియో అంటే ఏమిటి?") == "pe_ratio"
    assert keyword_hit("ఈ రోజు వాతావరణం ఎలా ఉంది?") is None          # non-concept -> no hit
