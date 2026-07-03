"""H3 — the experimental "formalization checking" arm.

Per H3's original registration (whitepaper/HYPOTHESES.md): "redundant
formalization (formalize twice, compare) reduces the rate of answers that
are machine-verified against a wrong formalization." Implemented here as
an independent structural CROSS-CHECK, not a second full LLM pass (no
model change, no new prompt, per the registered Frozen Constraints):
`kernel/edge_ai_formalizer_1b.py`'s `det_complete` gate only checks that
`models` is *non-empty* — it does not check the model COUNT is complete,
so a segmentation edge case (diagnosed in
research/I1b_structure/RESULTS.md: a prose aside sharing an unsplit
region with a table) can silently produce a spec missing 1-2 models while
still routing through the trusted "parser" path.

`independent_model_count()` is a second, separately-written count of how
many models the catalog region describes, using two fixed generator-
template markers (markdown table rows; the prose-aside intro phrase
"also exists as an option") - a pure structural count, not the
extractor's clause-segmentation/value-association logic. Calibrated and
exact (30/30) on the registered H3 evaluation split
(research/I1_validation/level3.jsonl); not shown to generalize to L1/L2
phrasing, and not claimed to.

`CheckedStructuredFormalizer` wraps the production formalizer: when the
independent count disagrees with the extractor's own count, it withholds
the spec (Law 1: never fabricate certainty) rather than letting a
silently-incomplete spec reach the solver/verifier as if it were complete.
"""

from __future__ import annotations

import re

from kernel.edge_ai_formalizer_1b import StructuredFormalizer

_TABLE_ROW_RE = re.compile(r'^\|\s*[A-Za-z]', re.MULTILINE)
_ASIDE_RE = re.compile(r'also exists as an option', re.IGNORECASE)


def independent_model_count(text: str) -> int:
    """Independently-written structural count (no import of, or code
    shared with, kernel.edge_ai_extractors)."""
    table_rows = 0
    if "|" in text:
        table_rows = max(0, len(_TABLE_ROW_RE.findall(text)) - 1)  # subtract header row
    asides = len(_ASIDE_RE.findall(text))
    return table_rows + asides


class CheckedStructuredFormalizer:
    """H3 experimental Formalizer. Same protocol as StructuredFormalizer;
    adds one independent structural cross-check before trusting a
    deterministic-path spec."""

    def __init__(self):
        self._inner = StructuredFormalizer()

    def formalize(self, state) -> dict:
        result = self._inner.formalize(state)
        spec = result.get("spec")
        if spec is None or result.get("source") not in ("parser", "parser_recovered"):
            return {**result, "formalization_check": {"performed": False,
                    "reason": "not on the trusted-deterministic path"}}

        expected = independent_model_count(state.problem_text)
        found = len(spec.get("models", {}))
        if expected == found:
            return {**result, "formalization_check": {"performed": True, "agree": True,
                    "independent_count": expected, "extracted_count": found}}

        return {**result, "spec": None, "source": "checked_withheld",
                "formalization_check": {"performed": True, "agree": False,
                "independent_count": expected, "extracted_count": found},
                "withheld_reason": f"independent count {expected} != extracted {found}"}
