# Actual demo output — from the current build

Regenerated from the current build every time `demo/prompt.md` is run
through the real pipeline (see `demo/README.md` for the update rule —
this file is expected to change, `expected_output.md` is the frozen
baseline it diffs against).

## Run: 2026-07-02, `llama3.2:1b`, kernel/edge_ai.py, both H1 arms

**Result: Open (not yet Verified) on both arms.** Honest report per
Guardrail 5 — this is real, measured data, not a placeholder.

### What happened

The Formalizer extracted the RAM budget as `1` GB instead of the true
`3.7` GB (the source text states it as `3789MB`, requiring a unit
conversion — one of the reasons this instance was picked). Worse than a
conversion slip: comparing extracted model stats against the source text
shows the catalog itself was largely **fabricated**, not transcribed —
e.g. XGBoost's true spec is `0.76GB/31GFLOPS/0.96acc/66ms`; the formalizer
produced `1.5GB/50GFLOPS/0.98acc/33ms`. FLOPS budget (92), latency budget
(123), and the accuracy threshold (0.9) all came through correctly — the
failure is concentrated in the model catalog and the RAM figure.

Both B2 (blind retry, 3 attempts) and B3 (guided retry, 3 attempts) failed
to reach Verified, because the Attempter and Verifier were both working
against this same wrong formalization the whole time — no amount of
retrying the *attempt* fixes an error in the *formalization*, which is
exactly why the escalation ladder includes `reformalize` as a rung
`DeterministicPolicy` can reach for. In this run, none of the failure
kinds seen (`constraint_violation` on ram/flops/latency budgets) mapped
to `reformalize` in the current rule table — they mapped to `patch`, then
escalated to `rederive` — because from the Verifier's point of view, the
*execution* looked like ordinary constraint violations. The Verifier has
no way to know the formalization itself, not the proposed counts, is
wrong. This is Law 1's caveat made concrete: verification is relative to
the formalization, and nothing here could see past that boundary.

### What this changes

This is a genuine Milestone 2 finding, not a setback to hide: the
dominant failure mode for the real pipeline is formalization fidelity,
exactly as flagged when L1 was diagnosed and exactly what H3 exists to
test. A broader run (10 bases, 20 problems, both arms) is in progress to
check whether this is instance-specific or systematic — see
`research/H1_edge_ai/` for results once it lands.
