# The Objective Function — ADTC 2026 Official Rubric

This is the only scoring function we optimize. Sources:
[Challenge page](https://africadeeptech.org/challenge-2026/) ·
[Devpost listing](https://adtc-2026.devpost.com/) ·
[Launch announcement](https://adtc.substack.com/p/the-africa-deep-tech-challenge-2026)

## The formula

```
S_total = 0.50 · S_acc  +  0.30 · S_perf  +  0.20 · S_eff  −  P_thermal
          (+ African Use Case bonus, up to +10)
          (+15% for African Language capability)
```

| Component | Weight | How it's scored | What it means for us |
|---|---|---|---|
| S_acc — Accuracy & Quality | 50% | **Judge panel, qualitative**: cross-disciplinary integration, software UX, live defense, prompt accuracy, documentation quality | Half the score is humans. The demo, the docs, the trust labels, and the live defense ARE the primary metric — not a bonus. |
| S_perf — Throughput | 30% | **Automated**: tokens/sec on standard target laptops, relative to max observed | Favors small quantized models + tuned llama.cpp CPU inference. Measured mechanically; our latency profiling maps to this. |
| S_eff — Efficiency | 20% | **Automated**: rewards lower RAM relative to the memory budget | Our 4 GB design target under the 8 GB budget is now rubric-optimal, not just discipline. Every MB saved scores. |
| P_thermal | −10 | Core/package temp > 85°C or thermal throttling flagged | Sustained retry loops are a thermal risk. Budget caps protect the score directly. |
| **Disqualification** | — | **OOM or sandbox crash = disqualified** | A RAM watchdog is not infrastructure vanity; it is existence. |
| African Use Case | +10 | Applicability to a real African use case | Theme demo/dataset problems as African SME scenarios (production scheduling, agri-logistics) — nearly free points. |
| African Language | +15% | Multiplicative bonus | Large. Feasibility on a 1.5B model is unknown → registered as a research row, not assumed. |

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
