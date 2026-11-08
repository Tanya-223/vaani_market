"""Refusal + disclaimer constants — hard-coded, pre-translated, never model-generated.

A model told to refuse will eventually refuse and then hint (report 9.1). So the
refusal is a constant the code emits deterministically. Pattern: refuse, name the
reason, offer the permitted action.

ALL Telugu below is DRAFT (reviewed=False) until a Telugu speaker signs off.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Constant:
    text: str
    reviewed: bool  # False = needs native-speaker review before public use


# Refusal for advice requests. Source: docs/vaani_context.md (draft).
# EN meaning: "I cannot tell you to buy or sell any share — that is the work of a
# SEBI-registered adviser. But I can explain what this company does and what happened
# to it today. Shall I?"
REFUSAL = {
    "te-IN": Constant(
        "నేను ఏ షేర్‌ని కొనమని లేదా అమ్మమని చెప్పలేను — అది SEBI నమోదు పొందిన సలహాదారు పని. "
        "కానీ ఈ కంపెనీ ఏం చేస్తుందో, ఈ రోజు దానికి ఏం జరిగిందో వివరించగలను. చెప్పమంటారా?",
        reviewed=False,
    ),
    "hi-IN": Constant(
        "मैं आपको कोई शेयर खरीदने या बेचने के लिए नहीं कह सकता — यह SEBI-रजिस्टर्ड सलाहकार का काम है। "
        "लेकिन मैं बता सकता हूँ कि यह कंपनी क्या करती है और आज इसके साथ क्या हुआ। बताऊँ?",
        reviewed=False,
    ),
    "en-IN": Constant(
        "I can't tell you to buy or sell any share — that's the work of a SEBI-registered "
        "adviser. But I can explain what this company does and what happened to it today. "
        "Shall I?",
        reviewed=True,
    ),
}

# Clean decline for out-of-scope questions (not advice — just not our job).
DECLINE = {
    "te-IN": Constant(
        "క్షమించండి, అది నా పని పరిధిలో లేదు. కానీ స్టాక్ మార్కెట్ గురించి లేదా ఈ రోజు "
        "ఒక కంపెనీకి ఏం జరిగిందో వివరించగలను.",
        reviewed=False,
    ),
    "hi-IN": Constant(
        "माफ़ कीजिए, यह मेरे काम के दायरे में नहीं है। लेकिन मैं स्टॉक मार्केट के बारे में या आज "
        "किसी कंपनी के साथ क्या हुआ, समझा सकता हूँ।",
        reviewed=False,
    ),
    "en-IN": Constant(
        "Sorry, that's outside what I do. But I can explain the stock market, or what "
        "happened to a company today.",
        reviewed=True,
    ),
}

# Mandatory disclaimer, shown on screen AND spoken.
DISCLAIMER = {
    "te-IN": Constant("విద్యా ప్రయోజనం కోసం మాత్రమే. ఇది పెట్టుబడి సలహా కాదు.", reviewed=False),
    "hi-IN": Constant("सिर्फ़ शैक्षणिक जानकारी। यह निवेश सलाह नहीं है।", reviewed=False),
    "en-IN": Constant("Educational only. Not advice.", reviewed=True),
}

# "I can see the movement but cannot confirm the reason" honesty line.
UNKNOWN_CAUSE = {
    "te-IN": Constant(
        "ఈ కదలికను నేను చూడగలను, కానీ దానికి కారణాన్ని నిర్ధారించలేను.", reviewed=False
    ),
    "hi-IN": Constant(
        "मैं यह हलचल देख सकता हूँ, लेकिन इसका कारण पक्का नहीं बता सकता।", reviewed=False
    ),
    "en-IN": Constant("I can see this movement, but I cannot confirm the reason.", reviewed=True),
}

# No-data honesty line (missing / unknown ticker).
NO_DATA = {
    "te-IN": Constant("క్షమించండి, దీనికి నా దగ్గర డేటా లేదు.", reviewed=False),
    "hi-IN": Constant("माफ़ कीजिए, इसके लिए मेरे पास डेटा नहीं है।", reviewed=False),
    "en-IN": Constant("Sorry, I don't have data for that.", reviewed=True),
}


def _get(table: dict, language: str) -> Constant:
    return table.get(language) or table["en-IN"]


def refusal(language: str = "te-IN") -> Constant:
    return _get(REFUSAL, language)


def decline(language: str = "te-IN") -> Constant:
    return _get(DECLINE, language)


def disclaimer(language: str = "te-IN") -> Constant:
    return _get(DISCLAIMER, language)
