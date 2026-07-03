"""Sprint Delta-1 Phase 2 — pre-registered model selection rule.

COMMITTED BEFORE ANY ACCURACY RESULT EXISTS (pre-registration: the rule
must provably predate the data it judges — same discipline as every
Gamma experiment).

Rule (from MODEL_CANDIDATES.md, made executable):
  1. s_acc proxy = 100 * gsm8k exact_match (flexible-extract).
     Pre-registered rationale: flexible-extract measures mathematical
     correctness; strict-match additionally measures '#### N' format
     compliance, which would penalize chain-of-thought output styles
     (the known DeepSeek-R1-distill risk) for formatting rather than
     math. Strict-match and arc_easy are REPORTED alongside as sanity
     checks but do not enter the rule.
  2. Predicted S_total = score_model.s_total(s_acc=proxy, tps, ram)
     with tps/ram from the Phase 1 frontier scan (CI run 28683815170),
     african_bonus held equal (0) across candidates, tps_max=15.
  3. Winner = argmax predicted S_total at tps_max=15, UNLESS the
     ranking inverts at tps_max in {25, 50} - in that case, escalate
     for a decision instead of picking silently.

    python3 -m competition.select_model results.json
      where results.json = {model_name: {"gsm8k_flexible": float 0-1,
                            "gsm8k_strict": float 0-1,
                            "arc_easy_acc_norm": float 0-1}, ...}
"""

from __future__ import annotations

import json
import sys

from .score_model import s_total

# Phase 1 frontier measurements [measured, CI run 28683815170]
FRONTIER = {
    "qwen2.5-math-1.5b-instruct": {"tps": 15.02, "ram_gb": 1699.6 / 1024},
    "deepseek-r1-distill-qwen-1.5b": {"tps": 17.34, "ram_gb": 1817.3 / 1024},
    "qwen2.5-1.5b-instruct": {"tps": 15.85, "ram_gb": 1824.8 / 1024},
}

TPS_MAX_SCENARIOS = (15.0, 25.0, 50.0)


def rank(accuracy: dict, tps_max: float) -> list[tuple[str, dict]]:
    rows = []
    for name, hw in FRONTIER.items():
        if name not in accuracy:
            raise KeyError(f"no accuracy result for finalist {name}")
        proxy = 100.0 * accuracy[name]["gsm8k_flexible"]
        rows.append((name, s_total(s_acc=proxy, tps=hw["tps"],
                                   peak_ram_gb=hw["ram_gb"],
                                   african_bonus=0.0, tps_max=tps_max)))
    rows.sort(key=lambda r: -r[1]["s_total"])
    return rows


def select(accuracy: dict) -> dict:
    rankings = {m: rank(accuracy, m) for m in TPS_MAX_SCENARIOS}
    primary = rankings[15.0]
    winner = primary[0][0]
    inverted = any(rankings[m][0][0] != winner for m in TPS_MAX_SCENARIOS[1:])
    return {"winner": None if inverted else winner,
            "escalate_ranking_inverts_across_scenarios": inverted,
            "rankings": {str(m): [(n, r["s_total"]) for n, r in rows]
                         for m, rows in rankings.items()},
            "detail_at_reference": {n: r for n, r in primary}}


def main() -> None:
    accuracy = json.load(open(sys.argv[1]))
    out = select(accuracy)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
