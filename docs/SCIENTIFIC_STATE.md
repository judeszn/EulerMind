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
| Implementation | ✓ — three verticals (bounded optimization, constraint CSP, linear programming) |
| Internal reproduction — deterministic | ✓ — includes H1b-Gamma-1, found 2026-07-03 to be deterministic (fixed seed pins output at temp 0.6), bit-identical rerun confirmed |
| Sampling-robustness (H1b-Gamma-2) | ✓ tested — only **1 of 5 batches was a valid H1b measurement** (Behaviour Variation Gate seed-fragile), so this is not five independent confirmations (`research/G2b_sampling_robustness/RESULTS.md`) |
| Independent reproduction | **✓ — certification path** (Delta D3, 2026-07-03): [GitHub Actions run 28673053751](https://github.com/judeszn/EulerMind/actions/runs/28673053751) on `ubuntu-latest` — crosses OS (macOS→Linux), CPU architecture (arm64→x86_64), Python patch version; all three verticals' reports bit-identical (sha256 match), selftest passed, 0 manual intervention (`research/D3_independent_reproduction/RESULTS.md`). Workflow now runs on every push to `main`. **✗ — LLM-dependent experiments** (Gamma's H1a/H1b/H1b-Gamma-2, which need Ollama) are out of D3's scope by design and remain unreproduced independently |
| Replication | ✗ — pipeline level (D3 is the same code on a second machine, not a second independently-written implementation); Partial at certificate level (the G3/D2 independent checkers already are separately-written implementations agreeing with the primary pipeline, for the narrower "is this answer correct" claim) |
| External validation | ✗ |

## Certificate properties (reported separately, per protocol)

| Property | Status |
|---|---|
| Certificate correctness | ✓ — 0% false-certification across all three verticals; cross-validated vs the benchmark's independently-implemented ground truth |
| Certificate independence — edge_ai (bounded optimization) | **Supported** (Gamma+1, 2026-07-03) — a brute-force checker sharing no search logic with the solver reached identical decisions on all 60 dev certificates, agreeing with a third independent enumeration (benchmark ground truth); controls pass, 0 false-cert (`research/G3_cert_independence/RESULTS.md`). Scope: implementation- + oracle-independent (not a different paradigm), native format, dev split |
| Certificate independence — constraint_csp | **Supported** (Gamma+2, 2026-07-03) — a backtracking checker sharing no search algorithm and no evaluator code with the solver reached identical decisions on all 52 dev certificates (42 SAT + 10 UNSAT, both types), agreeing with a third independent enumeration (benchmark ground truth); controls pass for both cert types, 0 false-cert (`research/G3_cert_independence/RESULTS_CSP.md`). Scope: implementation-independent (different algorithm + different evaluator), not paradigm-independent (no CP/SAT solver used), native format, dev split |
| Certificate independence — optimization_lp | **Supported** (Delta D2, 2026-07-03, first-measurement — no Partial interim stage needed) — the independent checker performs **zero search**, applying the LP Duality Theorem (complementary slackness + strong duality) instead of the solver's Fundamental-Theorem-of-LP vertex enumeration; a different *theorem*, not just a different algorithm. 80/80 agreement (dev+holdout, clean+messy), 80/80 match to `benchmark.metrics.grade()`, 0 false-cert (`research/D2_lp_vertical/RESULTS.md`). Scope: 2-variable LP with exactly 2 resource constraints (the only structure the generator produces) |

## Hypothesis state (Execution Status + Scientific Verdict, separated)

| Hyp | Execution Status | Scientific Verdict | Configuration scope |
|---|---|---|---|
| H0 | Completed | Supported (formalization measurable; deterministic extraction reaches 100% on native format) | edge_ai native phrasing; degrades on unstructured |
| H1a | Completed | Rejected by Registered Decision Rule (no behavioural variation) | llama3.2:1b, temp 0, prompt-appended textual feedback |
| H1b-Gamma-1 | Completed | **Rejected by the Registered Decision Rule** (Δ=+3.85, p=0.79; does not clear Δ≥7/p<0.05), **internally reproduced under the deterministic registered configuration** (bit-identical rerun; the earlier "stochastic/Provisional" label was a misclassification, now corrected). Scope: this exact configuration only | llama3.2:1b, constraint_csp, temp 0.6 fixed-seed, DeterministicPolicy, prompt-appended feedback |
| H1b-Gamma-2 (sampling robustness) | Completed | **One valid measurement (Behaviour Variation Gate satisfied), rejected by the registered decision rule. Four additional seed batches did not satisfy the gate and are not interpretable as H1b evidence. Generality not established.** (Deliberately not compressed to "robust" — four of five batches are non-interpretable, not four confirmations.) | as Gamma-1, seed varied (offsets 0/1000/2000/3000/4000) |
| H2 | **Blocked** (on H1b showing a real effect to compare repair strategies against) | — | — |
| H3 | **CLOSED — No Verdict** (2026-07-03) | First run Inconclusive (degenerate baseline: 100%-reproducible parser defect). After D1 repaired that defect, all four registered splits formalize at ~100% — the intervention has no opportunity to act on any registered distribution. Closed at current scope, not retired as a question. **Reopening trigger (pre-registered): an externally-justified distribution showing a non-degenerate formalization-error base rate re-registers H3 automatically** (direction-of-inference test: data chosen because the mission requires it, never constructed so the hypothesis can run). | all registered splits, post-D1 |
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

## Phase status: Gamma COMPLETE (2026-07-03) · next phase is Delta

**Gamma is officially complete.** Its charter — trustworthy certified
results on a verification-asymmetric domain, plus the H1 question — is
answered, including one valid negative. Final frozen record:
`whitepaper/GAMMA_FINAL_REPORT.md`. Future work cites Gamma; it does not
reopen, retune, or reinterpret it. Explicitly out of bounds: reopening
H1, another prompt/temperature/model at the same question, tweaking Gamma
artifacts, further governance polishing.

**Honest ceiling, carried forward:** the within-scope certification stack
has no internal weakest link, but the weakest link was *relocated, not
eliminated* — independent reproduction (second machine), replication
(checker written by a different author/environment), and external
validation all remain ✗. All Gamma claims are dev-split, native-format,
implementation-independence scope.

## Delta — next phase (declared, nothing registered)

Delta's mission: new scientific questions on top of the validated
foundation — not validating infrastructure (done), not product/UI (needs
evidence worth exposing first). Every Delta experiment must: (1)
investigate a genuinely new hypothesis, (2) leave Gamma's evidence
unchanged, (3) either establish a new capability or cleanly reject one.

No experiment carries a filled-in `BEGIN IMPLEMENTATION` Task. Per the
Execution Contract, nothing runs until one does. Candidates, ranked:

1. ~~H3 — formalization checking reduces verified-wrong outputs~~ —
   **executed 2026-07-03, no verdict (Inconclusive)**
   (`research/H3_formalization_checking/RESULTS.md`). The precondition
   binding note below (about base rate) turned out right for the wrong
   reason: the registered split's base rate wasn't ~0, it was ~100% from
   one systematic defect, which is its own kind of degenerate baseline —
   a lesson worth generalizing: *pre-registering "base rate > 0" is not
   enough; a valid comparison also needs the base rate to be**
   **non-degenerate (neither ~0% nor ~100% from a single cause)**, or
   there's no "preserve the good cases" signal to test against.
2. ~~H3-retry~~ — resolved (2026-07-03 review): D1 done (KEEP, bit-exact
   non-regression, `research/D1_parser_repair/RESULTS.md`); **H3 CLOSED —
   No Verdict at current scope**, reopening trigger pre-registered (see
   hypothesis table). No new benchmark is manufactured for it — the
   **direction-of-inference test** is locked as standing scientific
   judgment: a dataset is justified when chosen because the mission
   requires it, and is benchmark engineering when constructed so a
   hypothesis can run.
3. ~~D2 — optimization_lp vertical~~ — **executed 2026-07-03, Supported**
   (`research/D2_lp_vertical/RESULTS.md`). First theorem-backed
   certification domain (Fundamental Theorem of LP for the solver, LP
   Duality Theorem for the independent checker — two different theorems,
   not two search styles); correctness and independence both Supported
   from first measurement, 80/80 agreement dev+holdout. **Registered
   sequencing (locked): LP was made its own milestone rather than bundled
   with calculus_poly, because it changes the architecture's proof-style
   count (1→2) where calculus would only add a domain within an existing
   style. Next per the locked sequence is Δ3 (independent reproduction,
   CI), then Δ4 (reassess before calculus_poly) — not calculus
   immediately.**
4. ~~Δ3 — Independent reproduction (CI)~~ — **executed 2026-07-03,
   Supported** (`research/D3_independent_reproduction/RESULTS.md`).
   GitHub Actions run crossing OS/architecture/Python-patch-version;
   all three verticals' reports bit-identical, selftest passed. Raises
   the evidence ceiling for edge_ai/CSP/LP simultaneously. Now a standing
   check (`.github/workflows/reproduce.yml` runs on every push to
   `main`), not a one-off. Scope held: certification path only, one
   environment class (Independent Reproducibility, not Replicability).
5. **calculus_poly (Δ4)** — reassessment per the locked sequence: Δ3
   exposed nothing needing repair (0 diffs, all hashes matched
   first-try), and Δ2 (LP) surfaced no architectural weakness (D2
   RESULTS §9's honest-scope notes are all pre-registered, none
   blocking). Both gates the locked sequence required before calculus
   are now clear — calculus_poly is unblocked, pending registration.
6. **H5 — African-language formalization** (portability). Also the
   pre-registered reopening path for H3: its dataset is externally
   justified by the rubric's own +15% bonus, and multilingual
   formalization will have a genuine, non-manufactured error rate.
7. **H4 — typed IR vs raw Python** (representation as the limiting
   factor) — lowest-ranked candidate on both the research and competition
   rankings (2026-07-03 planning review); no current evidence points at
   representation as a bottleneck.

## Transferable findings (Delta, 2026-07-03)

- **The H3-1 → D1 loop is Delta's biggest contribution** — hypothesis →
  measurement → localization → minimal intervention → bit-exact
  regression protection → evidence update, demonstrated end-to-end on the
  project's own code with zero change to any frozen result. The workflow
  is now proven, not aspirational.
- **Field-accuracy metrics are structurally blind to fabricated extras**:
  `score()` computes accuracy only over ground-truth model names, so a
  fabricated pseudo-model is invisible to it by construction; only
  end-to-end verified-correctness grading caught it. Any future
  formalization metric must include an extracted-vs-true name-set check,
  not only per-field accuracy on known names.
- **Certificate correctness and independence can be built together from
  the start** (D2) rather than requiring a two-pass history (edge_ai/CSP
  needed Gamma, then separately Gamma+1/+2) — once a vertical has an
  independent-checker pattern to follow, there is no reason to ship
  Partial independence as an interim state. Apply this to any future
  vertical (calculus_poly, and beyond).
- **Two different theorems for two different verification jobs** (D2):
  the Fundamental Theorem of LP establishes *where an optimum can be* (a
  claim about the solver's search space); the LP Duality Theorem
  establishes *that a specific point is optimal* (a claim checkable
  without search at all, given the point). This is a stronger
  independence property than "different algorithm, same paradigm"
  (Gamma+1/+2) and is worth seeking again for calculus_poly if a
  comparable duality-style theorem exists for constrained critical-point
  verification.

Not a ranked item but a standing design constraint: any future experiment
using a variation gate must use the **differential** form (treatment −
control at matched seeds) — this travels with the experiment that needs
it (e.g. a PC-2026-07-03b confirmation), it is not a separate hypothesis.

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
   **Update (2026-07-03, Gamma+1/Gamma+2):** the parenthetical is
   superseded by exactly the mechanism this lock allows — two registered
   experiments upgraded independence to Supported in both verticals (see
   Certificate properties table). The strongest validated result is now
   certificate correctness *under independently-written verification*.
   Original wording kept; verdicts update by evidence, not by rewrite.
6. Frozen-artifact mapping: "mechanism gate / mechanism_gate / mechanism
   check" inside committed `research/G2_csp_h1b/` and
   `research/G2b_sampling_robustness/` artifacts = the Behaviour Variation
   Gate. Those files are frozen evidence and are NOT edited (Prop 6);
   the term is renamed only in the live/knowledge layer going forward.
