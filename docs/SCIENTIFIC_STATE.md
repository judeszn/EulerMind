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
| Internal reproduction — deterministic | ✓ — includes H1b-Gamma-1, found 2026-07-03 to be deterministic (fixed seed pins output at temp 0.6), bit-identical rerun confirmed |
| Sampling-robustness (H1b-Gamma-2) | ✓ tested — verdict robust across 5 seeds; but only **1 of 5 batches was a valid H1b measurement** (mechanism gate seed-fragile), so this is not five independent confirmations (`research/G2b_sampling_robustness/RESULTS.md`) |
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
| H1b-Gamma-2 (sampling robustness) | Completed | **One valid mechanism-compliant measurement, rejected by the registered decision rule. Four additional seed batches did not satisfy the mechanism gate and are not interpretable as H1b evidence. Generality not established.** (Deliberately not compressed to "robust" — four of five batches are non-interpretable, not four confirmations.) | as Gamma-1, seed varied (offsets 0/1000/2000/3000/4000) |
| H2 | **Blocked** (on H1b showing a real effect to compare repair strategies against) | — | — |
| H3 | Untested | — | formalization-checking on residual field-association errors |
| H4 | Untested | — | typed IR vs raw Python |
| H5 | Untested | — | African-language formalization |

## Most important transferable finding (Gamma-2)

**Mechanism activation is itself an experimental variable, not a given.**
"Feedback exists in the prompt" ≠ "the mechanism was exercised." Gamma-2
showed the mechanism gate passing at one seed and failing at four others,
so the pre-interpretation order — *intervention executed → behaviour
changed → certificates sound → only then read statistics* — is not
optional bookkeeping; a single-config mechanism pass does not certify the
mechanism is live in general. Recorded as **PC-2026-07-03b**
(`docs/EVIDENCE_PROTOCOL.md`), pending a second independent confirmation
before promotion to a frozen rule.

**Sharper post-hoc analysis (2026-07-03): the mechanism gate as
operationalized is confounded — it measures TOTAL cross-attempt variation,
not feedback-specific variation.** At batch 0 the blind arm (B2, no
feedback) already varied on 79% of multi-attempt problems from seed alone;
the guided arm (B3) reached 100%. So the gate's "pass" mostly captured
seed-driven sampling variation that was present without any feedback — the
feedback-specific increment was ≤21 points and not cleanly attributable.
The correct gate is **differential: B3-variation minus B2-variation at the
same seeds**, which isolates the feedback-attributable behavioural change
the hypothesis is about. Implication: even Gamma-1's "mechanism live"
established less feedback effect than the raw gate suggested. This is the
key design fix for any PC-2026-07-03b confirmation experiment. (Recorded as
analysis of existing evidence — not a governance change, not a re-run.)

## Open items — NONE currently registered

No experiment carries a filled-in `BEGIN IMPLEMENTATION` Task. Per the
Execution Contract, nothing runs until one does. Candidate next
experiments (each requires registration before execution):

1. **Confirm PC-2026-07-03b** — does mechanism-gate seed-fragility
   reproduce in a second configuration (different domain or temperature)?
   Confirmation would promote the methodological finding to a frozen rule.
2. **Certificate independence** — write a genuinely independent second
   checker (not sharing `solve()`'s logic) and confirm it agrees; would
   move the strongest claim's independence from Partial toward Confirmed.
3. **Independent reproduction** — clone-and-run on a second machine
   (structural; needs an external environment).
4. H3 / H4 / H5 — untested hypotheses (see table above).

Two governance Pending Clarifications stand recorded, awaiting a second
independent implementation each: PC-2026-07-03 (temperature≠stochastic),
PC-2026-07-03b (mechanism-gate fragility).
