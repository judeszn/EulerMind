"""Phase 1B — DeterministicPolicy. Pure rule table, no model.

Consumes FailureSignals (kind/location/evidence) from the previous attempt
and decides the next rung of the escalation ladder. This is B3's *first*
policy: the mapping from failure kind to repair action below is an
explicit, naive guess — not a claim that it's correct. H2 (patch vs.
rewrite) exists specifically to test and improve it with data. Ownership
matters here: this table lives in Policy, not in the Verifier, because
deciding what to do about a failure is a different job from detecting one
(see kernel/api.py's FailureSignal docstring).
"""

from __future__ import annotations

from .state import NEXT_ACTIONS

# kind -> default first-offense action. Anything unlisted escalates
# straight to "rederive" (unknown failure mode -> don't trust a patch).
DEFAULT_ACTION = {
    # Answer didn't even parse into the expected shape -> the plan itself
    # is probably wrong, not just a numeric slip.
    "answer_shape": "reformalize",
    "assignment_shape": "reformalize",
    "formalization_shape": "reformalize",  # formalizer produced no usable spec at all
    # Fabricated certainty (claiming sat/unsat against the evidence) is a
    # strategy error, not an arithmetic one.
    "unsat_claim": "reformalize",
    "sat_claim": "reformalize",
    # Numeric constraint violations and consistency checks: a nearby
    # candidate might satisfy them, worth one localized patch attempt.
    "constraint_violation": "patch",
    "distinct_projects": "patch",
    "profit_consistency": "patch",
    "nonnegativity": "patch",
    "fprime_zero": "patch",
    # Wrong structural count (e.g. wrong number of critical points) means
    # the derivation step itself is off, not just one bad value.
    "critical_point_count": "rederive",
}


class DeterministicPolicy:
    def next_action(self, state) -> str:
        result = state.verifier_result
        if not result or result.get("ok"):
            return "stop"

        signals = result.get("signals", [])
        if not signals:
            return "rederive"

        kinds = {s["kind"] if isinstance(s, dict) else s.kind for s in signals}
        actions = {DEFAULT_ACTION.get(k, "rederive") for k in kinds}

        # Escalate to the strongest rung any signal calls for.
        for rung in ("reformalize", "rederive", "patch"):
            if rung in actions:
                action = rung
                break
        else:
            action = "rederive"

        # If the SAME failure kind already showed up in a strictly prior
        # attempt on this run, patching again clearly isn't working —
        # escalate. Filtered by attempt number, not set difference: a kind
        # that repeats must NOT cancel itself out of "prior".
        prior_kinds = {
            k for h in state.history
            if h.get("event") == "attempt_done" and not h.get("ok")
            and h.get("attempt", state.attempt) < state.attempt
            for k in h.get("failure_kinds", [])
        }
        if action == "patch" and (kinds & prior_kinds):
            action = "rederive"

        assert action in NEXT_ACTIONS
        return action
