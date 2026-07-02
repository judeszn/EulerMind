# Flagship demo — "EulerMind Edge AI Optimizer"

Public name: **Edge AI Optimizer**. Internal category: `edge_ai_deployment`
(`benchmark/generator/edge_ai.py`). Pinned instance: **`edge-00000-messy`**,
dataset v1, **dev split** (deliberately not holdout — holdout is run once
per phase gate and never iterated on; a demo instance gets rehearsed on
every commit, so it must never be the holdout copy).

## The prompt (verbatim, as EulerMind receives it)

> An edge AI deployment must choose how many instances of each available
> model to run, given shared hardware budgets.
>
> Last quarter, the maintenance team replaced 323 light fixtures.
>
> Available models:
> - XGBoost: 0.76GB RAM, 31 GFLOPS, accuracy=0.96, latency=66ms
> - KNN: 0.66GB RAM, 18 GFLOPS, accuracy=0.93, latency=29ms
> - SVM-linear: 0.73GB RAM, 19 GFLOPS, accuracy=0.88, latency=18ms
> - DecisionTree: 0.43GB RAM, 19 GFLOPS, accuracy=0.91, latency=61ms
> - CNN: 0.42GB RAM, 38 GFLOPS, accuracy=0.85, latency=11ms
>
> The parking lot has space for 377 vehicles.
>
> Total RAM budget: 3789MB across all deployed models. FLOPS budget:
> 92 GFLOPS. Latency budget: 123ms total.
>
> At least one deployed model must have accuracy >= 0.9 for SOTA
> performance. Only integer counts are allowed.
>
> Determine how many units of each model to deploy to maximize the
> weighted score (0.7*accuracy + 0.3/latency per unit, summed over all
> deployed units), then verify that your plan satisfies every budget and
> the high-accuracy-model requirement.

## Why this instance was picked

- **Two irrelevant distractor sentences** (light fixtures, parking lot) —
  tests that formalization extracts only what matters.
- **RAM budget stated in MB (3789MB) against a GB-denominated catalog** —
  a real unit-conversion requirement, not just noise-filtering.
- **Optimal answer deploys two distinct model types** (3x KNN, 2x
  SVM-linear, score 3249) — richer to narrate live than a single-model
  answer, and not the obvious "just pick the highest accuracy" trap
  (XGBoost has the highest accuracy, 0.96, but is not part of the optimum
  — it's individually excellent but budget-inefficient at this instance's
  numbers, which is worth calling out on stage).

## Ground truth (for rehearsal only — never shown to the model)

```json
{"counts": {"XGBoost": 0, "KNN": 3, "SVM-linear": 2, "DecisionTree": 0, "CNN": 0},
 "score": 3249}
```
