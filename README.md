# Vaani Market
pitch doc : https://drive.google.com/file/d/1FgOmaz7zioz9aeBFg0j_bN7bAqEIVH5k/view?usp=sharing

**A voice-first, multilingual market explainer for India that explains — and never advises.**

Vaani Market lets anyone ask about the Indian stock market **in their own language, by voice**,
and hear a spoken answer back. A beginner can ask *"what is a candlestick chart?"*; a light
trader can ask *"why did GAIL move today?"*. It explains what the data shows and **refuses to
tell you to buy, sell, or hold** — the refusal is a hard-coded gate in the software, not a
polite prompt the model is trusted to honour.

Built for the **Great Indian AI Internship Challenge (Gnani AI)** on Gnani **Prisma v3.0**
(speech-to-text) and **Timbre v3.0** (text-to-speech). Languages: **Telugu, Hindi, English**.

> ⚠️ **Educational only. Not advice.** It never says buy / sell / hold and never predicts prices.
> Market data is delayed and from a free source; the as-of date is always shown.

---

## Why it's different

- **Refuses to advise, structurally.** Any buy/sell/hold/"should I" request is caught by a
  deterministic classifier *before the language model is ever called* and answered with a
  fixed, human-reviewed refusal. There is deliberately **no order-placing tool anywhere** in
  the codebase.
- **Every number is traceable.** Prices, % changes and trends are fetched and computed in
  **code**, never by the model. A **numeric provenance gate** rejects any digit in the spoken
  answer that doesn't trace back to a tool payload; measured numeric-hallucination rate is **0**.
- **Voice-first and multilingual.** Prisma auto-detects the spoken language and the assistant
  replies in it; the home screen also has a Telugu / Hindi / English selector.
- **Honest about its limits.** Delayed data is labelled, the reason for a move is only stated
  when a headline proves it, and unmeasured metrics are labelled "target", never faked.

---

## How it works

```
 microphone (browser, 16-bit mono WAV)
      │
      ▼
 [1] Prisma v3.0 STT ─────────► transcript + detected language
      │
      ▼
 [2] Deterministic guards (no LLM):  advice → refuse   |   bare "HDFC" → clarify
      │
      ▼
 [3] Planner (one constrained LLM call) ─► intent, tickers, language, plan, confidence
      │
      ├─► Ticker resolver (alias + fuzzy + phonetic)
      ├─► Market data tools (quote / 30-day series / news — fetched in parallel, in code)
      ├─► Retrieval: Tier-1 glossary (concepts) · Tier-2 hybrid BM25+dense+RRF (company notes)
      │
      ▼
 [4] Explainer (LLM writes 3 short sentences)  +  template fallback
      │
      ▼
 [5] Numeric provenance gate ─► every digit must trace to a tool payload (else regenerate → template)
      │
      ▼
 [6] Advice/prediction output guard ─► a leaked recommendation cannot ship
      │
      ▼
 [7] Timbre v3.0 TTS ─► sentence-chunked, played back-to-back; on-screen chart + "Not advice"
```

Four guardrail layers run across the whole pipeline: **intent** (advice → refusal), **capability**
(tool allowlist, no order tool), **output** (numeric gate + prediction rejection), and
**disclosure** (as-of date + disclaimer, shown and spoken).

---

## Models & tools

| Component | Choice | Notes |
|---|---|---|
| Speech-to-text | **Gnani Prisma v3.0** (`indic-auto`) | detects te/hi/en from voice |
| Text-to-speech | **Gnani Timbre v3.0** (voice *Kalpana*) | all 10 Indian languages; speed must be numeric |
| Reasoning | **Google Gemini `gemini-3.5-flash-lite`** via OpenAI-compatible API | behind one swappable adapter; fast, non-thinking |
| Embeddings | **Gemini `gemini-embedding-001`** | multilingual; used for retrieval |
| Market data | **Yahoo Finance** (`yfinance`) | delayed, unofficial; delay surfaced on screen |
| Keyword retrieval | **BM25** (`rank-bm25`) | fused with dense via Reciprocal Rank Fusion |

The auth header for Gnani's Speech APIs is **`X-API-Key-ID`** (confirmed empirically, not assumed).

---

## Project layout

```
src/vaani/
  config.py            env + secret masking         http.py        shared session, 429/5xx retry
  gnani/stt.py tts.py   Prisma / Timbre clients
  llm/adapter.py        one OpenAI-compatible chat + embeddings function
  data/market.py        fetch_quote / fetch_series / fetch_news (numbers computed in code)
  agent/
    planner.py          constrained-JSON planner        router? → retrieval/router.py
    ticker_resolver.py  alias + fuzzy + phonetic         advice.py   advice/prediction classifier
    facts.py            the grounded FactSheet payload   numeric_gate.py  provenance gate
    explainer.py        3-sentence explainer + template fallback
    refusal.py          hard-coded refusal/disclaimer constants (te/hi/en)
    memory.py           session (5-turn) + long-term prefs    lang.py  script language detector
    orchestrate.py      one turn: STT text → grounded answer
  retrieval/
    glossary.py         Tier-1 corpus (12 terms, te/hi/en)     tier1.py  keyword + embedding
    corpus.py           Tier-2 company notes                   tier2.py  BM25+dense+RRF
    router.py           per-tier hard timeout + downward degrade
  web/app.py            stdlib server            web/static/  mobile PWA (index/app.js/i18n.js)
probes/                 live checks (auth, stt, tts, market, llm, planner, answer, glossary, tier2, memory)
eval/                   harness + adversarial suite + committed results CSVs
tests/                  63 unit tests
docs/                   build context, Phase-1 findings, demo script, report figures, review sheet
```

A full file-by-file description is in [`docs/PROJECT_REPORT.md`](docs/PROJECT_REPORT.md).

---

## Setup & run

**Prerequisites:** Python 3.9+ and Node (for the web app you only need a browser). A Gnani
Speech API key (from [app.gnani.ai/voice](https://app.gnani.ai/voice)) and a Google Gemini
API key (free, from [aistudio.google.com](https://aistudio.google.com)).

```bash
# 1. install
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt

# 2. credentials — copy the template and fill in your keys
cp .env.example .env
#    GNANI_API_KEY=...            (your Gnani Speech key)
#    LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
#    LLM_API_KEY=...              (your Gemini key)
#    LLM_MODEL=gemini-3.5-flash-lite
```

`.env` is git-ignored — **never commit it.**

### Run the phone web app
```bash
./run_web.sh                 # serves http://localhost:8000
```
Open it in Chrome on your laptop (the mic works on `localhost`). For a **phone**, expose it
over HTTPS with a tunnel:
```bash
brew install cloudflared
cloudflared tunnel --url http://localhost:8000
```
Open the printed `https://…trycloudflare.com` link on your phone, pick a language, tap the mic,
and ask. "Add to Home Screen" installs it as an app.

### Verify the pipeline (live probes)
```bash
python -W ignore probes/probe_auth.py      # confirms the X-API-Key-ID header
python -W ignore probes/probe_tts.py       # Telugu TTS clips → probes/out/
python -W ignore probes/probe_stt.py       # STT loopback, detected language
python -W ignore probes/probe_market.py    # every test symbol + delay
python -W ignore probes/probe_planner.py   # 19 starter cases route correctly
python -W ignore probes/probe_answer.py    # full voice-answer for 5 data questions
```

### Tests & evaluation
```bash
python -W ignore -m pytest -q              # 63 unit tests
python -W ignore eval/harness.py           # writes eval/results/{adversarial,metrics}.csv
```

## Measured results

From `eval/results/metrics.csv` (produced by the harness on the working build):

| Metric | Result | Target |
|---|---|---|
| Routing accuracy (40-case adversarial suite) | **100%** | — |
| Refusal accuracy (18 advice cases) | **100%** | 100% |
| Numeric hallucination rate | **0** | 0 |
| Ticker resolution accuracy | **100%** | ≥90% |
| Tier-1 glossary P@1 / MRR@5 / nDCG@5 | **1.0 / 1.0 / 1.0** | — |
| Tier-2 hybrid P@1 / MRR@5 / nDCG@5 | **1.0 / 1.0 / 1.0** | — |

RAGAS generation metrics (faithfulness, relevancy, context precision/recall), word error rate,
and browser TTFA/E2E are **targets, not yet measured** — labelled as such in the CSV.

---


## Safety

Vaani Market is a demonstration, not a deployable financial service. It is **not** SEBI-registered
and gives no investment advice. Market data is delayed and unofficial. A production launch would
require legal review and, for any personalised output, SEBI registration.

## License

[MIT](LICENSE) © 2026 Tanya Kontisetty. The speech models (Gnani Prisma/Timbre), the reasoning
model (Google Gemini), and market data (Yahoo Finance) are third-party services under their own
terms; this licence covers the Vaani Market code only.
