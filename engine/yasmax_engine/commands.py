"""
File: engine/yasmax_engine/commands.py

Machine commands for the Instructions tab and the data memory window,
split out of machine.py to keep each file short. They are mixed into
Machine (class Machine(InstructionCommands, DataMemoryCommands)), so to
api.py and the tests they are ordinary Machine methods.

They rely on two things every Machine has: self.programs (ProgramList)
and self.config (MachineConfig).
"""

from __future__ import annotations

from .program import Program


class _ProgramLookup:
    def _program(self, program: str) -> Program:
        return self.programs.get(program)


class InstructionCommands(_ProgramLookup):
    """ADD NEW / INSERT / EDIT / DELETE / MOVE UP / MOVE DOWN / labels."""

    def add_instruction(self, program: str, text: str) -> None:
        self._program(program).add(text)

    def insert_instruction(self, program: str, index: int, text: str) -> None:
        self._program(program).insert(index, text)

    def edit_instruction(self, program: str, index: int, text: str) -> None:
        self._program(program).edit(index, text)

    def delete_instruction(self, program: str, index: int) -> None:
        self._program(program).delete(index)

    def move_instruction(self, program: str, index: int, delta: int) -> None:
        self._program(program).move(index, delta)

    def add_label(self, program: str, name: str, index: int | None = None) -> None:
        """NEW LABEL... -> Apply label (appends, or inserts at index)."""
        self._program(program).add_label(name, index)


class DataMemoryCommands(_ProgramLookup):
    """The data memory window ("<program>: Pid n")."""

    def data_memory(self, program: str) -> dict[str, object]:
        """Everything the data memory window shows. TODO: Pid is 0 until
        program instances (an OS feature) exist."""
        p = self._program(program)
        return {
            "name": p.name,
            "pid": 0,
            "pages": p.pages,
            "page_size": self.config.page_size,
            "size": p.data.size,
            "bytes": list(p.data.bytes),
        }

    def write_data(self, program: str, address: object, kind: str, value: object) -> None:
        """Initialise Data -> UPDATE (kind: integer, boolean or string)."""
        self._program(program).data.write_value(address, kind, value)

    def write_data_bytes(self, program: str, address: object, values: list) -> None:
        """Debug control -> UPDATE: the B0..B7 hex boxes of one row."""
        self._program(program).data.write_hex_row(address, values)

    def reset_data_memory(self, program: str) -> None:
        """RESET ALL in the data memory window."""
        self._program(program).data.reset()
