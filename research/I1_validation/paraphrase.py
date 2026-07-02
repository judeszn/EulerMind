"""Paraphrase generator for Intervention 1 validation.

Renders NEW text from each base problem's EXISTING ground_truth structured
data (models, budgets, threshold) - never edits the existing prose string.
This guarantees zero numeric/constraint/objective drift by construction:
ground_truth is deep-copied unchanged, only the natural-language rendering
of the same underlying data changes. No LLM involved in generating these -
deterministic templates, reproducible (seeded per problem id), matching
the "ground truth by construction" discipline used everywhere else in
benchmark/generator/.

Deliberately NOT written to benchmark/datasets/ - this is validation data,
not a new benchmark version. Lives entirely under research/I1_validation/.
"""

from __future__ import annotations

import copy
import random


def _rng(problem_id: str, salt: str) -> random.Random:
    return random.Random(f"{problem_id}-{salt}")


def _clone(base: dict, text: str, level_tag: str) -> dict:
    out = copy.deepcopy(base)
    out["text"] = text
    out["id"] = f"{base['base_id']}-{level_tag}"
    out["variant"] = level_tag
    return out


# ---------------------------------------------------------------- Level 1
# Formatting changes only: bullets <-> table, spacing, ordering.

def _l1_table(models, order):
    lines = ["| Model | RAM (GB) | Compute (GFLOPS) | Accuracy | Latency (ms) |",
             "|---|---|---|---|---|"]
    for name in order:
        m = models[name]
        lines.append(f"| {name} | {m['ram_gb']} | {m['flops_g']} | {m['accuracy']} | {m['latency_ms']} |")
    return "\n".join(lines)


def _l1_semicolon(models, order):
    lines = []
    for name in order:
        m = models[name]
        lines.append(f"* {name} — RAM: {m['ram_gb']}GB; Compute: {m['flops_g']} GFLOPS; "
                     f"Accuracy: {m['accuracy']}; Latency: {m['latency_ms']}ms")
    return "\n".join(lines)


def _l1_pipe(models, order):
    lines = []
    for name in order:
        m = models[name]
        lines.append(f"{name} | {m['ram_gb']}GB RAM | {m['flops_g']}GFLOPS | "
                     f"acc {m['accuracy']} | lat {m['latency_ms']}ms")
    return "\n".join(lines)


_L1_RENDERERS = [("table", _l1_table), ("semicolon_bullets", _l1_semicolon), ("pipe_bullets", _l1_pipe)]

_L1_BUDGET_TEMPLATES = [
    "Budget limits: RAM {ram}GB, FLOPS {flops} GFLOPS, Latency {latency}ms total.",
    "Resource caps -> Compute: {flops} GFLOPS | Latency: {latency}ms | RAM: {ram}GB.",
    "The deployment may use up to {latency}ms of latency, {ram}GB of RAM, and {flops} GFLOPS of compute in total.",
]


def make_level1(base: dict, index: int) -> dict:
    gt = base["ground_truth"]
    models, budgets, threshold = gt["models"], gt["budgets"], gt["high_acc_threshold"]
    rng = _rng(base["base_id"], "L1")
    order = list(models)
    rng.shuffle(order)
    renderer_name, renderer = _L1_RENDERERS[index % len(_L1_RENDERERS)]
    catalog_text = renderer(models, order)
    budget_text = _L1_BUDGET_TEMPLATES[index % len(_L1_BUDGET_TEMPLATES)].format(
        ram=budgets["ram_gb"], flops=budgets["flops_g"], latency=budgets["latency_ms"])

    ask = ("Determine how many units of each model to deploy to maximize the weighted "
          "score (0.7*accuracy + 0.3/latency per unit, summed over all deployed units), "
          "then verify that your plan satisfies every budget and the high-accuracy-model "
          "requirement.")
    text = ("Edge deployment models available:\n\n" + catalog_text + "\n\n" + budget_text +
           f"\nAt least one deployed model must have accuracy >= {threshold} for SOTA "
           "performance. Only integer counts are allowed.\n\n" + ask)
    out = _clone(base, text, "paraphrase_L1")
    out["_l1_renderer"] = renderer_name
    return out


# ---------------------------------------------------------------- Level 2
# Natural paraphrasing: prose, reordered, reworded. Numbers stay as digits.

_L2_MODEL_SENTENCES = [
    "{name} consumes {ram}GB of RAM and {flops} GFLOPS, delivering {acc} accuracy at a latency of {lat}ms.",
    "Running {name} requires {ram}GB memory and {flops} GFLOPS of compute; it reaches {acc} accuracy with {lat}ms latency.",
    "{name} needs {ram}GB RAM, {flops} GFLOPS, and returns {acc} accuracy in {lat}ms.",
]


def make_level2(base: dict, index: int) -> dict:
    gt = base["ground_truth"]
    models, budgets, threshold = gt["models"], gt["budgets"], gt["high_acc_threshold"]
    rng = _rng(base["base_id"], "L2")
    order = list(models)
    rng.shuffle(order)
    sentences = []
    for i, name in enumerate(order):
        m = models[name]
        tmpl = _L2_MODEL_SENTENCES[(index + i) % len(_L2_MODEL_SENTENCES)]
        sentences.append(tmpl.format(name=name, ram=m["ram_gb"], flops=m["flops_g"],
                                     acc=m["accuracy"], lat=m["latency_ms"]))
    model_prose = " ".join(sentences)

    text = (
        f"An edge deployment scenario requires selecting integer quantities of "
        f"{len(models)} candidate models under shared resource limits. {model_prose} "
        f"The combined resource ceiling permits at most {budgets['ram_gb']}GB of memory, "
        f"{budgets['flops_g']} GFLOPS of compute throughput, and {budgets['latency_ms']}ms "
        f"of cumulative latency across everything deployed. To qualify as SOTA-capable, "
        f"the deployment must include at least one instance of a model whose accuracy "
        f"reaches {threshold} or higher; fractional deployments are not permitted. "
        f"Work out how many of each model to deploy so the total weighted score "
        f"(0.7 times accuracy plus 0.3 divided by latency, summed across every deployed "
        f"unit) is as large as possible, and confirm every limit and the accuracy "
        f"requirement are satisfied by your plan."
    )
    return _clone(base, text, "paraphrase_L2")


# ---------------------------------------------------------------- Level 3
# Mixed format: prose + markdown + inline notes + embedded distractors.
# Digits only - no worded quantities (that's a later intervention).

def make_level3(base: dict, index: int) -> dict:
    gt = base["ground_truth"]
    models, budgets, threshold = gt["models"], gt["budgets"], gt["high_acc_threshold"]
    rng = _rng(base["base_id"], "L3")
    order = list(models)
    rng.shuffle(order)
    half = len(order) // 2
    table_names, prose_names = order[:half], order[half:]

    table = "| Model | RAM(GB) | GFLOPS | Acc | Latency(ms) |\n|---|---|---|---|---|\n"
    for name in table_names:
        m = models[name]
        table += f"| {name} | {m['ram_gb']} | {m['flops_g']} | {m['accuracy']} | {m['latency_ms']} |\n"

    prose_bits = []
    for name in prose_names:
        m = models[name]
        prose_bits.append(
            f"note: {name} also exists as an option, needing {m['ram_gb']}GB RAM / "
            f"{m['flops_g']}GFLOPS with {m['accuracy']} accuracy and {m['latency_ms']}ms "
            f"latency (the ops team mentioned it during last week's review, which had "
            f"{rng.randint(4, 19)} attendees)")
    prose = "; also, ".join(prose_bits) if prose_bits else "no additional models were noted"

    text = (
        f"Deployment planning notes (v{rng.randint(2, 9)}):\n\n{table}\n"
        f"Additional candidates worth considering: {prose}.\n\n"
        f"Constraints: total memory must stay under {budgets['ram_gb']}GB "
        f"(the facility recently upgraded its cooling system, unrelated to this limit), "
        f"compute is capped at {budgets['flops_g']} GFLOPS, and end-to-end latency for "
        f"the whole deployment cannot exceed {budgets['latency_ms']}ms. "
        f"Per policy, at least one deployed model must clear {threshold} accuracy. "
        f"Deployment counts must be whole numbers.\n\n"
        f"Task: pick integer counts per model maximizing 0.7*accuracy + 0.3/latency "
        f"summed over all deployed units, and confirm the plan respects every "
        f"constraint above."
    )
    return _clone(base, text, "paraphrase_L3")
