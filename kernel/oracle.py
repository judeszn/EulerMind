"""Oracle Mode — Mechanical EulerMind. No LLM anywhere.

Oracle stage implementations drive the real kernel loop to validate state
transitions, retry logic, budgeting, failure taxonomy, and trace logging
before any inference code exists. The MechanicalVerifier is NOT a stub: it
performs genuine arithmetic checks (feasibility, constraint satisfaction,
f'(c) = 0) and emits failure signals naming exactly which check failed —
the same signal shape H1 will feed back to a model.

Deliberately independent of benchmark/: the kernel must never import the
instrument that measures it, so small check logic is duplicated here.

FlakyOracleAttempter sabotages its first N attempts, letting the selftest
prove the retry path catches and recovers from failures mechanically.
"""

from __future__ import annotations


class OracleFormalizer:
    def formalize(self, state):
        # Stands in for NL->math; Phase 1 replaces this with the LLM formalizer.
        gt = state._problem_ground_truth  # attached by run_oracle_mode
        kind = state._problem_kind
        return {"kind": kind, "spec": gt}


class OracleAttempter:
    def attempt(self, state):
        return {"strategy": "oracle_lookup", "sabotage": False}


class FlakyOracleAttempter:
    """Fails its first `fail_first` attempts on purpose (returns an answer
    the verifier must reject), then behaves. Exercises the retry path."""

    def __init__(self, fail_first: int = 1):
        self.fail_first = fail_first

    def attempt(self, state):
        return {"strategy": "oracle_lookup",
                "sabotage": state.attempt <= self.fail_first}


class OracleExecutor:
    def execute(self, state, attempt):
        spec = state.formalization["spec"]
        kind = state.formalization["kind"]
        if kind == "lp":
            answer = {"x": spec["x"], "y": spec["y"], "profit": spec["profit"]}
            if attempt["sabotage"]:
                answer = {"x": spec["x"] * 100, "y": spec["y"] * 100,
                          "profit": spec["profit"]}
        elif kind == "calculus":
            answer = {"critical_points": spec["critical_points"]}
            if attempt["sabotage"]:
                answer = {"critical_points":
                          [{"x": c["x"] + 1, "type": c["type"]}
                           for c in spec["critical_points"]]}
        elif kind == "csp":
            if spec["satisfiable"]:
                answer = {"satisfiable": True, "assignment": dict(spec["example"])}
                if attempt["sabotage"]:
                    eng = spec["engineers"][0]
                    forbidden = next((c for c in spec["constraints_spec"]
                                      if c["kind"] == "forbidden"), None)
                    bad = dict(spec["example"])
                    if forbidden:
                        # Violate a forbidden constraint directly.
                        bad[forbidden["engineer"]] = forbidden["project"]
                    else:
                        bad[eng] = bad[spec["engineers"][1]]  # duplicate project
                    answer = {"satisfiable": True, "assignment": bad}
            else:
                answer = {"satisfiable": False}
                if attempt["sabotage"]:
                    # Fabricate certainty: claim satisfiable with no assignment.
                    answer = {"satisfiable": True, "assignment": {}}
        else:
            raise ValueError(kind)
        return {"tool": "oracle", "answer": answer, "tokens": 0}


class MechanicalVerifier:
    """Real arithmetic checks with failure signals. Independent of the
    benchmark graders (the system must not import its own ruler)."""

    TOL = 1e-6

    def verify(self, state, execution):
        kind = state.formalization["kind"]
        spec = state.formalization["spec"]
        answer = execution.get("answer") or {}
        signals = getattr(self, f"_check_{kind}")(spec, answer)
        if signals:
            return {"ok": False, "failure_type": "verification",
                    "signals": signals}
        return {"ok": True, "trust_label": "Verified",
                "failure_type": None, "signals": []}

    def _check_lp(self, spec, answer):
        m = spec["model"]
        signals = []
        try:
            x, y, profit = float(answer["x"]), float(answer["y"]), float(answer["profit"])
        except (KeyError, TypeError, ValueError):
            return [{"kind": "answer_shape", "location": "answer",
                    "evidence": {"detail": "missing/non-numeric fields"}}]
        for name, (ca, cb, cap) in {"constraint_1": (m["a1"], m["b1"], m["c1"]),
                                    "constraint_2": (m["a2"], m["b2"], m["c2"])}.items():
            lhs = ca * x + cb * y
            if lhs > cap + self.TOL:
                signals.append({"kind": "constraint_violation", "location": name,
                                "evidence": {"lhs": lhs, "capacity": cap,
                                            "violated_by": lhs - cap}})
        if x < -self.TOL or y < -self.TOL:
            signals.append({"kind": "nonnegativity", "location": "answer",
                            "evidence": {"x": x, "y": y}})
        if abs(m["p1"] * x + m["p2"] * y - profit) > self.TOL * max(1.0, abs(profit)):
            signals.append({"kind": "profit_consistency", "location": "profit",
                            "evidence": {"claimed": profit,
                                        "computed": m["p1"] * x + m["p2"] * y}})
        return signals

    def _check_calculus(self, spec, answer):
        fp = spec["fprime_coeffs"]  # integer coeffs, lowest degree first
        pts = answer.get("critical_points")
        if not isinstance(pts, list) or not pts:
            return [{"kind": "answer_shape", "location": "critical_points",
                    "evidence": {"detail": "missing critical_points"}}]
        signals = []
        for i, p in enumerate(pts):
            x = p.get("x")
            value = sum(c * x ** i for i, c in enumerate(fp))
            if abs(value) > self.TOL:
                signals.append({"kind": "fprime_zero", "location": f"critical_point_{i}",
                                "evidence": {"x": x, "fprime_value": value}})
        if len(pts) != len(fp) - 1:  # simple roots: deg(f') critical points
            signals.append({"kind": "critical_point_count", "location": "critical_points",
                            "evidence": {"claimed": len(pts), "expected": len(fp) - 1}})
        return signals

    def _check_csp(self, spec, answer):
        sat_claim = answer.get("satisfiable")
        if not spec["satisfiable"]:
            # Mechanical check: a claimed assignment must satisfy constraints;
            # an empty/invalid one on an unsat instance fails immediately.
            if sat_claim is False:
                return []
            assignment = answer.get("assignment") or {}
            return self._check_assignment(spec, assignment) or \
                [{"kind": "unsat_claim", "location": "satisfiable",
                  "evidence": {"detail": "claimed satisfiable on unsat instance"}}]
        if sat_claim is not True:
            return [{"kind": "sat_claim", "location": "satisfiable",
                    "evidence": {"detail": "instance is satisfiable"}}]
        return self._check_assignment(spec, answer.get("assignment") or {})

    def _check_assignment(self, spec, assignment):
        signals = []
        engineers, tags = spec["engineers"], spec["project_tags"]
        if set(assignment) != set(engineers):
            return [{"kind": "assignment_shape", "location": "assignment",
                    "evidence": {"detail": "wrong engineer set"}}]
        values = list(assignment.values())
        if len(set(values)) != len(values):
            signals.append({"kind": "distinct_projects", "location": "assignment",
                            "evidence": {"detail": "duplicate project"}})
        for i, con in enumerate(spec["constraints_spec"]):
            ok = True
            kind = con["kind"]
            if kind == "forbidden":
                ok = assignment[con["engineer"]] != con["project"]
            elif kind == "exact_tag":
                ok = sum(1 for p in values if tags.get(p) == con["tag"]) == con["count"]
            elif kind == "not_both_tag":
                ok = not (tags.get(assignment[con["e1"]]) == con["tag"]
                          and tags.get(assignment[con["e2"]]) == con["tag"])
            elif kind == "implies":
                ok = (assignment[con["e1"]] != con["p1"]
                      or assignment[con["e2"]] == con["p2"])
            if not ok:
                signals.append({"kind": "constraint_violation", "location": f"constraint_{i}",
                                "evidence": {"constraint_kind": kind, "constraint": con}})
        return signals


def run_oracle_mode(problem: dict, *, attempter=None, policy=None, budget=None,
                    logger=None):
    """Drive the real kernel loop with mechanical stages over a benchmark
    problem. Used by the selftest; the Phase 1 gate is: oracle mode must
    score 100% verified through the actual loop machinery.

    policy=None exercises the B2 control path (blind retry); pass a Policy
    (e.g. kernel.policy.DeterministicPolicy()) to exercise B3."""
    from .api import Budget
    from .loop import run_kernel

    state_kind = problem["answer_spec"]["type"]

    class _Bound(OracleFormalizer):
        def formalize(self, state):
            state._problem_ground_truth = problem["ground_truth"]
            state._problem_kind = state_kind
            return super().formalize(state)

    return run_kernel(
        problem,
        formalizer=_Bound(),
        attempter=attempter or OracleAttempter(),
        executor=OracleExecutor(),
        verifier=MechanicalVerifier(),
        policy=policy,
        budget=budget or Budget(),
        logger=logger,
    )
