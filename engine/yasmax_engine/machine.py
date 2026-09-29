"""
File: engine/yasmax_engine/machine.py

The Machine: one simulated CPU, and the ONLY object the outside world
talks to (see docs/ARCHITECTURE.md §3.1).

Current scope (batch 2)
-----------------------
The Machine owns the parts that already exist: config, general purpose
registers, special registers, flags and the run state. It exposes the
commands that don't depend on the instruction set:

    set_register, reset_all_registers, set_register_set_size, snapshot

Programs, memory, the stack and step/run are added in later batches, as
new attributes and new command methods. The rule stays the same: every
command is a plain method, takes JSON-friendly arguments, and either
changes state or raises a YasmaxError.

How it connects
---------------
- api.py creates one Machine and routes JSON commands to its methods.
- snapshot.py reads its attributes to build the state sent to the UI.
- Tests can create a Machine directly and call methods, no JSON needed.
"""

from __future__ import annotations

import dataclasses
from enum import StrEnum

from .config import DEFAULT_CONFIG, MachineConfig
from .errors import ProgramError
from .flags import StatusFlags
from .registers import RegisterFile, SpecialRegisters


class RunState(StrEnum):
    """The run state machine from docs/APP_FLOW.md §8."""

    EMPTY = "empty"
    IDLE = "idle"
    RUNNING = "running"
    HALTED = "halted"
    FAULT = "fault"


def parse_int(value: object, field: str) -> int:
    """Accept an int, or text a student typed (e.g. " -12 "), as an int.

    Anything else raises ProgramError naming the field, so the UI can
    show a dialog and focus the right input box.
    TODO(R-1): verify whether the original also accepts hex input.
    """
    if isinstance(value, bool):
        raise ProgramError("Please enter a whole number.", field=field)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip(), 10)
        except ValueError:
            pass
    raise ProgramError("Please enter a whole number.", field=field)


class Machine:
    """One simulated CPU."""

    def __init__(self, config: MachineConfig = DEFAULT_CONFIG) -> None:
        config.validate()
        self.config = config
        self.gpr = RegisterFile(config)
        self.special = SpecialRegisters.initial(config)
        self.flags = StatusFlags()
        self.run_state = RunState.EMPTY

    # ------------------------------------------------------------------
    # Register commands (Registers tab, bottom right of the window)
    # ------------------------------------------------------------------

    def set_register(self, name: str, value: object) -> None:
        """Reg Value -> CHANGE: set one register from the UI.

        Uses poke(), so this does NOT count as an instruction access.
        """
        number = parse_int(value, field="reg_value")
        self.gpr.poke(name, number)

    def reset_all_registers(self) -> None:
        """RESET ALL: every general purpose register back to 0."""
        self.gpr.reset_all()

    def set_register_set_size(self, size: object) -> None:
        """Select Register Set Size dropdown."""
        n = parse_int(size, field="register_set_size")
        if n not in self.config.gpr_set_sizes:
            raise ProgramError(
                f"Register set size must be one of {list(self.config.gpr_set_sizes)}.",
                field="register_set_size",
            )
        self.config = dataclasses.replace(self.config, gpr_count=n)
        self.gpr.set_size(self.config)

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    def snapshot(self) -> dict[str, object]:
        """Everything the UI needs to redraw the window (snapshot.py)."""
        from .snapshot import build_snapshot

        return build_snapshot(self)
