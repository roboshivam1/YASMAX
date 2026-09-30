"""
File: engine/yasmax_engine/machine.py

The Machine: one simulated CPU, and the ONLY object the outside world
talks to (docs/ARCHITECTURE.md §3.1). Every command is a plain method that
takes JSON-friendly arguments and either changes state or raises a
YasmaxError. api.py exposes them to the browser; tests call them directly.

Commands so far
---------------
Registers tab:     set_register, reset_all_registers, set_register_set_size
Program tab:       create_program, remove_program, remove_all_programs
Instructions tab:  add_instruction, insert_instruction, edit_instruction,
                   delete_instruction, move_instruction
Data memory:       data_memory, write_data, write_data_bytes, reset_data_memory
Running (cpu.py):  step, tick, fetch, decode, execute, reset_program,
                   execute_at, set_breakpoint, console_input, set_data_watch
Files (sasfile.py): save_program, load_program

A command may RETURN a JSON-safe value (e.g. data_memory); api.py passes
it to the UI as the reply's "result". Things that HAPPEN while running
(console output, HLT, breakpoints) are events: emit() queues them and
api.py sends them with the reply.
"""

from __future__ import annotations

import dataclasses
from typing import Any

from .commands import DataMemoryCommands, InstructionCommands
from .config import DEFAULT_CONFIG, MachineConfig
from .cpu import ExecutionCommands, RunState
from .errors import ProgramError
from .flags import StatusFlags
from .program import Program, ProgramList
from .registers import RegisterFile, SpecialRegisters
from .sasfile import FileCommands
from .stack import Stack

__all__ = ["Machine", "RunState", "parse_int"]


def parse_int(value: object, field: str) -> int:
    """Accept an int, or text a student typed (e.g. " -12 "), as an int.
    Anything else raises ProgramError naming the field, so the UI can show
    a dialog and focus the right input box.
    TODO(R-1): verify whether the original also accepts hex input."""
    if isinstance(value, bool):
        raise ProgramError("Please enter a whole number.", field=field)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip(), 10)
        except ValueError:
            pass
    raise ProgramError("Please enter a whole number.", field=field)


class Machine(InstructionCommands, DataMemoryCommands, ExecutionCommands, FileCommands):
    """One simulated CPU. Commands are split over commands.py, cpu.py and
    sasfile.py to keep each file short."""

    def __init__(self, config: MachineConfig = DEFAULT_CONFIG) -> None:
        config.validate()
        self.config = config
        self.gpr = RegisterFile(config)
        self.special = SpecialRegisters.initial(config)
        self.flags = StatusFlags()
        self.programs = ProgramList()
        self.stack = Stack(config)
        self.run_state = RunState.EMPTY
        self.current: str | None = None  # program the PC belongs to
        self.input_queue: list[str] = []
        self.events: list[dict[str, Any]] = []
        self._clear_exec_unit()

    def emit(self, kind: str, **data: Any) -> None:
        self.events.append({"type": kind, **data})

    def drain_events(self) -> list[dict[str, Any]]:
        events, self.events = self.events, []
        return events

    # ---- Registers tab -------------------------------------------------

    def set_register(self, name: str, value: object) -> None:
        """Reg Value -> CHANGE. Uses poke(), so it is not an instruction access."""
        self.gpr.poke(name, parse_int(value, field="reg_value"))

    def reset_all_registers(self) -> None:
        """RESET ALL: every general purpose register back to 0."""
        self.gpr.reset_all()

    def set_register_set_size(self, size: object) -> None:
        """Select Register Set Size dropdown (8, 16, 32 or 64 per the ISA document)."""
        n = parse_int(size, field="register_set_size")
        if n not in self.config.gpr_set_sizes:
            raise ProgramError(
                f"Register set size must be one of {list(self.config.gpr_set_sizes)}.",
                field="register_set_size",
            )
        self.config = dataclasses.replace(self.config, gpr_count=n)
        self.gpr.set_size(self.config)

    # ---- Program tab and program list ----------------------------------

    def create_program(self, name: str, base: object, pages: object = 1) -> None:
        """ADD: create an empty program. BR shows the current base address
        (tutorial). TODO(R-4): confirm when the original updates BR."""
        if isinstance(base, str) and not base.strip():
            raise ProgramError("Please enter a base address.", field="base_address")
        program = self.programs.create(
            name,
            parse_int(base, field="base_address"),
            parse_int(pages, field="pages"),
            page_size=self.config.page_size,
        )
        self._program_created(program)

    def _program_created(self, program: Program) -> None:
        """A new program (ADD or LOAD) becomes the one the PC runs in."""
        self.current = program.name
        self.special.BR = program.base
        self.special.PC = 0
        self._clear_exec_unit()
        self.run_state = RunState.IDLE

    def remove_program(self, name: str) -> None:
        self.programs.remove(name)
        if name == self.current:
            self.current, self.special.PC = None, 0
        self._update_run_state()

    def remove_all_programs(self) -> None:
        self.programs.remove_all()
        self.current, self.special.PC = None, 0
        self._update_run_state()

    # ---- State -------------------------------------------------------------

    def _update_run_state(self) -> None:
        if not self.programs.programs:
            self.run_state = RunState.EMPTY
            self._clear_exec_unit()
        elif self.run_state == RunState.EMPTY:
            self.run_state = RunState.IDLE

    def snapshot(self) -> dict[str, object]:
        """Everything the UI needs to redraw the window (snapshot.py)."""
        from .snapshot import build_snapshot

        return build_snapshot(self)
