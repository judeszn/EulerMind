"""Generator: polynomial critical-point problems (category: calculus_poly).

Construction runs backwards so ground truth is exact by design: choose the
critical points first, build f'(x) = lead * prod(x - c_i), integrate with
Fractions, then scale by the lcm of denominators (positive, so classification
is unchanged) to present f with integer coefficients.

Grading uses critical points + classification. The prose also asks for
monotonicity intervals and derivative verification — those are explanation
artifacts, redundant given the classification, and are stored in ground truth
but not machine-graded.
"""

from __future__ import annotations

import math
import random
from fractions import Fraction

from ..schema import make_problem
from .base import insert_distractors, join_paragraphs


def _poly_mul(p, q):
    out = [Fraction(0)] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            out[i + j] += a * b
    return out


def _poly_eval(p, x):
    return sum(c * x ** i for i, c in enumerate(p))


def _poly_str(coeffs) -> str:
    """Human-readable polynomial from integer coeffs (lowest degree first)."""
    terms = []
    for i in range(len(coeffs) - 1, -1, -1):
        c = coeffs[i]
        if c == 0:
            continue
        sign = "-" if c < 0 else "+"
        mag = abs(c)
        if i == 0:
            body = str(mag)
        elif i == 1:
            body = "x" if mag == 1 else f"{mag}x"
        else:
            body = f"x^{i}" if mag == 1 else f"{mag}x^{i}"
        terms.append((sign, body))
    if not terms:
        return "0"
    first_sign, first_body = terms[0]
    out = ("-" if first_sign == "-" else "") + first_body
    for sign, body in terms[1:]:
        out += f" {sign} {body}"
    return out


def generate(base_seed: int) -> list[dict]:
    """Returns [clean_problem, messy_problem] sharing one ground truth."""
    rng = random.Random(f"calc-{base_seed}")
    k = rng.choice([2, 3])
    crit = sorted(rng.sample(range(-6, 7), k))
    lead = rng.choice([1, -1, 2, -2])

    fprime = [Fraction(lead)]
    for c in crit:
        fprime = _poly_mul(fprime, [Fraction(-c), Fraction(1)])

    anti = [Fraction(0)] + [fprime[i] / (i + 1) for i in range(len(fprime))]
    scale = 1
    for c in anti:
        scale = scale * c.denominator // math.gcd(scale, c.denominator)
    coeffs = [int(c * scale) for c in anti]
    coeffs[0] = rng.randint(-9, 9)  # constant of integration; irrelevant to f'

    # Classify by the sign of f' on each side of every critical point.
    samples = [Fraction(crit[0] - 1)]
    samples += [Fraction(a + b, 2) for a, b in zip(crit, crit[1:])]
    samples.append(Fraction(crit[-1] + 1))
    signs = [1 if _poly_eval(fprime, t) > 0 else -1 for t in samples]

    critical_points = [
        {"x": c, "type": "local_max" if signs[i] > 0 else "local_min"}
        for i, c in enumerate(crit)
    ]
    intervals, lo = [], "-inf"
    for i, s in enumerate(signs):
        hi = crit[i] if i < len(crit) else "inf"
        intervals.append({"from": lo, "to": hi,
                          "direction": "increasing" if s > 0 else "decreasing"})
        lo = hi

    poly = _poly_str(coeffs)
    ground_truth = {
        "critical_points": critical_points,
        "intervals": intervals,
        "f_coeffs": coeffs,
        "fprime_coeffs": [int(c * scale) for c in fprime],
    }
    answer_spec = {
        "type": "calculus",
        "fields": {"critical_points":
                   "list of {x: number, type: 'local_max'|'local_min'}"},
    }
    ask = ("Find every critical point of f, classify each as a local maximum "
           "or a local minimum, determine the intervals on which f is "
           "increasing and decreasing, and verify each derivative computation.")

    clean_paras = [f"Let f(x) = {poly}.", ask]
    messy_paras = insert_distractors(rng, [
        "An engineer models the vertical deflection of a beam segment by the "
        f"function f(x) = {poly}, where x is the horizontal position in meters "
        "measured from the left support.",
        ask,
    ], count=2)

    base_id = f"calc-{base_seed:05d}"
    common = dict(base_id=base_id, category="calculus_poly", seed=base_seed,
                  ground_truth=ground_truth, answer_spec=answer_spec)
    return [
        make_problem(variant="clean", text=join_paragraphs(clean_paras), **common),
        make_problem(variant="messy", text=join_paragraphs(messy_paras), **common),
    ]
