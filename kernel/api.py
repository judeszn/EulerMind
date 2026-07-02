"""Frozen Kernel API — v2.

The only contract in the system. Stages consume and produce data through
ExecutionState; nothing else may mutate state. Swapping the model (or any
stage implementation) must never require touching another stage.

Freeze rule: this contract may be revised freely until the first Phase 1
measurement is recorded; after that, any change requires bumping
KERNEL_API_VERSION and a replay-compatibility note in docs/LOGGING.md.
(An API frozen with zero implementations is speculation — kernel/oracle.py
is the existence proof this contract is frozen against.)

v2 change: added FailureSignal and wired Policy into the loop (kernel/loop.py).
FailureSignal carries only what a Verifier can actually certify — kind,
location, evidence. It deliberately does NOT carry repair_scope or
confidence: deciding what to do about a failure is Policy's job, not the
Verifier's. Collapsing that distinction would bake an unmeasured guess
(which failures need patching vs. reformalizing) into a frozen contract —
that mapping is an open question (see H2), not a solved verifier feature.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Protocol

from .state import ExecutionState

KERNEL_API_VERSION = 2


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


@dataclass(frozen=True)
class FailureSignal:
    """The contract between Verifier and Policy — not the Policy itself.

    Fields are limited to what a mechanical/symbolic check can actually
    certify. `kind` and `location` together let a Policy group failures
    (e.g. "this is the third distinct_projects failure in a row") without
    the Verifier having to guess what should be done about them."""
    kind: str        # e.g. "constraint_violation", "answer_shape", "unsat_claim"
    location: str     # e.g. "constraint_1", "critical_point_0", "assignment"
    evidence: dict    # numeric/structural substance, e.g. {"violated_by": 12.0}

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
         "signals": list[FailureSignal | dict]}  — signals say WHICH check
        failed, WHERE, and with what evidence (never a bare pass/fail;
        Guardrail: the verifier produces gradients, not verdicts). The
        Verifier does not decide what to do about a failure — see Policy."""
        ...


class Policy(Protocol):
    def next_action(self, state: ExecutionState) -> str:
        """Escalation ladder decision, made from state.verifier_result's
        FailureSignals: one of kernel.state.NEXT_ACTIONS
        (attempt | patch | rederive | reformalize | stop).

        This is where the patch-vs-rederive-vs-reformalize judgment call
        lives. kernel.policy.DeterministicPolicy is a naive, explicit rule
        table — it is B3's first policy, not a claim that the mapping from
        failure kind to repair action is correct. H2 exists to improve it."""
        ...
