"""
File: engine/yasmax_engine/stack.py

The PROGRAM STACK (RAM) panel: the hardware stack used by PSH, POP, MSF,
CAL and RET.

What the lab showed (YASMIN 7.5.50)
-----------------------------------
- SP starts at 8096 and goes UP by 2 (one word) per entry: 8096 -> 8100
  after MSF pushed two entries.
- Each entry shows Pos (0 = bottom), Val (D) and Addr = the LAdd of the
  instruction that pushed it. The top row is marked "TOS->", the bottom
  row "BOS->".
- MSF on an empty stack pushed Val -1 then Val 0, both with its own Addr.
- POP on an empty stack gives the message "Stack overflow" (tutorial).
- RESET PROGRAM empties the stack.

TODO(research): how MSF / CAL / RET use the frame. Working model: MSF
pushes the previous frame position (-1 = none) and an empty return slot;
CAL writes the return address into that slot and jumps; RET jumps back to
it and removes the frame. Also the size limit (config.stack_limit).
"""

from __future__ import annotations

from dataclasses import dataclass

from .config import MachineConfig
from .errors import FaultCode, MachineFault


@dataclass
class StackEntry:
    val: int
    addr: int


class Stack:
    def __init__(self, config: MachineConfig) -> None:
        self._config = config
        self.entries: list[StackEntry] = []
        self.frame = -1  # position of the current MSF frame, -1 = none

    @property
    def sp(self) -> int:
        return self._config.initial_sp + self._config.word_bytes * len(self.entries)

    def reset(self) -> None:
        self.entries.clear()
        self.frame = -1

    def push(self, value: int, addr: int) -> None:
        if len(self.entries) >= self._config.stack_limit:
            raise MachineFault(FaultCode.STACK_OVERFLOW, "Stack overflow")
        self.entries.append(StackEntry(self._config.wrap(value), addr))

    def pop(self) -> int:
        if not self.entries:
            # The tutorial's wording for popping an empty stack.
            raise MachineFault(FaultCode.STACK_UNDERFLOW, "Stack overflow")
        entry = self.entries.pop()
        if self.frame >= len(self.entries):
            self.frame = -1
        return entry.val

    def mark_frame(self, addr: int) -> None:
        """MSF: previous frame position, then an empty return-address slot."""
        self.push(self.frame, addr)
        self.push(0, addr)
        self.frame = len(self.entries) - 2

    def call(self, return_addr: int, addr: int) -> None:
        """CAL: fill the frame's return slot (or push, if there is no MSF)."""
        if 0 <= self.frame < len(self.entries) - 1:
            self.entries[self.frame + 1].val = return_addr
        else:
            self.push(return_addr, addr)

    def ret(self) -> int:
        """RET: the return address; the frame is removed."""
        if 0 <= self.frame < len(self.entries) - 1:
            back = self.entries[self.frame + 1].val
            previous = self.entries[self.frame].val
            del self.entries[self.frame :]
            self.frame = previous if 0 <= previous < len(self.entries) else -1
            return back
        return self.pop()

    def rows(self) -> list[dict[str, int]]:
        """Bottom first: [{pos, val, addr}]."""
        return [{"pos": i, "val": e.val, "addr": e.addr} for i, e in enumerate(self.entries)]
