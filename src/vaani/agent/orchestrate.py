"""Orchestrator: one turn of text -> grounded answer.

Ties the pieces together with the safety routing and the numeric provenance gate.
Speech (STT in / TTS out) wraps this; here the input is a transcript and the output
is the spoken text plus a display payload for the UI.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import advice, explainer, facts, lang as langmod, memory as mem, numeric_gate, planner, refusal, ticker_resolver
from ..retrieval import tier1, tier2

_GENERIC_CLARIFY = {
    "te-IN": "మీరు ఏ కంపెనీ లేదా అంశం గురించి అడుగుతున్నారో కొంచెం స్పష్టంగా చెప్పగలరా?",
    "hi-IN": "आप किस कंपनी या विषय के बारे में पूछ रहे हैं, थोड़ा साफ़ बताएँगे?",
    "en-IN": "Could you say a bit more clearly which company or topic you mean?",
}


@dataclass
class Answer:
    routing: str                      # answer | refuse | decline | clarify | no_data | concept_pending
    text: str
    language: str
    disclaimer: str
    display: dict = field(default_factory=dict)
    gate_ok: bool | None = None
    used_template: bool = False
    plan: list[str] = field(default_factory=list)
    intent: str = ""


def handle(text: str, session: "mem.SessionMemory | None" = None,
           language: str | None = None) -> Answer:
    # `language` (set by the UI selector for typed input) forces the reply language.
    # Voice input passes None, so Prisma's detected language is used instead.
    g = language or langmod.detect(text)

    # Deterministic advice short-circuit — refuse WITHOUT calling the LLM.
    if advice.is_advice_request(text):
        return Answer("refuse", refusal.refusal(g).text, g,
                      refusal.disclaimer(g).text, intent="advice_request")

    # Deterministic ambiguous-ticker short-circuit: a shared prefix like "HDFC" with no
    # Bank/Life/AMC qualifier must ask which one, regardless of planner classification.
    amb = ticker_resolver.resolve(text)
    if amb.status == "ambiguous":
        return Answer("clarify", ticker_resolver.clarifying_question(amb, g), g,
                      refusal.disclaimer(g).text, intent="ambiguous_ticker",
                      display={"candidates": [c.symbol for c in amb.candidates]})

    p = planner.plan(text)
    lang = language or p.language_out or g or "te-IN"
    disc = refusal.disclaimer(lang).text

    def mk(routing, msg, symbol=None, **kw):
        if session is not None:
            session.record(text, p.intent, symbol, lang)
        return Answer(routing, msg, lang, disc, intent=p.intent, plan=p.plan, **kw)

    if p.action == "refuse":
        return mk("refuse", refusal.refusal(lang).text)
    if p.action == "decline":
        return mk("decline", refusal.decline(lang).text)

    # Concept questions are answered from the Tier-1 glossary (human-reviewable text,
    # no LLM generation -> nothing to hallucinate).
    if p.intent == "concept":
        entry, score = tier1.answer(text, lang)
        if entry is None:
            return mk("no_data", (refusal.NO_DATA.get(lang) or refusal.NO_DATA["en-IN"]).text)
        return mk("answer", entry.text(lang), display={
            "concept": entry.id, "visual": entry.visual,
            "reviewed": entry.reviewed, "retrieval_score": round(score, 3),
        })

    # Everything else needs a ticker. A follow-up with none ("దాని ట్రెండ్?") reuses the
    # last resolved ticker from session memory.
    if not p.tickers:
        carried = session.last_symbol() if session else None
        if carried and p.intent in mem.DATA_INTENTS and carried in ticker_resolver._BY_SYMBOL:
            res = ticker_resolver.Resolution("resolved", [ticker_resolver._cand(carried, 1.0)])
        else:
            return mk("clarify", _GENERIC_CLARIFY.get(lang, _GENERIC_CLARIFY["en-IN"]))
    else:
        res = ticker_resolver.resolve(p.tickers[0], lang)
    if res.status == "ambiguous":
        return mk("clarify", ticker_resolver.clarifying_question(res, lang),
                  display={"candidates": [c.symbol for c in res.candidates]})
    if res.status == "none":
        return mk("no_data", (refusal.NO_DATA.get(lang) or refusal.NO_DATA["en-IN"]).text)
    if p.action == "clarify":   # low confidence but ticker resolved -> still ask
        return mk("clarify", _GENERIC_CLARIFY.get(lang, _GENERIC_CLARIFY["en-IN"]))

    fs = facts.build(res.symbol, p.intent, lang)
    if fs is None:
        return mk("no_data", (refusal.NO_DATA.get(lang) or refusal.NO_DATA["en-IN"]).text)

    # Tier-2: attach the company's reference note as background for why-moved/trend answers.
    # The ticker is already resolved, so this is a direct metadata lookup (no extra LLM call);
    # the hybrid retriever (tier2.query) is evaluated separately in the harness.
    if p.intent in ("why_moved", "trend"):
        fs.background = tier2.note_for(res.symbol)

    allowed = fs.allowed_numbers()
    used_template = False
    if p.intent in ("price_check", "market_overview"):
        # Simple factual readout -> deterministic template (guarantees the market-closed /
        # as-of wording, no LLM call, faster). why_moved/trend keep the richer LLM explainer.
        draft = explainer.template_answer(fs, lang)
        used_template = True
        ok, _ = numeric_gate.check(draft, allowed)
    else:
        draft = explainer.explain(fs, lang)
        ok, _ = numeric_gate.check(draft, allowed)
        if not ok:                              # regenerate once, stricter
            draft = explainer.explain(fs, lang, stricter=True)
            ok, _ = numeric_gate.check(draft, allowed)
        if not ok:                              # deterministic template fallback
            draft = explainer.template_answer(fs, lang)
            used_template = True
            ok, _ = numeric_gate.check(draft, allowed)

    # Output guard: a leaked recommendation or prediction must not ship. Fall back to
    # the template (which states only facts); if even that trips, refuse outright.
    if advice.output_is_unsafe(draft):
        draft = explainer.template_answer(fs, lang)
        used_template = True
        if advice.output_is_unsafe(draft):
            return mk("refuse", refusal.refusal(lang).text)
        ok, _ = numeric_gate.check(draft, allowed)

    return mk("answer", draft, symbol=res.symbol, display=_display(fs),
              gate_ok=ok, used_template=used_template)


def _display(fs: facts.FactSheet) -> dict:
    q = fs.quote
    d: dict = {
        "symbol": fs.symbol, "name_en": fs.name_en, "name_te": fs.name_te, "kind": fs.kind,
        "price": q.price, "currency": q.currency, "change_pct": q.change_pct,
        "previous_close": q.previous_close, "volume": q.volume,
        "as_of": fs.as_of, "source": q.source,
        "delayed_by_seconds": q.delayed_by_seconds,
    }
    if fs.series and fs.series.ok:
        d["series"] = {
            "days": fs.series.days, "closes": fs.series.closes,
            "return_pct": fs.series.period_return_pct,
            "high": fs.series.high, "low": fs.series.low,
            "volume_vs_avg_pct": fs.series.volume_vs_avg_pct,
        }
    if fs.news:
        d["headlines"] = [
            {"title": h.title, "publisher": h.publisher, "published_at": h.published_at}
            for h in fs.news
        ]
    if fs.gold:
        d["gold"] = fs.gold
    return d
