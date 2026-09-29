"""
File: engine/tests/unit/test_registers.py

Tests for registers.py: register naming, wrapping on write, access
tracking (for "Show Reg Access Status"), resizing and special registers.
"""

import dataclasses

import pytest

from yasmax_engine import (
    Access,
    FaultCode,
    MachineConfig,
    MachineFault,
    RegisterFile,
    SpecialRegisters,
    reg_name,
)

CFG = MachineConfig(word_bits=8, signed=True, gpr_count=8, gpr_set_sizes=(8, 16), initial_sp=100)


@pytest.fixture
def regs():
    return RegisterFile(CFG)


def test_names_are_two_digit():
    assert reg_name(0) == "R00"
    assert reg_name(31) == "R31"


@pytest.mark.parametrize("name", ["R01", "r1", "R1", " R01 "])
def test_name_parsing_is_forgiving(regs, name):
    assert regs.index_of(name) == 1


@pytest.mark.parametrize("name", ["R08", "X01", "R", "", "R-1"])
def test_invalid_register_faults(regs, name):
    with pytest.raises(MachineFault) as e:
        regs.index_of(name)
    assert e.value.code == FaultCode.INVALID_REGISTER


def test_write_wraps_to_word(regs):
    assert regs.write("R01", 130) == -126
    assert regs.peek("R01") == -126


def test_access_tracking(regs):
    regs.read("R01")
    regs.write("R02", 5)
    regs.read("R03")
    regs.write("R03", 1)
    rows = {r["name"]: r["access"] for r in regs.rows()}
    assert rows["R01"] == Access.READ
    assert rows["R02"] == Access.WRITE
    assert rows["R03"] == Access.BOTH
    assert rows["R00"] is None


def test_begin_step_clears_access(regs):
    regs.write("R01", 1)
    regs.begin_step()
    assert all(r["access"] is None for r in regs.rows())


def test_peek_and_poke_are_not_accesses(regs):
    regs.poke("R04", 9)
    regs.peek("R04")
    assert all(r["access"] is None for r in regs.rows())
    assert regs.peek("R04") == 9


def test_reset_all(regs):
    regs.write("R05", 42)
    regs.reset_all()
    assert all(r["val"] == 0 for r in regs.rows())


def test_resize_keeps_existing_values(regs):
    regs.poke("R07", 3)
    regs.set_size(dataclasses.replace(CFG, gpr_count=16))
    assert regs.size == 16
    assert regs.peek("R07") == 3
    assert regs.peek("R15") == 0


def test_special_registers_initial_and_reset():
    sp = SpecialRegisters.initial(CFG)
    assert sp.SP == 100 and sp.PC == 0 and sp.IR is None
    sp.PC, sp.IR = 12, "HLT"
    same_object = sp
    sp.reset(CFG)
    assert same_object.PC == 0 and same_object.IR is None and same_object.SP == 100


def test_special_as_dict_keys():
    assert list(SpecialRegisters().as_dict()) == ["PC", "SP", "SR", "BR", "IR", "MAR", "MDR"]
