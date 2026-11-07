"""Unit tests for the ticker resolver (offline, no network/LLM)."""
from vaani.agent import ticker_resolver as tr


def _resolve(text):
    return tr.resolve(text)


def test_bare_hdfc_is_ambiguous():
    r = _resolve("HDFC")
    assert r.status == "ambiguous"
    syms = {c.symbol for c in r.candidates}
    assert syms == {"HDFCBANK.NS", "HDFCLIFE.NS", "HDFCAMC.NS"}


def test_hdfc_with_filler_still_ambiguous():
    # "HDFC ఈ రోజు ఏమైంది?" -> content reduces to just "hdfc"
    r = _resolve("HDFC ఈ రోజు ఏమైంది")
    assert r.status == "ambiguous"


def test_hdfc_bank_resolves_directly():
    r = _resolve("HDFC Bank")
    assert r.status == "resolved"
    assert r.symbol == "HDFCBANK.NS"


def test_hdfc_bank_telugu_script():
    r = _resolve("హెచ్‌డిఎఫ్‌సి బ్యాంక్ షేర్")
    assert r.status == "resolved"
    assert r.symbol == "HDFCBANK.NS"


def test_hdfc_life_and_amc_distinct():
    assert _resolve("HDFC Life").symbol == "HDFCLIFE.NS"
    assert _resolve("HDFC AMC").symbol == "HDFCAMC.NS"


def test_gail_variants():
    for q in ["GAIL", "gail share", "గేల్", "గెయిల్"]:
        r = _resolve(q)
        assert r.status == "resolved" and r.symbol == "GAIL.NS", q


def test_gail_fuzzy_phonetic():
    # transcription slip "gale" should still reach GAIL via fuzzy+phonetic
    r = _resolve("gale")
    assert r.status == "resolved" and r.symbol == "GAIL.NS"


def test_ioc_variants():
    for q in ["IOC", "indian oil", "ఐఓసి"]:
        r = _resolve(q)
        assert r.status == "resolved" and r.symbol == "IOC.NS", q


def test_goldbees():
    for q in ["GoldBEES", "gold bees", "గోల్డ్ బీస్"]:
        assert _resolve(q).symbol == "GOLDBEES.NS", q


def test_indices():
    assert _resolve("Nifty").symbol == "^NSEI"
    assert _resolve("నిఫ్టీ ఈరోజు ఎలా ఉంది").symbol == "^NSEI"
    assert _resolve("Sensex").symbol == "^BSESN"


def test_unknown_returns_none():
    assert _resolve("zxcvbnm qwerty").status == "none"


def test_tata_motors_not_resolved():
    # Deliberately absent (delisted). Must not false-match a tracked instrument.
    assert _resolve("Tata Motors").status == "none"


def test_keyterms_nonempty_and_capped():
    kt = tr.keyterms()
    assert "GAIL" in kt and "HDFC Bank" in kt
    assert len(kt) == len(set(kt))  # de-duplicated
