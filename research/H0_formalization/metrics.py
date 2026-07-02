"""Stage A - Formalization Accuracy metrics.

Pure functions comparing an extracted formalization spec against the
benchmark's ground truth, field by field. No LLM calls here - this module
only grades what kernel.edge_ai.LLMFormalizer already produced; it does
not modify that class.

Tolerance: 5% relative error counts as "correct" for numeric fields -
generous enough to absorb reasonable rounding, tight enough to catch
real extraction/fabrication errors.

Field Association Accuracy (required by the Stage A spec): a number that
is individually correct but attached to the wrong model is a SWAP, scored
separately from FABRICATED (a number that doesn't match any true value in
the catalog at all). Numeric Extraction Accuracy counts only exact
(model, field) correctness; Association Accuracy is conditional on the
true value being findable somewhere (correct or swapped) - it excludes
pure fabrication, which is a different failure class, not a mislocation.
"""

from __future__ import annotations

NUMERIC_FIELDS = ("ram_gb", "flops_g", "accuracy", "latency_ms")
TOL = 0.05  # 5% relative tolerance


def _close(a, b, tol: float = TOL) -> bool:
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return False
    if b == 0:
        return abs(a - b) < 1e-9
    return abs(a - b) / abs(b) <= tol


def score(ground_truth: dict, spec: dict | None) -> dict:
    """Returns per-problem metrics + raw counts for aggregation."""
    true_models = ground_truth["models"]
    true_names = set(true_models)
    extracted_models = spec.get("models") if isinstance(spec, dict) else None
    extracted_models = extracted_models if isinstance(extracted_models, dict) else {}
    extracted_names = set(extracted_models)

    # Variable extraction: F1 of the model-name set.
    tp = len(true_names & extracted_names)
    precision = tp / len(extracted_names) if extracted_names else 0.0
    recall = tp / len(true_names) if true_names else 0.0
    var_f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    # Numeric extraction + field association, over the intersection only -
    # can't score a field for a model that wasn't even identified.
    correct = swapped = fabricated = 0
    for name in true_names & extracted_names:
        ext_model = extracted_models[name]
        if not isinstance(ext_model, dict):
            fabricated += len(NUMERIC_FIELDS)
            continue
        for field in NUMERIC_FIELDS:
            true_val = true_models[name].get(field)
            ext_val = ext_model.get(field)
            if _close(ext_val, true_val):
                correct += 1
            elif any(_close(ext_val, true_models[other].get(field))
                     for other in true_names if other != name):
                swapped += 1
            else:
                fabricated += 1
    total_checked = correct + swapped + fabricated
    numeric_accuracy = correct / total_checked if total_checked else 0.0
    findable = correct + swapped
    association_accuracy = correct / findable if findable else None  # None = not applicable

    # Unit normalization: the RAM budget specifically - the deliberate
    # MB->GB conversion stress test present in every messy variant.
    true_ram_budget = ground_truth["budgets"]["ram_gb"]
    ext_budgets = spec.get("budgets") if isinstance(spec, dict) else None
    ext_budgets = ext_budgets if isinstance(ext_budgets, dict) else {}
    unit_accuracy = 1.0 if _close(ext_budgets.get("ram_gb"), true_ram_budget) else 0.0

    # Constraint extraction: all budget fields + the accuracy threshold.
    constraint_checks = [
        _close(ext_budgets.get(field), ground_truth["budgets"][field])
        for field in ("ram_gb", "flops_g", "latency_ms")
    ]
    ext_threshold = spec.get("high_acc_threshold") if isinstance(spec, dict) else None
    constraint_checks.append(_close(ext_threshold, ground_truth["high_acc_threshold"]))
    constraint_accuracy = sum(constraint_checks) / len(constraint_checks)

    schema_accuracy = (var_f1 + numeric_accuracy + constraint_accuracy) / 3

    return {
        "var_f1": var_f1,
        "numeric_accuracy": numeric_accuracy,
        "association_accuracy": association_accuracy,
        "unit_accuracy": unit_accuracy,
        "constraint_accuracy": constraint_accuracy,
        "schema_accuracy": schema_accuracy,
        "counts": {
            "correct": correct, "swapped": swapped, "fabricated": fabricated,
            "true_model_count": len(true_names),
            "extracted_model_count": len(extracted_names),
            "missing_models": len(true_names - extracted_names),
        },
        "spec_present": spec is not None,
    }
