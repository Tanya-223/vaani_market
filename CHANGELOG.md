# Changelog

All notable changes to Vaani Market. Dates are IST.

## [Unreleased] — Phase 2 (agent core) — in progress
### Added
- `src/vaani/llm/adapter.py` — one function over an OpenAI-compatible chat/completions
  endpoint (provider-agnostic, capped output, JSON mode). Decision: **Google Gemini Flash**
  (`gemini-3.8-flash`), base `https://generativelanguage.googleapis.com/v1beta/openai/`.
- `src/vaani/agent/ticker_resolver.py` — alias table (Latin + Telugu script) + fuzzy
  (difflib) + phonetic matching; bare "HDFC" forced to a clarifying question; exposes
  `keyterms()` for Prisma STT biasing.
- `tests/test_ticker_resolver.py` — 13 tests, all passing.
- `probes/probe_llm.py` — verifies Telugu generation + JSON output (run once LLM key added).
- `pytest.ini`.

### Decisions
- No number-to-words layer (Phase 1 listening test: Timbre normalizes rupees/percent itself).

### Pending
- LLM endpoint credentials (Gemini) → then run `probe_llm.py`, build planner + explainer.

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
