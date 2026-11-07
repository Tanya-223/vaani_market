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

## Status
Phases 1–3 and the phone web app (Phase 5) are built and run live. Guardrail finish
(output-side advice check) and the evaluation harness (Phase 7) are next. See `CHANGELOG.md`.
Metric values are **targets** until the evaluation harness produces them.
