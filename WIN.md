# WIN.md — read this before anything else

## Mission

Win the Africa Deep Tech Challenge 2026.

## Definition of winning

Final score > every competing submission. Nothing else.

## Primary constraints

- Runs offline.
- Runs on reference hardware.
- Never exceeds the RAM budget (OOM = disqualification).
- Never crashes.
- Never overheats (>85°C = −10 points).

## Every feature must improve at least one

- [ ] Accuracy (S_acc, 50%, judge panel)
- [ ] Performance (S_perf, 30%, tokens/sec, automated)
- [ ] Efficiency (S_eff, 20%, low RAM, automated)
- [ ] African Use Case (+10 / +15% language)
- [ ] Demo
- [ ] Documentation

Otherwise remove it.

## 48-Hour Rule

Every experiment ends with **KEEP**, **DELETE**, or **DEFER**. No fourth
option. The clock starts when results land.

## Engineering rule

Working software beats elegant software.
Measured software beats argued software.

## Issue format (no feature requests — only score investments)

```
Hypothesis:
Expected score gain (which criterion):
Cost (days):
Risk:
Owner:
Decision date:
```

## The Ladder (the only roadmap)

| Level | Name | Experiment ID |
|---|---|---|
| L0 | Raw Model | B0 |
| L1 | Reasoning Prompt | B1 |
| L2 | Tool-Assisted Reasoning | B2 (H1 control) |
| L3 | Verification-Guided Reasoning | B3 (H1 treatment) |

Every proposed change must answer: **which rung does this improve?**
If none: don't build it.

## No Vertical Optimization

Never optimize one level of the ladder before every level exists as a thin
slice. Thin slices first. Optimization second.

## Scoreboard First

`scoreboard.md` is the heartbeat. Every **measurement** updates it (not
every commit — cells stay `?` until a run fills them; no faked precision).

## No feature code without an experiment

Every feature change states: Hypothesis / Expected gain / Acceptance
metric / Delete threshold. Required infrastructure and bugfixes are exempt
from hypotheses but must cite the rubric constraint they serve
(e.g. RAM watchdog → OOM = disqualification).

## When uncertain

Ship the version with the higher expected final score.

## FROZEN — the vertical slice (2026-07-02)

No new benchmark families. No new architectures. No new model bake-offs.
Finish this, in this order, before anything else:

```
Edge AI Optimizer vertical slice (Phase 1C, edge_ai_deployment ONLY)
  -> demo/ recorded and working
  -> Phase 1D: generalize the executor to LP/CSP/calculus, no UI changes
  -> Phase 1E: measure H1 (must span >=2 categories before the verdict
     is treated as general — see whitepaper/HYPOTHESES.md)
  -> polish
  -> submit
```

Public name: **"Edge AI Optimizer."** Internal category name
(`edge_ai_deployment`) stays internal. `demo/` holds the frozen pitch —
see `demo/README.md` for the file-by-file update discipline — pinned to a
**dev** split instance, never holdout (holdout is run once per phase gate;
a demo instance gets rehearsed on every commit, so it can never be the
holdout copy).

**Phase 1C exit criterion — corrected:** repair *capability* and repair
*shown live* are different requirements, and conflating them made the
exit criterion unsatisfiable the moment the system gets good (a
first-try success would "fail" a rule requiring failure — backwards).
- Capability: proven by tests (already true — Oracle Mode's 28/28
  selftest covers policy-driven repair; Phase 1C re-validates it against
  the real, non-cheating pipeline as ordinary build-and-test work).
- Shown live: a curation decision for `demo/`, not a blocking gate on the
  pinned instance. Use it if it naturally needs a retry; pair it with a
  second rehearsed clip if it doesn't. The engine never intentionally
  fails to satisfy a requirement.

Explanation is a deterministic template over `ExecutionState`, called
`ExplanationRenderer` — not "Teacher," which invites someone to make it
LLM-backed later, in the one place a hallucination would be worst. No new
frozen protocol; `kernel/api.py`'s five stages are unchanged. False
Verification Rate on the pinned instance must be 0% before release (see
`scoreboard.md`).

## Milestones (judge-facing framing of the same phases)

| Milestone | Maps to | What a judge can watch |
|---|---|---|
| 1. Kernel works | Policy wired, Oracle-validated | 28/28 mechanical selftest |
| 2. Kernel solves Edge AI | Phase 1C, B2 (blind retry) | Formalize → attempt → verify, real model |
| 3. Kernel repairs itself | Phase 1C, B3 (guided retry) | FailureSignal → Policy → repair → verified |
| 4. Kernel generalizes | Phase 1D | Same kernel, LP/CSP/calculus adapters |
| 5. Research claim measured | Phase 1E, H1 | Δ Verified-Correct Rate, ≥2 categories |

## Guardrail 14 (corrected to OR, matching Guardrail Zero)

No feature is finished until it changes at least one of: `benchmark/`
(a grader/generator), `demo/` (the pinned pitch), `scoreboard.md` (a
cell). Not all three — a harness bug fix doesn't need new demo content to
be real work. The requirement is *observability*, not omnipresence: if a
change can't be measured, demonstrated, or scored anywhere, it didn't
happen. Sharpens Guardrail Zero's existing "artifact required" clause;
doesn't replace it.

**API/protocol discipline continues, not suspended:** no new speculative
architecture discussions, but `kernel/api.py`'s existing freeze rule
(revise freely pre-measurement; after, version-bump + document) still
applies to fixes implementation reveals — exactly the kind that already
surfaced twice while wiring Policy. Building Phase 1C for real, against a
non-cheating model, will surface more of these; fixing them is
engineering, not scope creep.

**Demo priority is a tiebreaker among benchmark work, not a fourth gate
replacing the others above.** S_perf and S_eff are 50% of the score,
automated, and demo-independent — a RAM watchdog doesn't improve the demo
narrative, it prevents the OOM that disqualifies regardless of how the
demo looked. When two benchmark-improving changes are otherwise equal,
prefer the one that makes `demo/prompt.md`'s pinned run more solid.
