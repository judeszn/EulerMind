# research/ — the experiment quarantine

Every experiment lives here, one directory per pre-registered hypothesis
(`H1/`, `H2/`, ...), matching `whitepaper/HYPOTHESES.md`. Each directory
holds the experiment's config, run scripts, traces, and a RESULTS.md with
the paired-comparison verdict (`benchmark.metrics.compare_paired`).

Rules:
- Nothing experimental is imported by `kernel/` or `benchmark/`.
- An experiment graduates into `kernel/` only after a keep verdict
  (better, McNemar p < 0.05) on dev — and survives the holdout gate.
- Killed experiments keep their RESULTS.md (negative results are results)
  and their code is deleted, not commented out.
