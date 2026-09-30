# ruff: noqa: E501
"""
File: engine/yasmax_engine/isa/spec.py

The instruction set table: every opcode the YASMIN CPU simulator
supports, transcribed from the "CPU Simulator Instruction Set
Architecture" document (47 opcodes in 7 groups).

Each row says:
    opcode     the 1-byte opcode value (decimal, as in the document)
    mnemonic   e.g. "MOV"
    group      the tab it lives on in the instruction dialog
    summary    one-line description (shown under the dialog)
    forms      which addressing-mode combinations are allowed, one tuple
               per form, e.g. (AM.IMM, AM.REG) means "MOV #20, R00"
    sets_sr    True if the instruction updates the status flags

This table is the single source of truth for: parsing and validating
instructions (operands.py), instruction sizes, the instruction dialog in
the UI (sent at boot through api.py) and, next batch, execution handlers.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .modes import AM, operand_size


class Group(StrEnum):
    DATA = "Data Transfer"
    ARITH = "Arithmetic"
    LOGIC = "Logical"
    CONTROL = "Control Transfer"
    COMPARE = "Comparison"
    IO = "I/O"
    MISC = "Miscellaneous"


@dataclass(frozen=True)
class OpSpec:
    opcode: int
    mnemonic: str
    group: Group
    summary: str
    forms: tuple[tuple[AM, ...], ...]
    sets_sr: bool

    @property
    def operand_count(self) -> int:
        return len(self.forms[0]) if self.forms else 0

    def size(self, form: tuple[AM, ...]) -> int:
        """Instruction length in bytes: 1 opcode byte + each operand."""
        return 1 + sum(operand_size(m) for m in form)


IM, R, M, RI, MI, REL, RR, RRI = AM  # short names for the table below

_REG_OR_VALUE = ((R, R), (IM, R))
_STRING = ((RI, RI), (RI, M), (M, RI), (MI, RI), (M, M), (MI, MI))
_LOAD = ((RI, R), (M, R), (MI, R))
_JUMP = ((R,), (RR,), (RRI,), (M,), (REL,))

# fmt: off
_TABLE: list[tuple] = [
    # opcode, mnemonic, group, summary, forms, sets_sr
    (0, "MOV", Group.DATA, "Move value to register, move register to register", _REG_OR_VALUE, True),
    (1, "MVS", Group.DATA, "Move string in memory to memory", _STRING, False),
    (4, "LDB", Group.DATA, "Load a byte from memory to register", _LOAD, True),
    (5, "LDW", Group.DATA, "Load a word from memory to register", _LOAD, True),
    (7, "LDBI", Group.DATA, "Load byte from memory into register, increment indirect source address", _LOAD, True),
    (8, "LDWI", Group.DATA, "Load word from memory into register, increment indirect source address", _LOAD, True),
    (9, "TAS", Group.DATA, "Test and set", _LOAD, True),
    (10, "STB", Group.DATA, "Store a byte value or register to memory", ((R, RI), (IM, RI), (R, M), (R, MI), (IM, M), (IM, MI)), False),
    (11, "STW", Group.DATA, "Store a word value or register to memory", ((R, RI), (IM, RI), (R, M), (R, MI), (IM, M), (IM, MI)), False),
    (12, "STBI", Group.DATA, "Store a byte to memory, increment indirect destination address", ((R, RI), (IM, RI), (R, MI), (IM, MI)), False),
    (13, "STWI", Group.DATA, "Store a word to memory, increment indirect destination address", ((R, RI), (IM, RI), (R, MI), (IM, MI)), False),
    (14, "PSH", Group.DATA, "Push value or register to top of stack", ((R,), (IM,)), False),
    (15, "POP", Group.DATA, "Pop a value from top of stack into register", ((R,),), True),
    (16, "SWP", Group.DATA, "Swap register values", ((R, R),), False),
    (17, "ADD", Group.ARITH, "Add value or register to destination register", _REG_OR_VALUE, True),
    (18, "SUB", Group.ARITH, "Subtract value or register from destination register", _REG_OR_VALUE, True),
    (19, "SUBU", Group.ARITH, "Subtract with unsigned result", _REG_OR_VALUE, True),
    (20, "MUL", Group.ARITH, "Multiply value or register with destination register", _REG_OR_VALUE, True),
    (21, "DIV", Group.ARITH, "Divide value or register with destination register", _REG_OR_VALUE, True),
    (22, "INC", Group.ARITH, "Increment register value by 1", ((R,),), True),
    (23, "DEC", Group.ARITH, "Decrement register value by 1", ((R,),), True),
    (24, "AND", Group.LOGIC, "And value or register with destination register", _REG_OR_VALUE, True),
    (25, "OR", Group.LOGIC, "Or value or register with destination register", _REG_OR_VALUE, True),
    (26, "NOT", Group.LOGIC, "Invert value (bitwise) into register", _REG_OR_VALUE, True),
    (27, "SHL", Group.LOGIC, "Shift register left by specified bit positions", ((M, R),), True),
    (28, "SHR", Group.LOGIC, "Shift register right by specified bit positions", ((M, R),), True),
    (29, "JMP", Group.CONTROL, "Unconditionally jump to memory location", _JUMP, False),
    (30, "JEQ", Group.CONTROL, "Jump to memory location if equal", _JUMP, False),
    (31, "JNE", Group.CONTROL, "Jump to memory location if not equal", _JUMP, False),
    (32, "JGT", Group.CONTROL, "Jump to memory location if greater than", _JUMP, False),
    (33, "JGE", Group.CONTROL, "Jump to memory location if greater than or equal", _JUMP, False),
    (34, "JLT", Group.CONTROL, "Jump to memory location if less than", _JUMP, False),
    (35, "JLE", Group.CONTROL, "Jump to memory location if less than or equal", _JUMP, False),
    (36, "JNZ", Group.CONTROL, "Jump if Z status flag is not set", _JUMP, False),
    (37, "JZR", Group.CONTROL, "Jump if Z status flag is set", _JUMP, False),
    (38, "CAL", Group.CONTROL, "Jump to subroutine", _JUMP, False),
    (39, "LOOP", Group.CONTROL, "Loop while register value is greater than 0", ((M, R), (REL, R)), False),
    (43, "MSF", Group.CONTROL, "Mark stack frame", ((),), False),
    (44, "RET", Group.CONTROL, "Return from subroutine", ((),), False),
    (45, "IRET", Group.CONTROL, "Return from interrupt subroutine", ((),), False),
    (46, "SWI", Group.CONTROL, "Generate software interrupt", ((M,),), False),
    (47, "HLT", Group.CONTROL, "Halt simulator", ((),), False),
    (48, "CMP", Group.COMPARE, "Compare value or register with register", _REG_OR_VALUE, True),
    (49, "CPS", Group.COMPARE, "Compare string in memory with string in memory", _STRING, True),
    (50, "IN", Group.IO, "Get characters from external input device", ((M, R), (M, M)), False),
    (51, "OUT", Group.IO, "Put characters to external output device", ((R, M), (RI, M), (IM, M), (M, M), (MI, M)), False),
    (52, "NOP", Group.MISC, "No operation", ((),), False),
]
# fmt: on

OPCODES: dict[str, OpSpec] = {row[1]: OpSpec(*row) for row in _TABLE}


def lookup(mnemonic: str) -> OpSpec | None:
    """Find an instruction by mnemonic, ignoring case. None if unknown."""
    return OPCODES.get(mnemonic.strip().upper())


def isa_table() -> list[dict[str, object]]:
    """JSON-safe copy of the table for the UI's instruction dialog."""
    return [
        {
            "opcode": s.opcode,
            "mnemonic": s.mnemonic,
            "group": str(s.group),
            "summary": s.summary,
            "forms": [[int(m) for m in f] for f in s.forms],
            "sets_sr": s.sets_sr,
        }
        for s in OPCODES.values()
    ]
