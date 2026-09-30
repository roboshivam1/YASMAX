"""
File: engine/yasmax_engine/isa/operands.py

Turns instruction TEXT into structured instructions and back:

    parse_instruction("mov #20, r0")  ->  Instruction(MOV, [#20, R00])
    str(that instruction)             ->  "MOV #20, R00"   (as YASMIN shows it)

Operand syntax comes from the ISA document's addressing-mode table:
    #n  Rnn  n  @Rnn  @n  +n/-n  +Rnn/-Rnn  +@Rnn/-@Rnn
plus $Name, a label used as a jump address ("JNE $L0", Programming
Model 2 tutorial). A label operand is a memory-direct operand whose
address is looked up when the instruction runs.
Numbers are decimal. Values are 2 bytes; register numbers 00..63.

Every parsed instruction is checked against the allowed forms in
spec.py, so an instruction the original simulator could not encode
(e.g. "MOV R01, #5") is rejected with a ProgramError before it ever
reaches memory. Its size in bytes is known from its form.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..errors import ProgramError
from .modes import AM
from .spec import OpSpec, lookup

MAX_REGISTER = 63
# 2-byte value field. TODO(R-1): confirm the accepted range in the original.
MIN_VALUE, MAX_VALUE = -32768, 65535

_PATTERNS = [
    (AM.IMM, re.compile(r"^#([+-]?\d+)$")),
    (AM.REG, re.compile(r"^R(\d{1,2})$", re.I)),
    (AM.REG_IND, re.compile(r"^@R(\d{1,2})$", re.I)),
    (AM.MEM_IND, re.compile(r"^@(\d+)$")),
    (AM.REL_REG_IND, re.compile(r"^([+-])@R(\d{1,2})$", re.I)),
    (AM.REL_REG, re.compile(r"^([+-])R(\d{1,2})$", re.I)),
    (AM.REL, re.compile(r"^([+-]\d+)$")),
    (AM.MEM, re.compile(r"^(\d+)$")),
]
_LABEL = re.compile(r"^\$([A-Za-z_][A-Za-z0-9_]*)$")


@dataclass(frozen=True)
class Operand:
    """One operand. `value` is a register number or a number; `negative`
    is the sign of the relative register modes (-R04, -@R03)."""

    mode: AM
    value: int
    negative: bool = False
    label: str | None = None

    def __str__(self) -> str:
        sign = "-" if self.negative else "+"
        return {
            AM.IMM: f"#{self.value}",
            AM.REG: f"R{self.value:02d}",
            AM.MEM: f"${self.label}" if self.label else f"{self.value}",
            AM.REG_IND: f"@R{self.value:02d}",
            AM.MEM_IND: f"@{self.value}",
            AM.REL: f"{self.value:+d}",
            AM.REL_REG: f"{sign}R{self.value:02d}",
            AM.REL_REG_IND: f"{sign}@R{self.value:02d}",
        }[self.mode]


def parse_operand(text: str) -> Operand:
    """Parse one operand, e.g. "#20", "R00", "@R01", "-R04"."""
    t = text.strip().replace(" ", "")
    if m := _LABEL.match(t):
        return Operand(AM.MEM, 0, label=m.group(1))
    for mode, pattern in _PATTERNS:
        m = pattern.match(t)
        if not m:
            continue
        if mode in (AM.REL_REG, AM.REL_REG_IND):
            number, negative = int(m.group(2)), m.group(1) == "-"
        else:
            number, negative = int(m.group(1)), False
        if mode in (AM.REG, AM.REG_IND, AM.REL_REG, AM.REL_REG_IND):
            if number > MAX_REGISTER:
                raise ProgramError(f"Invalid register: {text.strip()}", field="operand")
        elif not MIN_VALUE <= number <= MAX_VALUE:
            raise ProgramError(f"Value out of range: {text.strip()}", field="operand")
        return Operand(mode, number, negative)
    raise ProgramError(f"Invalid operand: {text.strip()}", field="operand")


@dataclass(frozen=True)
class Instruction:
    spec: OpSpec
    operands: tuple[Operand, ...]

    @property
    def form(self) -> tuple[AM, ...]:
        return tuple(o.mode for o in self.operands)

    @property
    def size(self) -> int:
        """Length in bytes (1..7), which is how far LAdd advances."""
        return self.spec.size(self.form)

    def __str__(self) -> str:
        if not self.operands:
            return self.spec.mnemonic
        return f"{self.spec.mnemonic} " + ", ".join(str(o) for o in self.operands)


def parse_instruction(text: str) -> Instruction:
    """Parse and validate e.g. "MOV #20, R00". Raises ProgramError."""
    parts = text.strip().split(None, 1)
    if not parts:
        raise ProgramError("Please enter an instruction.", field="instruction")
    spec = lookup(parts[0])
    if spec is None:
        raise ProgramError(f"Unknown instruction: {parts[0]}", field="instruction")
    raw = parts[1].split(",") if len(parts) > 1 else []
    operands = tuple(parse_operand(p) for p in raw)
    form = tuple(o.mode for o in operands)
    if form not in spec.forms:
        raise ProgramError(
            f"{spec.mnemonic} does not accept these operands: {text.strip()}", field="instruction"
        )
    return Instruction(spec, operands)
