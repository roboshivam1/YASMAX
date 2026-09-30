"""
File: engine/yasmax_engine/isa/__init__.py

The instruction set architecture (ISA) of the YASMIN CPU simulator:
    modes.py     the 8 addressing modes and operand sizes
    spec.py      the table of all 47 opcodes
    operands.py  instruction text <-> Instruction objects, with validation
"""

from .modes import AM, UI_NAMES, operand_size
from .operands import Instruction, Operand, parse_instruction, parse_operand
from .spec import OPCODES, Group, OpSpec, isa_table, lookup

__all__ = [
    "AM",
    "OPCODES",
    "UI_NAMES",
    "Group",
    "Instruction",
    "OpSpec",
    "Operand",
    "isa_table",
    "lookup",
    "operand_size",
    "parse_instruction",
    "parse_operand",
]
