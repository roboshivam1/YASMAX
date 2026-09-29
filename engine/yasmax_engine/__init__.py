"""
File: engine/yasmax_engine/__init__.py

Public face of the yasmax_engine package.

Anything the worker (web/js/worker.js) or tests should use is re-exported
here, so callers write `from yasmax_engine import Machine` and never
depend on the internal file layout. `Machine` is the main entry point.

The browser does not use these names directly: the worker talks only to
`yasmax_engine.api` (boot / dispatch), which wraps a Machine in JSON.
"""

__version__ = "0.2.0"

from .config import DEFAULT_CONFIG, MachineConfig  # noqa: E402
from .errors import FaultCode, MachineFault, ProgramError, YasmaxError  # noqa: E402
from .flags import FlagResult, StatusFlags, evaluate  # noqa: E402
from .machine import Machine, RunState  # noqa: E402
from .registers import Access, RegisterFile, SpecialRegisters, reg_name  # noqa: E402

__all__ = [
    "DEFAULT_CONFIG",
    "Access",
    "FaultCode",
    "FlagResult",
    "Machine",
    "MachineConfig",
    "MachineFault",
    "ProgramError",
    "RunState",
    "RegisterFile",
    "SpecialRegisters",
    "StatusFlags",
    "YasmaxError",
    "evaluate",
    "reg_name",
]
