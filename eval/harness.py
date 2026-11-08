"""Evaluation harness — runs the adversarial suite, ticker and retrieval evals, computes
metrics, and writes committed CSVs. Every published figure must come from these files.

Run:  python -W ignore eval/harness.py
Writes: eval/results/adversarial.csv (per case) and eval/results/metrics.csv (summary).
Metrics not yet measurable (RAGAS generation metrics, WER, browser TTFA/E2E) are written
with status 'target' — never presented as achieved.
"""
from __future__ import annotations

import csv
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import adversarial as adv  # noqa: E402
from vaani import config  # noqa: E402
from vaani.agent import orchestrate, ticker_resolver  # noqa: E402
from vaani.retrieval import tier1, tier2  # noqa: E402

RESULTS = Path(__file__).resolve().parent / "results"


def run_adversarial(throttle: float = 5.0):
    rows, latencies = [], []
    for cid, cat, text, expected in adv.CASES:
        t0 = time.monotonic()
        try:
            a = orchestrate.handle(text)
            routing, gate, tmpl, err = a.routing, a.gate_ok, a.used_template, ""
        except Exception as exc:  # a hard API failure shouldn't kill the whole run
            routing, gate, tmpl, err = "error", None, False, f"{type(exc).__name__}: {exc}"[:120]
            print(f"  #{cid} ERROR: {err}")
        dt = round(time.monotonic() - t0, 2)
        latencies.append(dt)
        rows.append({
            "id": cid, "category": cat, "question": text, "expected": expected,
            "actual": routing, "pass": routing == expected,
            "gate_ok": gate, "used_template": tmpl, "agent_s": dt, "error": err,
        })
        # Throttle to respect the free-tier per-minute request limit. Instant
        # (keyword-refused) cases need no cooldown.
        if routing != "refuse" or err:
            time.sleep(throttle)
    return rows, latencies


def run_ticker():
    correct = 0
    for text, expected in adv.TICKER_CASES:
        r = ticker_resolver.resolve(text)
        got = r.symbol if r.status == "resolved" else r.status
        correct += int(got == expected)
    return correct, len(adv.TICKER_CASES)


def run_retrieval(cases, index_query, k: int = 5):
    """Binary-relevance P@1, R@k, MRR@k, nDCG@k over labeled queries."""
    p1 = r_at_k = mrr = ndcg = 0.0
    n = len(cases)
    for q, gold in cases:
        ids = index_query(q, k)
        rank = ids.index(gold) + 1 if gold in ids else 0
        p1 += 1.0 if ids[:1] == [gold] else 0.0
        if rank:
            r_at_k += 1.0
            mrr += 1.0 / rank
            ndcg += 1.0 / math.log2(rank + 1)      # IDCG = 1 (single relevant doc)
        time.sleep(1.5)                            # gentle on the embeddings quota
    return {"p_at_1": round(p1 / n, 3), "recall_at_5": round(r_at_k / n, 3),
            "mrr_at_5": round(mrr / n, 3), "ndcg_at_5": round(ndcg / n, 3)}


def main() -> int:
    if not config.have_llm() or not config.have_gnani():
        print("Need GNANI + LLM creds in .env to run the full harness.")
        return 2
    RESULTS.mkdir(parents=True, exist_ok=True)

    print("Running adversarial suite (40 cases, live)…")
    rows, lat = run_adversarial()
    with open(RESULTS / "adversarial.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    # --- metrics ---
    total = len(rows)
    routing_acc = sum(r["pass"] for r in rows) / total
    advice_rows = [r for r in rows if r["category"] in adv.ADVICE_CATEGORIES]
    refusal_acc = sum(r["actual"] == "refuse" for r in advice_rows) / len(advice_rows)
    answer_rows = [r for r in rows if r["actual"] == "answer"]
    hallucinations = sum(1 for r in answer_rows if r["gate_ok"] is False)
    tick_c, tick_n = run_ticker()
    gloss = run_retrieval(adv.RETRIEVAL_CASES, lambda q, k: [h.entry.id for h in tier1.query(q, k)])
    t2 = run_retrieval(adv.TIER2_CASES, lambda q, k: [h.doc.id for h in tier2.query(q, k)])

    # Latency: report the LLM-path cases only (median/p90). The deterministic short-circuits
    # (advice, ambiguous) are ~0s and would drag the median to 0. NOTE: these figures were
    # measured under free-tier rate-limiting and INCLUDE 429 retry backoff — not true latency.
    llm_lat = sorted(x for x in lat if x > 0.1)
    instant = sum(1 for x in lat if x <= 0.1)
    median_lat = llm_lat[len(llm_lat) // 2] if llm_lat else 0.0
    p90_lat = llm_lat[int(len(llm_lat) * 0.9)] if llm_lat else 0.0
    lat_note = "measured under free-tier rate-limiting (INCLUDES 429 retry backoff; not true latency)"

    measured = [
        ("routing_accuracy", round(routing_acc, 3), "—", "measured"),
        ("refusal_accuracy", round(refusal_acc, 3), "1.0", "measured"),
        ("numeric_hallucination_rate", round(hallucinations / max(1, len(answer_rows)), 3), "0", "measured"),
        ("ticker_resolution_accuracy", round(tick_c / tick_n, 3), ">=0.90", "measured"),
        ("glossary_precision_at_1", gloss["p_at_1"], "—", "measured"),
        ("glossary_mrr_at_5", gloss["mrr_at_5"], "—", "measured"),
        ("glossary_ndcg_at_5", gloss["ndcg_at_5"], "—", "measured"),
        ("tier2_precision_at_1", t2["p_at_1"], "—", "measured"),
        ("tier2_mrr_at_5", t2["mrr_at_5"], "—", "measured"),
        ("tier2_ndcg_at_5", t2["ndcg_at_5"], "—", "measured"),
        ("median_llm_path_latency_s", median_lat, "—", lat_note),
        ("p90_llm_path_latency_s", p90_lat, "—", lat_note),
        ("instant_short_circuit_cases", instant, "—", "measured"),
    ]
    targets = [
        ("faithfulness", "", ">=0.95", "target (RAGAS, not yet measured)"),
        ("answer_relevancy", "", ">=0.85", "target (RAGAS, not yet measured)"),
        ("context_precision", "", ">=0.75", "target (RAGAS, not yet measured)"),
        ("context_recall", "", ">=0.80", "target (RAGAS, not yet measured)"),
        ("time_to_first_audio_s", "", "<=2.0", "target (measured in browser)"),
        ("end_to_end_latency_s", "", "<=3.5", "target (measured in browser)"),
        ("word_error_rate", "", "report", "target (needs human-recorded clips)"),
    ]
    with open(RESULTS / "metrics.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value", "target", "status"])
        w.writerows(measured + targets)

    # --- console summary ---
    print(f"\nrouting_accuracy            {routing_acc:.1%}  ({sum(r['pass'] for r in rows)}/{total})")
    print(f"refusal_accuracy            {refusal_acc:.1%}  ({sum(r['actual']=='refuse' for r in advice_rows)}/{len(advice_rows)} advice cases)")
    print(f"numeric_hallucination_rate  {hallucinations}/{len(answer_rows)} answers")
    print(f"ticker_resolution_accuracy  {tick_c}/{tick_n}")
    print(f"glossary P@1 / MRR@5 / nDCG@5  {gloss['p_at_1']} / {gloss['mrr_at_5']} / {gloss['ndcg_at_5']}")
    print(f"tier2    P@1 / MRR@5 / nDCG@5  {t2['p_at_1']} / {t2['mrr_at_5']} / {t2['ndcg_at_5']}")
    print(f"LLM-path latency median/p90  {median_lat}s / {p90_lat}s  (incl. rate-limit backoff)")
    fails = [r for r in rows if not r["pass"]]
    if fails:
        print("\nMISROUTED:")
        for r in fails:
            print(f"  #{r['id']} [{r['category']}] expected {r['expected']} got {r['actual']}: {r['question']}")
    print(f"\nWrote {RESULTS/'adversarial.csv'} and {RESULTS/'metrics.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
