"""
File: engine/tests/unit/test_sasfile.py

SAVE... / LOAD... with YASMIN's .sas program files. TRAIN below is the
exact file a student saved from YASMIN 7.5.50 in the lab.
"""

import json

from yasmax_engine import api

TRAIN = "\r\n".join([
    '1,12,#FALSE#,#FALSE#,"TRAIN",0,0,0,63,1,6,1997370671', "0,0,0,0,0,0", "0", "0", "1",
    '"Label",36',
    '0,4,"OUT #10, 0",0,0,0,0,#FALSE#', '7,4,"OUT #10, 1",0,0,0,0,#FALSE#',
    '14,4,"OUT #32, 1",0,0,0,0,#FALSE#', '21,4,"OUT #32, 0",0,0,0,0,#FALSE#',
    '28,4,"OUT #42, 1",0,0,0,0,#FALSE#', '35,2,"MSF",0,0,0,0,#FALSE#',
    '36,-1,"Label",0,0,0,0,#FALSE#', '36,4,"OUT #10, 0",0,0,0,0,#FALSE#',
    '43,2,"HLT",0,0,0,0,#FALSE#', '44,4,"OUT #10, 0",0,0,0,0,#FALSE#',
    '51,3,"CMP #0, R00",0,0,0,0,#FALSE#', '57,1,"DIV #0, R00",0,0,0,0,#FALSE#',
    "0", "0", "0", "-1", "",
])  # fmt: skip


def call(cmd, **args):
    return json.loads(api.dispatch(cmd, json.dumps(args)))


def test_load_lab_file():
    api.boot()
    reply = call("load_program", text=TRAIN, base=-1)
    assert reply["ok"] and reply["result"] == "TRAIN"
    rows = reply["snapshot"]["memory"]
    assert len(rows) == 12
    assert [(r["ladd"], r["t"], r["text"]) for r in rows][5:8] == [
        (35, 2, "MSF"), (36, -1, "Label:"), (36, 4, "OUT #10, 0")]  # fmt: skip
    assert rows[-1]["ladd"] == 57 and reply["snapshot"]["programs"][0]["base"] == 0


def test_save_matches_lab_layout():
    api.boot()
    call("load_program", text=TRAIN)
    saved = call("save_program", program="TRAIN")["result"]
    assert saved["filename"] == "TRAIN.sas"
    ours, lab = saved["text"].split("\r\n"), TRAIN.split("\r\n")
    assert ours[0].rsplit(",", 1)[0] == lab[0].rsplit(",", 1)[0]
    assert ours[1:] == lab[1:]


def test_load_with_new_base_and_breakpoint():
    api.boot()
    text = TRAIN.replace('"MSF",0,0,0,0,#FALSE#', '"MSF",0,0,0,0,#TRUE#')
    snap = call("load_program", text=text, base="200")["snapshot"]
    assert snap["programs"][0]["base"] == 200 and snap["memory"][5]["breakpoint"]
    assert "#TRUE#" in call("save_program", program="TRAIN")["result"]["text"]


def test_bad_files():
    api.boot()
    assert not call("load_program", text="hello")["ok"]
    call("load_program", text=TRAIN)
    assert not call("load_program", text=TRAIN)["ok"]  # name already used
