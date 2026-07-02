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

## When uncertain

Ship the version with the higher expected final score.
