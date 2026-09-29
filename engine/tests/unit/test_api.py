"""
File: engine/tests/unit/test_api.py

Tests for machine.py, snapshot.py and api.py, the JSON doorway the
browser worker uses. Everything goes through `dispatch()` with JSON text,
exactly as worker.js calls it, so passing tests here mean the worker's
side of the contract is right.
"""

import json

import pytest

from yasmax_engine import Machine, ProgramError, RunState, api


def call(cmd, **args):
    """Helper: call dispatch like the worker does and decode the reply."""
    return json.loads(api.dispatch(cmd, json.dumps(args)))


@pytest.fixture(autouse=True)
def fresh_machine():
    api.boot()


# --------------------------------------------------------------- boot


def test_boot_describes_engine():
    info = json.loads(api.boot())
    assert info["engine_version"]
    assert "set_register" in info["commands"]
    assert info["snapshot"]["run"]["state"] == "empty"


# ------------------------------------------------------ snapshot shape


def test_snapshot_has_every_section():
    snap = call("snapshot")["snapshot"]
    for key in ("special", "flags", "gpr", "memory", "stack", "programs", "run", "config"):
        assert key in snap
    assert snap["special"]["SP"] == 8096
    assert len(snap["gpr"]) == 32
    assert snap["gpr"][0] == {"name": "R00", "val": 0, "access": None}


# ---------------------------------------------------- register commands


def test_set_register_accepts_typed_text():
    reply = call("set_register", name="R05", value=" -12 ")
    assert reply["ok"] and reply["events"] == []
    assert reply["snapshot"]["gpr"][5]["val"] == -12


def test_set_register_rejects_non_number():
    reply = call("set_register", name="R05", value="abc")
    assert not reply["ok"]
    assert reply["events"][0] == {
        "type": "program_error",
        "message": "Please enter a whole number.",
        "field": "reg_value",
    }


def test_set_register_bad_name_is_a_fault_event():
    reply = call("set_register", name="R99", value=1)
    assert not reply["ok"]
    assert reply["events"][0]["type"] == "fault"
    assert reply["events"][0]["code"] == "invalid_register"


def test_reset_all_registers():
    call("set_register", name="R01", value=7)
    snap = call("reset_all_registers")["snapshot"]
    assert all(r["val"] == 0 for r in snap["gpr"])


def test_register_set_size():
    snap = call("set_register_set_size", size=16)["snapshot"]
    assert len(snap["gpr"]) == 16
    assert snap["config"]["gpr_count"] == 16
    assert not call("set_register_set_size", size=12)["ok"]


# ------------------------------------------------------- bad requests


def test_unknown_command():
    reply = call("launch_missiles")
    assert not reply["ok"] and reply["events"][0]["type"] == "bad_request"


def test_wrong_argument_names():
    reply = call("set_register", nme="R01", value=1)
    assert reply["events"][0]["type"] == "bad_request"


def test_arguments_must_be_an_object():
    reply = json.loads(api.dispatch("snapshot", "[1, 2]"))
    assert reply["events"][0]["type"] == "bad_request"


def test_internal_errors_are_caught(monkeypatch):
    def boom(self):
        raise TypeError("a real bug, not a bad request")

    monkeypatch.setattr(Machine, "reset_all_registers", boom)
    reply = call("reset_all_registers")
    assert reply["events"][0]["type"] == "internal_error"


# --------------------------------------------------- machine directly


def test_machine_starts_empty():
    assert Machine().run_state == RunState.EMPTY


def test_booleans_are_not_numbers():
    with pytest.raises(ProgramError):
        Machine().set_register("R01", True)
