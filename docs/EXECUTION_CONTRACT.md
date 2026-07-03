# EulerMind Execution Contract v3.0 (FROZEN)

Governs every future implementation session. v2.0 was first exercised by
the temperature-matched H1b task (`research/G2_csp_h1b/`). v3.0 adds the
Interpretation Rules ordering and tightens the reporting vocabulary,
incorporating what the last two rounds of confirmation review found.

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

## Reporting vocabulary (frozen, mutually exclusive — use exactly one)

| Term | Meaning | Precedent |
|---|---|---|
| **Supported** | Pre-registered decision rule applied; result cleared the threshold favorably | — |
| **Rejected by the Registered Decision Rule** | Pre-registered decision rule applied; result did not clear the threshold. The *only* negative-verdict term when a formal test was run — there is no separate "Not Supported" category, because a softer alternative next to a precise one invites reporting a negative finding without running the decision-rule machinery | H1b-Gamma-1 |
| **Untested** | Nothing prevents running this; hasn't been attempted | H1b at other configurations, H4, H5 |
| **Blocked** | A specific prerequisite (a premise, a missing component) must resolve before this can be validly tested — different from Untested, where nothing is in the way | H2 (blocked on H1b's premise) |
| **Provisional** | A *valid* experiment produced a real result; required reproduction has not yet completed. The design was sound — the result just isn't confirmed yet | H1b-Gamma-1 (single stochastic execution) |
| **Deferred** | The experimental *design* was found confounded or invalid during/after execution; no verdict on the hypothesis is possible from this run — but the data remains diagnostically useful for the next design, not discarded | Knapsack H1 run, CSP-1 (its 42/42 finding directly informed the G2 redesign) |
| **Invalidated** | Reserved for the stricter case where the *data itself*, not just the verdict, is later found untrustworthy (e.g. a bug discovered in shared logic) — distinct from Deferred, where the data stays useful even though the verdict doesn't | Not yet used — reserved |

Always include the exact tested configuration. Never generalize beyond
measured evidence.

## Implementation rules

Do not: redesign architecture, rename kernel interfaces, redefine trust
labels, modify benchmark definitions, modify success metrics after
registration, reinterpret hypotheses after results.

## Conflict resolution

If implementation conflicts with a frozen contract: **STOP.** Produce the
conflicting principle, why the conflict exists, possible resolutions, and
await instruction. Do not silently redesign.

## Required deliverables (every task)

1. Implementation Summary 2. Scientific Objective 3. Experimental Design
4. Mechanism Audit 5. Evidence Protocol Audit 6. Results
7. Statistical Analysis 8. Scientific Interpretation
9. Evidence Classification 10. Limitations 11. Updated Scientific State
12. Decision (using the reporting vocabulary above, never "true/false")

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
