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
