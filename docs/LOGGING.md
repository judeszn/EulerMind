# Frozen Logging Schemas (JSONL, append-only)

Format is JSONL forever. Fields may be **added** under the same
`schema_version`; renaming or removing a field requires bumping the version.
Replay logs are a dataset — the execution-trace corpus (attempts, failures,
verifier signals, repairs) is a long-term asset of the project. Never break it.

## Kernel attempt record — v1 (written by `kernel/loop.py`)

One record per attempt (Guardrail 6: every retry, every execution, every
verifier output). Cost accounting fields let us later answer questions like
"is attempt 3 ever worth it?".

```json
{
  "schema_version": 1,
  "kernel_api_version": 1,
  "problem_id": "lp-00042-messy",
  "attempt": 2,
  "tool": "sympy",
  "verification": "verified | failed",
  "failure_type": null,
  "signals": [{"check": "constraint_1", "violated_by": 12.0}],
  "latency_ms": 823.4,
  "tokens": 194,
  "budget": {"attempts": 3, "timeout_s": 15.0, "ram_gb": 4.0}
}
```

- `failure_type` is one of the frozen taxonomy in `kernel/state.py`:
  `formalization | planning | execution | verification | timeout | memory | unknown`
  (or `null` on success).
- `signals` name **which** check failed and by how much — never a bare fail.
- `budget` is serialized into every record so runs are comparable by
  construction; the kernel never chooses its own budget.

## Benchmark result record — v1 (written by `benchmark/runner.py`)

One record per problem per solver run.

```json
{
  "schema_version": 1,
  "id": "lp-00042-messy",
  "base_id": "lp-00042",
  "category": "optimization_lp",
  "variant": "messy",
  "split": "dev",
  "solver": "oracle",
  "correct": true,
  "trust_label": "Verified",
  "attempts": 1,
  "duration_s": 0.000813,
  "peak_rss_bytes": 19100000
}
```
