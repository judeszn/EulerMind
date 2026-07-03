# H1b-Gamma-1 Reproduction — STOPPED: registered task cannot achieve its objective

**Date:** 2026-07-03 · Registered task: execute N=3 confirmatory reruns of
H1b-Gamma-1 at identical configuration to establish internal
reproducibility.

**Outcome: STOPPED after diagnosis + 1 confirming rerun, per Conflict
Resolution.** The task as registered cannot achieve its stated scientific
objective, for a reason that also corrects a classification in the
scientific state.

## Registered Configuration (recorded per protocol)

| Field | Value |
|---|---|
| Model | llama3.2:1b (Ollama 0.30.10) |
| Temperature | 0.6 (both arms) |
| Seed strategy | `seed=state.attempt` (fixed: attempt 1→seed 1, 2→2, 3→3) |
| Benchmark / Dataset | `benchmark/datasets/v1`, constraint_csp dev, 52 problems |
| Policy | B2 `policy=None`; B3 `DeterministicPolicy` |
| Feedback encoding | prompt-appended failure-signal text (B3 only) |
| Executor / Verifier / Certificate | `DeterministicCSPExecutor` / `CSPCertifyingVerifier` / SAT-assignment or minimal-conflict |
| Hardware / Software | Darwin arm64, Python 3.11.13 |
| Code drift since committed result (754df5a) | **none** — every experiment-relevant file byte-identical |

## The finding

**Fixed seed + temperature 0.6 is deterministic across process
invocations** — verified two independent ways:

1. Isolated call test: the same prompt at `seed=1, temp=0.6` returned
   byte-identical output on three separate calls.
2. Full-experiment rerun: reproduced the committed result **bit-for-bit**
   — Δ=0.0385, McNemar p=0.790527, B2=0.1923, B3=0.2308 (committed:
   identical to all digits).

Every other stage is already deterministic (parser formalizer — 0 LLM
fallback on this dataset; exhaustive solver; rule-table policy). The only
entropy source is the LLM call, and the fixed per-attempt seed pins it.
**Therefore the entire G2 experiment is deterministic, not stochastic.**

## Why this stops the registered task

H1b-Gamma-1 was classified two reviews ago as a **stochastic** result
(rationale: "temperature > 0"), and marked PROVISIONAL pending N=3
stochastic-stability reruns. That classification is **wrong**: temperature
> 0 *with a fixed seed* is deterministic. Consequences:

- **N=3 identical-configuration reruns are bit-identical.** Running three
  is not meaningfully different from running one; "3/3 agree" would be a
  tautology, not evidence of stability. Mechanically completing the N=3
  count would satisfy the task's letter while measuring nothing.
- **The question N=3 was meant to answer — is the Δ=+3.85 / p=0.79
  conclusion robust to sampling variation, or an artifact of one random
  draw? — is not answerable by identical-seed reruns.** Answering it
  requires *varying* the seed per rerun so each is an independent draw —
  but that changes the registered `seed strategy` field, making it a
  **new experiment**, not a rerun of H1b-Gamma-1. The registered task
  forbids configuration changes; so it structurally cannot reach its own
  objective.

## Evidence produced (real, recorded)

- **Internal reproducibility in the deterministic sense: CONFIRMED.** One
  bit-identical rerun (`report_20260703-073952.json` vs the committed
  `report_20260703-064121.json`). Per the Evidence Protocol's own
  definition, a deterministic result's internal reproducibility *is*
  bit-identical rerun — which is demonstrated. A third and fourth run
  would add nothing a deterministic computation doesn't already
  guarantee.
- Verifier soundness held (0% false-certification), certificates
  rechecked, mechanism gate values reproduced exactly.

## Two resolutions (Conflict Resolution — presented, not silently chosen)

**A. Accept deterministic reproducibility; finalize H1b-Gamma-1's
verdict.** Reclassify the result deterministic; its internal
reproducibility is confirmed (bit-identical); move its Scientific Verdict
from Provisional to its final value — **Rejected by the Registered
Decision Rule** (Δ=+3.85, p=0.79, does not clear Δ≥7/p<0.05), for this
exact configuration. Add a *new, distinct* untested question:
**robustness to sampling variation**, which reproduction never tested and
which is a separate validity concern (statistical-conclusion validity),
not internal reproducibility.

**B. Register a new experiment for sampling robustness.** Vary the seed
per rerun (e.g. `seed = run_index*1000 + attempt`), N pre-registered as a
confirmatory-or-power batch, to test whether the qualitative conclusion
survives independent stochastic draws. This is a *new registered task*
(changes the seed-strategy field), not a rerun — and it is the
scientifically meaningful version of what N=3 was reaching for.

These are not exclusive: A finalizes H1b-Gamma-1 honestly now; B is the
follow-up that actually probes sampling robustness. My recommendation is
**A now, B as a separately-registered next task** — but per Conflict
Resolution I am not choosing unilaterally; awaiting instruction on the
verdict flip and on whether to register B.

## Protocol note (contradictory evidence against a frozen rule's phrasing)

The Evidence Protocol's stochastic-reproducibility rule uses "sampling at
temperature > 0" as the proxy for "stochastic." This experiment is a
controlled counterexample: temperature 0.6 with a fixed seed is
deterministic. The frozen-governance principle permits changes
"contradicted by controlled experimental evidence"; the minimal correction
is to define **stochastic** as *output varies across identical reruns*
(equivalently: temperature > 0 **and no fixed/pinned seed**), not
temperature > 0 alone. Applied minimally in `docs/EVIDENCE_PROTOCOL.md`
with this experiment cited.
