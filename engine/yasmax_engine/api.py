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

- ok=false with a "program_error" or "fault" event is NORMAL. It means
  the student did something invalid, and the UI shows a dialog.
- A "bad_request" event means the UI sent a wrong command or wrong
  arguments. That is a bug in our JS, not the student's fault.
- An "internal_error" event means a bug in the engine. It is caught here
  so one bug never kills the worker.

Adding a command = add one entry to COMMANDS pointing at a Machine method.
"""

from __future__ import annotations

import inspect
import json
import traceback
from typing import Any

from . import __version__
from .errors import YasmaxError
from .machine import Machine

# Command name (sent by the UI) -> Machine method name.
# This is a whitelist: the UI can only call what is listed here.
COMMANDS: dict[str, str] = {
    "snapshot": "snapshot",
    "set_register": "set_register",
    "reset_all_registers": "reset_all_registers",
    "set_register_set_size": "set_register_set_size",
}

_machine: Machine | None = None


def _get_machine() -> Machine:
    global _machine
    if _machine is None:
        _machine = Machine()
    return _machine


def _reply(ok: bool, events: list[dict[str, Any]]) -> str:
    return json.dumps({"ok": ok, "snapshot": _get_machine().snapshot(), "events": events})


def boot() -> str:
    """Create a fresh Machine and describe it. Called once by the worker."""
    global _machine
    _machine = Machine()
    return json.dumps(
        {
            "engine_version": __version__,
            "commands": sorted(COMMANDS),
            "snapshot": _machine.snapshot(),
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
        method(**args)
    except YasmaxError as exc:
        return _reply(False, [exc.to_event()])
    except Exception as exc:  # noqa: BLE001 - last line of defence, see module docstring
        return _reply(
            False,
            [{"type": "internal_error", "message": repr(exc), "trace": traceback.format_exc()}],
        )
    return _reply(True, [])
