# Measured results — for the project report

**Audience:** you, filling Section 10/13 of the report. Every number here is copied from the
committed file `eval/results/metrics.csv`, produced by `eval/harness.py` on the working build.
Do not quote any figure that isn't in that CSV. "Target" rows are thresholds, not results.

_Last harness run: 2026-11-08. Demo language: Telugu (te-IN)._

## Measured (from the working build)
| Metric | Result | Note |
|---|---|---|
| Routing accuracy (40-case adversarial suite) | **100%** (40/40) | all categories correct |
| **Refusal accuracy** (18 advice cases) | **100%** (18/18) | target 100% — met |
| **Numeric hallucination rate** | **0** / 10 answer turns | target 0 — met |
| Ticker resolution accuracy | **100%** (16/16) | target ≥90% — met |
| Glossary retrieval (Tier-1) P@1 / MRR@5 / nDCG@5 | **1.0 / 1.0 / 1.0** | 8 labelled concept queries |
| Tier-2 hybrid retrieval P@1 / MRR@5 / nDCG@5 | **1.0 / 1.0 / 1.0** | 8 labelled note queries (BM25+dense+RRF) |
| LLM-path latency (agent) median / p90 | 1.49 s / 3.67 s | see caveat ↓ |

## Targets (NOT yet measured — state as targets, not results)
| Metric | Target | Why not measured |
|---|---|---|
| Faithfulness | ≥0.95 | needs RAGAS / LLM-judge harness |
| Answer relevancy | ≥0.85 | needs RAGAS |
| Context precision / recall | ≥0.75 / ≥0.80 | needs RAGAS |
| Time to first audio (TTFA) | ≤2.0 s | measured in the browser, per session |
| End-to-end latency | ≤3.5 s | measured in the browser |
| Word error rate (WER) | report only | needs 5 human-recorded Telugu clips |

## Honest caveats to include verbatim
- **Latency** figures were measured under Gemini **free-tier rate-limiting** and may include
  429 retry backoff; they are an upper bound, not true model latency. Clean single-request
  probes were ~1.5–2.7 s per LLM call. TTFA/E2E must be reported from the browser.
- **23 of 40** suite cases are handled by **deterministic short-circuits** (advice → refuse,
  ambiguous ticker → clarify) with **no LLM call** — faster and safer, and the reason the
  median latency is low.
- **Tier-2** is built and evaluated with BM25+dense+RRF+metadata+query-rewrite; the
  **cross-encoder reranker is deferred** (first item in the report's cut order). Tier-3 and
  graph retrieval remain designed-but-not-implemented.
- All Telugu strings are **draft (`reviewed:false`)** pending native-speaker review.

## Build status for Section 13
Built & run live: data layer, agent core, Tier-1 glossary, Tier-2 hybrid retrieval, all four
guardrail layers, phone web app, three-tier memory, evaluation harness. Deferred: Tier-2
reranker, Tier-3 (HyDE / corrective / self-critique), graph retrieval, languages beyond Telugu.
