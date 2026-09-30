"""
File: engine/tests/unit/test_isa.py

Tests for the ISA table, operand syntax and instruction sizes, checked
against the "CPU Simulator Instruction Set Architecture" document:
- 47 opcodes with the documented opcode numbers and groups
- every allowed form has a size matching one of the 11 documented formats
- every example instruction printed in the document parses and prints back
"""

import pytest

from yasmax_engine import ProgramError
from yasmax_engine.isa import AM, OPCODES, Group, isa_table, parse_instruction, parse_operand

# Sizes of the 11 instruction formats in the ISA document (bytes).
FORMAT_SIZES = {1: 1, 2: 3, 3: 3, 4: 5, 5: 4, 6: 6, 7: 6, 8: 6, 9: 4, 10: 7, 11: 7}


def test_47_opcodes_in_7_groups():
    assert len(OPCODES) == 47
    counts = {g: sum(1 for s in OPCODES.values() if s.group == g) for g in Group}
    assert counts == {
        Group.DATA: 14, Group.ARITH: 7, Group.LOGIC: 5, Group.CONTROL: 16,
        Group.COMPARE: 2, Group.IO: 2, Group.MISC: 1,
    }  # fmt: skip


@pytest.mark.parametrize(
    ("mnemonic", "opcode"),
    [("MOV", 0), ("LDB", 4), ("PSH", 14), ("ADD", 17), ("SHR", 28), ("JMP", 29),
     ("LOOP", 39), ("MSF", 43), ("HLT", 47), ("CMP", 48), ("OUT", 51), ("NOP", 52)],
)  # fmt: skip
def test_opcode_numbers(mnemonic, opcode):
    assert OPCODES[mnemonic].opcode == opcode


def test_every_form_has_a_documented_size():
    sizes = set(FORMAT_SIZES.values())
    for spec in OPCODES.values():
        for form in spec.forms:
            assert spec.size(form) in sizes, (spec.mnemonic, form)


@pytest.mark.parametrize(
    ("text", "size"),
    [("HLT", 1), ("PSH R03", 3), ("POP R05", 3), ("PSH #6", 4), ("JMP 100", 4),
     ("MOV R01, R03", 5), ("MOV #2, R01", 6), ("STW R04, 1000", 6), ("SHL 2, R10", 6),
     ("STB #2, 1000", 7)],
)  # fmt: skip
def test_instruction_sizes(text, size):
    assert parse_instruction(text).size == size


# Every example instruction printed in the ISA document.
DOC_EXAMPLES = [
    "MOV #2, R01", "MOV R01, R03", "LDB 1000, R02", "LDB @R00, R01", "LDW 1000, R02",
    "LDW @R00, R01", "STB #2, 1000", "STB R02, @R01", "STW R04, 1000", "STW R02, @2000",
    "PSH #6", "PSH R03", "POP R05", "TAS 100, R01", "TAS @R02, R03", "ADD #3, R02",
    "ADD R00, R01", "INC R08", "JMP 100", "JLT 1000", "JLT +20", "JLT -R04", "JLT -@R03",
    "JEQ 200", "LOOP 100, R05", "MSF", "CAL 1000", "RET", "HLT", "CMP #5, R02",
    "CMP R01, R03", "OUT 120, 0", "OUT @R02, 0", "AND #1, R07", "AND R09, R00",
    "NOT #3, R01", "SHL 2, R10",
]  # fmt: skip


@pytest.mark.parametrize("text", DOC_EXAMPLES)
def test_document_examples_round_trip(text):
    assert str(parse_instruction(text)) == text


def test_parsing_is_forgiving_but_prints_canonically():
    assert str(parse_instruction("  mov   #20 ,r0 ")) == "MOV #20, R00"
    assert str(parse_instruction("psh #-2")) == "PSH #-2"


@pytest.mark.parametrize(
    ("text", "mode"),
    [("#1000", AM.IMM), ("R01", AM.REG), ("1000", AM.MEM), ("@R01", AM.REG_IND),
     ("@1000", AM.MEM_IND), ("+100", AM.REL), ("-100", AM.REL), ("-R01", AM.REL_REG),
     ("+@R12", AM.REL_REG_IND)],
)  # fmt: skip
def test_addressing_modes(text, mode):
    assert parse_operand(text).mode == mode


@pytest.mark.parametrize(
    "text",
    ["FOO R01", "MOV R01, #5", "MOV #5", "HLT R01", "MOV #5, R64", "PSH #70000", "MOV #x, R01", ""],
)
def test_invalid_instructions_are_rejected(text):
    with pytest.raises(ProgramError):
        parse_instruction(text)


def test_isa_table_is_json_friendly():
    row = next(r for r in isa_table() if r["mnemonic"] == "MOV")
    assert row == {
        "opcode": 0, "mnemonic": "MOV", "group": "Data Transfer",
        "summary": row["summary"], "forms": [[1, 1], [0, 1]], "sets_sr": True,
    }  # fmt: skip
