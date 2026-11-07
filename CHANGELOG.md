# Changelog

All notable changes to Vaani Market. Dates are IST.

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
