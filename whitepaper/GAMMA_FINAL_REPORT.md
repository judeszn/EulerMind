# Phase Gamma — Final Report (FROZEN, 2026-07-03)

**Status: frozen historical record.** Gamma is officially complete. Future
work cites this report and the artifacts it points to; it does not edit
them. A future registered experiment that contradicts a conclusion here
updates `docs/SCIENTIFIC_STATE.md` with an explanation — this report stays
as written, per the Evidence-vs-Knowledge rule (`docs/EXECUTION_CONTRACT.md`).

## 1. Charter

Gamma was not designed to prove that EulerMind "reasons." It was designed
to establish, on a verification-asymmetric domain (constraint CSP:
checking is O(constraints); finding a solution over P(7,5)=2520
permutations is not), whether EulerMind can produce **trustworthy
certified results** — and whether verifier feedback measurably improves a
small LLM's retry behaviour (H1). It inherited the edge_ai (bounded
optimization) vertical's prior validation
(`research/V1_validation/RESULTS.md`) as its starting evidence base.

## 2. The four evidence questions Gamma registered, and their answers

| Question | Verdict |
|---|---|
| Can deterministic certification produce correct results? | **Supported** — 0% false certification across both verticals, cross-validated against the benchmark's independently-implemented ground truth |
| Can those certificates be independently verified? | **Supported** — independently-written checkers (no shared search logic) agree 60/60 (edge_ai) and 52/52 (constraint_csp) with the production checkers and with a third oracle |
| Does verifier-guided retry outperform blind retry in the registered configuration? | **Rejected by the Registered Decision Rule** — Δ=+3.85pts, p=0.79 at the only gate-valid measurement; no seed produces a guided advantage near the kill threshold (Δ≥7, p<0.05) |
| Were all claims scoped honestly and protocol-governed? | **Supported** — every claim states its exact tested configuration; two overreaches were caught and corrected in-phase (§7) |

A phase that answers its registered questions — including one in the
negative — is complete. Negative results are legitimate endpoints when
the experiment was valid.

## 3. Experiment chronology (evidence pointers)

1. **CSP vertical construction + H1a** (`research/G1_csp_validation/`):
   parser-first CSPFormalizer, exhaustive CSPSolver, certifying verifier,
   SAT-assignment / minimal-conflict certificates. H1a (does feedback
   produce observable behavioural variation?): **no variation detected at
   temp 0** — 42/42 multi-attempt cases, configuration-scoped.
2. **H1b-Gamma-1, temperature-matched** (`research/G2_csp_h1b/`): both
   arms temp 0.6, seed=attempt. Δ=+3.85pts, McNemar p=0.79 — rejected by
   the registered decision rule.
3. **Reproduction correction** (`research/G2_csp_h1b/REPRODUCTION.md`):
   the registered N=3 stochastic reruns were structurally impossible —
   fixed seed at temp 0.6 is bit-deterministic on this stack. Stopped per
   the Conflict Resolution rule; Resolution A reclassified the result as
   deterministic (bit-identical rerun confirmed). Recorded as
   PC-2026-07-03, deliberately *not* promoted into frozen governance.
4. **H1b-Gamma-2, sampling robustness**
   (`research/G2b_sampling_robustness/`): seed as the sole variable, N=5
   pre-registered batches. Verdict robust across all seeds; only 1 of 5
   batches satisfied the Behaviour Variation Gate (PC-2026-07-03b);
   post-hoc analysis showed the raw gate conflates sampling variation
   with feedback effect (the differential-gate design fix).
5. **Interpretation Lock v1.0**: "Mechanism Gate" renamed **Behaviour
   Variation Gate** in the knowledge layer — the gate shows outputs
   differ, never that feedback caused the difference.
6. **Gamma+1, certificate independence, edge_ai**
   (`research/G3_cert_independence/RESULTS.md`): unpruned brute-force
   checker, no shared search code — 60/60 agreement, 60/60 ground-truth
   match, 0 false-cert, all controls pass. Partial → Supported.
7. **Gamma+2, certificate independence, constraint_csp**
   (`research/G3_cert_independence/RESULTS_CSP.md`): backtracking checker
   (different algorithm *and* different evaluator), both certificate
   types — 52/52 agreement, 52/52 ground-truth match, 0 false-cert, all
   controls pass. Partial → Supported.

Full per-experiment measurements: `scoreboard.md` (the Evidence ledger).
Hypothesis registrations and history: `whitepaper/HYPOTHESES.md`.

## 4. Registered hypotheses — final verdicts

| Hypothesis | Execution | Scientific Verdict |
|---|---|---|
| H1a (feedback → behavioural variation) | Completed | Rejected by the Registered Decision Rule (at temp 0, registered encoding) |
| H1b-Gamma-1 (guided beats blind, gate-valid) | Completed | Rejected by the Registered Decision Rule; internally reproduced (deterministic) |
| H1b-Gamma-2 (verdict robust to sampling) | Completed | Robustness Supported — one gate-valid measurement, rejected; four batches non-interpretable (gate failed); generality not established |
| H-Independence (edge_ai) | Completed | Supported |
| H-Independence-CSP | Completed | Supported |
| H2 (patch vs rewrite) | Blocked (needs an H1b effect to compare against) | — |

## 5. Negative results as outputs

Gamma produced three findings that are *earned knowledge*, not failures:

1. **Certificate soundness survives everything thrown at it** — 0% false
   certification across two verticals, ten arm-runs, five seeds, and two
   independently-written checkers per vertical.
2. **Behaviour variation depends on configuration** — at temp 0.6,
   llama3.2:1b is only weakly stochastic; most seed triples collapse to
   identical outputs. A gate that passes at one seed may fail at others.
3. **This feedback encoding does not outperform blind retry at the tested
   configuration** — prompt-appended textual failure signals, llama3.2:1b,
   3-attempt budget. Scoped exactly; no claim about other encodings,
   models, or budgets.

## 6. Evidence hierarchy achieved — the weakest link relocated, not eliminated

Within tested scope, the certification stack has no internal weakest
link: architecture → implementation → certificate correctness →
certificate independence → conclusion, each supported. What remains open
is *who has checked it and where*, not what the pipeline does:

| Level | Status |
|---|---|
| Internal reproduction (deterministic) | ✓ |
| Independent reproduction (second machine) | ✗ |
| Replication (independently-written checker, **different author/environment**) | ✗ — Gamma+1/+2's checkers are independently written but same-author, same-environment; a real step toward replication, not its satisfaction |
| External validation | ✗ |

Scope boundaries that travel with every Gamma claim: dev split only,
native/parser-matched input format, implementation-independence (not
paradigm-independence — no ILP/CP-SAT third paradigm), one model and one
inference stack for all H1 results.

## 7. Methodological lessons (where each now lives)

1. **Verify the failure mode exists before testing the fix.** Gamma-2's
   core lesson: four of five batches could not test H1b because the
   behaviour the intervention needs never occurred. Generalized: any
   experiment claiming "X reduces Y" must pre-register a base-rate
   measurement showing Y occurs at the registered configuration.
   (Applies directly to H3's design — see `docs/SCIENTIFIC_STATE.md`.)
2. **A variation gate must be differential** (treatment − control at
   matched seeds) to attribute anything to the intervention; a raw gate
   measures total variation, which is analytically incapable of
   distinguishing sampling from feedback effect. (Principle in
   `docs/SCIENTIFIC_STATE.md`; magnitudes are evidence in
   `research/G2b_sampling_robustness/RESULTS.md`.)
3. **Classify determinism by observed rerun behaviour, never by
   configuration proxies** like temperature (PC-2026-07-03, pending
   second confirmation).
4. **Decompose hypotheses instead of reporting "untested"** when a
   precondition fails — H1 → H1a + H1b preserved an earned answer.
5. **One implementation's finding does not rewrite frozen governance** —
   the Pending Clarification mechanism exists because this project
   nearly violated its own evidence-escalation rule twice, and caught
   itself both times (the premature protocol edit; the "~79%" number
   nearly frozen as project knowledge).
6. **Evidence / Knowledge / Governance separation** — measurements are
   permanent (`scoreboard.md`, RESULTS files), conclusions live in one
   mutable doc (`docs/SCIENTIFIC_STATE.md`), rules are frozen and change
   only by logged, evidenced exception.

## 8. What Gamma claims — and does not claim

**Claims:** EulerMind produces certified answers on two reasoning domains
whose certificates are correct (0% false certification, cross-validated)
and independently verifiable (no shared search logic), within the tested
scope; and that, at the one registered configuration where the test was
valid, verifier-guided retry did not outperform blind retry.

**Does not claim:** that EulerMind reasons; that feedback cannot help
under other encodings/models/budgets; that the results hold on holdout,
non-native phrasings, other machines, or under checkers written by other
people; that the Behaviour Variation Gate certifies feedback utilization.

## 9. Citation rule

This report and every artifact it cites are frozen. Delta experiments
cite Gamma; they do not reopen, rerun, retune, or reinterpret it. New
evidence about a Gamma question goes through a new registered experiment
and updates `docs/SCIENTIFIC_STATE.md` — never this file.
