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
`prompt.md`, `expected_output.md`, `speaker_notes.md` — pinned to a **dev**
split instance, never holdout (holdout is run once per phase gate; a demo
instance gets rehearsed on every commit, so it can never be the holdout
copy).

**Demo priority is a tiebreaker among benchmark work, not a fourth gate
replacing the others above.** S_perf and S_eff are 50% of the score,
automated, and demo-independent — a RAM watchdog doesn't improve the demo
narrative, it prevents the OOM that disqualifies regardless of how the
demo looked. When two benchmark-improving changes are otherwise equal,
prefer the one that makes `demo/prompt.md`'s pinned run more solid.
