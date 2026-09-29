"""
File: engine/tests/unit/test_config_flags.py

Tests for config.py (word wrapping, overflow) and flags.py (Z/N/OV).

Tests use small word sizes (8 bits) where possible because the edge cases
(127 + 1, -128 - 1) are easy to reason about by hand. The logic is the
same for any width, so this also covers the 32-bit default.
"""

import pytest

from yasmax_engine import MachineConfig, StatusFlags, evaluate

C8 = MachineConfig(word_bits=8, signed=True, gpr_count=8, initial_sp=0)
U8 = MachineConfig(word_bits=8, signed=False, gpr_count=8, initial_sp=0)


# ---------------------------------------------------------------- config


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(0, 0), (127, 127), (128, -128), (255, -1), (256, 0), (-1, -1), (-129, 127)],
)
def test_wrap_signed_8bit(raw, expected):
    assert C8.wrap(raw) == expected


@pytest.mark.parametrize(("raw", "expected"), [(255, 255), (256, 0), (-1, 255)])
def test_wrap_unsigned_8bit(raw, expected):
    assert U8.wrap(raw) == expected


def test_ranges():
    assert (C8.min_value, C8.max_value) == (-128, 127)
    assert (U8.min_value, U8.max_value) == (0, 255)


def test_overflow_detection():
    assert not C8.is_overflow(127)
    assert C8.is_overflow(128)
    assert C8.is_overflow(-129)
    assert U8.is_overflow(-1)


def test_default_config_is_valid():
    MachineConfig().validate()


def test_validate_rejects_bad_register_count():
    with pytest.raises(ValueError):
        MachineConfig(gpr_count=7).validate()


# ----------------------------------------------------------------- flags


def test_evaluate_zero():
    r = evaluate(0, C8)
    assert (r.value, r.z, r.n, r.ov) == (0, True, False, False)


def test_evaluate_negative():
    r = evaluate(-5, C8)
    assert (r.value, r.z, r.n, r.ov) == (-5, False, True, False)


def test_evaluate_overflow_wraps():
    r = evaluate(127 + 1, C8)
    assert (r.value, r.z, r.n, r.ov) == (-128, False, True, True)


def test_evaluate_unsigned_negative_uses_sign_bit():
    r = evaluate(200, U8)
    assert r.n and not r.ov


def test_update_only_touches_given_flags():
    f = StatusFlags(ov=True, z=False, n=True)
    f.update(z=True)
    assert f.as_dict() == {"OV": True, "Z": True, "N": True}


def test_apply_can_skip_flags():
    f = StatusFlags(ov=True)
    f.apply(evaluate(0, C8), ov=False)
    assert f.as_dict() == {"OV": True, "Z": True, "N": False}


def test_clear():
    f = StatusFlags(ov=True, z=True, n=True)
    f.clear()
    assert f.as_dict() == {"OV": False, "Z": False, "N": False}
