"""EulerMind Reasoning Kernel.

Phase 0 ships the frozen Execution State schema (state.py), the frozen
Kernel API v1 (api.py), the loop machinery (loop.py), and Oracle Mode
(oracle.py) — mechanical validation of the loop with no LLM anywhere.
Phase 1 replaces the oracle stages with real ones; the loop, API, and
logging schema do not change (see docs/VISION.md and docs/LOGGING.md).
"""

from .api import Budget, KERNEL_API_VERSION  # noqa: F401
from .loop import run_kernel  # noqa: F401
from .state import (  # noqa: F401
    ExecutionState, TraceLogger, TRUST_LABELS, FAILURE_TYPES,
    STATE_SCHEMA_VERSION,
)
