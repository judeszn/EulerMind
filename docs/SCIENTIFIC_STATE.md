# EulerMind Scientific State (LIVE — the one mutable doc)

This is the **only** document expected to change with every experiment. It
is the *Knowledge* layer (current best conclusion), derived from the
*Evidence* layer (permanent records: `scoreboard.md`, per-experiment
`research/*/RESULTS.md`, `whitepaper/HYPOTHESES.md` registration+history).

Governance is frozen elsewhere and does not change when this does. Update
this file per the Evidence-vs-Knowledge rule (`docs/EXECUTION_CONTRACT.md`):
a conclusion changes only when a new result is the first valid measurement
of a question **or** explains a discrepancy from prior valid results —
never merely because it is most recent.

_Last updated: 2026-07-03._

## Layers (frozen — the structure, not the state)

- **Architecture / Kernel interfaces** — LOCKED (`docs/VISION.md`, `kernel/api.py`).
- **Governance** — LOCKED: Research Contract v1.0, Evidence Protocol v1.0,
  Trust Taxonomy, Execution Contract v3.1, Evidence Escalation Rule.

## Evidence level (current ceiling)

| Level | Status |
|---|---|
| Architecture | ✓ |
| Implementation | ✓ — two verticals (bounded optimization, constraint CSP) |
| Internal reproduction — deterministic | ✓ |
| Internal reproduction — deterministic (corrected scope) | ✓ — includes H1b-Gamma-1, found 2026-07-03 to be deterministic (fixed seed pins output at temp 0.6), bit-identical rerun confirmed |
| Sampling-robustness (new, distinct question) | ✗ — not tested for any result; requires seed-varied reruns (see `research/G2_csp_h1b/REPRODUCTION.md`) |
| Independent reproduction | ✗ |
| Replication | ✗ |
| External validation | ✗ |

## Certificate properties (reported separately, per protocol)

| Property | Status |
|---|---|
| Certificate correctness | ✓ — 0% false-certification across both verticals; cross-validated vs the benchmark's independently-implemented ground truth |
| Certificate independence | **Partial** — `recheck_certificate` shares `solve()`'s search logic in both verticals; a second, independently-written checker would close this |

## Hypothesis state (Execution Status + Scientific Verdict, separated)

| Hyp | Execution Status | Scientific Verdict | Configuration scope |
|---|---|---|---|
| H0 | Completed | Supported (formalization measurable; deterministic extraction reaches 100% on native format) | edge_ai native phrasing; degrades on unstructured |
| H1a | Completed | Rejected by Registered Decision Rule (no behavioural variation) | llama3.2:1b, temp 0, prompt-appended textual feedback |
| H1b-Gamma-1 | Completed | **Rejected by the Registered Decision Rule** (Δ=+3.85, p=0.79; does not clear Δ≥7/p<0.05), **internally reproduced under the deterministic registered configuration** (bit-identical rerun; the earlier "stochastic/Provisional" label was a misclassification, now corrected). Scope: this exact configuration only | llama3.2:1b, constraint_csp, temp 0.6 fixed-seed, DeterministicPolicy, prompt-appended feedback |
| H1b-Gamma-2 (sampling robustness) | **Planned** (registered, not executed) | — is the H1b-Gamma-1 conclusion robust when seed is the independent variable (varied per rerun)? Different objective, criteria, and configuration from Gamma-1 — a new experiment, not a rerun | as Gamma-1 but seed varied across runs |
| H2 | **Blocked** (on H1b showing a real effect to compare repair strategies against) | — | — |
| H3 | Untested | — | formalization-checking on residual field-association errors |
| H4 | Untested | — | typed IR vs raw Python |
| H5 | Untested | — | African-language formalization |

## Immediate open item

**H1b-Gamma-2 (sampling robustness)** is registered-but-unexecuted: does
the Gamma-1 conclusion survive when the seed is varied per rerun (genuine
independent stochastic draws)? Distinct objective/criteria/config from
Gamma-1 — a new experiment (`research/G2_csp_h1b/REPRODUCTION.md`,
Resolution B). This is the next task that would produce new evidence.
Governance carries one **Pending Clarification (PC-2026-07-03)** awaiting
a second independent implementation before promotion.
