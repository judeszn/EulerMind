# Demo scene 2 — "EulerMind Optimization Advisor" (optimization_lp)

Public name: **"EulerMind Optimization Advisor."** Internal category name
(`optimization_lp`) stays out of judge-facing language, same rule as
scene 1. Pinned instance: **`lp-00000-clean`**, dataset v1, **dev split**.

This scene exists to show something scene 1 (Edge AI) cannot: a
**theorem-backed** certificate, not an exhaustive-search one. Both scenes
run through the identical frozen kernel shape
(Formalizer → Solver → Verifier → Independent Checker) — the point of
having two scenes is proving that shape generalizes across mathematically
different domains, not just working once.

## The prompt (verbatim)

> A workshop produces two products: small drones and large drones.
>
> Each unit of small drones requires 3 hours of cutting and 5 hours of
> finishing. Each unit of large drones requires 5 hours of cutting and 4
> hours of finishing.
>
> The workshop has 247 hours of cutting capacity and 286 hours of
> finishing capacity available.
>
> Each unit of small drones yields $40 profit and each unit of large
> drones yields $63 profit.
>
> Determine how many units of each product maximize total profit, report
> the maximum profit, and verify that your plan satisfies every capacity
> constraint.

## What happens (verbatim to what the pipeline actually does)

1. **Formalization** (`kernel/lp_formalizer.py`, parser-first, zero LLM
   calls): extracts the 8-number model — 2 products × (cutting hours,
   finishing hours, profit) + 2 capacities — by matching the sentence
   shape, not fixed positions. Exact match to ground truth: **80/80** on
   every LP problem in the dataset, this instance included.
2. **Solving** (`kernel/lp_solver.py`): the **Fundamental Theorem of
   Linear Programming** — a bounded feasible LP's optimum occurs at a
   vertex of the feasible region — lets the solver skip searching the
   entire (infinite) feasible region and check only the handful of
   candidate vertices. Result: **34 small drones, 29 large drones,
   profit 3187** — exact match to ground truth.
3. **Certification**: a re-checkable certificate is issued and the
   production recheck confirms it.
4. **Independent verification — the scene's actual point.** A second,
   separately-written checker (`research/D2_lp_vertical/independent_checker.py`)
   verifies the SAME answer using a **completely different theorem**: the
   **LP Duality Theorem**. It performs **zero search** — given the claimed
   answer, it solves a tiny linear system for two "shadow price" numbers
   (**cutting hour ≈ $11.92, finishing hour ≈ $0.85** — literally what
   one more hour of each resource would be worth) and checks that this
   dual solution proves the same $3187 is optimal, via weak/strong
   duality. Two unrelated theorems agreeing is a stronger guarantee than
   one solver double-checking itself.

## The narrative beat (say this out loud)

"The system isn't just solving this — it's proving it's solved *two
different ways*, using two different pieces of 80-year-old math that have
nothing to do with each other. If either one had a bug, the other would
catch it."

Optional deeper beat, if a judge asks "how do you know the checker isn't
just as wrong as the solver": the independent checker never enumerates a
single candidate deployment. It only knows the claimed answer and the
problem. There is no shared code path for a shared bug to hide in.

## Result summary

| | Value |
|---|---|
| Trust label | **Verified** |
| Deployment | 34 × small drones, 29 × large drones |
| Profit | **3187** (exact match to ground truth) |
| Primary certificate | accepted |
| Independent certificate (LP Duality) | accepted — dual witness (u1≈11.923077, u2≈0.846154) |
| False certification on this vertical | 0% (80/80 dev+holdout) |

Full evidence: `research/D2_lp_vertical/RESULTS.md`.
