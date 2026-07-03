"""Delta D2 Task 1 — LP Formalizer for optimization_lp.

Parser-first, deterministic, value-semantic (not fixed positional) - same
idiom as kernel/csp_formalizer.py and kernel/edge_ai_extractors.py. The
generator (benchmark/generator/lp.py) renders from a small set of fixed
sentence templates per the standing "explicit structure -> template
matching, not value-semantic guessing" rule, so a template-matching
parser is the right tool. No LLM fallback (mirrors CSPFormalizer, not
StructuredFormalizer's dual-path design) - parser-only is a valid,
established pattern for this project when the source is fully templated.

Independent of benchmark/ - the two sentence templates below are
duplicated here by necessity (parsing is the inverse of
benchmark/generator/lp.py's rendering, not an import of it).

Output spec shape (consumed by kernel/lp_solver.py):
{a1,b1,c1,a2,b2,c2,p1,p2} - constraint i is a_i*x + b_i*y <= c_i, x is the
first-named product, y the second; objective maximize p1*x+p2*y.
"""

from __future__ import annotations

import re

_REQUIRES_RE = re.compile(
    r'each unit of ([A-Za-z0-9][\w\s\-]*?) requires ([\d.]+) hours of ([\w\s\-]+?) '
    r'and ([\d.]+) hours of ([\w\s\-]+?)\.', re.IGNORECASE)
_YIELDS_RE = re.compile(
    r'each unit of ([A-Za-z0-9][\w\s\-]*?) yields \$([\d.]+) profit', re.IGNORECASE)


def _parse_products(text: str) -> list[dict] | None:
    """Two "Each unit of X requires A hours of RES1 and B hours of RES2."
    sentences give product identity and both resource usages in one
    value-semantic match - immune to distractor sentences (electricity
    cost, light fixtures, etc.) since none of them match this shape."""
    matches = _REQUIRES_RE.findall(text)
    if len(matches) != 2:
        return None
    products = [{"name": name.strip(), "res1": res1.strip(), "use1": float(a),
                "res2": res2.strip(), "use2": float(b)}
               for name, a, res1, b, res2 in matches]
    if products[0]["res1"] != products[1]["res1"]:
        return None
    if products[0]["res2"] != products[1]["res2"]:
        return None
    return products


def _capacity(text: str, resource: str) -> float | None:
    """Value-semantic, keyed on the resource NAME extracted above (not a
    closed vocabulary) - handles both the clean combined phrasing
    ("N hours of RES capacity") and the messy split-with-unit-conversion
    phrasing ("RES department reports N minutes of available capacity")."""
    m = re.search(rf'([\d.]+)\s*hours of {re.escape(resource)} capacity',
                  text, re.IGNORECASE)
    if m:
        return float(m.group(1))
    m = re.search(rf'{re.escape(resource)} department reports ([\d.]+)\s*minutes',
                  text, re.IGNORECASE)
    if m:
        return round(float(m.group(1)) / 60.0, 6)
    return None


def _profits(text: str, names: list[str]) -> dict[str, float] | None:
    found = {n.strip(): float(v) for n, v in _YIELDS_RE.findall(text)}
    if not all(n in found for n in names):
        return None
    return found


def try_parse(text: str) -> dict | None:
    products = _parse_products(text)
    if products is None:
        return None
    p0, p1 = products
    c1 = _capacity(text, p0["res1"])
    c2 = _capacity(text, p0["res2"])
    if c1 is None or c2 is None:
        return None
    profits = _profits(text, [p0["name"], p1["name"]])
    if profits is None:
        return None
    return {"a1": p0["use1"], "b1": p1["use1"], "c1": c1,
           "a2": p0["use2"], "b2": p1["use2"], "c2": c2,
           "p1": profits[p0["name"]], "p2": profits[p1["name"]],
           "var_names": {"x": p0["name"], "y": p1["name"]}}


class LPFormalizer:
    def formalize(self, state) -> dict:
        spec = try_parse(state.problem_text)
        if spec is None:
            return {"kind": "lp", "spec": None, "formalizer_tokens": 0, "source": "none"}
        return {"kind": "lp", "spec": spec, "formalizer_tokens": 0, "source": "parser"}
