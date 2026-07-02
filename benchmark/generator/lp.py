"""Generator: two-variable linear-programming word problems (category:
optimization_lp).

Ground truth is computed exactly at generation time by vertex enumeration
with Fractions — the harness never depends on the solvers it will measure.
Instances are filtered so the optimum is unique and sits at the integer
intersection vertex, giving clean integer answers.

Messy variant: distractor facts + one capacity expressed in minutes instead
of hours (the solver must convert units).
"""

from __future__ import annotations

import random
from fractions import Fraction

from ..schema import make_problem
from .base import insert_distractors, join_paragraphs

PRODUCT_PAIRS = [
    ("Product A", "Product B"),
    ("standard chairs", "deluxe chairs"),
    ("basic widgets", "premium widgets"),
    ("small drones", "large drones"),
    ("cotton shirts", "denim jackets"),
]
RESOURCE_PAIRS = [
    ("machining", "assembly"),
    ("cutting", "finishing"),
    ("printing", "binding"),
    ("welding", "painting"),
]


def _solve(a1, b1, c1, a2, b2, c2, p1, p2):
    """Exact optimum of max p1*x + p2*y s.t. a1x+b1y<=c1, a2x+b2y<=c2, x,y>=0.

    Returns (x, y, value) or None when the optimum is not unique across
    vertices (ties are rejected at generation time so grading is unambiguous).
    """
    verts = {
        (Fraction(0), Fraction(0)),
        (min(Fraction(c1, a1), Fraction(c2, a2)), Fraction(0)),
        (Fraction(0), min(Fraction(c1, b1), Fraction(c2, b2))),
    }
    det = a1 * b2 - a2 * b1
    if det != 0:
        ix = Fraction(c1 * b2 - c2 * b1, det)
        iy = Fraction(a1 * c2 - a2 * c1, det)
        if ix >= 0 and iy >= 0:
            verts.add((ix, iy))
    feasible = [(x, y) for x, y in verts
                if a1 * x + b1 * y <= c1 and a2 * x + b2 * y <= c2]
    scored = sorted(((p1 * x + p2 * y, x, y) for x, y in feasible), reverse=True)
    if len(scored) > 1 and scored[0][0] == scored[1][0]:
        return None
    val, x, y = scored[0]
    return x, y, val


def generate(base_seed: int) -> list[dict]:
    """Returns [clean_problem, messy_problem] sharing one ground truth."""
    rng = random.Random(f"lp-{base_seed}")
    for _ in range(500):
        x, y = rng.randint(8, 45), rng.randint(8, 45)
        a1, b1, a2, b2 = (rng.randint(2, 6) for _ in range(4))
        if a1 * b2 == a2 * b1:
            continue
        c1, c2 = a1 * x + b1 * y, a2 * x + b2 * y
        p1, p2 = rng.randint(20, 90), rng.randint(20, 90)
        opt = _solve(a1, b1, c1, a2, b2, c2, p1, p2)
        if opt is not None and (opt[0], opt[1]) == (Fraction(x), Fraction(y)):
            break
    else:
        raise RuntimeError(f"no valid LP instance for seed {base_seed}")

    prod1, prod2 = rng.choice(PRODUCT_PAIRS)
    res1, res2 = rng.choice(RESOURCE_PAIRS)
    profit = p1 * x + p2 * y

    ground_truth = {
        "x": x, "y": y, "profit": profit,
        "model": {"a1": a1, "b1": b1, "c1": c1,
                  "a2": a2, "b2": b2, "c2": c2, "p1": p1, "p2": p2},
        "var_names": {"x": prod1, "y": prod2},
    }
    answer_spec = {
        "type": "lp",
        "fields": {"x": f"units of {prod1}", "y": f"units of {prod2}",
                   "profit": "maximum total profit in dollars"},
    }

    requirements = (
        f"Each unit of {prod1} requires {a1} hours of {res1} and {a2} hours of {res2}. "
        f"Each unit of {prod2} requires {b1} hours of {res1} and {b2} hours of {res2}."
    )
    ask = ("Determine how many units of each product maximize total profit, "
           "report the maximum profit, and verify that your plan satisfies "
           "every capacity constraint.")

    clean_paras = [
        f"A workshop produces two products: {prod1} and {prod2}.",
        requirements,
        f"The workshop has {c1} hours of {res1} capacity and {c2} hours of {res2} capacity available.",
        f"Each unit of {prod1} yields ${p1} profit and each unit of {prod2} yields ${p2} profit.",
        ask,
    ]
    messy_paras = insert_distractors(rng, [
        f"A workshop produces two products: {prod1} and {prod2}.",
        requirements,
        f"The workshop has {c1} hours of {res1} capacity available. "
        f"The {res2} department reports {c2 * 60} minutes of available capacity.",
        f"Each unit of {prod1} yields ${p1} profit and each unit of {prod2} yields ${p2} profit.",
        ask,
    ], count=2)

    base_id = f"lp-{base_seed:05d}"
    common = dict(base_id=base_id, category="optimization_lp", seed=base_seed,
                  ground_truth=ground_truth, answer_spec=answer_spec)
    return [
        make_problem(variant="clean", text=join_paragraphs(clean_paras), **common),
        make_problem(variant="messy", text=join_paragraphs(messy_paras), **common),
    ]
