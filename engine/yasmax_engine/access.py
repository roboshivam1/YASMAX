"""
File: engine/yasmax_engine/access.py

Operand access for ONE executing instruction: what an operand's value is,
which address it names, where a jump goes. Handlers (handlers.py) only
ever touch registers, data memory and the stack through this object, so
the addressing-mode rules live in one place.

    mode             read_value          address_of          jump_target
    0 #n             n                   -                   -
    1 Rnn            register            -                   register (absolute)
    2 n              word at n           n                   n (absolute)
    3 @Rnn           word at Rnn         Rnn                 -
    4 @n             word at (word at n) word at n           -
    5 +/-n           -                   -                   here +/- n
    6 +/-Rnn         -                   -                   here +/- Rnn
    7 +/-@Rnn        -                   -                   here +/- word at Rnn

"here" is the LAdd of the executing instruction (ISA doc: "20 bytes ahead
of the current address"). Memory means the program's data memory.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .errors import FaultCode, MachineFault
from .isa import AM, Instruction, Operand
from .registers import reg_name

if TYPE_CHECKING:
    from .machine import Machine
    from .program import Program


class Access:
    def __init__(self, machine: Machine, program: Program, ins: Instruction, here: int) -> None:
        self.m = machine
        self.cfg = machine.config
        self.data = program.data
        self.ins = ins
        self.here = here
        self.next = here + ins.size

    def reg(self, op: Operand) -> str:
        return reg_name(op.value)

    def get_reg(self, op: Operand) -> int:
        return self.m.gpr.read(self.reg(op))

    def set_reg(self, op: Operand, value: int) -> int:
        return self.m.gpr.write(self.reg(op), value)

    def address_of(self, op: Operand) -> int:
        if op.mode == AM.MEM:
            return op.value
        if op.mode == AM.REG_IND:
            return self.get_reg(op) & 0xFFFF
        if op.mode == AM.MEM_IND:
            return self.data.read_word(op.value) & 0xFFFF
        raise MachineFault(
            FaultCode.INVALID_INSTRUCTION, f"{self.ins}: operand {op} is not an address"
        )

    def read_value(self, op: Operand) -> int:
        if op.mode == AM.IMM:
            return self.cfg.wrap(op.value)
        if op.mode == AM.REG:
            return self.get_reg(op)
        return self.data.read_word(self.address_of(op))

    def write_value(self, op: Operand, value: int) -> None:
        if op.mode == AM.REG:
            self.set_reg(op, value)
        else:
            self.data.write_word(self.address_of(op), value)

    def bump_pointer(self, op: Operand, step: int) -> None:
        """The "I" in LDBI / STWI: move an indirect address on by `step`."""
        if op.mode == AM.REG_IND:
            self.set_reg(op, self.get_reg(op) + step)
        elif op.mode == AM.MEM_IND:
            self.data.write_word(op.value, self.data.read_word(op.value) + step)

    def jump_target(self, op: Operand) -> int:
        sign = -1 if op.negative else 1
        if op.mode == AM.REG:
            return self.get_reg(op)
        if op.mode == AM.MEM:
            return op.value
        if op.mode == AM.REL:
            return self.here + op.value
        if op.mode == AM.REL_REG:
            return self.here + sign * self.get_reg(op)
        if op.mode == AM.REL_REG_IND:
            return self.here + sign * self.data.read_word(self.get_reg(op) & 0xFFFF)
        raise MachineFault(
            FaultCode.INVALID_INSTRUCTION, f"{self.ins}: operand {op} is not a jump address"
        )

    def shown_value(self, op: Operand) -> int | None:
        """Value for the Execution Unit "Opnd = value" boxes. Never faults
        and never marks registers as accessed."""
        try:
            if op.mode == AM.IMM:
                return op.value
            if op.mode in (AM.REG, AM.REL_REG):
                return self.m.gpr.peek(self.reg(op))
            if op.mode in (AM.MEM, AM.REL):
                return op.value
            if op.mode == AM.REG_IND:
                return self.data.read_word(self.m.gpr.peek(self.reg(op)) & 0xFFFF)
            if op.mode == AM.MEM_IND:
                return self.data.read_word(self.data.read_word(op.value) & 0xFFFF)
            return self.data.read_word(self.m.gpr.peek(self.reg(op)) & 0xFFFF)
        except MachineFault:
            return None
