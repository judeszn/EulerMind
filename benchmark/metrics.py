"""Grading and statistics.

Graders re-verify answers against the machine-readable ground-truth spec
(feasibility, constraint satisfaction) rather than string-matching, so any
valid alternative answer is accepted where the mathematics permits one.

Statistics: paired system comparison via McNemar's exact test. At n≈100
paired problems, rate differences under ~7 points are noise — kill decisions
must come from compare_paired, never from eyeballing two rates.
"""

from __future__ import annotations

import math

from .generator.csp import check_assignment

TOL = 1e-6


# --------------------------------------------------------------------------
# Graders
# --------------------------------------------------------------------------

def grade(problem: dict, answer) -> bool:
    """True iff `answer` is a correct solution to `problem`."""
    if not isinstance(answer, dict):
        return False
    kind = problem["answer_spec"]["type"]
    try:
        if kind == "lp":
            return _grade_lp(problem, answer)
        if kind == "calculus":
            return _grade_calculus(problem, answer)
        if kind == "csp":
            return _grade_csp(problem, answer)
        if kind == "knapsack":
            return _grade_knapsack(problem, answer)
    except (TypeError, ValueError, KeyError):
        return False
    raise ValueError(f"unknown answer_spec type: {kind}")


def _num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _grade_lp(problem, answer):
    gt = problem["ground_truth"]
    m = gt["model"]
    x, y, profit = _num(answer.get("x")), _num(answer.get("y")), _num(answer.get("profit"))
    if x is None or y is None or profit is None:
        return False
    feasible = (x >= -TOL and y >= -TOL
                and m["a1"] * x + m["b1"] * y <= m["c1"] + TOL
                and m["a2"] * x + m["b2"] * y <= m["c2"] + TOL)
    consistent = abs(m["p1"] * x + m["p2"] * y - profit) <= TOL * max(1.0, abs(profit))
    optimal = abs(profit - gt["profit"]) <= TOL * max(1.0, abs(gt["profit"]))
    return feasible and consistent and optimal


def _grade_calculus(problem, answer):
    expected = problem["ground_truth"]["critical_points"]
    got = answer.get("critical_points")
    if not isinstance(got, list) or len(got) != len(expected):
        return False
    remaining = list(got)
    for exp in expected:
        match = next((g for g in remaining
                      if isinstance(g, dict)
                      and _num(g.get("x")) is not None
                      and abs(_num(g.get("x")) - exp["x"]) <= TOL
                      and g.get("type") == exp["type"]), None)
        if match is None:
            return False
        remaining.remove(match)
    return True


def _grade_knapsack(problem, answer):
    gt = problem["ground_truth"]
    models = gt["models"]
    counts = answer.get("counts")
    score = _num(answer.get("score"))
    if not isinstance(counts, dict) or score is None:
        return False
    if set(counts) - set(models):
        return False  # unknown model name
    resolved = {name: counts.get(name, 0) for name in models}
    for c in resolved.values():
        if not isinstance(c, (int, float)) or c < 0 or abs(c - round(c)) > TOL:
            return False
    resolved = {name: round(c) for name, c in resolved.items()}

    ram = sum(c * models[n]["ram_gb"] for n, c in resolved.items())
    flops = sum(c * models[n]["flops_g"] for n, c in resolved.items())
    latency = sum(c * models[n]["latency_ms"] for n, c in resolved.items())
    b = gt["budgets"]
    if ram > b["ram_gb"] + TOL or flops > b["flops_g"] + TOL or latency > b["latency_ms"] + TOL:
        return False

    high_acc_units = sum(c for n, c in resolved.items()
                         if models[n]["accuracy"] >= gt["high_acc_threshold"])
    if high_acc_units < 1:
        return False

    computed_score = sum(c * models[n]["score"] for n, c in resolved.items())
    if abs(computed_score - score) > TOL:
        return False  # claimed score inconsistent with the claimed counts
    return computed_score == gt["score"]  # must also be optimal


def _grade_csp(problem, answer):
    gt = problem["ground_truth"]
    sat = answer.get("satisfiable")
    if not gt["satisfiable"]:
        return sat is False  # inventing an assignment for an unsat instance = wrong
    if sat is not True:
        return False
    assignment = answer.get("assignment")
    if not isinstance(assignment, dict):
        return False
    if set(assignment) != set(gt["engineers"]):
        return False
    values = list(assignment.values())
    if len(set(values)) != len(values) or not set(values) <= set(gt["projects"]):
        return False
    return check_assignment(gt["constraints_spec"], gt["project_tags"], assignment)


# --------------------------------------------------------------------------
# Aggregation
# --------------------------------------------------------------------------

def _rate(results):
    return round(sum(r["correct"] for r in results) / len(results), 4) if results else None


def _verified_rate(results):
    if not results:
        return None
    hits = sum(1 for r in results if r["correct"] and r["trust_label"] == "Verified")
    return round(hits / len(results), 4)


def summarize(problems: list[dict], results: list[dict]) -> dict:
    pmap = {p["id"]: p for p in problems}
    summary = {
        "n": len(results),
        "correct_rate": _rate(results),
        "verified_correct_rate": _verified_rate(results),
        "by_category": {}, "by_variant": {}, "by_split": {},
    }
    for key in ("category", "variant", "split"):
        groups: dict[str, list] = {}
        for r in results:
            groups.setdefault(r[key], []).append(r)
        summary[f"by_{key}"] = {
            g: {"n": len(rs), "correct_rate": _rate(rs),
                "verified_correct_rate": _verified_rate(rs)}
            for g, rs in sorted(groups.items())
        }

    # Formalization robustness: paired clean-vs-messy delta on shared base_ids.
    clean = {r["base_id"]: r for r in results if r["variant"] == "clean"}
    messy = {r["base_id"]: r for r in results if r["variant"] == "messy"}
    shared = sorted(set(clean) & set(messy))
    if shared:
        c_rate = sum(clean[b]["correct"] for b in shared) / len(shared)
        m_rate = sum(messy[b]["correct"] for b in shared) / len(shared)
        summary["robustness"] = {
            "n_pairs": len(shared),
            "clean_rate": round(c_rate, 4),
            "messy_rate": round(m_rate, 4),
            "delta": round(c_rate - m_rate, 4),
        }

    # Epistemic discipline: accuracy on unsatisfiable instances (Law 1).
    unsat = [r for r in results
             if pmap[r["id"]]["category"] == "constraint_csp"
             and not pmap[r["id"]]["ground_truth"]["satisfiable"]]
    if unsat:
        summary["epistemic_unsat"] = {"n": len(unsat), "correct_rate": _rate(unsat)}

    durations = sorted(r["duration_s"] for r in results)
    if durations:
        summary["timing"] = {
            "mean_s": round(sum(durations) / len(durations), 6),
            "p95_s": round(durations[min(len(durations) - 1,
                                         int(0.95 * len(durations)))], 6),
        }
    peaks = [r.get("peak_rss_bytes") for r in results if r.get("peak_rss_bytes")]
    if peaks:
        summary["peak_rss_mb"] = round(max(peaks) / 1e6, 1)
    return summary


# --------------------------------------------------------------------------
# Paired comparison (the only sanctioned basis for keep/delete decisions)
# --------------------------------------------------------------------------

def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar p-value from discordant-pair counts."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def compare_paired(results_a: list[dict], results_b: list[dict],
                   alpha: float = 0.05) -> dict:
    """Compare two systems on the same problems. b = A-only correct,
    c = B-only correct. Verdict is 'indistinguishable' unless p < alpha."""
    a_map = {r["id"]: r["correct"] for r in results_a}
    b_map = {r["id"]: r["correct"] for r in results_b}
    shared = sorted(set(a_map) & set(b_map))
    b_count = sum(1 for i in shared if a_map[i] and not b_map[i])
    c_count = sum(1 for i in shared if b_map[i] and not a_map[i])
    p = mcnemar_exact(b_count, c_count)
    if p < alpha:
        verdict = "a_better" if b_count > c_count else "b_better"
    else:
        verdict = "indistinguishable"
    return {
        "n_paired": len(shared),
        "a_rate": round(sum(a_map[i] for i in shared) / len(shared), 4) if shared else None,
        "b_rate": round(sum(b_map[i] for i in shared) / len(shared), 4) if shared else None,
        "a_only_correct": b_count,
        "b_only_correct": c_count,
        "p_value": round(p, 6),
        "verdict": verdict,
    }
