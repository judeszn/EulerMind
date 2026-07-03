# The Objective Function — ADTC 2026 Official Rubric

This is the only scoring function we optimize. Sources:
[Challenge page](https://africadeeptech.org/challenge-2026/) ·
[Devpost listing](https://adtc-2026.devpost.com/) ·
[Launch announcement](https://adtc.substack.com/p/the-africa-deep-tech-challenge-2026)

**Corrected 2026-07-03 (Sprint Δ0)** against the live Devpost rules, the
official submission template, and the profiler *source code*
(`github.com/Africa-Deep-Tech-Foundation/adtc-profiler`) — not memory.
Two errors fixed, both material: (1) S_acc was described as purely
judge-panel/qualitative; the real rule is "a combination of
**multiple-choice benchmarks** and qualitative evaluations" — the
automated part runs `lm_eval` against the bare GGUF on a hidden
per-domain validation subset. (2) A "+15% African Language multiplicative
bonus" appeared here that does **not exist** in the official rules —
only the +10 African Use Case bonus is real. H5's competition-priority
ranking was justified partly by that fabricated multiplier and is
re-ranked accordingly (see `docs/SCIENTIFIC_STATE.md`).

## The formula

```
S_total = 0.50 · S_acc  +  0.30 · S_perf  +  0.20 · S_eff  −  P_thermal
          (+ African Use Case bonus, up to +10)
```

| Component | Weight | How it's scored (verified) | What it means for us |
|---|---|---|---|
| S_acc — Accuracy & Quality | 50% | **Mixed**: automated multiple-choice benchmarks (`lm_eval` on the bare GGUF, hidden per-domain subset) + judge-panel qualitative assessment of prompt responses and documentation quality | The automated share is decided by **model selection**, full stop — the kernel is not in that path. The qualitative share is where REPORT.md, the demo, and the certification evidence earn. |
| S_perf — Throughput | 30% | **Automated**: `llama-bench` generation TPS on the bare GGUF; `S_perf = 100 × TPS_act/TPS_max`, TPS_REFERENCE = 15.0 provisional, TPS_max = max observed across teams | Adversarially exposed — we don't control TPS_max. Sensitivity analysis mandatory (`competition/score_model.py`). |
| S_eff — Efficiency | 20% | **Automated, exact**: `S_eff = 100 × ((7 GB − peak RAM) ÷ 7 GB)` | Linear all the way down: ~2.9 pts/GB saved. 4 GB is the ceiling, not the target — target the smallest model that clears the accuracy bar. |
| P_thermal | −10 | Temp > 85°C or throttling flagged, else 0 | Low risk for small CPU-only models; confirmed only by measurement. |
| **Disqualification** | — | **OOM or sandbox crash = disqualified** | A RAM watchdog is not infrastructure vanity; it is existence. |
| **Audit drift** | flag/fail | Submitted numbers vs audit VM re-measurement: ±25% TPS, ±15% RAM tolerance (profiler `comparator.py`) | Measure on audit-like x86 CI, never on the arm64 dev machine. |
| African Use Case | +10 | Judge-awarded; `african_alpha_claim` in metadata.json + load-bearing cross-disciplinary pairing | Theme demo/dataset problems as African SME scenarios — nearly free points, must be load-bearing not cosmetic. |
| ~~African Language +15%~~ | — | **Does not exist in the official rules** — removed 2026-07-03 | H5 remains a valid research question; it is no longer a competition-scoring lever. |

## Guardrail Zero (frozen)

We do not optimize for elegance. We optimize for the highest final judge
score. Every experiment must measurably improve benchmark performance,
demonstration quality, judge confidence, or satisfy a required
infrastructure dependency. If it improves none of these, it is removed
within 48 hours of results landing.

**The artifact rule (closes the Goodhart backdoor):** a "judge confidence"
claim must point to an artifact a judge will actually see — a scene in the
demo, a section of the docs, a slide, a line in the submission. Invisible
to judges = does not improve judge confidence, by definition.

**Kill velocity:** idea → experiment → decision → delete/keep → next idea.
The 48-hour clock starts when results land (compute time doesn't count —
a paired run on 4 GB hardware can take a day of wall-clock by itself).

## Required infrastructure (rubric-mandated, not optional)

- RAM watchdog + hard ceiling (OOM = disqualification)
- Thermal telemetry in the harness (P_thermal = −10)
- Tokens/sec measurement on target-class hardware (S_perf is automated)

## Feature decision matrix

Every proposed feature gets a row before it gets a branch.
(+++ strong, + weak, 0 none, − negative)

| Feature | S_acc (50%) | S_perf (30%) | S_eff (20%) | Demo/Judge artifact | African bonus | Keep? |
|---|---|---|---|---|---|---|
| Verifier feedback loop (H1) | +++ | 0 | 0 | +++ (failed→signal→repaired scene) | + | ✅ |
| Trust labels in UI | ++ (UX, live defense) | 0 | 0 | +++ | 0 | ✅ |
| Replay/trace logs | + (docs, defense) | 0 | 0 | +++ (the demo IS a trace) | 0 | ✅ |
| RAM watchdog | 0 | 0 | + | + (judge confidence: no DQ) | 0 | ✅ required |
| Thermal telemetry | 0 | 0 | 0 | + | 0 | ✅ required |
| African-themed problem set (demo) | + | 0 | 0 | ++ | ++ | ✅ cheap |
| African language capability | ? | −? | −? | ++ | +++ (×1.15) | 🔬 research row, 48h scoping |
| Typed IR (H4) | ? | 0 | ? | 0 | 0 | 🔬 pre-registered, benchmark decides |
| General reasoning kernel abstractions | 0 | 0 | − | 0 | 0 | ❌ → future/ |
| Enterprise SDK / plugin system | 0 | 0 | − | 0 | 0 | ❌ → future/ |

## Experiment policy (replaces all earlier phrasings)

A measured negative result is a successful experiment **only if it causes
an immediate engineering decision.** The pivot is the success, not the no.
