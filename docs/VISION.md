# EulerMind — Frozen Vision (v1.1, 2026-07-02)

A verification-guided mathematical reasoning engine optimized for commodity hardware.

Not a chatbot. Not a tutor. Not a solver. A **Reasoning Engine**.

This document is frozen. Changes require a measured result that contradicts it.
(v1.1: mission reoriented to the official ADTC 2026 rubric; experiment policy
rephrased. See docs/SCORING.md.)

---

## Mission — Guardrail Zero

**Win the Africa Deep Tech Challenge 2026.**

We do not optimize for elegance. We optimize for the highest final judge
score. The objective function is the official rubric — not our guess at it:

> S_total = 0.50·S_acc + 0.30·S_perf + 0.20·S_eff − P_thermal
> (+ African Use Case bonus up to +10; +15% African Language bonus;
> OOM or sandbox crash = disqualification)

The rubric, its strategy implications, and the feature decision matrix live
in `docs/SCORING.md`. Every feature must improve benchmark performance,
demonstration quality, or judge confidence (**artifact required** — it must
be visible in something a judge actually sees), or satisfy a required
infrastructure dependency. Otherwise it is removed within 48 hours of
results landing. Non-goals until after submission live in `future/`.

---

## The Research Question (in service of the mission)

> Can verifier-guided iterative reasoning enable a compact offline
> mathematical model (< 4 GB RAM) to outperform blind resampling
> under identical compute budgets?

This question is our largest S_acc lever and the demo centerpiece; H1 in
`whitepaper/HYPOTHESES.md` is its pre-registered form. Experiment policy:
**a measured negative result is a successful experiment only if it causes
an immediate engineering decision.** The pivot is the success, not the no —
if H1 fails, the blind-resampling loop ships, because it scores higher.

---

## The Three Laws

**Law 1 — Never fabricate certainty.**
Every output carries exactly one trust label: `Verified`, `Derived`, `Heuristic`, `Open`.
Nothing earns `Verified` unless both the solution *and the formalization* passed a
machine check. Verification is relative to the formalization; a verified answer to a
misread problem is still wrong, so formalization checks gate the top label.

**Law 2 — Everything measurable.**
Every feature must improve **verified-correct rate on the full benchmark, subject to
RAM ≤ 4 GB and the per-problem time budget**. (Constrained objective — not a ratio,
not "improve accuracy AND RAM AND latency", which nothing satisfies.) Features that
don't move the primary metric within the constraints are deleted, including on ties.
The measuring instruments (harness, generators, graders) are exempt — the ruler is
not a hypothesis.

**Law 3 — Reasoning before generation.**
The model never writes an answer. It builds one through execution. All arithmetic,
algebra, and constraint checking is executed, never generated.

---

## The Engine (corrected and frozen)

```
                 INPUT (text problem)
                        │
                        ▼
        ┌────────── Reasoning Kernel ──────────┐
        │                                      │
        │   Formalize ◄────────────────┐       │
        │       │                      │       │
        │       ▼                      │       │
        │   Attempt                    │       │
        │       │               (escalation:   │
        │       ▼                patch →       │
        │   Execute               re-derive →  │
        │       │                 re-formalize)│
        │       ▼                      │       │
        │   VERIFY (in the loop)       │       │
        │       │                      │       │
        │       ├─ failure signals ────┘       │
        │       │                              │
        │       ▼ verified, or budget spent    │
        └───────┼──────────────────────────────┘
                ▼
          Trust Labelling
                │
                ▼
        Explanation Layer (from the logged trace only)
                │
                ▼
               User
```

Two deliberate corrections to earlier drafts, frozen here:

1. **The verifier lives inside the loop.** Its failure signals feed the next attempt.
   Only trust labelling happens after the loop. A post-loop verifier is a pass/fail
   gate, and the entire bet (H1) is that feedback beats gating.
2. **The retry path reaches formalization.** The escalation ladder is
   patch → re-derive → re-formalize → change strategy. Formalization error is the
   dominant expected failure mode; it cannot live outside the loop's reach.

## The Four Stages

| Stage | Job | Rule |
|---|---|---|
| Formalizer | Natural language → executable mathematics (variables, constraints, objective, unknowns, units) | Confidence is **derived** (back-translation / redundant-formalization agreement), never self-reported by the model |
| Reasoning Kernel | Attempt → Execute → Observe → Update → Retry | The only loop in the system |
| Verifier | SymPy / Z3 / OR-Tools checks | Returns **failure signals** (which constraint, where), never a bare "wrong" |
| Teacher | Explanation | Never reasons. Explains **from the logged trace, citing artifacts** — a free-generating explainer is a fabrication channel |

## Guardrails (mandatory)

1. Never answer before execution.
2. Never trust LLM arithmetic — always execute.
3. Never hide uncertainty.
4. If verification fails: retry, following the escalation ladder, within budget.
5. If retries are exhausted: return `Open` or `Derived`. Never fake.
6. Everything is logged — every retry, every execution, every verifier output.

## Internal Data Model — Execution State

See `kernel/state.py`. One object flows through the loop:
problem, formalization, attempt #, execution result, verifier result
(with failure signals), trust label, next action, history.

## Phases

- **Phase 0 — Research instrument** (this repo, now): benchmark harness, procedural
  dataset generator, metrics, logging. Nothing else.
- **Phase 1 — Reasoning MVP**: llama.cpp + Qwen2.5-Math-1.5B Q4, Python executor,
  SymPy, Z3, trust labels. Runs under 4 GB. Plus rubric-mandated infrastructure:
  RAM watchdog with hard ceiling (OOM = disqualification), thermal telemetry
  (P_thermal = −10), tokens/sec measurement (S_perf is automated).
- **Phase 2 — Verification feedback (the bet)**: does feedback beat blind retry? → H1.
- **Phase 3 — Formalization research**: back-translation, redundant formalization → H3.
- **Phase 4 — Optimization**: RAM, CPU, quantization, caching.
- **Phase 5 — Hackathon packaging.** Phase 6 — Product. Phase 7 — Vision vertical.

## The Bet

> Can high-quality verifier feedback enable a 1.5B offline model running under a
> 4 GB memory budget to achieve a significantly higher verified solve rate than
> repeated blind sampling with the same compute budget?

If true, EulerMind has a genuine contribution. If false, the harness says so early
and we pivot on evidence. Pre-registered as H1 in `whitepaper/HYPOTHESES.md`.
