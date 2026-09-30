"""
File: engine/yasmax_engine/program.py

Programs, as shown in the PROGRAM LIST and CPU INSTRUCTIONS IN MEMORY views.

A Program has a name, a base address, an ordered list of LINES and its own
data memory (datamem.py) of `pages` x 256 bytes. A line is an Instruction
or a Label. Addresses follow the tutorial:
    LAdd  (logical)  = sum of the sizes of the lines before it
    PAdd  (physical) = base address + LAdd
A label takes no bytes: YASMIN 7.5.50 shows it as "Label:" with the same
address as the next instruction and T = -1.

T column ("Type of instruction", YASMIN 7.5.50 help): seen in the lab as
Arithmetic 1, Control Transfer 2, Comparison 3, I/O 4, label -1.
TODO(research): Data Transfer 0, Logical 5, Miscellaneous 6 are guesses.

Breakpoints are the row checkboxes of the memory view (saved as #TRUE# /
#FALSE# in .sas files). They belong to the line object, so they move with
it when lines are inserted, moved or deleted.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .datamem import DataMemory
from .errors import ProgramError
from .isa import Group, Instruction, parse_instruction

TYPE_CODE = {
    Group.DATA: 0,
    Group.ARITH: 1,
    Group.CONTROL: 2,
    Group.COMPARE: 3,
    Group.IO: 4,
    Group.LOGIC: 5,
    Group.MISC: 6,
}
_LABEL_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(eq=False)
class Label:
    name: str
    size: int = 0

    def __str__(self) -> str:
        return f"{self.name}:"


Line = Instruction | Label


def type_code(line: Line) -> int:
    return -1 if isinstance(line, Label) else TYPE_CODE[line.spec.group]


@dataclass
class Program:
    name: str
    base: int
    pages: int = 1
    instructions: list[Line] = field(default_factory=list)
    data: DataMemory = field(default_factory=lambda: DataMemory(256))
    breakpoints: set[int] = field(default_factory=set)

    def layout(self) -> list[tuple[int, Line]]:
        """[(LAdd, line), ...] in memory order."""
        rows, ladd = [], 0
        for line in self.instructions:
            rows.append((ladd, line))
            ladd += line.size
        return rows

    @property
    def code_size(self) -> int:
        return sum(line.size for line in self.instructions)

    def instruction_at(self, ladd: int) -> tuple[int, Instruction] | None:
        """(index, instruction) of the instruction starting at `ladd`."""
        for index, (a, line) in enumerate(self.layout()):
            if a == ladd and isinstance(line, Instruction):
                return index, line
        return None

    def label_address(self, name: str) -> int | None:
        for ladd, line in self.layout():
            if isinstance(line, Label) and line.name.lower() == name.lower():
                return ladd
        return None

    def ladd_of(self, index: int) -> int:
        return self.layout()[self._check(index)][0]

    # ---- breakpoints (row checkboxes) ----

    def is_breakpoint(self, line: Line) -> bool:
        return id(line) in self.breakpoints

    def set_breakpoint(self, index: int, on: bool) -> None:
        key = id(self.instructions[self._check(index)])
        if on:
            self.breakpoints.add(key)
        else:
            self.breakpoints.discard(key)

    # ---- editing (Instructions tab) ----

    def _check(self, index: int, allow_end: bool = False) -> int:
        top = len(self.instructions) if allow_end else len(self.instructions) - 1
        if not isinstance(index, int) or not 0 <= index <= top:
            raise ProgramError("Please select an instruction first.", field="instruction")
        return index

    def add(self, text: str) -> None:
        self.instructions.append(parse_instruction(text))

    def insert(self, index: int, text: str) -> None:
        self.instructions.insert(self._check(index, allow_end=True), parse_instruction(text))

    def edit(self, index: int, text: str) -> None:
        if isinstance(self.instructions[self._check(index)], Label):
            raise ProgramError("A label cannot be edited. Delete it and add a new one.")
        new = parse_instruction(text)
        self.breakpoints.discard(id(self.instructions[index]))
        self.instructions[index] = new

    def delete(self, index: int) -> None:
        self.breakpoints.discard(id(self.instructions[self._check(index)]))
        del self.instructions[index]

    def move(self, index: int, delta: int) -> None:
        """Swap with a neighbour: delta -1 = MOVE UP, +1 = MOVE DOWN."""
        i = self._check(index)
        j = i + (1 if delta > 0 else -1)
        if 0 <= j < len(self.instructions):
            self.instructions[i], self.instructions[j] = self.instructions[j], self.instructions[i]

    def add_label(self, name: str, index: int | None = None) -> None:
        """NEW LABEL... -> Apply label. Appends, or inserts at `index`."""
        name = (name or "").strip()
        if not _LABEL_RE.match(name):
            raise ProgramError("A label name must start with a letter; use letters, digits or _.")
        if any(isinstance(x, Label) and x.name.lower() == name.lower() for x in self.instructions):
            raise ProgramError(f"The label {name} already exists.")
        at = len(self.instructions) if index is None else self._check(index, allow_end=True)
        self.instructions.insert(at, Label(name))


class ProgramList:
    def __init__(self) -> None:
        self.programs: list[Program] = []

    def get(self, name: str) -> Program:
        for p in self.programs:
            if p.name == name:
                return p
        raise ProgramError(f"No program named {name!r}.", field="program")

    def create(self, name: str, base: int, pages: int = 1, page_size: int = 256) -> Program:
        name = (name or "").strip()
        if not name:
            raise ProgramError("Please enter a program name.", field="program_name")
        if any(p.name == name for p in self.programs):
            raise ProgramError(f"A program named {name!r} already exists.", field="program_name")
        if base < 0:
            raise ProgramError("Base address must not be negative.", field="base_address")
        if pages < 1:
            raise ProgramError("A program needs at least 1 page.", field="pages")
        program = Program(name=name, base=base, pages=pages, data=DataMemory(pages * page_size))
        # YASMIN 7.5.50 shows 02 in data byte 0 of a new program.
        # TODO(research): why; confirm on a brand new program.
        program.data.bytes[0] = 2
        self.programs.append(program)
        return program

    def remove(self, name: str) -> None:
        self.programs.remove(self.get(name))

    def remove_all(self) -> None:
        self.programs.clear()
