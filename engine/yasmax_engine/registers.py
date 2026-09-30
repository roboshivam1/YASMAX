"""
File: engine/yasmax_engine/registers.py

The CPU's registers: the GENERAL PURPOSE CPU REGISTERS panel (R00..R31)
and the SPECIAL CPU REGISTERS panel (PC, SP, SR, BR, IR, MAR, MDR).

Key ideas
---------
1. Every write is wrapped to the machine word size (config.wrap), so a
   register can never hold a value real hardware couldn't.
2. Reads and writes made by INSTRUCTIONS are tracked, which powers the
   "Show Reg Access Status" checkbox. Reads made by the UI use `peek()`
   instead of `read()`, so just displaying a register never marks it as
   "accessed".
3. Register names are always shown as R00, R01, ... (two digits, as in
   the original). Input is accepted case-insensitively ("r1", "R01").

How it connects
---------------
- Instruction handlers (later) call read()/write() with names from their
  decoded operands.
- machine.py calls `begin_step()` before each step, so access status
  shows only what the latest step touched.
- The snapshot reads `rows()` and `special.as_dict()`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, fields
from enum import StrEnum

from .config import MachineConfig
from .errors import FaultCode, MachineFault

_NAME_RE = re.compile(r"^R(\d{1,2})$", re.IGNORECASE)


class Access(StrEnum):
    """How a register was touched in the latest step (for highlighting)."""

    READ = "read"
    WRITE = "write"
    BOTH = "both"


def reg_name(index: int) -> str:
    """Display name for a register index: 3 -> "R03"."""
    return f"R{index:02d}"


class RegisterFile:
    """The general purpose registers."""

    def __init__(self, config: MachineConfig) -> None:
        self._config = config
        self._values: list[int] = [0] * config.gpr_count
        self._access: dict[int, Access] = {}

    # ------------------------------------------------------------------
    # Names and sizes
    # ------------------------------------------------------------------

    @property
    def size(self) -> int:
        return len(self._values)

    def index_of(self, name: str) -> int:
        """Turn "R05" (or "r5") into 5. Faults if it isn't a valid register."""
        match = _NAME_RE.match(name.strip())
        if not match or int(match.group(1)) >= self.size:
            raise MachineFault(
                FaultCode.INVALID_REGISTER, f"Invalid register: {name}", register=name
            )
        return int(match.group(1))

    def set_size(self, new_config: MachineConfig) -> None:
        """Switch register set size (the "Select Register Set Size" dropdown).

        TODO(R-12): verify what the original does to values on resize.
        For now: registers that still exist keep their values, and new
        ones start at 0.
        """
        new_size = new_config.gpr_count
        self._config = new_config
        self._values = (self._values + [0] * new_size)[:new_size]
        self._access = {i: a for i, a in self._access.items() if i < new_size}

    # ------------------------------------------------------------------
    # Instruction access (tracked)
    # ------------------------------------------------------------------

    def read(self, name: str) -> int:
        """Read a register as an instruction does. Marks it as read."""
        i = self.index_of(name)
        self._mark(i, Access.READ)
        return self._values[i]

    def write(self, name: str, value: int) -> int:
        """Write a register as an instruction does. Wraps the value, marks
        it as written, and returns the value actually stored."""
        i = self.index_of(name)
        stored = self._config.wrap(value)
        self._values[i] = stored
        self._mark(i, Access.WRITE)
        return stored

    def _mark(self, i: int, kind: Access) -> None:
        previous = self._access.get(i)
        self._access[i] = kind if previous in (None, kind) else Access.BOTH

    def begin_step(self) -> None:
        """Forget access marks from the previous step."""
        self._access.clear()

    # ------------------------------------------------------------------
    # UI access (untracked)
    # ------------------------------------------------------------------

    def peek(self, name: str) -> int:
        """Read without marking access (for display and tests)."""
        return self._values[self.index_of(name)]

    def poke(self, name: str, value: int) -> int:
        """Set a value from the UI (Reg Value -> CHANGE). Not an access."""
        i = self.index_of(name)
        self._values[i] = self._config.wrap(value)
        return self._values[i]

    def reset_all(self) -> None:
        """RESET ALL button: every register back to 0."""
        self._values = [0] * self.size
        self._access.clear()

    def rows(self) -> list[dict[str, object]]:
        """One dict per register, in the shape the snapshot sends to the UI."""
        return [
            {"name": reg_name(i), "val": v, "access": self._access.get(i)}
            for i, v in enumerate(self._values)
        ]


@dataclass
class SpecialRegisters:
    """PC, SP, SR, BR, IR, MAR, MDR.

    IR and MDR are strings or None because the UI shows them as text
    (e.g. an instruction during fetch). None means "empty field".
    TODO(R-4, R-6): verify what SR and BR hold and what IR/MAR/MDR show
    during each clock phase.
    """

    PC: int = 0
    SP: int = 0
    SR: int = 0
    BR: int = 0
    IR: str | None = None
    MAR: int = 0
    MDR: str | None = None

    @classmethod
    def initial(cls, config: MachineConfig) -> SpecialRegisters:
        """Values shown when the simulator first opens. YASMIN 7.5.50 shows
        MAR 2 and MDR 0 before anything runs. TODO(research): why."""
        return cls(SP=config.initial_sp, MAR=2, MDR="0")

    def reset(self, config: MachineConfig) -> None:
        """Back to initial values, keeping the same object (the machine
        and tests may hold references to it)."""
        fresh = SpecialRegisters.initial(config)
        for f in fields(self):
            setattr(self, f.name, getattr(fresh, f.name))

    def as_dict(self) -> dict[str, object]:
        return {f.name: getattr(self, f.name) for f in fields(self)}
