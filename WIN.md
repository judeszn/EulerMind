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
