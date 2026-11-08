# Vaani Market — project report

A step-by-step account of what was built, the decisions and live discoveries along the way,
and what every file in the repository does.

*Written for reviewers and for anyone picking up the codebase. Scope: Telugu + Hindi + English
demo on Gnani Prisma/Timbre. All figures here trace to `eval/results/metrics.csv`.*

---

## 1. What it is

A voice-first assistant for the Indian stock market that **explains and never advises**.
Two kinds of user:

- **Beginners** ask concept questions ("what is a stock / NSE / BSE / candlestick / P/E") —
  answered from a human-reviewable glossary, with an illustrative diagram.
- **Light traders** ask "what happened today" for HDFC, GAIL, IOC, GoldBEES, Nifty, Sensex —
  answered from live (delayed) data plus timestamped headlines, with a 30-day chart.

The defining rule: it never says buy/sell/hold, never says whether it's a good time to enter,
and never predicts a price. Every spoken number traces to fetched data.

---

## 2. How it was built, step by step

The build followed the project plan in strict priority order, proving the riskiest dependency
(the live APIs) first and keeping guardrails and the evaluation harness as never-cut.

**Phase 0 — setup.** Git repo, `.gitignore` committed *before* any `.env`, virtualenv,
`config.py` (loads `.env`, never logs secrets) and `http.py` (one reused session; retries
**only** 429/5xx with exponential backoff + jitter, since Gnani's 429 carries no `Retry-After`).

**Phase 1 — prove the data layer (gate).** Live probes confirmed, not assumed:
- The Speech-API auth header is **`X-API-Key-ID`** (proved with the 401-vs-422 trick).
- Telugu TTS → STT round-trip works; language detected as `te-IN`.
- **Discovery:** Timbre normalises rupees and percentages itself, so **no number-to-words layer
  is needed**. Another discovery: Timbre's `speed` must be **numeric** (the documented word
  forms are rejected).
- All demo symbols resolve on Yahoo; `TATAMOTORS.NS` is delisted (used only as the
  changed-ticker test).

**Phase 2 — the agent core.** The planner (one constrained Gemini call returning JSON only),
the tool allowlist (no order tool exists), the ticker resolver (alias + fuzzy + phonetic, with
bare "HDFC" forced to a clarifying question), and the data tools (every payload carries value,
unit, source, as-of, delay). Then the **FactSheet** (the single grounded payload), the
**explainer** (3 sentences in the target language), and the **numeric provenance gate**.
**19/19 starter cases routed correctly**, including advice → refuse and a prompt-injection that
did not flip to advice.

**Phase 3 — retrieval.** Tier-1 glossary (12 terms, document-aware, cosine over Gemini
embeddings, plus an instant keyword fast-path). Tier-2 hybrid (BM25 + dense fused with
Reciprocal Rank Fusion + metadata filter + query rewriting) over company notes. *Decision,
flagged:* Gemini embeddings instead of BGE-M3, because the dev machine had only Python 3.9 and
no GPU — kept behind a pluggable interface.

**Phase 4 — guardrails.** A deterministic advice/prediction classifier that runs on **both the
input** (short-circuits to refusal before any LLM call) **and the drafted output** (a leaked
recommendation falls back to a template or refuses). Numeric gate wired with
regenerate-once-then-template. Disclaimer + as-of on screen and in speech.

**Phase 5 — the phone web app.** A dependency-light stdlib server and a mobile PWA: mic →
in-browser 16-bit mono WAV, 30-second countdown, sentence-chunked playback (fetched in parallel
so there's no gap between sentences), a live 30-day chart, an illustrative candlestick diagram,
and a language selector. *Fix found in testing:* the sentence splitter was breaking on the
decimal point in "8.14"; now it splits only on punctuation followed by whitespace.

**Phase 6 — memory.** Session memory (last 5 turns, so "and its trend?" reuses the last ticker)
and long-term preferences (language, voice, watchlist). It deliberately stores **no** holdings,
orders, PAN, Aadhaar, or inferred financial profile.

**Phase 7 — evaluation harness (never cut).** The 40-case adversarial suite, retrieval metrics
(P@k / Recall@k / MRR@k / nDCG@k), and product metrics (refusal accuracy, numeric-hallucination
rate, ticker-resolution accuracy, latency) written to a committed CSV. The harness **caught two
real bugs** (a false refuse and a wrong no-data on vague "HDFC" phrasings), which were fixed with
a deterministic ambiguous-ticker short-circuit — then re-run to 40/40.

**After the phases:** Tier-2 wired into answers; a planner over-refusal fixed; a **tier
timeout/degrade router** added (hard per-tier budget, degrades downward); and **market-closed
messaging** so a weekend price is stated as "latest available as of <date>". Finally,
**Hindi + English** were added (the pipeline was already language-agnostic; only the glossary and
constants needed translating), and the **home screen** was redesigned with a language selector,
a logo, "learn the basics" cards, a faint background grid, and a mic waveform.

---

## 3. Key decisions and honest notes

- **Reasoning model chosen by benchmark, not guesswork.** `gemini-3.5-flash-lite` — the full
  flash model was ~9.6 s with thinking overhead; lite is ~1.5 s and non-thinking.
- **Deterministic refusal.** The refusal is a constant, emitted before the LLM runs — a model
  told to refuse will eventually refuse and then hint.
- **Latency.** "Why did it move" turns take a few seconds (two LLM calls); concept answers and
  refusals are near-instant (keyword fast-path / deterministic). Reported latency figures were
  measured under free-tier rate-limiting and are an upper bound.
- **Everything unmeasured is labelled "target".** RAGAS generation metrics, WER, and browser
  TTFA/E2E are not presented as achieved results.
- **All Telugu/Hindi text is draft** until a native speaker reviews it (`docs/TELUGU_REVIEW.md`).

---

## 4. File-by-file

### Configuration & infrastructure
| File | What it does |
|---|---|
| `src/vaani/config.py` | Loads `.env`; exposes keys/URLs/model; `masked()` logs a key's identity without revealing it. |
| `src/vaani/http.py` | One reused `requests.Session`; `request_with_retry` retries only 429/5xx with backoff + jitter; `Timing` captures wall-clock. |
| `.env.example` | Template for the keys. `.env` itself is git-ignored. |
| `requirements.txt` | Python deps (requests, python-dotenv, yfinance, rank-bm25, pytest). |
| `run_web.sh` | Starts the web app. |
| `pytest.ini` | Puts `src/` on the test path. |

### Gnani speech clients
| File | What it does |
|---|---|
| `src/vaani/gnani/stt.py` | Prisma v3.0 client; multipart upload; returns transcript + detected language + `processing_time`. |
| `src/vaani/gnani/tts.py` | Timbre v3.0 client; JSON in, raw WAV bytes out; numeric `speed`; voice list. |

### Reasoning layer
| File | What it does |
|---|---|
| `src/vaani/llm/adapter.py` | One function over an OpenAI-compatible `/chat/completions` (+ `/embeddings`); capped output, JSON mode, provider-swappable. |

### Market data
| File | What it does |
|---|---|
| `src/vaani/data/market.py` | `fetch_quote`, `fetch_series` (30-day closes, return, 30d high/low, volume-vs-average), `fetch_news`. All numbers computed in code; payloads carry unit/source/as-of/delay. |

### Agent
| File | What it does |
|---|---|
| `src/vaani/agent/planner.py` | One constrained LLM call → JSON (intent, tickers, language, plan, confidence). `validate()` is pure: advice→refuse, out-of-scope→decline, low-confidence→clarify, plan filtered to the allowlist. |
| `src/vaani/agent/tools.py` | The tool **allowlist** and `filter_plan`. Lists forbidden capabilities (no `place_order`); asserted by a test. |
| `src/vaani/agent/ticker_resolver.py` | Spoken name → exchange symbol via alias table (Latin + Telugu/Hindi) + fuzzy (difflib) + phonetic; bare "HDFC" → clarify; `keyterms()` for STT biasing. |
| `src/vaani/agent/advice.py` | Deterministic advice/prediction classifier (te/hi/en) for input and output. |
| `src/vaani/agent/facts.py` | `FactSheet` — the one grounded payload: `to_prompt_block()` (data the explainer quotes), `allowed_numbers()` (what the gate permits), `is_stale` (market-closed detection). |
| `src/vaani/agent/explainer.py` | Writes the spoken answer in the target language; deterministic template fallback that cannot hallucinate numbers. |
| `src/vaani/agent/numeric_gate.py` | Extracts every number from the draft and checks it against the allowed set (rounding tolerated). |
| `src/vaani/agent/refusal.py` | Hard-coded refusal / decline / disclaimer / unknown-cause / no-data constants in te/hi/en, each with a `reviewed` flag. |
| `src/vaani/agent/memory.py` | SessionMemory (5-turn carry-over) + LongTermMemory (language/voice/watchlist). No financial-profile fields (asserted). |
| `src/vaani/agent/lang.py` | Script-based language detector (te/hi/en) for the pre-planner short-circuits. |
| `src/vaani/agent/orchestrate.py` | Ties it together: text → guards → planner → resolve → facts → explain → numeric gate → output guard → answer + display payload. |

### Retrieval
| File | What it does |
|---|---|
| `src/vaani/retrieval/glossary.py` | Tier-1 corpus: 12 terms with English source + Telugu + Hindi drafts; `Entry.text(language)`. |
| `src/vaani/retrieval/tier1.py` | Keyword fast-path (instant) + embedding cosine top-k; `answer()` runs the embedding fallback under a hard time budget. |
| `src/vaani/retrieval/corpus.py` | Tier-2 company/instrument notes with metadata (ticker/sector/type). |
| `src/vaani/retrieval/tier2.py` | Hybrid retrieval: BM25 + dense fused with Reciprocal Rank Fusion + metadata filter + query rewriting. `note_for()` enriches answers. |
| `src/vaani/retrieval/router.py` | Per-tier hard timeouts; `within_budget` degrades downward on overrun. |

### Web app
| File | What it does |
|---|---|
| `src/vaani/web/app.py` | stdlib server. `/api/turn` (WAV→STT→answer), `/api/tts` (text→WAV), `/api/ask_text` (typed, honours the selected language). |
| `src/vaani/web/static/index.html` | Mobile PWA shell: logo, language selector, basics cards, chips, answer card, mic dock, faint background grid. |
| `src/vaani/web/static/app.js` | Recording → in-browser WAV encode, countdown, chunked TTS playback, charts, language switching. |
| `src/vaani/web/static/i18n.js` | UI translations (te/hi/en) + inline SVG icons; per-language `reviewed` flag. |
| `src/vaani/web/static/manifest.json`, `sw.js`, `icon.svg` | PWA install + minimal service worker + app icon. |

### Probes (live checks)
| File | What it does |
|---|---|
| `probes/probe_auth.py` | Confirms the `X-API-Key-ID` header empirically. |
| `probes/probe_tts.py` | Telugu TTS listening-test clips. |
| `probes/probe_stt.py` | STT loopback + detected language. |
| `probes/probe_market.py` | Verifies every test symbol + delay. |
| `probes/probe_llm.py` | Telugu generation + JSON output. |
| `probes/probe_planner.py` | Routing over the 19 starter cases. |
| `probes/probe_answer.py` | Full voice-answer for 5 data questions. |
| `probes/probe_glossary.py` | Tier-1 retrieval demo. |
| `probes/probe_tier2.py` | Tier-2 hybrid retrieval demo. |
| `probes/probe_memory.py` | Session follow-up carry-over. |

### Evaluation
| File | What it does |
|---|---|
| `eval/adversarial.py` | The 40-case suite + ticker and retrieval labels. |
| `eval/harness.py` | Runs the suite live, computes metrics, writes the CSVs. |
| `eval/results/metrics.csv` | Summary metrics (measured vs target) — the source of every published figure. |
| `eval/results/adversarial.csv` | Per-case routing results. |

### Tests (63)
`tests/test_ticker_resolver.py`, `test_refusal.py`, `test_planner.py`, `test_numeric_gate.py`,
`test_tier1.py`, `test_advice.py`, `test_orchestrate.py`, `test_memory.py`, `test_tier2.py`,
`test_router.py` — the deterministic, safety-critical logic, all runnable offline.

### Docs
| File | What it does |
|---|---|
| `docs/PHASE1_FINDINGS.md` | Live-verified API facts and discrepancies. |
| `docs/DEMO_SCRIPT.md` | Video recording script. |
| `docs/REPORT_FIGURES.md` | Measured figures for the academic report. |
| `docs/TELUGU_REVIEW.md` | Every Telugu + Hindi draft string with English meaning, for native-speaker review. |
| `CHANGELOG.md` | Chronological record of every phase and fix. |

---

## 5. Limitations

One demonstration language set (te/hi/en), not a product. Market data is delayed and unofficial.
Advanced retrieval (Tier-3, graph) is designed but not implemented. Retrieval quality in Telugu
and Hindi is an open experiment, not a solved result. This is engineering design, not legal
advice; a production launch would require counsel and SEBI registration.
