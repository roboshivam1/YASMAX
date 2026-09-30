"""
File: engine/yasmax_engine/errors.py

All exceptions the engine can raise, split into two families:

1. ProgramError: the USER asked for something invalid while building a
   program (bad name, bad base address, bad operand). The machine state
   is unchanged. The UI shows a dialog and nothing else happens.

2. MachineFault: something went wrong WHILE EXECUTING (bad address,
   stack overflow, divide by zero). The machine stops in the "fault"
   run state, just like real hardware raising an exception.

How it connects
---------------
- Engine modules raise these.
- machine.py (later) catches them at the command boundary and converts
  them into protocol events with `to_event()`, so the worker never has
  to understand Python exceptions.

Messages
--------
The exact wording YASMIN uses for each error is research item R-9.
Until verified, messages are plain English and every fault carries a
stable `code` that the UI can map to the real wording later.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any


class FaultCode(StrEnum):
    """Stable identifiers for runtime faults.

    StrEnum means each member is also a plain string, so it serialises
    to JSON as e.g. "stack_overflow" with no extra work.
    """

    INVALID_ADDRESS = "invalid_address"
    INVALID_REGISTER = "invalid_register"
    INVALID_INSTRUCTION = "invalid_instruction"
    STACK_OVERFLOW = "stack_overflow"
    STACK_UNDERFLOW = "stack_underflow"
    DIVIDE_BY_ZERO = "divide_by_zero"
    NO_INSTRUCTION = "no_instruction"
    NOT_AVAILABLE = "not_available"


class YasmaxError(Exception):
    """Base class, so callers can catch everything from the engine at once."""

    def to_event(self) -> dict[str, Any]:
        """Convert to a JSON-safe event for the worker protocol."""
        return {"type": "error", "message": str(self)}


class ProgramError(YasmaxError):
    """Invalid request while creating or editing a program.

    `field` names the input the user got wrong (e.g. "base_address"),
    so the UI can focus that field after showing the dialog.
    """

    def __init__(self, message: str, field: str | None = None) -> None:
        super().__init__(message)
        self.field = field

    def to_event(self) -> dict[str, Any]:
        return {"type": "program_error", "message": str(self), "field": self.field}


class MachineFault(YasmaxError):
    """Runtime fault raised during execution.

    `detail` holds context such as the offending address or register,
    so the dialog and any future logging can show it.
    """

    def __init__(self, code: FaultCode, message: str, **detail: Any) -> None:
        super().__init__(message)
        self.code = code
        self.detail = detail

    def to_event(self) -> dict[str, Any]:
        return {
            "type": "fault",
            "code": str(self.code),
            "message": str(self),
            "detail": self.detail,
        }
