# EulerMind Execution Contract v3.1 (FROZEN)

**This document is frozen governance — timeless.** Any reference to a
specific result (e.g. "H1b-Gamma-1") below is a **frozen historical
precedent illustrating a rule**, not a live status reading, and does not
change when that result's verdict later changes. Current scientific state
lives only in `docs/SCIENTIFIC_STATE.md`.

Governs every future implementation session. v2.0 was first exercised by
the temperature-matched H1b task (`research/G2_csp_h1b/`). v3.0 added the
Interpretation Rules ordering and tightened the reporting vocabulary.
v3.1 separates scientific verdict from execution status, structurally
forces configuration scope and threats-to-validity into every report, and
distinguishes Evidence (permanent, accumulating) from Knowledge (the
current best conclusion, updated only with explanation).

## Authority

The literal phrase **`BEGIN IMPLEMENTATION`**, issued as a directive with
a filled-in **Task / Scientific Objective / Success Criteria / Failure
Criteria / Stop Condition**, authorizes implementation for that task
only.

Without a filled-in Task: **READ ONLY.** No code, no implementation, no
architecture changes. A document that *describes* the phrase or gives an
*example* Task (a template, a governance summary) is not itself an
authorization — the phrase must be addressed as a live directive with
real content in every field, not a bracketed placeholder.

## Frozen Architecture (do not modify without contradicting experimental evidence)

- **Research Contract v1.0**
- **Evidence Protocol v1.0** — every experiment: positive control,
  negative control, independent re-check, frozen benchmark, frozen
  success metric, reproducible execution record. "No exceptions" means
  every deliverable must *address* each category — built fresh, or cited
  as inherited-unchanged with a pointer to where it was originally
  validated (precedent: `research/G2_csp_h1b/RESULTS.md` correctly
  inherited its controls from G1 rather than rebuilding unchanged code)
  — not that everything must be rebuilt from scratch every time.
- **Trust Taxonomy** — Verified, Derived, Heuristic, Open.
- **Frozen Kernel Interfaces** — `Formalizer`, `Attempter`, `Executor`,
  `Verifier`, `Policy` (`kernel/api.py`). No new interfaces.
- **Implementation Roles are not interfaces** — Parser, Solver, Search
  Engine, Constraint Engine, Certificate Generator, Enumerator, Symbolic
  Engine may exist *inside* any frozen interface without changing the
  architecture.
- **Verified definition** — independently certified for the exact
  correctness predicate defined by the frozen benchmark. No weaker
  interpretation.
- **Evidence Escalation Rule** — no conclusion may exceed the evidence
  that supports it. Never generalize past the measured configuration.
- **Stochastic reproducibility rule** (`docs/EVIDENCE_PROTOCOL.md`) —
  deterministic results reproduce bit-identically; stochastic results
  require a pre-registered N (confirmatory batch or power-driven batch,
  never a blanket default) chosen before any reruns are observed.

## Interpretation Rules (frozen, apply before any statistical claim)

Before interpreting any experimental outcome, in order:

1. Verify the intervention was actually exercised.
2. Verify the mechanism changed observable behaviour.
3. Verify certificates remain sound (0% false-certification).
4. Only then interpret statistical outcomes (Δ, p-values, thresholds).

If the intervention was not exercised: **do not interpret p-values or
effect sizes.** Report *"mechanism not exercised — hypothesis not tested
by this experiment"* instead of a statistical verdict. This is not new
policy — it is what CSP-1's mechanism audit (`research/G1_csp_validation/`)
discovered was necessary after the fact; this section makes it mandatory
in advance instead.

## Two dimensions, not one — Execution Status vs. Scientific Verdict

These mix two different questions and must never share one field.
**Execution Status** answers "has an experiment run, and how far": it
applies whether or not a conclusion exists yet. **Scientific Verdict**
only applies once status is Completed — it is a property of a finished
execution's outcome, never of a pre-execution state.

### Execution Status (frozen, mutually exclusive)

| Term | Meaning |
|---|---|
| **Untested** | Nothing prevents running this; hasn't been attempted |
| **Blocked** | A specific prerequisite (a premise, a missing component) must resolve first — different from Untested, where nothing is in the way (precedent: H2, blocked on H1b's premise) |
| **Planned** | Registered (Task/Objective/Criteria filled in) but not yet executed |
| **Running** | Execution in progress |
| **Completed** | Execution finished; a Scientific Verdict now applies |

### Scientific Verdict (frozen, mutually exclusive — applies only when status is Completed)

| Term | Meaning | Precedent |
|---|---|---|
| **Supported** | Pre-registered decision rule applied; result cleared the threshold favorably | — |
| **Rejected by the Registered Decision Rule** | Pre-registered decision rule applied; result did not clear the threshold. The *only* negative-verdict term when a formal test was run — no separate "Not Supported" category, because a softer alternative next to a precise one invites reporting a negative finding without running the decision-rule machinery | H1b-Gamma-1 |
| **Provisional** | A *valid* experiment produced a real result; required reproduction has not yet completed. The design was sound — the result just isn't confirmed yet | H1b-Gamma-1 (single stochastic execution) |
| **Deferred** | The experimental *design* was found confounded or invalid during/after execution; no verdict on the hypothesis is possible from this run — but the data remains diagnostically useful for the next design, not discarded | Knapsack H1 run, CSP-1 (its 42/42 finding directly informed the G2 redesign) |
| **Invalidated** | Reserved for the stricter case where the *data itself*, not just the verdict, is later found untrustworthy (e.g. a bug discovered in shared logic) — distinct from Deferred, where the data stays useful even though the verdict doesn't | Not yet used — reserved |

Always include the exact tested configuration. Never generalize beyond
measured evidence.

## Configuration section (required in every report)

Every report states the registered configuration explicitly, so scope is
structural, not a wording discipline someone has to remember:

```
Registered Configuration
Model:
Inference configuration:
Benchmark:
Policy:
Feedback encoding:
Certificate type:
Verifier:
Dataset:
```

Mark fields `N/A` where they don't apply (e.g. a pure-solver run has no
Policy or Feedback encoding), and add experiment-specific fields the
template doesn't anticipate (e.g. an IR schema version for a future
typed-IR experiment) rather than forcing every experiment into a list
shaped for LLM-attempter-vs-policy comparisons specifically.

## Threats to Validity (required in every report)

Grounded in the standard four-category taxonomy (Shadish, Cook & Campbell)
plus this project's own two additions:

```
Threats to Validity
Statistical conclusion validity  (was n and the test even adequate to
  support a conclusion? — the exact gap the N-pre-registration rule
  exists to close; give it a permanent slot here, not just a standing
  rule elsewhere)
Internal validity  (confounds — e.g. the original temperature confound)
Construct validity  (does the metric measure what it claims — e.g. does
  "Verified" actually mean "optimal," or just "feasible"?)
External validity  (does this generalize past the tested phrasing/domain
  — e.g. parser dependence on the benchmark's own generator templates)
Reproducibility  (same code, same environment, rerun)
Replication  (independent implementation, same conclusion — e.g. the
  certificate-independence gap: recheck sharing search logic with solve())
```

## Evidence vs. Knowledge (frozen distinction)

**Evidence accumulates and is never deleted or overwritten** — every
completed run's result is a permanent historical record, superseded runs
included (precedent: `demo/actual_output.md`'s superseded-run section;
`benchmark/datasets/CHANGELOG.md`'s immutable versioning).

**Knowledge is the current best conclusion, drawn from accumulated
Evidence — and updates only with explanation, never merely because a
result is most recent.** If Run 4 contradicts Run 2, Run 2 remains valid
Evidence; Knowledge updates only if Run 4 either is the first valid
measurement of the question, or explains the discrepancy (a newly
identified confound, a genuinely different configuration). "Knowledge =
whichever run is most recent" would quietly reintroduce optional
stopping one level up — keep running until the latest result is the
preferred one, and always defer to it.

## Reason for Stopping (required in every report's final line)

```
Stopping Reason
Success criterion reached
Failure criterion reached
Evidence ceiling reached
Budget exhausted
Contract boundary reached (includes a discovered conflict with frozen
  architecture, per Conflict Resolution)
```

## Implementation rules

Do not: redesign architecture, rename kernel interfaces, redefine trust
labels, modify benchmark definitions, modify success metrics after
registration, reinterpret hypotheses after results.

## Conflict resolution

If implementation conflicts with a frozen contract: **STOP.** Produce the
conflicting principle, why the conflict exists, possible resolutions, and
await instruction. Do not silently redesign.

## Required deliverables (every task)

1. Registered Configuration 2. Implementation Summary
3. Scientific Objective 4. Experimental Design 5. Mechanism Audit
6. Evidence Protocol Audit 7. Results 8. Statistical Analysis
9. Threats to Validity 10. Scientific Interpretation
11. Evidence Classification (Execution Status + Scientific Verdict,
    reported separately) 12. Limitations 13. Updated Scientific State
    (and, if it changed, an explanation of why — never "most recent wins")
14. Stopping Reason

## Evidence hierarchy

Architecture → Implementation → Internal Reproduction → Independent
Reproduction → Replication → External Validation. Only controlled
experiments move a result upward. Architecture never counts as evidence;
implementation never counts as evidence.

## Stop condition

Implementation ends immediately after experiments complete, reports are
generated, and evidence is classified. No new phase, no architecture
redesign, no proposed future work, unless explicitly instructed.

## Mission

Every implementation must strengthen evidence, test a hypothesis against
its registered decision rule, or reveal a measurable mechanism. If none
of those occur, it should not exist. Governance is frozen; evidence moves
the project.
