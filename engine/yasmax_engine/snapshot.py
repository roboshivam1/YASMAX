"""
File: engine/yasmax_engine/snapshot.py

Turns a Machine into one plain dict: the "snapshot" contract from
docs/ARCHITECTURE.md §5. The UI renders ONLY from this, so if a panel
needs a value, it must appear here.

Rules
-----
- Only JSON-safe values: dict, list, str, int, bool, None.
  (StrEnum members count as str, so they serialise as plain strings.)
- Always include every section, even when empty.
- Never compute CPU behaviour here. This file only copies and formats.

memory rows carry `program` and `index` so the UI can say which
instruction a click refers to (EDIT, DELETE, MOVE UP ...), `t` for the T
column, `label`, `breakpoint` (the row checkbox) and `current` (the PC
arrow). `stack` is bottom first. `exec` fills the Execution Unit tab.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .program import Label, type_code

if TYPE_CHECKING:
    from .machine import Machine

# Bump when the snapshot shape changes in a way the UI must know about.
SNAPSHOT_VERSION = 4


def _memory_rows(m: Machine) -> list[dict[str, object]]:
    rows = []
    for program in m.programs.programs:
        here = program.instruction_at(m.special.PC) if program.name == m.current else None
        for index, (ladd, ins) in enumerate(program.layout()):
            label = isinstance(ins, Label)
            rows.append(
                {
                    "padd": program.base + ladd,
                    "ladd": ladd,
                    "text": str(ins),
                    "op": None if label else ins.spec.mnemonic,
                    "operands": []
                    if label
                    else [
                        {"mode": int(o.mode), "value": o.value, "negative": o.negative}
                        for o in ins.operands
                    ],
                    "base": program.base,
                    "size": ins.size,
                    "t": type_code(ins),
                    "label": label,
                    "breakpoint": program.is_breakpoint(ins),
                    "program": program.name,
                    "index": index,
                    "current": here is not None and here[0] == index,
                }
            )
    return rows


def _program_rows(m: Machine) -> list[dict[str, object]]:
    # YASMIN 7.5.50 shows Start 0000 and Type R for a program created with
    # ADD. TODO(R-17): what R stands for, and other types (compiled code?).
    return [
        {
            "name": p.name,
            "base": p.base,
            "pages": p.pages,
            "count": len(p.instructions),
            "start": 0,
            "type": "R",
        }
        for p in m.programs.programs
    ]


def build_snapshot(m: Machine) -> dict[str, object]:
    """Build the full snapshot for machine `m`."""
    return {
        "version": SNAPSHOT_VERSION,
        "special": m.special.as_dict(),
        "flags": m.flags.as_dict(),
        "gpr": m.gpr.rows(),
        "memory": _memory_rows(m),
        "stack": m.stack.rows(),
        "programs": _program_rows(m),
        "run": {"state": m.run_state, "cycle_phase": m.phase, "program": m.current},
        "exec": m.exec_unit,
        "cpu_mode": "User",
        "config": {
            "word_bits": m.config.word_bits,
            "signed": m.config.signed,
            "gpr_count": m.config.gpr_count,
            "gpr_set_sizes": list(m.config.gpr_set_sizes),
        },
    }
