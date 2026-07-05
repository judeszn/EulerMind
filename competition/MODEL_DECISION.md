# Model Decision — RATIFIED (Priority 1 closed)

**Decision: `qwen2.5-math-1.5b-instruct`, GGUF Q4_K_M.**
Ratifies the "pending" recommendation in `MODEL_CANDIDATES.md` using the
full-range `tps_max` sweep below, which resolves the escalation the
pre-registered rule raised. Selection was by measurement through the official
profiler on audit-like x86 CI, never by reputation.

## Why the escalation resolves *for* math (not "it depends")

`select_model.py` escalated because the winner inverts across the three
canned scenarios {15, 25, 50}. But those three points hid the real shape.
Sweeping the whole plausible range (measured TPS/RAM, gsm8k proxy for S_acc,
`african_bonus=0` held equal):

| tps_max | winner | margin (1st−2nd) | math | deepseek | qwen-ctrl |
|---:|---|---:|---:|---:|---:|
| 15 (published anchor) | **qwen2.5-math** | 1.33 | **79.3** | 77.9 | 70.9 |
| 20 | deepseek | 2.15 | 71.8 | 73.9 | 64.7 |
| 25 | deepseek | 1.46 | 67.3 | 68.7 | 59.9 |
| 30 | deepseek | 0.99 | 64.3 | 65.3 | 56.8 |
| 40 | deepseek | 0.41 | 60.5 | 60.9 | 52.8 |
| 50 | deepseek | 0.06 | 58.3 | 58.3 | 50.4 |
| 75 | **qwen2.5-math** | 0.40 | 55.3 | 54.9 | 47.2 |
| 100 | **qwen2.5-math** | 0.63 | 53.8 | 53.1 | 45.7 |

**deepseek wins only a narrow middle band (~18–52), and never by more than
2.15 pts (0.06 at the top of the band). Math wins both ends.** deepseek's edge
is purely its higher raw TPS (17.34 vs 15.02) buying S_perf while S_perf is
uncapped; as `tps_max` grows that difference vanishes and math's constant
accuracy+efficiency lead takes over.

## The five ratification reasons

1. **Wins the only *published* anchor.** At `TPS_REFERENCE=15`, math = 79.26,
   the top score.
2. **Wins the realistic high-`tps_max` world.** A-05 ("max observed across
   teams") will land high because tiny fast models exist — the scan measured
   SmolLM2-135M at **91.77 TPS**. At `tps_max=100`, math wins (53.8 vs 53.1).
   The deepseek band requires `tps_max ∈ (17, 52)` — the *least* likely
   outcome given a 135M can push it to ~90.
3. **Never trails on the 50%-weighted accuracy axis.** gsm8k proxy: math 68% ≥
   deepseek 66% ≥ control 52%. (68 vs 66 = 1 question of 50, ±6.7pt stderr —
   a statistical *tie* with deepseek; the +16 vs the control is the real
   signal that 1.5B-math is the right tier.)
4. **Every qualitative / product surface favors it.** Concise math-tuned
   output parses cleanly into the Σ2 tutor lane's `## sections` + `FINAL
   ANSWER:` line, the 2 test prompts, and the deterministic formalizer.
   deepseek's R1 chain-of-thought is verbose, token-hungry, slower wall-clock,
   and harder to constrain — a direct hit to our parse-dependent UX and TAR.
5. **Coherent narrative:** the math-specialized model on the math track.

## Downstream consequences (now locked)

- **Peak RAM ≈ 1.7 GB → S_eff ≈ 76**, far under the 4 GB ceiling. This
  *settles the RAM-target argument by measurement*: the joint optimum is the
  1.5B tier (~1.7 GB), not 4 GB (would forfeit S_eff) and not 0.5B/135M (max
  S_eff but die on the 50%-weighted accuracy). RAM was an output of model
  choice, exactly as argued.
- `app/tutor.py::discover_server` already prefers a served model id containing
  `math`/`qwen`, so the running system is consistent with this decision with
  no code change.
- The tutor UX, demo, and eval harness now target this model.

## Single reopening trigger (pre-registered)

Reopen **only if** the organizer resolves A-05 to a rule that puts `tps_max`
inside the (~18–52) band *and* deepseek's ≤2.15-pt edge there is judged to
outweigh reasons 3–5. Any other A-05 resolution (reference=15, or "max
observed" landing high) confirms this decision. Absent that specific trigger:
**locked.**

Evidence: `accuracy_results_ci_28684426883.json` (accuracy, CI run
28684426883), frontier scan CI run 28683815170, `select_model.py` /
`score_model.py` (pre-registered rule + exact formula).
