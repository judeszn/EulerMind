# ADTC 2026 — Score targets (Sprint Δ0)

Every number below is labeled **[exact]** (published formula), **[measured]**
(we ran it), or **[assumption]** (scenario, not data). Unlabeled numbers are
banned from this file — that is the point of this file.

## The scoring reality (verified against profiler source, 2026-07-03)

The automated components score the **bare GGUF through llama.cpp** —
`llama-bench` for S_perf, `lm_eval` for the automated part of S_acc.
EulerMind's certification kernel is not in the automated path. It earns
credit only through: REPORT.md quality, the demo video, the 2 test
prompts (mechanism unconfirmed — see GAP_ANALYSIS open questions),
cross-disciplinary pairing, and the African Use Case bonus.

**Therefore: model selection is the dominant automated-score lever, and
the kernel is the dominant qualitative-score lever.** Both matter; they
are optimized separately.

## Targets

| Component | Target | Basis |
|---|---|---|
| S_eff | ≥ 80 → peak RAM ≤ 1.4 GB **[exact math]** | A ~1.5B Q4 model + llama.cpp overhead lands ~1.1–1.4 GB **[assumption until CI-measured]**. The 4 GB design ceiling stays as a hard cap; the target is far below it — every GB saved is ~2.9 pts |
| S_perf | ≥ 12 TPS on Standard-Laptop-class x86 **[measure in CI]** | At TPS_REFERENCE=15: 12 TPS → 80 pts. Sensitivity mandatory: same 12 TPS → 48 pts if tps_max=25 **[exact math, assumed tps_max]** |
| S_acc (automated proxy) | Top score among ≤2B candidates on our lm_eval proxy suite **[measure]** | "Accuracy > 92" is meaningless without knowing the hidden task. Target is *relative*: pick the best measured candidate, re-anchor when the official math validation set is obtained |
| P_thermal | 0 **[exact]** | 4 vCPU CPU-only inference on a 135M–2B model is unlikely to sustain >85°C **[assumption until measured]** |
| African bonus | Claim it: `african_alpha_claim: true` + load-bearing SME framing | Math domain problems themed as African SME scenarios (already planned pre-Δ0); REPORT must make the pairing load-bearing, not cosmetic |
| Disqualification risks | OOM = DQ; submitted-vs-audit drift ±25% TPS / ±15% RAM = flag | **This is why measurement happens in CI (x86, 4 vCPU, ~7GB) and not on the arm64 dev machine** |

## Scenario table — all [assumption], for sensitivity only

Fabricated competitor profiles are not intelligence. What IS knowable:
the *structure* of the tradeoff.

| Scenario | What it does to us (tps=12, ram=1.4GB, s_acc_proxy=80, bonus=10) |
|---|---|
| tps_max = 15 (reference holds) | S_total ≈ 90.0 **[exact given assumptions]** |
| tps_max = 25 (someone ships a fast 1B) | ≈ 80.4 |
| tps_max = 50 (someone ships a 360M) | ≈ 73.2 |
| tps_max = 100 (someone games it with a 135M) | ≈ 69.6 |

Consequence **[analysis, not data]**: S_perf is adversarially exposed —
we cannot control tps_max. S_eff and S_acc are not — they're absolute.
So the robust strategy is: **win S_eff (tiny peak RAM) and the
qualitative S_acc (report/demo/use-case), take whatever S_perf gives.**
A knowingly-losing race to the fastest tiny model sacrifices the
accuracy that 50% of the score weights.

## The 4 GB question (answered)

Agreed, and it was already the project's design target (docs/SCORING.md,
pre-Δ0) — but Δ0 sharpens it: 4 GB is the *ceiling*, not the target.
S_eff pays linearly all the way down: 4 GB → 42.9 pts, 1.4 GB → 80 pts.
The target is the smallest peak RAM that clears the accuracy bar, which
the model leaderboard (MODEL_CANDIDATES.md) exists to find empirically.
