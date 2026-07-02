# demo/ — the flagship pitch, kept working by every commit

Public name: **"EulerMind Edge AI Optimizer."** Internal category name
(`edge_ai_deployment`) stays out of judge-facing language.

| File | Purpose | Update rule |
|---|---|---|
| `prompt.md` | The pinned instance (`edge-00000-messy`, dataset v1, **dev** split — never holdout) | Frozen. Changing the demo problem is a deliberate decision, logged here if it ever happens. |
| `expected_output.md` | The frozen baseline: what a correct, reviewed run looks like | Never overwritten silently — updates require a one-line dated reason in its own baseline history, same discipline as `benchmark/datasets/CHANGELOG.md`. |
| `expected_trace.jsonl` | Same baseline, machine-readable — reuses the **existing** frozen trace schema (`docs/LOGGING.md`), not a new format | Same rule as `expected_output.md`. |
| `actual_output.md` | Regenerated from the current build on every real run | Expected to change. Demo readiness = diff against `expected_output.md` is empty or an already-accepted diff. |
| `speaker_notes.md` | Live-pitch narrative, what to say and not say | Frozen except for factual updates (measured RAM/latency numbers once Phase 1C produces them). |

## Phase 1C exit criterion

Not just "a Verified result" — a lucky first-try success proves nothing
about the actual thesis. The recorded/rehearsed run must show a genuine
**attempt → fail → FailureSignal → Policy repair → verified** sequence on
the pinned instance, either because the target model naturally needs more
than one attempt, or via a rehearsed fallback take if it doesn't.

Explanation ("Teacher") is a deterministic template over
`ExecutionState.to_dict()` — no LLM call, no new frozen protocol. Given
Law 1, the one place we can't afford a hallucination risk is the
explanation of how certain we are.

## Verification-integrity gate

`False Verification Rate` on **this pinned instance** = 0% is a hard
release requirement (rehearsed, so achievable). Benchmark-wide
False Verification Rate is a tracked scoreboard metric we try to drive
down via H3, not yet a blanket gate — see `scoreboard.md`.
