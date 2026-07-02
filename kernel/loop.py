"""The Reasoning Kernel loop — the only loop in the system.

Formalize -> Attempt -> Execute -> Verify (in the loop) -> Observe -> Retry,
under a frozen Budget, logging every attempt with cost accounting and a
failure-taxonomy classification (Guardrail 6).

Phase 0 validates this machinery mechanically (kernel/oracle.py, no LLM):
if the kernel cannot pass with an oracle, the LLM will never save it.
"""

from __future__ import annotations

import time

from .api import KERNEL_API_VERSION, Budget
from .state import ExecutionState, STATE_SCHEMA_VERSION


def run_kernel(problem: dict, *, formalizer, attempter, executor, verifier,
               budget: Budget = Budget(), logger=None) -> ExecutionState:
    state = ExecutionState(problem_id=problem["id"], problem_text=problem["text"])
    started = time.perf_counter()

    state.formalization = formalizer.formalize(state)
    state.record("formalized")
    state.next_action = "attempt"

    while state.attempt < budget.attempts:
        if time.perf_counter() - started > budget.timeout_s:
            state.record("budget_exhausted", reason="timeout")
            state.verifier_result = {"ok": False, "failure_type": "timeout",
                                     "signals": []}
            break

        state.attempt += 1
        t0 = time.perf_counter()
        attempt = attempter.attempt(state)
        execution = executor.execute(state, attempt)
        state.execution_result = execution
        verdict = verifier.verify(state, execution)
        state.verifier_result = verdict  # failure signals feed the next attempt
        latency_ms = round((time.perf_counter() - t0) * 1000, 3)

        if logger is not None:
            logger.log({
                "schema_version": STATE_SCHEMA_VERSION,
                "kernel_api_version": KERNEL_API_VERSION,
                "problem_id": state.problem_id,
                "attempt": state.attempt,
                "tool": execution.get("tool"),
                "verification": "verified" if verdict["ok"] else "failed",
                "failure_type": None if verdict["ok"] else verdict.get("failure_type", "unknown"),
                "signals": verdict.get("signals", []),
                "latency_ms": latency_ms,
                "tokens": execution.get("tokens", 0),
                "budget": budget.to_dict(),
            })
        state.record("attempt_done", ok=verdict["ok"],
                     failure_type=None if verdict["ok"] else verdict.get("failure_type"))

        if verdict["ok"]:
            state.trust_label = verdict.get("trust_label", "Derived")
            state.next_action = "stop"
            return state

    # Retries exhausted. Guardrail 5: return Open or Derived — never fake.
    state.trust_label = "Open"
    state.next_action = "stop"
    return state
