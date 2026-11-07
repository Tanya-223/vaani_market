# Phase 1 findings — live verification (2026-11-07)

These supersede the "VERIFY" items in `docs/vaani_context.md`. Everything below was
run against the live Gnani API and Yahoo Finance from this workspace.

## Gnani auth — CONFIRMED
- Correct Speech-API header is **`X-API-Key-ID`**. Proven empirically:
  - `X-API-Key-ID` + missing `audio_file` → **422** (auth OK, param wrong).
  - `x-api-key` (Platform-style) + same body → **401 `MISSING_API_KEY`**.
- Your key is valid (len 134). Error bodies match the documented shapes.

## Timbre TTS (Timbre v3.0) — CONFIRMED, with one doc discrepancy
- `POST /api/v1/tts/inference`, JSON body, returns **raw `audio/wav` bytes**. Works for
  `language=te-IN`, `voice=Kalpana`, `model=timbre-v3.0`.
- **DISCREPANCY:** `speed` must be a **number** (e.g. `1.0`). The doc's word forms
  (`slow`/`medium`/`fast`) are **rejected** with HTTP 400. Code now sends numeric speed.
- **WAV header quirk:** the returned WAV's declared length field is unreliable
  (`wave.getnframes()` reports a nonsense duration). Real duration = bytes ÷ (rate·ch·width).
  Did NOT break Prisma STT; still must confirm the browser `<audio>` player is happy.

## Number & ticker pronunciation — LISTENING TEST DONE (number-to-words NOT needed)
Verified by sending Timbre output back through STT:
| Written | Timbre spoke | 
|---|---|
| `₹185.40` | "నూట ఎనభై ఐదు రూపాయలు మరియు నలభై పైసలు" (185 rupees 40 paise) |
| `2.3%` | "రెండు పాయింట్ మూడు పర్సెంట్" (two point three percent) |
| `GAIL` | "గేల్ / గేయిల్" (as a word) |
| `IOC` | "ఐఓసి" (as letters I-O-C) |
**Decision:** Timbre normalizes rupees/percent itself → do NOT add number-to-words.
(User to confirm by ear from `probes/out/*.wav`.)

## Prisma STT (Prisma v3.0) — CONFIRMED
- Returns transcript + `detected_language_code`. Telugu detected as **`te-IN`** with both
  `language_code=te-IN` and `indic-auto`.
- `processing_time` ≈ 0.10–0.25 s. **Connection reuse** cut wall time from 0.96 s (first,
  with TLS handshake) to ~0.20 s (kept-alive) — validates the single-session design.

## Market data (Yahoo Finance via yfinance) — CONFIRMED (delayed, unofficial)
All demo symbols resolve: `HDFCBANK.NS`, `HDFCLIFE.NS`, `HDFCAMC.NS`, `GAIL.NS`, `IOC.NS`,
`GOLDBEES.NS`, `^NSEI`, `^BSESN`, and gold supports `GC=F` (USD/oz) + `INR=X` (USD/INR).
- `exchangeDataDelayedBy`: 15 (NSE equities), 10 (gold futures), 0 (FX). Market was CLOSED
  (weekend) so quotes are end-of-day; as-of timestamp is surfaced on every quote.
- **`TATAMOTORS.NS` → delisted/no-data** (restructuring confirmed). Use only as the
  missing/changed-ticker test case.
- **TODO (Phase 2):** 10-day average volume is `None` from `fast_info`; compute it from
  history in `fetch_series` for the "volume vs recent average" line.

## Environment
- Python **3.9.6** only (no 3.10+). Fine for Phases 1–2; a newer interpreter is needed for
  BGE-M3 in Phase 3 (plan: separate venv or a lighter embedding model).
- Sandbox has outbound network. yfinance handled Yahoo's throttling (raw curl got 429).
