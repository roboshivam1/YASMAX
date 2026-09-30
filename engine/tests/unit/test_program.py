"""
File: engine/tests/unit/test_program.py

Tests for programs and the Program / Instructions tab commands, through
dispatch() exactly as the browser calls them. Covers the tutorial's
exercise: a program at base address 100 whose instructions get LAdd
0, 6, 11 ... (each instruction's LAdd grows by the previous one's size).
"""

import json

import pytest

from yasmax_engine import api


def call(cmd, **args):
    return json.loads(api.dispatch(cmd, json.dumps(args)))


@pytest.fixture(autouse=True)
def fresh():
    api.boot()


def add(*texts, program="P1"):
    for t in texts:
        reply = call("add_instruction", program=program, text=t)
        assert reply["ok"], reply["events"]
    return reply["snapshot"]


def test_create_program_like_the_tutorial():
    snap = call("create_program", name="P1", base="100", pages=1)["snapshot"]
    assert snap["programs"][0]["name"] == "P1" and snap["programs"][0]["base"] == 100
    assert snap["special"]["BR"] == 100
    assert snap["run"]["state"] == "idle"


@pytest.mark.parametrize(
    ("args", "field"),
    [({"name": "", "base": 100}, "program_name"), ({"name": "P", "base": ""}, "base_address"),
     ({"name": "P", "base": "abc"}, "base_address"), ({"name": "P", "base": -5}, "base_address"),
     ({"name": "P", "base": 1, "pages": 0}, "pages")],
)  # fmt: skip
def test_create_program_validation(args, field):
    reply = call("create_program", **args)
    assert not reply["ok"] and reply["events"][0]["field"] == field


def test_duplicate_program_name_rejected():
    call("create_program", name="P1", base=100)
    assert not call("create_program", name="P1", base=200)["ok"]


def test_logical_and_physical_addresses():
    call("create_program", name="P1", base=100)
    snap = add("MOV #5, R00", "MOV #8, R01", "ADD R00, R01", "PSH R01", "HLT")
    rows = [(r["padd"], r["ladd"], r["text"]) for r in snap["memory"]]
    assert rows == [
        (100, 0, "MOV #5, R00"),
        (106, 6, "MOV #8, R01"),
        (112, 12, "ADD R00, R01"),
        (117, 17, "PSH R01"),
        (120, 20, "HLT"),
    ]


def test_bad_instruction_leaves_program_unchanged():
    call("create_program", name="P1", base=0)
    add("HLT")
    reply = call("add_instruction", program="P1", text="MOV R01, #5")
    assert not reply["ok"] and reply["events"][0]["type"] == "program_error"
    assert len(reply["snapshot"]["memory"]) == 1


def test_insert_edit_move_delete():
    call("create_program", name="P1", base=0)
    add("NOP", "HLT")
    call("insert_instruction", program="P1", index=1, text="INC R01")
    call("edit_instruction", program="P1", index=0, text="MOV #1, R01")
    snap = call("move_instruction", program="P1", index=2, delta=-1)["snapshot"]
    assert [r["text"] for r in snap["memory"]] == ["MOV #1, R01", "HLT", "INC R01"]
    snap = call("delete_instruction", program="P1", index=1)["snapshot"]
    assert [r["text"] for r in snap["memory"]] == ["MOV #1, R01", "INC R01"]
    assert [r["ladd"] for r in snap["memory"]] == [0, 6]


def test_move_past_the_end_does_nothing():
    call("create_program", name="P1", base=0)
    snap = add("NOP", "HLT")
    assert call("move_instruction", program="P1", index=0, delta=-1)["snapshot"] == snap


def test_bad_index_and_unknown_program():
    call("create_program", name="P1", base=0)
    assert call("delete_instruction", program="P1", index=0)["events"][0]["type"] == "program_error"
    assert not call("add_instruction", program="NOPE", text="HLT")["ok"]


def test_two_programs_and_removal():
    call("create_program", name="A", base=0)
    call("create_program", name="B", base=500)
    add("HLT", program="A")
    snap = add("NOP", program="B")
    assert [(r["padd"], r["program"]) for r in snap["memory"]] == [(0, "A"), (500, "B")]
    snap = call("remove_program", name="A")["snapshot"]
    assert [p["name"] for p in snap["programs"]] == ["B"]
    snap = call("remove_all_programs")["snapshot"]
    assert snap["programs"] == [] and snap["memory"] == [] and snap["run"]["state"] == "empty"


def test_boot_sends_the_isa_for_the_dialog():
    info = json.loads(api.boot())
    assert len(info["isa"]) == 47
    assert info["address_modes"]["0"] == "Literal Value"
