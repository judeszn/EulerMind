# Delta Intervention D2 — optimization_lp Vertical: RESULTS

**Date:** 2026-07-03 · `optimization_lp` (two-variable LP: 2 workshop
products, 2 resource constraints, maximize profit), 80 problems (58 dev +
22 holdout, clean + messy) · fully offline. **The first THEOREM-BACKED
certification domain** — edge_ai and constraint_csp both certify by
exhaustively enumerating a finite search space that IS the problem; LP's
completeness instead rests on the **Fundamental Theorem of Linear
Programming** (a bounded feasible LP's optimum occurs at a vertex of the
feasible region).

## 1. Design review

**Solver → certificate → recheck (Task 2–4).** Candidate optima are the
pairwise intersections of the four boundary lines {x=0, y=0, constraint1,
constraint2} — up to 6 points, generalizing the benchmark generator's own
3-fixed-vertex shortcut to any relative orientation. Feasible vertices are
filtered by the four inequalities; the maximum-objective one is the
answer. Unboundedness is checked via the region's recession cone: for
this specific structure (2 general half-planes + non-negativity in 2D),
an unbounded edge is necessarily parallel to one of the four boundary
lines (a standard fact for 2D polyhedra) — so checking the 2 axis
directions and both orientations of each constraint's direction vector is
a complete check *for this structure*, not a claim of a general
n-dimensional algorithm. Infeasibility is "no candidate vertex satisfies
all four inequalities."

**Independent checker (Task 5) uses a different theorem, not just a
different search.** `kernel/lp_solver.py`'s production `recheck_certificate`
shares the solver's vertex-enumeration search (matching the established
precedent in `edge_ai_solver.py`/`csp_solver.py`). The dedicated
independent checker (`research/D2_lp_vertical/independent_checker.py`)
instead applies the **LP Duality Theorem**: given a claimed optimal
point, it determines the active constraint set (arithmetic only), solves
the small linear system implied by Complementary Slackness for dual
variables (u1, u2) — at most a 2×2 solve, never a search — and accepts
only if the dual witness is feasible and Strong Duality holds (dual
objective == claimed primal objective). **Zero optimization or search is
performed by the independent checker at all** — a stronger form of
independence than Gamma+1/+2's "different search algorithm," since there
is no search to potentially share.

## 2. Formalizer validation

`LPFormalizer` (parser-first, no LLM fallback — mirrors `CSPFormalizer`'s
precedent for fully-templated domains) extracts the 8-parameter model
`{a1,b1,c1,a2,b2,c2,p1,p2}` via three value-semantic sentence patterns
(product/resource identity + usage; capacity, handling the messy
variant's minutes→hours conversion; profit). **80/80 specs match the
dataset's ground-truth model exactly** (dev + holdout, clean + messy) —
0 LLM fallback engaged.

## 3. Solver validation

**80/80 solver outputs (x, y, profit) match ground truth exactly.**
Verified on 6 synthetic vertex-type cases beyond the dataset (interior
intersection, origin, both axis vertices, unbounded, infeasible) — all
classified correctly (`kernel/lp_solver.py` inline verification).

## 4. Controls

| Control | Result |
|---|---|
| Positive — independent checker accepts the true optimum | **accept** ✓ |
| Negative — infeasible claim | **reject** ✓ |
| Negative — feasible-but-suboptimal claim | **reject** ✓ |
| Negative — synthetic unbounded instance | **classified `unbounded`** ✓ |
| Negative — synthetic infeasible instance | **classified `infeasible`** ✓ |

Unbounded/infeasible controls are necessarily synthetic — the real
dataset is bounded and feasible by construction (positive coefficients,
non-negative capacities) — constructed per the standing rule that
synthetic cases validate the *mechanism*, never manufacture benchmark
evidence (the direction-of-inference test: these exist to prove the
classifier works, not to give an intervention something to catch).

## 5. Agreement matrix

| Comparison | Agree / total |
|---|---|
| Primary (shared vertex search) vs Independent (LP Duality Theorem) | **80 / 80** |
| Independent-accepted certificates vs `benchmark.metrics.grade()` | **80 / 80** |
| Dev split | 58 / 58 |
| Holdout split | 22 / 22 |
| Degenerate vertices (no unique dual witness) | **0** — real data is always non-degenerate (generator requires `det = a1*b2 - a2*b1 != 0` and a unique best vertex) |
| Disagreements | **0** |

**Holdout note:** per the standing rule ("Holdout split is run once per
phase gate, never iterated on"), this is that single gate-check for the
LP vertical — the formalizer and solver were validated primarily against
dev-split structure during development; holdout was scored once, in this
same combined run, and no code changed afterward on the strength of its
result.

## 6. False-certification report

**0** false certifications under the independent check. Every certificate
the independent checker accepted also passed `benchmark.metrics.grade()`
against ground truth.

## 7. Evidence classification

Internal reproduction, deterministic (parser-first formalizer + exact
vertex/duality arithmetic — no stochastic component; bit-identical on
rerun). Scope: `optimization_lp`, dev + holdout, clean + messy, 80
problems, 2-variable LPs with 2 resource constraints (the only structure
the benchmark generator produces).

## 8. Success / failure criteria

All 7 registered success criteria met: (1) formalizer extracts correctly
— 80/80 exact; (2) solver finds the optimal vertex — 80/80 exact; (3)
verifier certifies feasibility and optimality — `LPCertifyingVerifier`,
0% false certification; (4) independent checker shares no optimization
logic with the solver — confirmed by construction (LP Duality Theorem,
zero search); (5) false certification 0%; (6) regression — n/a, new
vertical, no prior LP behavior to regress; existing verticals untouched
(verified via diff); (7) selftest passes. No failure criterion triggered:
theorem assumptions held throughout (bounded-feasible-region LP, per the
generator's construction), verifier/independent-checker agreement 80/80,
false certification stayed 0, no architectural modification was needed.

## 9. Scientific conclusion

**Registered Hypothesis: Supported.** The frozen kernel
(Formalizer → Attempter → Executor → Verifier → Policy) generalizes to
theorem-backed optimization without architectural modification —
`LPAttempter`, `DeterministicLPExecutor`, `LPCertifyingVerifier` are new
*implementations* of the existing frozen protocols, not new protocol
shapes. The architecture now spans two proof styles: **enumeration-backed**
(edge_ai, constraint_csp — the finite candidate set the search visits IS
the problem) and **theorem-backed** (LP — completeness is guaranteed by a
theorem about where optima can occur, and independence is established by
an entirely different theorem about duality). Certificate Correctness and
Certificate Independence are both **Supported** for this vertical from
first measurement — no Partial-independence interim stage was needed,
unlike edge_ai/constraint_csp's original two-pass history (Gamma → Gamma+1/+2).

### Honest scope (Evidence Escalation Rule)

- Two-variable LPs with exactly 2 resource constraints — the only
  structure `benchmark/generator/lp.py` produces. Generalizing to more
  variables/constraints is untested and would need a different
  (simplex-based) solver; vertex-pair enumeration is specific to 2D.
- Unboundedness detection's completeness argument is scoped to this
  exact structure (2 general constraints + non-negativity in 2D), not
  claimed as a general algorithm (§1).
- Dev + holdout, both variants (clean/messy) — 80/80. This is a single
  holdout gate-check per the standing rule, not an iterated result.

## Stopping Reason

Success criteria reached — LP certified with both correctness and
independence Supported, all controls passed, evidence classified,
existing verticals and Gamma artifacts unchanged (verified via diff).
Per the registered Stop Condition: not beginning calculus_poly, not
registering H4, no architecture changes proposed. Awaiting scientific
review.
