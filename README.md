# Vaani Market

A phone-friendly, **voice-in / voice-out** assistant that **explains** the Indian stock
market and **never advises**. Demo language: **Telugu (te-IN)**. Built on Gnani Prisma
(STT) + Timbre (TTS); the reasoning layer is an external OpenAI-compatible model behind one
adapter. Market data is delayed Yahoo Finance (the delay is always shown).

> Educational only. Not advice. It never says buy / sell / hold and never predicts prices.

## Who it serves
- **Beginners** — "what is a stock / NSE / BSE / candlestick?" → glossary (Tier 1) + an
  illustrative diagram.
- **Light traders** — "what happened to GAIL / IOC / HDFC / GoldBEES today?" → live data +
  timestamped headlines, with a 30-day chart. States what the data shows; never invents a cause.

## Layout
```
src/vaani/   config, http (retry), gnani/ (stt,tts), llm/, data/, agent/, retrieval/, web/
probes/      Phase-1 live checks (auth, tts, stt, market)
eval/        metrics harness + committed results CSV
tests/       unit tests (ticker resolver, numeric gate, refusal gate)
docs/        PHASE1_FINDINGS.md (live-verified facts), build context
```

## Run the Phase 1 probes
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env     # then paste your Gnani key into GNANI_API_KEY
python -W ignore probes/probe_auth.py     # confirms X-API-Key-ID
python -W ignore probes/probe_tts.py      # Telugu clips -> probes/out/*.wav
python -W ignore probes/probe_stt.py      # loopback: transcript + te-IN
python -W ignore probes/probe_market.py   # verifies all symbols + delay
```

## Run the phone web app
```bash
./run_web.sh            # serves on http://localhost:8000
```
Phone browsers only allow the microphone over **HTTPS**, so expose it with a tunnel:
```bash
brew install cloudflared                      # one-time (or: npm i -g localtunnel)
cloudflared tunnel --url http://localhost:8000
```
Open the printed `https://…trycloudflare.com` URL on your phone, tap the mic, and ask in
Telugu. "Add to Home Screen" installs it as an app (PWA). Typed input is available for
testing without a mic.

## Architecture (one agent loop + guardrails)
```
mic → Prisma STT → planner (JSON) → [advice? → refuse]  [ambiguous ticker? → clarify]
                                   → ticker resolver → data tools (quote/series/news, parallel)
                                   → explainer (Telugu) → numeric provenance gate
                                   → advice/prediction output guard → Timbre TTS (sentence-chunked)
Tier-1 glossary answers concept questions directly (no LLM generation).
Every answer: as-of date + "Not advice" disclaimer, shown and spoken.
```
- **Two deterministic short-circuits run before the LLM:** advice → refusal, ambiguous
  prefix ("HDFC") → clarify. Guardrails work even if the LLM is down.
- **No order-placing tool exists** anywhere (the strongest guardrail).
- **Numbers:** fetched and computed in code; the gate rejects any digit not in a tool payload.
- **Memory:** session (5-turn ticker carry-over) + long-term prefs; never stores holdings/PAN/Aadhaar.

## Run the evaluation harness
```bash
python -W ignore eval/harness.py     # writes eval/results/{adversarial,metrics}.csv
```
`metrics.csv` is the single source of truth for every published figure. Measured rows are
measured; RAGAS generation metrics, WER, and browser TTFA/E2E are labelled **target**.

## Tests
```bash
python -W ignore -m pytest -q        # 54 offline unit tests
```

## Status
All seven phases are built and run live: data layer, agent core, Tier-1 glossary, guardrails,
phone web app, memory, evaluation harness. Tier-2 hybrid retrieval and Tier-3 are scoped per
the report's cut order. **Measured** results are in `eval/results/metrics.csv`; anything not
yet measured stays labelled **target**. Remaining before submission: the Telugu review (every
Telugu string is `reviewed:false`) and the demo video (`docs/DEMO_SCRIPT.md`). See `CHANGELOG.md`.
