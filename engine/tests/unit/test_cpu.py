"""
File: engine/tests/unit/test_cpu.py

Running programs (cpu.py, handlers.py, access.py, stack.py), checked
against what the lab saw in YASMIN 7.5.50 and what the ISA document and
tutorial say. Everything goes through dispatch(), as the browser does.
"""

import json

import pytest

from yasmax_engine import api


def call(cmd, **args):
    return json.loads(api.dispatch(cmd, json.dumps(args)))


def program(*lines, base=100):
    api.boot()
    call("create_program", name="TRAIN", base=base)
    for text in lines:
        assert call("add_instruction", program="TRAIN", text=text)["ok"], text
    return call("snapshot")["snapshot"]


def run(n):
    reply = None
    for _ in range(n):
        reply = call("step")
    return reply


def reg(snap, name):
    return next(r["val"] for r in snap["gpr"] if r["name"] == name)


TRAIN = ["OUT #10, 0", "OUT #10, 1", "OUT #32, 1", "OUT #32, 0", "OUT #42, 1", "MSF"]


def test_lab_train_program_after_msf():
    snap = program(*TRAIN)
    assert snap["special"]["MAR"] == 2 and snap["special"]["MDR"] == "0"
    assert [r["t"] for r in snap["memory"]] == [4, 4, 4, 4, 4, 2]
    snap = run(6)["snapshot"]
    s = snap["special"]
    got = (s["PC"], s["SP"], s["BR"], s["IR"], s["MAR"], s["MDR"])
    assert got == (35, 8100, 100, "MSF", 135, "MSF")
    assert snap["stack"] == [{"pos": 0, "val": -1, "addr": 35}, {"pos": 1, "val": 0, "addr": 35}]
    assert [r["current"] for r in snap["memory"]] == [False] * 5 + [True]
    assert snap["run"]["state"] == "ended"
    assert run(1)["events"][0]["type"] == "end"


def test_reset_program_clears_stack_and_goes_to_top():
    program(*TRAIN)
    run(6)
    snap = call("reset_program")["snapshot"]
    assert snap["stack"] == [] and snap["special"]["SP"] == 8096 and snap["special"]["PC"] == 0
    assert snap["memory"][0]["current"]


def test_cmp_equal_sets_z_and_sr_1():
    program("CMP #0, R00")
    snap = run(1)["snapshot"]
    assert snap["flags"] == {"OV": False, "Z": True, "N": False} and snap["special"]["SR"] == 1


@pytest.mark.parametrize(("r00", "flags"), [(3, (False, False)), (7, (False, True))])
def test_cmp_greater_and_less(r00, flags):
    program("CMP R00, R01")
    call("set_register", name="R00", value=r00)
    call("set_register", name="R01", value=5)
    f = run(1)["snapshot"]["flags"]
    assert (f["Z"], f["N"]) == flags


def test_cmp_needs_a_register():
    api.boot()
    call("create_program", name="T", base=0)
    assert not call("add_instruction", program="T", text="CMP #1, #1")["ok"]


def test_hlt_stays_and_reports_every_time():
    program("MOV #5, R00", "HLT", "MOV #6, R00")
    run(1)
    for _ in range(2):
        reply = call("step")
        assert reply["events"][0]["type"] == "halt"
        assert reply["snapshot"]["special"]["PC"] == 6 and reg(reply["snapshot"], "R00") == 5


def test_divide_by_zero_does_nothing():
    program("MOV #9, R01", "DIV #0, R01")
    reply = run(2)
    assert reply["ok"] and reg(reply["snapshot"], "R01") == 9


def test_arithmetic_and_flags():
    program("MOV #5, R00", "MOV #8, R01", "ADD R00, R01", "SUB #20, R01", "MUL #3, R00",
            "DIV #2, R00", "INC R00", "DEC R02")  # fmt: skip
    snap = run(8)["snapshot"]
    assert (reg(snap, "R01"), reg(snap, "R00"), reg(snap, "R02")) == (-7, 8, -1)
    assert snap["flags"]["N"]


def test_push_pop_and_empty_pop():
    program("PSH #6", "PSH R00", "POP R02", "POP R03", "POP R04")
    snap = run(2)["snapshot"]
    assert snap["special"]["SP"] == 8100 and [e["val"] for e in snap["stack"]] == [6, 0]
    run(2)
    reply = call("step")
    assert not reply["ok"] and reply["events"][0]["message"] == "Stack overflow"


def test_jumps_and_loop():
    program("MOV #3, R05", "INC R01", "LOOP 6, R05", "HLT")
    reply = run(8)
    assert reg(reply["snapshot"], "R01") == 3 and reply["events"][0]["type"] == "halt"


def test_msf_cal_ret():
    program("MSF", "CAL 13", "HLT", "NOP", "MOV #1, R00", "RET")
    assert [r["ladd"] for r in call("snapshot")["snapshot"]["memory"]] == [0, 1, 5, 6, 7, 13]
    run(1)
    snap = call("step")["snapshot"]
    assert snap["special"]["PC"] == 13 and snap["stack"][1]["val"] == 5
    snap = call("step")["snapshot"]
    assert snap["special"]["PC"] == 5 and snap["stack"] == []


def test_memory_load_store():
    program("MOV #48, R01", "STW #25, @R01", "LDW 48, R02", "STBI #65, @R01", "LDB @R01, R03")
    snap = run(5)["snapshot"]
    assert (reg(snap, "R02"), reg(snap, "R01")) == (25, 49)
    assert call("data_memory", program="TRAIN")["result"]["bytes"][48:50] == [65, 0]


def test_out_events():
    program("OUT #65, 1", "OUT #42, 0", "OUT 48, 0")
    call("write_data", program="TRAIN", address=48, kind="string", value="hi")
    texts = [call("step")["events"][0]["text"] for _ in range(3)]
    assert texts == ["A", "42", "hi"]


def test_double_click_executes_that_instruction():
    program("MOV #1, R00", "MOV #2, R00", "HLT")
    snap = call("execute_at", program="TRAIN", index=1)["snapshot"]
    assert reg(snap, "R00") == 2 and snap["special"]["PC"] == 12


def test_ticks_and_execution_unit():
    program("OUT #32, 1", "HLT")
    snap = call("tick")["snapshot"]
    assert snap["exec"]["instruction"] == "OUT #32, 1" and snap["run"]["cycle_phase"] == "fetched"
    snap = call("tick")["snapshot"]
    assert snap["exec"]["opcode"] == "OUT"
    reply = call("tick")
    ops = reply["snapshot"]["exec"]["operands"]
    assert [(o["text"], o["value"], o["mode"]) for o in ops] == [("#32", 32, 0), ("1", 1, 2)]
    assert reply["events"][0] == {"type": "output", "text": " "}
    assert not call("decode")["ok"]


def test_breakpoint_stops_run_step():
    program("NOP", "NOP", "HLT")
    call("set_breakpoint", program="TRAIN", index=1, on=True)
    assert call("snapshot")["snapshot"]["memory"][1]["breakpoint"]
    call("step", stop_at_breakpoint=True)
    reply = call("step", stop_at_breakpoint=True)
    assert reply["events"][0]["type"] == "breakpoint" and reply["snapshot"]["special"]["PC"] == 1


def test_labels_take_no_space():
    program("NOP")
    call("add_label", program="TRAIN", name="Label")
    call("add_instruction", program="TRAIN", text="OUT #10, 0")
    rows = call("snapshot")["snapshot"]["memory"]
    assert [(r["text"], r["ladd"], r["t"]) for r in rows] == [
        ("NOP", 0, 6), ("Label:", 1, -1), ("OUT #10, 0", 1, 4)]  # fmt: skip
    assert not call("add_label", program="TRAIN", name="label")["ok"]
    assert not call("add_label", program="TRAIN", name="9x")["ok"]


def test_input_and_watch():
    program("IN 0, R00", "IN 0, R01", "STB #1, 20")
    call("console_input", text="AB")
    call("set_data_watch", program="TRAIN", addresses=[20])
    reply = run(3)
    assert (reg(reply["snapshot"], "R00"), reg(reply["snapshot"], "R01")) == (65, 66)
    assert reply["events"][0]["type"] == "watch"


def test_step_with_nothing_in_memory():
    api.boot()
    reply = call("step")
    assert not reply["ok"] and reply["events"][0]["type"] == "program_error"


def test_label_jumps_like_programming_model_2():
    """The tutorial's loop: MOV #0, R01 / L0: / ADD #1, R01 / CMP #5, R01 / JNE $L0 / HLT."""
    program("MOV #0, R01")
    call("add_label", program="TRAIN", name="L0")
    for text in ["ADD #1, R01", "CMP #5, R01", "JNE $L0", "HLT"]:
        call("add_instruction", program="TRAIN", text=text)
    rows = call("snapshot")["snapshot"]["memory"]
    assert rows[4]["text"] == "JNE $L0" and rows[4]["operands"][0]["label"] == "L0"
    reply = run(20)
    assert reg(reply["snapshot"], "R01") == 5 and reply["events"][0]["type"] == "halt"


def test_unknown_label_faults():
    program("JMP $nowhere")
    reply = call("step")
    assert not reply["ok"] and "nowhere" in reply["events"][0]["message"]


def test_click_moves_pc():
    program("MOV #1, R00", "MOV #2, R01", "HLT")
    snap = call("set_pc", program="TRAIN", index=1)["snapshot"]
    assert snap["special"]["PC"] == 6 and snap["memory"][1]["current"]
    assert reg(call("step")["snapshot"], "R01") == 2


def test_isa_command():
    api.boot()
    assert len(call("isa")["result"]) == 47


def test_subroutine_with_parameter_like_programming_model_2():
    """MSF / PSH #8 / CAL $L2 / HLT / L2: / POP R02 / RET: the pushed value
    sits above the return address, so POP in the subroutine gets 8."""
    program("MSF", "PSH #8", "CAL $L2", "HLT")
    call("add_label", program="TRAIN", name="L2")
    call("add_instruction", program="TRAIN", text="POP R02")
    call("add_instruction", program="TRAIN", text="RET")
    reply = run(6)
    assert reg(reply["snapshot"], "R02") == 8 and reply["events"][0]["type"] == "halt"
    assert reply["snapshot"]["stack"] == []
