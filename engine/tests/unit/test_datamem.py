"""
File: engine/tests/unit/test_datamem.py

Tests for program data memory (the "<program>: Pid n" window) and the
snapshot fields added for YASMIN 7.5.50: structured operands (so EDIT...
can fill the instruction dialog) and the program list's Start / Type.
All through dispatch(), exactly as the browser calls it.
"""

import json

import pytest

from yasmax_engine import api


def call(cmd, **args):
    return json.loads(api.dispatch(cmd, json.dumps(args)))


@pytest.fixture(autouse=True)
def fresh():
    api.boot()
    call("create_program", name="TRAIN", base=100, pages=2)


FRESH = [2] + [0] * 511  # YASMIN 7.5.50 shows 02 in byte 0 of a new program


def mem():
    return call("data_memory", program="TRAIN")["result"]


def test_size_is_pages_times_256():
    m = mem()
    assert (m["name"], m["pid"], m["pages"], m["size"]) == ("TRAIN", 0, 2, 512)
    assert m["bytes"] == FRESH


def test_debug_control_row_update():
    assert call("write_data_bytes", program="TRAIN", address=8, values=["02", "ff", "", "0A"])["ok"]
    assert mem()["bytes"][8:13] == [2, 255, 0, 10, 0]


@pytest.mark.parametrize("bad", ["G1", "100", "-1"])
def test_bad_hex_bytes_are_rejected(bad):
    reply = call("write_data_bytes", program="TRAIN", address=0, values=[bad])
    assert not reply["ok"] and reply["events"][0]["field"] == "byte"


@pytest.mark.parametrize(
    ("kind", "value", "expected"),
    [("integer", "25", [2, 0, 25, 0]), ("integer", "258", [2, 0, 2, 1]),
     ("integer", "-1", [2, 0, 255, 255]), ("boolean", "True", [1, 1]),
     ("boolean", "False", [1, 0]), ("string", "Hi!", [3, 72, 105, 33, 0])],
)  # fmt: skip
def test_initialise_data(kind, value, expected):
    assert call("write_data", program="TRAIN", address="16", kind=kind, value=value)["ok"]
    assert mem()["bytes"][16 : 16 + len(expected)] == expected


@pytest.mark.parametrize(
    ("kind", "value", "address"),
    [("integer", "70000", 0), ("integer", "x", 0), ("boolean", "maybe", 0),
     ("string", "", 0), ("string", "é", 0), ("integer", "1", 509), ("boolean", "True", 511)],
)  # fmt: skip
def test_initialise_data_errors(kind, value, address):
    reply = call("write_data", program="TRAIN", address=address, kind=kind, value=value)
    assert not reply["ok"] and reply["events"][0]["type"] == "program_error"
    assert mem()["bytes"] == FRESH


def test_reset_all():
    call("write_data", program="TRAIN", address=0, kind="string", value="abc")
    call("reset_data_memory", program="TRAIN")
    assert mem()["bytes"] == [0] * 512


def test_programs_have_separate_data():
    call("create_program", name="OTHER", base=500)
    call("write_data", program="OTHER", address=0, kind="boolean", value="True")
    assert mem()["bytes"][0] == 2
    assert call("data_memory", program="OTHER")["result"]["size"] == 256


def test_commands_without_a_value_send_no_result():
    assert "result" not in call("reset_data_memory", program="TRAIN")
    assert "result" not in call("snapshot")


def test_structured_operands_for_edit():
    call("add_instruction", program="TRAIN", text="JLT -@R03")
    row = call("snapshot")["snapshot"]["memory"][0]
    assert row["op"] == "JLT"
    assert row["operands"] == [{"mode": 7, "value": 3, "negative": True, "label": None}]


def test_program_list_start_and_type_as_in_7_5_50():
    p = call("snapshot")["snapshot"]["programs"][0]
    assert (p["start"], p["type"]) == (0, "R")
