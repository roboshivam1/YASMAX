"""
File: engine/yasmax_engine/api.py

The JSON doorway between the browser and the engine.

The worker (web/js/worker.js) calls exactly two Python functions:

    boot()                     -> JSON string
    dispatch(cmd, args_json)   -> JSON string

Why strings? Passing JSON text across the JS <-> Python boundary is the
simplest way to use Pyodide. Strings convert automatically, and nothing
leaks: no Python objects are left alive on the JS side (PyProxies)
that you would have to remember to destroy.

Reply shape (every command)
---------------------------
    {"ok": true|false, "snapshot": {...}, "events": [ {...}, ... ]}
plus "result": ... when the command returns a value (e.g. data_memory).

- ok=false with a "program_error" or "fault" event is NORMAL. It means
  the student did something invalid, and the UI shows a dialog.
- A "bad_request" event means the UI sent a wrong command or wrong
  arguments. That is a bug in our JS, not the student's fault.
- An "internal_error" event means a bug in the engine. It is caught here
  so one bug never kills the worker.
- Running adds events on successful replies too: "output" (console text),
  "halt", "end", "breakpoint" and "watch".

Adding a command = add one entry to COMMANDS pointing at a Machine method.
"""

from __future__ import annotations

import inspect
import json
import traceback
from typing import Any

from . import __version__
from .errors import YasmaxError
from .isa import UI_NAMES, isa_table
from .machine import Machine

# Command name (sent by the UI) -> Machine method name.
# This is a whitelist: the UI can only call what is listed here.
COMMANDS: dict[str, str] = {
    "snapshot": "snapshot",
    "set_register": "set_register",
    "reset_all_registers": "reset_all_registers",
    "set_register_set_size": "set_register_set_size",
    "create_program": "create_program",
    "remove_program": "remove_program",
    "remove_all_programs": "remove_all_programs",
    "add_instruction": "add_instruction",
    "insert_instruction": "insert_instruction",
    "edit_instruction": "edit_instruction",
    "delete_instruction": "delete_instruction",
    "move_instruction": "move_instruction",
    "data_memory": "data_memory",
    "write_data": "write_data",
    "write_data_bytes": "write_data_bytes",
    "reset_data_memory": "reset_data_memory",
    "add_label": "add_label",
    "step": "step",
    "tick": "tick",
    "fetch": "fetch",
    "decode": "decode",
    "execute": "execute",
    "reset_program": "reset_program",
    "execute_at": "execute_at",
    "set_pc": "set_pc",
    "isa": "isa",
    "set_breakpoint": "set_breakpoint",
    "console_input": "console_input",
    "set_data_watch": "set_data_watch",
    "save_program": "save_program",
    "load_program": "load_program",
}

_machine: Machine | None = None


def _get_machine() -> Machine:
    global _machine
    if _machine is None:
        _machine = Machine()
    return _machine


def _reply(ok: bool, events: list[dict[str, Any]], result: Any = None) -> str:
    """Error events first, then what happened while running (output, HLT)."""
    machine = _get_machine()
    reply = {"ok": ok, "snapshot": machine.snapshot(), "events": events + machine.drain_events()}
    if result is not None:
        reply["result"] = result
    return json.dumps(reply)


def boot() -> str:
    """Create a fresh Machine and describe it. Called once by the worker."""
    global _machine
    _machine = Machine()
    return json.dumps(
        {
            "engine_version": __version__,
            "commands": sorted(COMMANDS),
            "snapshot": _machine.snapshot(),
            # For the instruction dialog: every opcode and the mode labels.
            "isa": isa_table(),
            "address_modes": {int(m): name for m, name in UI_NAMES.items()},
        }
    )


def dispatch(cmd: str, args_json: str = "{}") -> str:
    """Run one command and return the reply as JSON text."""
    method_name = COMMANDS.get(cmd)
    if method_name is None:
        return _reply(False, [{"type": "bad_request", "message": f"Unknown command: {cmd}"}])

    try:
        args = json.loads(args_json or "{}")
        if not isinstance(args, dict):
            raise TypeError("arguments must be a JSON object")
    except (ValueError, TypeError) as exc:
        return _reply(False, [{"type": "bad_request", "message": f"Bad arguments: {exc}"}])

    machine = _get_machine()
    method = getattr(machine, method_name)

    # Check argument names and count BEFORE calling, so a TypeError raised
    # by a real bug inside the engine is never mistaken for a bad request.
    try:
        inspect.signature(method).bind(**args)
    except TypeError as exc:
        return _reply(False, [{"type": "bad_request", "message": f"{cmd}: {exc}"}])

    try:
        result = method(**args)
    except YasmaxError as exc:
        return _reply(False, [exc.to_event()])
    except Exception as exc:  # noqa: BLE001 - last line of defence, see module docstring
        return _reply(
            False,
            [{"type": "internal_error", "message": repr(exc), "trace": traceback.format_exc()}],
        )
    # "snapshot" already IS the snapshot; don't send it twice.
    return _reply(True, [], None if cmd == "snapshot" else result)
