# Expected demo output — STATUS: MEASURED (2026-07-02)

Update discipline (mirrors `benchmark/datasets/CHANGELOG.md`): **never
overwrite silently.** Updates require a one-line dated reason appended to
the history below.

## Baseline history

- **2026-07-02** — First real baseline. Pipeline: `StructuredFormalizer`
  (Intervention 1B, parser-first) → `SolverAttempter` (exhaustive
  optimality search, `kernel/edge_ai_solver.py`) → `DeterministicExecutor`
  → `OptimalityVerifier`. Not the LLM-attempter pipeline (that path was
  run first, produced Open on this instance, and is superseded — see
  `demo/actual_output.md`'s history for that record).

---

## Result

**Trust label: Verified.**

**Formalization** (source: `parser`, zero LLM calls):
- Models: XGBoost, KNN, SVM-linear, DecisionTree, CNN — all 5 extracted
  correctly from the messy text (2 distractor sentences ignored).
- Budgets: RAM 3.7GB (converted from the source's stated 3789MB), FLOPS
  92 GFLOPS, latency 123ms.
- High-accuracy threshold: 0.9.

**Solved deployment:** KNN ×3, SVM-linear ×2 (all others ×0). Score **3249**
— exact match to the dataset's ground-truth optimum.

**Certificate:** `exhaustive_feasible_region_search`, certifying
optimality over all feasible integer deployments under the extracted
spec. Independently rechecked: **accepted** — "feasible, consistent, and
optimal."

**Why XGBoost isn't in the plan** (the demo's key narrative beat, still
true): XGBoost has the single highest per-unit accuracy (0.96) of any
model in the catalog, yet the optimal deployment uses zero of it — it's
individually excellent but budget-inefficient at this instance's numbers.
The system optimized, it didn't pattern-match on accuracy.

**Instrumentation:** peak RSS 27.6–27.7 MB (run-to-run noise; see
`research/V1_validation/RESULTS.md`'s reproducibility note), solve time
sub-millisecond. This is one instance (`edge-00000-messy`) drawn from a
60-problem run at 100% Verified-Correct, 0% false certification.

## Scope note (carried from the original placeholder, still true)

This is the deterministic-solver pipeline, not an LLM reasoning through
the problem — that's the point (Guardrail 2: never trust LLM arithmetic
or optimization). It has not been re-validated against paraphrased or
unstructured phrasing of this exact instance; see
`research/I1_validation/RESULTS.md` for what's known about formalization
robustness on this domain more broadly.
