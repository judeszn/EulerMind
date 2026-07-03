"""D1 parser unit tests (registered deliverable 3).

Positive controls: previously-failing L3 constructs now parse correctly.
Negative controls: native catalog/budget/threshold parsing is unchanged.

    python3 -m research.D1_parser_repair.test_parser
"""

from __future__ import annotations

import json
import unittest

from kernel.edge_ai_extractors import (_looks_like_catalog_line, extract_budgets,
                                       extract_catalog, extract_threshold)

# Real L3 constructs (from research/I1_validation/level3.jsonl, frozen).
L3_CONSTRAINTS_PARAGRAPH = (
    "Constraints: total memory must stay under 3.7GB (the facility recently "
    "upgraded its cooling system, unrelated to this limit), compute is capped "
    "at 92 GFLOPS, and end-to-end latency for the whole deployment cannot "
    "exceed 123ms. Per policy, at least one deployed model must clear 0.9 "
    "accuracy. Deployment counts must be whole numbers.")

L3_ASIDE_LINE = (
    "Additional candidates worth considering: note: KNN also exists as an "
    "option, needing 0.66GB RAM / 18GFLOPS with 0.93 accuracy and 29ms latency "
    "(the ops team mentioned it during last week's review, which had 10 "
    "attendees); also, note: XGBoost also exists as an option, needing 0.76GB "
    "RAM / 31GFLOPS with 0.96 accuracy and 66ms latency (the ops team "
    "mentioned it during last week's review, which had 10 attendees); also, "
    "note: SVM-linear also exists as an option, needing 0.73GB RAM / 19GFLOPS "
    "with 0.88 accuracy and 18ms latency (the ops team mentioned it during "
    "last week's review, which had 15 attendees).")

# Real native constructs (benchmark/datasets/v1, frozen).
NATIVE_CATALOG_LINE = "- XGBoost: 0.76GB RAM, 31 GFLOPS, accuracy=0.96, latency=66ms"
NATIVE_BUDGET_LINE = ("Total budget: 3.7GB RAM, 92 GFLOPS, 123ms total latency "
                      "across all deployed models.")
NATIVE_THRESHOLD_LINE = ("At least one deployed model must have accuracy >= 0.9 "
                         "for SOTA performance. Only integer counts are allowed.")

L3_FULL_TEXT = (
    "Deployment planning notes (v2):\n\n"
    "| Model | RAM(GB) | GFLOPS | Acc | Latency(ms) |\n"
    "|---|---|---|---|---|\n"
    "| DecisionTree | 0.43 | 19 | 0.91 | 61 |\n"
    "| CNN | 0.42 | 38 | 0.85 | 11 |\n\n"
    + L3_ASIDE_LINE + "\n\n" + L3_CONSTRAINTS_PARAGRAPH + "\n\n"
    "Task: pick integer counts per model maximizing 0.7*accuracy + 0.3/latency "
    "summed over all deployed units, and confirm the plan respects every "
    "constraint above.")


class TestD1Repair(unittest.TestCase):

    # ---- positive controls: previously-failing L3 constructs ----

    def test_constraints_paragraph_is_not_a_catalog_line(self):
        self.assertFalse(_looks_like_catalog_line(L3_CONSTRAINTS_PARAGRAPH))

    def test_no_fabricated_constraints_pseudo_model(self):
        models, _ = extract_catalog(L3_FULL_TEXT)
        self.assertNotIn("Constraints", models)
        self.assertNotIn("Task", models)

    def test_all_five_l3_models_extracted(self):
        models, _ = extract_catalog(L3_FULL_TEXT)
        self.assertEqual(set(models),
                         {"DecisionTree", "CNN", "KNN", "XGBoost", "SVM-linear"})

    def test_l3_aside_values_correct(self):
        models, _ = extract_catalog(L3_FULL_TEXT)
        self.assertEqual(models["SVM-linear"]["ram_gb"], 0.73)
        self.assertEqual(models["SVM-linear"]["accuracy"], 0.88)
        self.assertEqual(models["KNN"]["latency_ms"], 29.0)
        self.assertEqual(models["XGBoost"]["flops_g"], 31.0)

    def test_l3_budgets_and_threshold_still_extracted(self):
        self.assertEqual(extract_budgets(L3_FULL_TEXT),
                         {"ram_gb": 3.7, "flops_g": 92.0, "latency_ms": 123.0})
        self.assertEqual(extract_threshold(L3_FULL_TEXT), 0.9)

    # ---- negative controls: native behaviour unchanged ----

    def test_native_catalog_line_still_recognized(self):
        self.assertTrue(_looks_like_catalog_line(NATIVE_CATALOG_LINE))

    def test_native_budget_line_not_a_catalog_line(self):
        self.assertFalse(_looks_like_catalog_line(NATIVE_BUDGET_LINE))

    def test_native_threshold_line_not_a_catalog_line(self):
        self.assertFalse(_looks_like_catalog_line(NATIVE_THRESHOLD_LINE))

    def test_native_full_extraction_unchanged(self):
        native = ("An edge AI deployment must choose how many instances of each "
                  "available model to run, given shared hardware budgets.\n\n"
                  "Available models:\n"
                  "- XGBoost: 0.76GB RAM, 31 GFLOPS, accuracy=0.96, latency=66ms\n"
                  "- KNN: 0.66GB RAM, 18 GFLOPS, accuracy=0.93, latency=29ms\n"
                  "- SVM-linear: 0.73GB RAM, 19 GFLOPS, accuracy=0.88, latency=18ms\n"
                  "- DecisionTree: 0.43GB RAM, 19 GFLOPS, accuracy=0.91, latency=61ms\n"
                  "- CNN: 0.42GB RAM, 38 GFLOPS, accuracy=0.85, latency=11ms\n\n"
                  + NATIVE_BUDGET_LINE + "\n\n" + NATIVE_THRESHOLD_LINE + "\n\n"
                  "Determine how many units of each model to deploy.")
        models, _ = extract_catalog(native)
        self.assertEqual(set(models),
                         {"XGBoost", "KNN", "SVM-linear", "DecisionTree", "CNN"})
        self.assertEqual(models["XGBoost"]["accuracy"], 0.96)
        self.assertEqual(extract_budgets(native),
                         {"ram_gb": 3.7, "flops_g": 92.0, "latency_ms": 123.0})
        self.assertEqual(extract_threshold(native), 0.9)


if __name__ == "__main__":
    unittest.main(verbosity=2)
