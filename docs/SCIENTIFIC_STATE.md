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
| Sampling-robustness (H1b-Gamma-2) | ✓ tested — only **1 of 5 batches was a valid H1b measurement** (Behaviour Variation Gate seed-fragile), so this is not five independent confirmations (`research/G2b_sampling_robustness/RESULTS.md`) |
| Independent reproduction | ✗ |
| Replication | ✗ |
| External validation | ✗ |

## Certificate properties (reported separately, per protocol)

| Property | Status |
|---|---|
| Certificate correctness | ✓ — 0% false-certification across both verticals; cross-validated vs the benchmark's independently-implemented ground truth |
| Certificate independence — edge_ai (bounded optimization) | **Supported** (Gamma+1, 2026-07-03) — a brute-force checker sharing no search logic with the solver reached identical decisions on all 60 dev certificates, agreeing with a third independent enumeration (benchmark ground truth); controls pass, 0 false-cert (`research/G3_cert_independence/RESULTS.md`). Scope: implementation- + oracle-independent (not a different paradigm), native format, dev split |
| Certificate independence — constraint_csp | **Supported** (Gamma+2, 2026-07-03) — a backtracking checker sharing no search algorithm and no evaluator code with the solver reached identical decisions on all 52 dev certificates (42 SAT + 10 UNSAT, both types), agreeing with a third independent enumeration (benchmark ground truth); controls pass for both cert types, 0 false-cert (`research/G3_cert_independence/RESULTS_CSP.md`). Scope: implementation-independent (different algorithm + different evaluator), not paradigm-independent (no CP/SAT solver used), native format, dev split |

## Hypothesis state (Execution Status + Scientific Verdict, separated)

| Hyp | Execution Status | Scientific Verdict | Configuration scope |
|---|---|---|---|
| H0 | Completed | Supported (formalization measurable; deterministic extraction reaches 100% on native format) | edge_ai native phrasing; degrades on unstructured |
| H1a | Completed | Rejected by Registered Decision Rule (no behavioural variation) | llama3.2:1b, temp 0, prompt-appended textual feedback |
| H1b-Gamma-1 | Completed | **Rejected by the Registered Decision Rule** (Δ=+3.85, p=0.79; does not clear Δ≥7/p<0.05), **internally reproduced under the deterministic registered configuration** (bit-identical rerun; the earlier "stochastic/Provisional" label was a misclassification, now corrected). Scope: this exact configuration only | llama3.2:1b, constraint_csp, temp 0.6 fixed-seed, DeterministicPolicy, prompt-appended feedback |
| H1b-Gamma-2 (sampling robustness) | Completed | **One valid measurement (Behaviour Variation Gate satisfied), rejected by the registered decision rule. Four additional seed batches did not satisfy the gate and are not interpretable as H1b evidence. Generality not established.** (Deliberately not compressed to "robust" — four of five batches are non-interpretable, not four confirmations.) | as Gamma-1, seed varied (offsets 0/1000/2000/3000/4000) |
| H2 | **Blocked** (on H1b showing a real effect to compare repair strategies against) | — | — |
| H3 | Untested | — | formalization-checking on residual field-association errors |
| H4 | Untested | — | typed IR vs raw Python |
| H5 | Untested | — | African-language formalization |

## Most important transferable finding (Gamma-2)

**Behaviour variation is an experimental variable — and it is NOT the same
object as feedback utilization.** "Feedback exists in the prompt" ≠ "the
candidate's behaviour changed," and "behaviour changed" ≠ "feedback caused
the change." Gamma-2 showed candidate outputs varying at one seed and not
at four others, so the pre-interpretation order — *intervention executed →
behaviour varied → certificates sound → only then read statistics* — is
not optional bookkeeping. But note the ceiling on what a variation check
can ever earn: it shows outputs differ, never that feedback produced the
difference. Recorded as **PC-2026-07-03b** (`docs/EVIDENCE_PROTOCOL.md`),
pending a second independent confirmation before promotion to a frozen rule.

**Principle (config-independent, carried forward as knowledge): a
Behaviour Variation Gate measures TOTAL cross-attempt variation and cannot
distinguish sampling-driven from intervention-driven variation.** This is
analytically true, not an empirical finding — attributing variation to the
intervention requires a **differential gate (treatment variation − control
variation at matched seeds)**, since a raw gate also captures the sampling
variation present in the control arm. Consequence: a satisfied raw gate
establishes less about the intervention than a causal reading implies, and
the differential gate is the design fix for a PC-2026-07-03b confirmation
experiment.

The *config-specific numbers* that exhibited this in Gamma (blind-arm
variation magnitude, feedback increment, seed-fragility) are **evidence**
and live only in `research/G2b_sampling_robustness/RESULTS.md` — not
restated here, per Evidence-vs-Knowledge separation. The number is
evidence; the seed-fragility is pending evidence (PC-2026-07-03b); only the
definitional principle above is settled knowledge.

## Open items — NONE currently registered

No experiment carries a filled-in `BEGIN IMPLEMENTATION` Task. Per the
Execution Contract, nothing runs until one does. Candidate next
experiments (each requires registration before execution):

1. **Confirm PC-2026-07-03b** — does Behaviour-Variation-Gate
   seed-fragility reproduce in a second configuration (different domain or
   temperature)? Confirmation would promote the methodological finding to a
   frozen rule. (Design note: use the differential gate B3−B2.)
2. ~~Certificate independence — CSP vertical~~ — **done** (Gamma+2,
   2026-07-03). Both validated verticals (edge_ai, constraint_csp) now
   carry Supported certificate correctness *and* Supported certificate
   independence. Remaining independence scope note: implementation-
   independent (different algorithm + evaluator) in both verticals, not
   paradigm-independent (no ILP or CP/SAT solver used as a third
   paradigm) — judged unnecessary at current problem scale, but a future
   candidate if problem sizes grow beyond exhaustive-search range.
3. **Independent reproduction** — clone-and-run on a second machine
   (structural; needs an external environment).
4. H3 / H4 / H5 — untested hypotheses (see table above).

Two governance Pending Clarifications stand recorded, awaiting a second
independent implementation each: PC-2026-07-03 (temperature≠stochastic),
PC-2026-07-03b (Behaviour-Variation-Gate fragility).

## Gamma — CLOSED · Interpretation Lock v1.0 (2026-07-03)

Frozen. Gamma answered the questions it registered; it is now historical
evidence. This interpretation does not mutate unless a *future registered
experiment directly contradicts it* (the Evidence-vs-Knowledge rule).

1. Gamma did not validate verifier-guided reasoning — it validated
   something narrower (below).
2. Negative results are scientific outputs. Gamma earned three: verifier
   soundness survives; behaviour variation depends on configuration; this
   feedback encoding does not outperform blind retry at the tested config.
3. **Terminology (locked): "Behaviour Variation Gate," never "Mechanism
   Gate."** The gate measures that candidate outputs differ across
   attempts — it does NOT show feedback caused the difference. The old
   name embedded an unearned causal claim.
4. The Behaviour Variation Gate is necessary but not sufficient: passing
   it means attempts are not identical, not that verifier feedback
   affected the candidate.
5. **Strongest validated result is certificate correctness** — 0% false
   certification across two verticals within tested scope. (Not "verifier
   soundness" wholesale: certificate *independence* remains Partial.)
6. Frozen-artifact mapping: "mechanism gate / mechanism_gate / mechanism
   check" inside committed `research/G2_csp_h1b/` and
   `research/G2b_sampling_robustness/` artifacts = the Behaviour Variation
   Gate. Those files are frozen evidence and are NOT edited (Prop 6);
   the term is renamed only in the live/knowledge layer going forward.
