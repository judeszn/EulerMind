"""EulerMind Reasoning Kernel.

Phase 0 ships the frozen Execution State schema (state.py), the frozen
Kernel API v2 (api.py), the loop machinery with Policy wired in (loop.py),
a naive deterministic Policy (policy.py), and Oracle Mode (oracle.py) —
mechanical validation of the loop with no LLM anywhere.

`policy=None` in run_kernel() is the B2 control arm (blind retry, no
failure signal changes behavior). `policy=DeterministicPolicy()` (or any
Policy implementation) is the B3 treatment arm. Phase 1 replaces the
oracle stages with real ones; the loop, API, and logging schema do not
change (see docs/VISION.md and docs/LOGGING.md).
"""

from .api import Budget, FailureSignal, KERNEL_API_VERSION  # noqa: F401
from .loop import run_kernel  # noqa: F401
from .policy import DeterministicPolicy  # noqa: F401
from .state import (  # noqa: F401
    ExecutionState, TraceLogger, TRUST_LABELS, FAILURE_TYPES,
    STATE_SCHEMA_VERSION,
)
