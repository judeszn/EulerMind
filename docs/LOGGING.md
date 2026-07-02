# Frozen Logging Schemas (JSONL, append-only)

Format is JSONL forever. Fields may be **added** under the same
`schema_version`; renaming or removing a field requires bumping the version.
Replay logs are a dataset — the execution-trace corpus (attempts, failures,
verifier signals, repairs) is a long-term asset of the project. Never break it.

## Kernel attempt record — v2 (written by `kernel/loop.py`)

One record per attempt (Guardrail 6: every retry, every execution, every
verifier output). Cost accounting fields let us later answer questions like
"is attempt 3 ever worth it?".

```json
{
  "schema_version": 2,
  "kernel_api_version": 2,
  "problem_id": "lp-00042-messy",
  "attempt": 2,
  "tool": "sympy",
  "verification": "verified | failed",
  "failure_type": null,
  "signals": [{"kind": "constraint_violation", "location": "constraint_1",
               "evidence": {"lhs": 27.0, "capacity": 15.0, "violated_by": 12.0}}],
  "next_action": "patch",
  "latency_ms": 823.4,
  "tokens": 194,
  "budget": {"attempts": 3, "timeout_s": 15.0, "ram_gb": 4.0},
  "policy": "DeterministicPolicy"
}
```

- `failure_type` is one of the frozen taxonomy in `kernel/state.py`:
  `formalization | planning | execution | verification | timeout | memory | unknown`
  (or `null` on success).
- `signals` is a list of `FailureSignal`s — `kind`/`location`/`evidence`,
  never a bare fail. **Ownership matters**: the Verifier only certifies
  what failed and how (`evidence`); it never decides `repair_scope` —
  that's `next_action`, computed by `Policy` (see `kernel/api.py`).
- `next_action` is the escalation-ladder decision for the *next* attempt:
  one of `attempt | patch | rederive | reformalize | stop`.
  `policy: null` means the B2 control arm (blind retry — `next_action` is
  always `"attempt"`, no signal ever changes it). A named policy class
  means the B3 treatment arm.
- `budget` is serialized into every record so runs are comparable by
  construction; the kernel never chooses its own budget.

**v1 -> v2 change:** `signals` shape changed from ad hoc `{"check": ...}`
dicts to `{"kind", "location", "evidence"}`; added `next_action` and
`policy` fields. Historical v1 trace files in the repo are left as-is
(immutable) and are read as v1 records, not silently reinterpreted.

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
