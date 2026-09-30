"""
File: engine/yasmax_engine/isa/modes.py

The 8 operand addressing modes of the YASMIN CPU, exactly as listed in
the "CPU Simulator Instruction Set Architecture" document.

    Code  Mode                      Syntax     Meaning
    0     Immediate                 #1000      the literal value 1000
    1     Register direct           R01        register R01
    2     Memory direct             1000       memory address 1000
    3     Register indirect         @R01       address held in R01
    4     Memory indirect           @1000      address held at address 1000
    5     Relative address          +/-100     jump 100 bytes from the PC
    6     Relative register         +/-R01     jump by the value in R01
    7     Relative indirect register +/-@R12   jump by the value at address in R12

Encoding (also from the ISA document): every operand is a 1-byte mode
code followed by either a 1-byte register number (modes 1, 3, 6, 7) or a
2-byte value (modes 0, 2, 4, 5). That is all we need to compute exact
instruction sizes, which students are asked about (LAdd differences).

UI_NAMES are the labels shown in the original instruction dialog.
"""

from __future__ import annotations

from enum import IntEnum


class AM(IntEnum):
    """Addressing mode codes (the value stored in the Opnd AM byte)."""

    IMM = 0
    REG = 1
    MEM = 2
    REG_IND = 3
    MEM_IND = 4
    REL = 5
    REL_REG = 6
    REL_REG_IND = 7


# Modes whose operand field is a 1-byte register number.
REGISTER_MODES = frozenset({AM.REG, AM.REG_IND, AM.REL_REG, AM.REL_REG_IND})

# Labels used by the original "Instructions: CPU 0" dialog.
UI_NAMES = {
    AM.IMM: "Literal Value",
    AM.REG: "Reg Direct",
    AM.MEM: "Direct Mem",
    AM.REG_IND: "Reg Indirect",
    AM.MEM_IND: "Indirect Mem",
    AM.REL: "Rel Direct Mem",
    AM.REL_REG: "Rel Reg Direct",
    AM.REL_REG_IND: "Rel Reg Indirect",
}


def operand_size(mode: AM) -> int:
    """Bytes one operand takes in memory: 1 mode byte + register (1) or value (2)."""
    return 1 + (1 if mode in REGISTER_MODES else 2)
