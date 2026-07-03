# Actual demo output — from the current build

Regenerated from the current build every time `demo/prompt.md` is run
through the real pipeline (see `demo/README.md` for the update rule —
this file is expected to change, `expected_output.md` is the frozen
baseline it diffs against).

## Run: 2026-07-02, solver pipeline — SUPERSEDES the run below

**Result: Verified.** Matches `demo/expected_output.md` exactly — deploy
KNN ×3, SVM-linear ×2, score 3249, certificate independently rechecked
as accepted.

This used the pipeline built in Validation Phase 1
(`kernel/edge_ai_formalizer_1b.StructuredFormalizer` →
`kernel/edge_ai_solver.SolverAttempter` → `DeterministicExecutor` →
`OptimalityVerifier`), not the LLM-attempter pipeline the earlier run
below used. The earlier failure was real and is kept for the record, not
hidden — it's the diagnostic finding that motivated building the solver
in the first place. Diff against `expected_output.md`: **none.**

---

## Superseded run: 2026-07-02, `llama3.2:1b` LLM-attempter, both H1 arms

**Result at the time: Open (not yet Verified) on both arms.**

The Formalizer in use at the time (pre-Intervention-1B) extracted the RAM
budget as `1`GB instead of `3.7`GB, and fabricated most of the model
catalog rather than transcribing it (e.g. XGBoost's true spec is
`0.76GB/31GFLOPS/0.96acc/66ms`; the formalizer produced
`1.5GB/50GFLOPS/0.98acc/33ms`). FLOPS budget, latency budget, and the
accuracy threshold all came through correctly — the failure was
concentrated in the model catalog and the RAM figure specifically.

This finding is exactly what motivated Intervention 1A/1B (deterministic
parser-first extraction) and, downstream, the solver built for Validation
Phase 1. It is preserved here as the diagnostic record it was, not
because it's still the current state of the demo.
