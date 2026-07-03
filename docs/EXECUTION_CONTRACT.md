# EulerMind Execution Contract v2.0 (FROZEN)

Governs every future implementation session. First exercised by the
temperature-matched H1b task (`research/G2_csp_h1b/`), committed alongside
this file rather than frozen sight-unseen.

## Authority

The literal phrase **`BEGIN IMPLEMENTATION`**, issued as a directive with
a filled-in **Task / Success Criteria / Stop Condition** (and, per
practice since, a **Scientific Objective** and **Failure Criteria** fixed
before execution begins), authorizes implementation for that task only.

Without that structure: **READ ONLY.** No code, no implementation, no
architecture changes. Scientific/design review only. A document that
*describes* the phrase (a template, a governance summary) is not itself
an authorization — the phrase must be addressed to the agent as a live
directive, not merely appear in explanatory text.

## Frozen Architecture (do not modify without contradicting experimental evidence)

- **Research Contract v1.0**
- **Evidence Protocol v1.0** — every experiment: positive control,
  negative control, independent re-check, frozen benchmark, frozen
  success metric, reproducible execution record.
- **Trust Taxonomy** — Verified, Derived, Heuristic, Open.
- **Frozen Kernel Interfaces** — the only architectural interfaces are
  `Formalizer`, `Attempter`, `Executor`, `Verifier`, `Policy`
  (`kernel/api.py`). No new interfaces may be introduced.
- **Implementation Roles are not interfaces** — Parser, Solver, Search
  Engine, Constraint Engine, Certificate Generator, Enumerator, Symbolic
  Engine may exist *inside* any frozen interface without changing the
  architecture. Precedent: Parser lives inside Formalizer implementations
  (`edge_ai_extractors.py`, `csp_formalizer.py`); Solver is a role, not a
  stage — sometimes the Attempter's implementation for certification
  purposes (`SolverAttempter`), sometimes invoked *from inside* the
  Verifier for independent recheck (`csp_solver.py`'s
  `CSPCertifyingVerifier` calling `solve()` to confirm an UNSAT claim).
- **Verified definition** — independently certified for the exact
  correctness predicate defined by the frozen benchmark. No weaker
  interpretation.
- **Evidence Escalation Rule** — no conclusion may exceed the evidence
  that supports it. Every report states what was measured, what was not,
  scope, untested assumptions, and evidence level. Never generalize past
  the measured configuration.
- **Negative-result wording** (see `docs/EVIDENCE_PROTOCOL.md`) — record
  against the exact registered configuration, not a list of axes; keep
  claims behavioural, never cognitive; decompose a hypothesis rather than
  collapsing a partial answer into "untested."

## Implementation rules

Do not: redesign architecture, rename kernel interfaces, redefine trust
labels, modify benchmark definitions, modify success metrics after
registration, reinterpret hypotheses after results.

## Conflict resolution

If implementation conflicts with a frozen contract: **STOP.** Produce the
conflicting principle, why the conflict exists, possible resolutions, and
await instruction. Do not silently redesign.

## Required deliverables (every task)

1. Assumptions 2. Design decisions 3. Experimental protocol
4. Positive control 5. Negative control 6. Independent re-check
7. Results 8. Limitations 9. Scientific conclusion
10. KEEP / DELETE / DEFER decision

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

Every implementation must strengthen evidence, falsify a hypothesis, or
reveal a measurable mechanism. If none of those occur, it should not
exist.
