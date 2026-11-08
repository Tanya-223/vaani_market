# Changelog

All notable changes to Vaani Market. Dates are IST.

## [Unreleased] — Phase 2 (agent core) — in progress
### Added
- `src/vaani/llm/adapter.py` — one function over an OpenAI-compatible chat/completions
  endpoint (provider-agnostic, capped output, JSON mode).
- `src/vaani/agent/ticker_resolver.py` — alias table (Latin + Telugu script) + fuzzy
  (difflib) + phonetic matching; bare "HDFC" forced to a clarifying question; `keyterms()`.
- `src/vaani/agent/tools.py` — tool ALLOWLIST (no order-placement tool exists) + `filter_plan`.
- `src/vaani/agent/refusal.py` — hard-coded refusal/decline/disclaimer/no-data constants;
  all Telugu flagged `reviewed=False`.
- `src/vaani/agent/planner.py` — one constrained LLM call → JSON; deterministic routing
  (advice→refuse, out-of-scope→decline, confidence<0.5→clarify, plan filtered to allowlist).
- Tests: `test_ticker_resolver` (13), `test_refusal` (7), `test_planner` (8) — **28 passing**.
- Probes: `probe_llm` (Telugu + JSON), `probe_planner` (routing demo).

### Verified (live)
- LLM model chosen by benchmark: **`gemini-3.5-flash-lite`** (fast ~2s, non-thinking, natural
  Telugu). `gemini-2.5-flash*` are 404 for new keys; full `gemini-3.8-flash` too slow
  (thinking overhead, ~9.6s, truncated output).
- `probe_planner`: **19/19 starter cases route as expected** — all advice→refuse,
  out-of-scope→decline, bare HDFC→clarify, unknown→no_data, prompt-injection did not flip to advice.

### Decisions
- No number-to-words layer (Phase 1 listening test: Timbre normalizes rupees/percent itself).

### Pending (next)
- Tier-1 glossary (concept flow, Phase 3); output-side advice classifier + prediction
  rejection (Phase 4 finish); web app + charts (Phase 5); eval harness (Phase 7).

### Added — "what happened today" flow (end to end)
- `data/market.py`: `fetch_series` (30-day closes, return, 30d high/low, volume-vs-average)
  and `fetch_news` (handles both yfinance news schemas).
- `agent/facts.py`: `FactSheet` — the one grounded payload; `to_prompt_block()` (data the
  explainer quotes from) + `allowed_numbers()` (what the numeric gate permits). GoldBEES gets
  gold (GC=F) + USD/INR support, never P/E.
- `agent/explainer.py`: spoken-Telugu explainer (Telugu-script only, numbers copied verbatim,
  no predictions/advice) + deterministic template fallback that cannot hallucinate numbers.
- `agent/numeric_gate.py`: extracts every number from the draft, checks against allowed
  (rounding tolerated); orphan → regenerate once → template fallback.
- `agent/orchestrate.py`: full turn — planner → resolve → facts → explain → numeric gate →
  grounded answer + display payload + disclaimer.
- `tests/test_numeric_gate.py` (6) → **34 tests passing**.
- `probes/probe_answer.py`: 5 live data cases all gate-pass; GAIL answer synthesized to audio.

### Verified (live)
- End-to-end grounded Telugu answers for price / why-moved / trend / GoldBEES / Nifty;
  every answer carries the as-of time + disclaimer; numeric gate passes on all five.
- Numeric gate caught a real edge case (the "50" in "Nifty 50") — fixed by allowing
  name-embedded numbers. Explainer script-mixing (Bengali) fixed with a Telugu-only rule.

## [Unreleased] — Phase 3 (Tier-1 glossary) — done
### Added
- `retrieval/glossary.py` — 12 starter entries, English source + natural spoken Telugu
  DRAFTS (all `reviewed=False`); candlestick flagged `visual`.
- `retrieval/tier1.py` — document-aware (1 entry = 1 chunk), Gemini `gemini-embedding-001`
  embeddings, cosine top-k; concept answers returned from glossary text (no LLM generation).
- `llm/adapter.py`: `embed()` over the OpenAI-compatible /embeddings endpoint.
- `tests/test_tier1.py` (5) → **39 tests passing**. `probes/probe_glossary.py`.

### Deviation (flagged)
- Tier-1 uses Gemini embeddings instead of BGE-M3/E5 (Python 3.9, no GPU, deadline). Kept
  behind a pluggable embedder. Consequence: Tier-1 latency > the report's 150ms local budget;
  eval harness will measure the real figure.

### Verified (live)
- Concept routing: NSE/BSE 0.86, P/E 0.85, candlestick 0.82 (visual), dividend 0.82; a
  non-lexical paraphrase correctly matched market_cap (0.765).
- Known tie: "share market" vs "share" (0.745 vs 0.744) returns the share definition.

### Pending
- Tier-2 hybrid retrieval (company notes + 90d news) and Tier-3 remain interfaces/deferred;
  why_moved currently uses live quote+series+headlines directly (not a hybrid-retrieval store).

## [Unreleased] — Phase 5 (phone web app) — done
### Added
- `web/app.py` — stdlib server. Endpoints: `/` , `/static/*`, `/api/turn` (WAV -> STT ->
  orchestrator -> answer+sentences+display+timings), `/api/tts` (text -> WAV), `/api/ask_text`.
- `web/static/` — mobile UI: mic -> in-browser 16-bit mono 16kHz WAV, 30s countdown + auto-stop,
  sentence-chunked TTS playback with TTFA/E2E timing, live 30-day line chart + change pill +
  volume-vs-avg, illustrative labeled candlestick diagram, headlines, disclaimer, as-of.
  PWA (manifest + service worker + icon). Typed fallback for testing.
- `run_web.sh`; README run + HTTPS-tunnel (cloudflared) instructions.

### Fixed (safety/quality)
- Explainer now writes numbers as DIGITS (the numeric gate only reads Arabic digits, so
  Telugu-word numbers previously bypassed it) and states the as-of as a clean date.
- `facts.build` fetches quote/series/news/gold in parallel: agent turn ~8.6s -> ~6.4s.

### Verified (live, through the server)
- `/api/turn` with a Telugu WAV: STT (te-IN) -> grounded answer -> 3 sentences; gate passed.
- `/api/ask_text` concept -> candlestick (visual flag); why_moved -> 30 close points for chart.
- `/api/tts` returns audio/wav with X-Wall-Seconds.

### Known / honest
- No tunnel binary installed in the dev sandbox; browser mic/audio untested here (works by
  construction) — to be confirmed on a real phone over the cloudflared HTTPS URL.
- "why/how" turns ~6.4s agent time (two sequential LLM calls dominate); above the 3.5s target.

## [Unreleased] — Phase 4 (guardrails finish) + Phase 7 (eval harness) — done
### Added
- `agent/advice.py` — deterministic advice/prediction classifier (Telugu+English), run on
  INPUT (short-circuits to refusal BEFORE the LLM) and on the drafted OUTPUT (a leaked
  recommendation/prediction falls back to the template, else refuses).
- Orchestrator short-circuits (no LLM): advice -> refuse; ambiguous prefix (bare "HDFC")
  -> clarify. Stronger guardrail + fixes vague "how is HDFC"/"tell me about HDFC".
- `eval/adversarial.py` — 40-case suite (report 10.4 counts) + ticker + retrieval labels.
- `eval/harness.py` — runs the suite live, writes `eval/results/adversarial.csv` (per case)
  and `eval/results/metrics.csv` (summary). Throttled + resilient to 429.
- Tests: `test_advice` (6), `test_orchestrate` (5) -> **50 tests passing**.

### Measured (eval/results/metrics.csv)
- routing_accuracy 100% (40/40); refusal_accuracy 100% (18/18); numeric_hallucination 0/10;
  ticker_resolution 16/16; glossary P@1/MRR@5/nDCG@5 = 1.0.
- RAGAS generation metrics, WER, and browser TTFA/E2E are written as **target** (not measured).

### Honest caveats
- Latency rows (median 3.76s / p90 14s / max 135s) were measured UNDER free-tier
  rate-limiting and INCLUDE 429 retry backoff — not true model latency. Clean per-call
  probes were ~1.5-2.7s; one full why-moved turn ~6.4s. Real TTFA/E2E = browser-measured (target).
- Fix caught by the harness: two ambiguous-HDFC phrasings were misrouted (false refuse /
  no_data); the deterministic ambiguous short-circuit fixed both (now 40/40).

### Still pending
- Phase 6 memory (session follow-ups, prefs); Tier-2/Tier-3 retrieval (deferred per cut order).
- Telugu review of all `reviewed:false` strings (needs a Telugu speaker = you).
- Demo video + publishing (report 12.6).

## [Unreleased] — Phase 6 (memory) — done
### Added
- `agent/memory.py` — SessionMemory (rolling 5 turns; `last_symbol()` carry-over) and
  LongTermMemory (preferred language/voice + watchlist, persisted JSON). HARD RULE: no
  holdings/orders/PAN/Aadhaar/profile fields (asserted by a test).
- Orchestrator: optional `session`; a follow-up with no ticker ("దాని ట్రెండ్?") reuses the
  last resolved symbol. Wired a single in-process session into the web server (one-user demo).
- `tests/test_memory.py` (4) -> **54 tests passing**. `probes/probe_memory.py`.

### Verified (live)
- Carry-over works: "GAIL ... / దాని ట్రెండ్?" -> both resolved GAIL.NS without repeating the name.

### Known limitation (honest)
- The lite planner occasionally over-classifies an unusual follow-up opener ("మరి IOC ఎలా ఉంది?")
  as advice and over-refuses (safe-side error). Not patched yet to avoid invalidating the
  committed 40/40 metrics without a re-run; flagged for deliberate tuning.
- Web server must be restarted to pick up memory wiring (the demo instance predates it).

## [Unreleased] — Tier-2 retrieval + planner fix + submission artifacts — done
### Added
- `retrieval/corpus.py` — 8 factual company/instrument notes with metadata (ticker/sector/type).
- `retrieval/tier2.py` — hybrid retrieval: BM25 + dense (Gemini) fused with Reciprocal Rank
  Fusion, metadata filter, query rewriting. Cross-encoder reranker intentionally omitted
  (first in the report's cut order). `note_for()` enriches why-moved/trend answers.
- `tests/test_tier2.py` (5) -> **59 tests passing**. `probes/probe_tier2.py`.
- `docs/DEMO_SCRIPT.md` (video recording script) and `docs/REPORT_FIGURES.md` (measured
  figures for the report). README expanded (architecture, eval, status).

### Fixed
- Planner over-refusal: a neutral "how is X / మరి X ఎలా ఉంది" is no longer misclassified as
  advice. Verified: "మరి IOC ఎలా ఉంది?" now answers (IOC.NS) and the follow-up carries IOC.
- Harness now reports honest LLM-path latency (median/p90 over non-short-circuit cases) baked
  in, so re-runs stay truthful.

### Measured (eval/results/metrics.csv, 2026-11-08)
- routing 100% (40/40); refusal 100% (18/18); numeric hallucination 0; ticker 16/16;
  glossary AND tier2 retrieval P@1/MRR@5/nDCG@5 = 1.0; LLM-path latency median 1.49s / p90 3.67s.

## [Unreleased] — UI polish + Telugu review sheet
### Added
- `docs/TELUGU_REVIEW.md` — every Telugu string (12 glossary + refusal/decline/disclaimer/
  clarify + company names) with English gloss and a blank Fix line, generated from the code.
### Changed (web UI)
- Reworked `web/static/index.html` + `app.js`: logo header, "Not advice" badge, tappable
  example-question chips, visible states (listening/thinking/speaking), user bubble,
  routing badge, price stat tile + up/down status pill, KPI tiles (30d return / high / low /
  volume-vs-avg), headlines, Tier-2 background note, as-of/verified meta, disclaimer bar.
- Charts follow the dataviz method: 30-day line is a single BLUE series (gridlines, soft
  area, 2px line, end dot + value); up/down use status green/red ONLY with ▲/▼ + number
  (secondary encoding — validated, no colour-alone meaning). Candlestick stays illustrative/labeled.
- Noto Sans Telugu webfont for clean Telugu rendering.
## [Unreleased] — TTS decimal fix + market-closed messaging
### Fixed
- Sentence chunker split on the decimal point ("8.14" -> "8" pause "14 percent"). Now splits
  only on punctuation followed by whitespace/end, so decimals never break across TTS clips.
- Stale/weekend prices were presented without context. Added data-driven staleness
  (`FactSheet.is_stale`: latest data point older than today) — independent of yfinance's flaky
  market_state. Answers now state "మార్కెట్ ప్రస్తుతం మూసి ఉంది … చివరి ధర <date> నాటికి …".
### Changed
- price_check and market_overview now use the deterministic template (no LLM call): guarantees
  the market-closed/as-of wording and is faster. why_moved/trend keep the LLM explainer.

## [Unreleased] — Multi-language: Hindi + English (Telugu was first)
### Added
- `agent/lang.py` — script-based language detector (te/hi/en) for the pre-planner short-circuits.
- Hindi drafts for all 12 glossary entries, the 5 guardrail constants, clarify prompts; English
  was already present. Glossary gains `Entry.text(language)`.
- STT now `indic-auto` (detects te/hi/en from voice); TTS speaks the answer's language; the web
  chips include Hindi + English examples.
### Changed
- Short-circuits (advice/ambiguous), clarify questions, concept answers, and the template
  fallback are all language-aware now (te-IN / hi-IN / en-IN). Telugu routing unchanged (60 tests pass).
### Note
- Hindi strings are DRAFT (`reviewed:false`) — see `docs/TELUGU_REVIEW.md` (now te + hi).
- Other languages (Tamil, etc.) are a future add: the pipeline is language-agnostic; only the
  glossary + constants need translation per language.
## [Phase 1] — 2026-11-07 — Data layer proven (GATE PASSED)
### Added
- Project scaffolding: git repo, `.gitignore` (committed before `.env`), Python 3.9 venv,
  `requirements.txt`, `.env` / `.env.example`.
- `src/vaani/config.py` — env loader; never logs secrets (`masked()` helper).
- `src/vaani/http.py` — single reused `requests.Session`; retry ONLY on 429/5xx with
  exponential backoff + jitter (429 has no `Retry-After`).
- `src/vaani/gnani/tts.py` — Timbre v3.0 client (raw WAV bytes out).
- `src/vaani/gnani/stt.py` — Prisma v3.0 client (transcript + detected language + timing).
- `src/vaani/data/market.py` — yfinance quote tool; payloads carry value/unit/source/as-of/delay.
- `probes/` — `probe_auth`, `probe_tts`, `probe_stt`, `probe_market` (all run live).
- `docs/PHASE1_FINDINGS.md` — verified facts + discrepancies vs the context file.

### Verified (live)
- Auth header `X-API-Key-ID` confirmed (401-vs-422 method).
- Telugu TTS + STT round-trip works; `detected_language_code=te-IN`.
- Timbre normalizes rupees/percent → **number-to-words not needed**.
- All demo market symbols resolve; `TATAMOTORS.NS` delisted (changed-ticker test).

### Fixed / discrepancies
- Timbre `speed` must be numeric; documented word forms are rejected (HTTP 400).

### Pending
- LLM reasoning endpoint not yet provided → planner/explainer built but not run end-to-end.
- 10-day average volume to be computed from history in Phase 2.
