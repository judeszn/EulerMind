"""Generator: edge AI model deployment (category: edge_ai_deployment).

An integer knapsack: choose how many units of each of 5 model types to
deploy, maximizing a weighted accuracy/latency score subject to aggregate
RAM, FLOPS, and latency budgets, plus a "deploy at least one high-accuracy
model" constraint. This is the one new domain family adopted from the
proposed "Edge AI Optimization" pitch — chosen because it fills a real gap
(our LP generator is continuous-only; this is genuine integer programming)
and ties directly to the competition's own theme (on-device AI under RAM
constraints), unlike the other four proposed families, which are either
already built (sabotage = "Verifier Challenge", messy variants = H3
"Formalization") or deferred as separate, non-trivial solver problems
(ML scheduling, quantization selection).

Ground truth by brute-force enumeration over a small bounded search space
(<= 4^5 = 1024 combinations) — stdlib only, no OR-Tools/PuLP dependency,
matching the rest of benchmark/: the harness must not depend on the
solvers it will later measure.
"""

from __future__ import annotations

import itertools
import random

from ..schema import make_problem
from .base import insert_distractors, join_paragraphs

MODEL_NAMES = ["CNN", "Transformer-lite", "XGBoost", "KNN", "MobileNet",
               "TinyBERT", "DecisionTree", "SVM-linear"]
MAX_COUNT = 3
HIGH_ACC_THRESHOLD = 0.90


def _score(acc: float, latency_ms: float) -> int:
    """Integer per-unit utility: 0.7*accuracy + 0.3*(1/latency), scaled and
    rounded so the objective is exact-integer (no float tie ambiguity)."""
    return round(1000 * (0.7 * acc + 0.3 * (1.0 / latency_ms)))


def _enumerate_best(models, budgets):
    """Brute-force every combination of counts in [0, MAX_COUNT]^n.
    Returns (best_counts, best_score, is_unique)."""
    ranges = [range(MAX_COUNT + 1)] * len(models)
    best_score, best_counts, tie = None, None, False
    for counts in itertools.product(*ranges):
        ram = sum(c * m["ram_gb"] for c, m in zip(counts, models))
        flops = sum(c * m["flops_g"] for c, m in zip(counts, models))
        latency = sum(c * m["latency_ms"] for c, m in zip(counts, models))
        if ram > budgets["ram_gb"] or flops > budgets["flops_g"] or latency > budgets["latency_ms"]:
            continue
        high_acc_units = sum(c for c, m in zip(counts, models)
                             if m["accuracy"] >= HIGH_ACC_THRESHOLD)
        if high_acc_units < 1:
            continue
        score = sum(c * m["score"] for c, m in zip(counts, models))
        if best_score is None or score > best_score:
            best_score, best_counts, tie = score, counts, False
        elif score == best_score:
            tie = True
    return best_counts, best_score, tie


def generate(base_seed: int) -> list[dict]:
    """Returns [clean_problem, messy_problem] sharing one ground truth.
    Retries internally (bounded search space -> cheap) until a feasible,
    unique-optimum instance with a non-trivial (nonzero) answer is found."""
    for attempt in range(300):
        rng = random.Random(f"edge-{base_seed}-{attempt}")
        result = _try_generate(rng, base_seed)
        if result is not None:
            return result
    raise RuntimeError(f"no valid edge_ai instance for seed {base_seed}")


def _try_generate(rng, base_seed):
    names = rng.sample(MODEL_NAMES, 5)
    models = []
    for name in names:
        acc = round(rng.uniform(0.78, 0.97), 2)
        latency = rng.randint(8, 70)
        models.append({
            "name": name,
            "ram_gb": round(rng.uniform(0.15, 1.6), 2),
            "flops_g": rng.randint(4, 45),
            "accuracy": acc,
            "latency_ms": latency,
            "score": _score(acc, latency),
        })
    if not any(m["accuracy"] >= HIGH_ACC_THRESHOLD for m in models):
        return None  # resample: constraint would be unsatisfiable by construction

    budgets = {
        "ram_gb": round(rng.uniform(2.0, 4.0), 1),
        "flops_g": rng.randint(60, 120),
        "latency_ms": rng.randint(80, 160),
    }

    counts, score, tie = _enumerate_best(models, budgets)
    if counts is None or tie or score == 0 or sum(counts) == 0:
        return None  # infeasible, ambiguous, or trivial all-zero optimum

    ground_truth = {
        "counts": dict(zip(names, counts)),
        "score": score,
        "models": {m["name"]: m for m in models},
        "budgets": budgets,
        "high_acc_threshold": HIGH_ACC_THRESHOLD,
    }
    answer_spec = {
        "type": "knapsack",
        "fields": {"counts": "dict model_name -> non-negative integer count",
                   "score": "total weighted score, integer"},
    }

    model_lines = "\n".join(
        f"- {m['name']}: {m['ram_gb']}GB RAM, {m['flops_g']} GFLOPS, "
        f"accuracy={m['accuracy']}, latency={m['latency_ms']}ms"
        for m in models)
    ask = ("Determine how many units of each model to deploy to maximize "
           "the weighted score (0.7*accuracy + 0.3/latency per unit, summed "
           "over all deployed units), then verify that your plan satisfies "
           "every budget and the high-accuracy-model requirement.")

    clean_paras = [
        "An edge AI deployment must choose how many instances of each "
        "available model to run, given shared hardware budgets.",
        "Available models:\n" + model_lines,
        f"Total budget: {budgets['ram_gb']}GB RAM, {budgets['flops_g']} GFLOPS, "
        f"{budgets['latency_ms']}ms total latency across all deployed models.",
        f"At least one deployed model must have accuracy >= {HIGH_ACC_THRESHOLD} "
        "for SOTA performance. Only integer counts are allowed.",
        ask,
    ]
    messy_paras = insert_distractors(rng, [
        "An edge AI deployment must choose how many instances of each "
        "available model to run, given shared hardware budgets.",
        "Available models:\n" + model_lines,
        f"Total RAM budget: {round(budgets['ram_gb']*1024)}MB across all "
        f"deployed models. FLOPS budget: {budgets['flops_g']} GFLOPS. "
        f"Latency budget: {budgets['latency_ms']}ms total.",
        f"At least one deployed model must have accuracy >= {HIGH_ACC_THRESHOLD} "
        "for SOTA performance. Only integer counts are allowed.",
        ask,
    ], count=2)

    base_id = f"edge-{base_seed:05d}"
    common = dict(base_id=base_id, category="edge_ai_deployment", seed=base_seed,
                  ground_truth=ground_truth, answer_spec=answer_spec)
    return [
        make_problem(variant="clean", text=join_paragraphs(clean_paras), **common),
        make_problem(variant="messy", text=join_paragraphs(messy_paras), **common),
    ]
