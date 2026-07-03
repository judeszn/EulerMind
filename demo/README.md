# demo/ — the flagship pitch, kept working by every commit

**Current state (2026-07-03):** two scenes, one architecture. Scene 1
(`edge_ai_deployment`, public name "Edge AI Optimizer") and Scene 2
(`optimization_lp`, public name "Optimization Advisor") run through the
identical frozen kernel shape — Formalizer → Solver → Verifier →
Independent Checker — proving the shape generalizes, not that it worked
once. Internal category names stay out of judge-facing language.

## What EulerMind is, right now (for anyone picking this up cold)

Three certified reasoning domains, each with its own independently-written
checker agreeing with the primary solver:

| Domain | Certificate correctness | Certificate independence | Proof style |
|---|---|---|---|
| Edge AI Deployment | ✓ Supported | ✓ Supported | Exhaustive enumeration |
| Constraint CSP | ✓ Supported | ✓ Supported | Exhaustive enumeration |
| Optimization LP | ✓ Supported | ✓ Supported | **Theorem-backed** (LP Duality) |

Plus: the whole certification pipeline reproduces byte-for-byte on an
independent machine (different OS, different CPU architecture) — checked
automatically on every push
(`research/D3_independent_reproduction/RESULTS.md`).

Current evidence ladder (`docs/EVIDENCE_PROTOCOL.md`'s six rungs — see
`docs/SCIENTIFIC_STATE.md` for the live, authoritative version of this
table): Architecture ✓ · Implementation ✓ (3 domains) · Internal
reproducibility ✓ · **Independent reproducibility ✓ (certification path)**
· Replicability — Partial at the certificate level, not yet at the
pipeline level · External validation ✗.

One hypothesis was tested and rejected, honestly: verifier-guided retry
does not beat blind retry at the registered configuration (H1,
`whitepaper/HYPOTHESES.md`). That is not part of the current pitch — see
the correction at the top of `speaker_notes.md` before presenting.

| File | Purpose | Update rule |
|---|---|---|
| `prompt.md` | Scene 1's pinned instance (`edge-00000-messy`, dataset v1, **dev** split — never holdout) | Frozen. Changing the demo problem is a deliberate decision, logged here if it ever happens. |
| `expected_output.md` | Scene 1's frozen baseline: what a correct, reviewed run looks like | Never overwritten silently — updates require a one-line dated reason in its own baseline history, same discipline as `benchmark/datasets/CHANGELOG.md`. |
| `expected_trace.jsonl` | Same baseline, machine-readable — reuses the **existing** frozen trace schema (`docs/LOGGING.md`), not a new format | Same rule as `expected_output.md`. |
| `actual_output.md` | Scene 1, regenerated from the current build on every real run | Expected to change. Demo readiness = diff against `expected_output.md` is empty or an already-accepted diff. |
| `lp_scene.md` | Scene 2, self-contained (prompt + walkthrough + result) — `optimization_lp`, pinned instance `lp-00000-clean` | Frozen. Same discipline as `prompt.md`. |
| `speaker_notes.md` | Live-pitch narrative for both scenes, what to say and not say | Frozen except for factual updates. Corrected 2026-07-03 — see the note at its top before using an older copy. |

## Phase 1C exit criterion (historical — scene 1's original bring-up gate)

Not just "a Verified result" — a lucky first-try success proves nothing
about the actual thesis. The recorded/rehearsed run must show a genuine
**attempt → fail → FailureSignal → Policy repair → verified** sequence on
the pinned instance, either because the target model naturally needs more
than one attempt, or via a rehearsed fallback take if it doesn't.

Explanation (`ExplanationRenderer` — named for what it does, not
"Teacher," which invites someone six months from now to make it smarter
i.e. LLM-backed, in the one place that would be worst) is a deterministic
template over
`ExecutionState.to_dict()` — no LLM call, no new frozen protocol. Given
Law 1, the one place we can't afford a hallucination risk is the
explanation of how certain we are.

## Verification-integrity gate

`False Verification Rate` on **this pinned instance** = 0% is a hard
release requirement (rehearsed, so achievable). Benchmark-wide False
Verification Rate is a tracked scoreboard metric, currently 0% across all
three certified verticals (`scoreboard.md`). H3 (formalization checking
to drive this down further if it ever rises) was tested and closed —
**No Verdict** — because no registered split currently has a nonzero
formalization-error base rate to test against
(`whitepaper/HYPOTHESES.md`); not a blanket gate, but nothing is
currently pushing against it either.
