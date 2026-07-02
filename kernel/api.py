"""Frozen Kernel API — v1.

The only contract in the system. Stages consume and produce data through
ExecutionState; nothing else may mutate state. Swapping the model (or any
stage implementation) must never require touching another stage.

Freeze rule: this contract may be revised freely until the first Phase 1
measurement is recorded; after that, any change requires bumping
KERNEL_API_VERSION and a replay-compatibility note in docs/LOGGING.md.
(An API frozen with zero implementations is speculation — kernel/oracle.py
is the existence proof this contract is frozen against.)
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Protocol

from .state import ExecutionState

KERNEL_API_VERSION = 1


@dataclass(frozen=True)
class Budget:
    """Frozen per-run resource budget. The kernel never decides its own
    budget (item 8): experiments stay comparable because the budget is
    config, serialized into every trace record."""
    attempts: int = 3
    timeout_s: float = 15.0
    ram_gb: float = 4.0

    def to_dict(self) -> dict:
        return asdict(self)


class Formalizer(Protocol):
    def formalize(self, state: ExecutionState) -> dict:
        """Natural language -> executable mathematics.
        Returns the formalization dict (variables/constraints/objective/
        unknowns/units). Confidence, if any, must be derived — never
        model-self-reported."""
        ...


class Attempter(Protocol):
    def attempt(self, state: ExecutionState) -> dict:
        """Produce the next attempt (plan/program/answer candidate).
        state.verifier_result from the previous attempt carries failure
        signals — using them is the entire H1 mechanism."""
        ...


class Executor(Protocol):
    def execute(self, state: ExecutionState, attempt: dict) -> dict:
        """Run the attempt deterministically (Guardrail 2: never trust LLM
        arithmetic). Returns execution result incl. candidate `answer` and
        cost fields (`tokens`, if an LLM was involved)."""
        ...


class Verifier(Protocol):
    def verify(self, state: ExecutionState, execution: dict) -> dict:
        """Machine-check the execution. Returns:
        {"ok": bool, "trust_label": str, "failure_type": str|None,
         "signals": list}  — signals say WHICH check failed and how
        (never a bare pass/fail; Guardrail: the verifier produces
        gradients, not verdicts)."""
        ...


class Policy(Protocol):
    def next_action(self, state: ExecutionState) -> str:
        """Escalation ladder decision: one of kernel.state.NEXT_ACTIONS
        (attempt | patch | rederive | reformalize | stop)."""
        ...
