"""
File: engine/yasmax_engine/snapshot.py

Turns a Machine into one plain dict: the "snapshot" contract from
docs/ARCHITECTURE.md §5. The UI renders ONLY from this, so if a panel
needs a value, it must appear here.

Rules
-----
- Only JSON-safe values: dict, list, str, int, bool, None.
  (StrEnum members count as str, so they serialise as plain strings.)
- Always include every section, even when empty. Panels can then read
  `snap.stack` without checking whether it exists.
- Never compute CPU behaviour here. This file only copies and formats.

How it connects
---------------
- Machine.snapshot() calls build_snapshot().
- api.py puts the result in every reply to the worker.
- web/js/store.js keeps the latest one, and panels subscribe to it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .machine import Machine

# Bump when the snapshot shape changes in a way the UI must know about.
SNAPSHOT_VERSION = 1


def build_snapshot(m: Machine) -> dict[str, object]:
    """Build the full snapshot for machine `m`."""
    return {
        "version": SNAPSHOT_VERSION,
        "special": m.special.as_dict(),
        "flags": m.flags.as_dict(),
        "gpr": m.gpr.rows(),
        # Filled in by later batches (memory.py, stack.py, program.py).
        "memory": [],
        "stack": [],
        "programs": [],
        "run": {"state": m.run_state, "cycle_phase": None},
        "config": {
            "word_bits": m.config.word_bits,
            "signed": m.config.signed,
            "gpr_count": m.config.gpr_count,
            "gpr_set_sizes": list(m.config.gpr_set_sizes),
        },
    }
