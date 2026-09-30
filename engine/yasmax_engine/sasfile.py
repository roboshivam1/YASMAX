"""
File: engine/yasmax_engine/sasfile.py

SAVE... and LOAD... in the Program tab: YASMIN's ".sas" program files, so
students can move programs between the lab and YASMAX.

The format, read from a file saved by YASMIN 7.5.50 (CRLF line ends):

    1,12,#FALSE#,#FALSE#,"TRAIN",0,0,0,63,1,6,1997370671   header
    0,0,0,0,0,0                                              ?
    0                                                        ?
    0                                                        ?
    1                                                        label count
    "Label",36                                               name, LAdd
    0,4,"OUT #10, 0",0,0,0,0,#FALSE#                         one per line:
    36,-1,"Label",0,0,0,0,#FALSE#                            LAdd, T, text,
    ...                                                      ?, breakpoint
    0 / 0 / 0 / -1                                           trailer

Header: 12 = line count, "TRAIN" = name, 0 = base, 63 = code size,
1 = pages. TODO(R-10): the other fields (including 6 and the large last
number). SAVE writes them as seen in that file; LOAD ignores them.
TODO(R-10): check that YASMIN loads files saved by YASMAX.
"""

from __future__ import annotations

import csv
import io
import zlib

from .errors import ProgramError
from .program import Label, Program, type_code

_B = {True: "#TRUE#", False: "#FALSE#"}


def _q(text: str) -> str:
    return '"' + text.replace('"', '""') + '"'


def dump_program(p: Program) -> str:
    rows = p.layout()
    labels = [(ladd, line) for ladd, line in rows if isinstance(line, Label)]
    body = [
        f"{ladd},{type_code(line)},{_q(line.name if isinstance(line, Label) else str(line))},"
        f"0,0,0,0,{_B[p.is_breakpoint(line)]}"
        for ladd, line in rows
    ]
    stamp = zlib.crc32("\n".join(body).encode()) & 0x7FFFFFFF
    lines = [
        f"1,{len(rows)},#FALSE#,#FALSE#,{_q(p.name)},{p.base},0,0,{p.code_size},{p.pages},6,{stamp}",
        "0,0,0,0,0,0",
        "0",
        "0",
        str(len(labels)),
        *[f"{_q(line.name)},{ladd}" for ladd, line in labels],
        *body,
        "0",
        "0",
        "0",
        "-1",
    ]
    return "\r\n".join(lines) + "\r\n"


def parse_program(text: str) -> dict:
    """{name, base, pages, lines: [(text, is_label, breakpoint)]}."""
    try:
        rows = [r for r in csv.reader(io.StringIO(text.replace("\r\n", "\n"))) if r]
        head = rows[0]
        count, name, base, pages = int(head[1]), head[4], int(head[5]), int(head[9])
        at = 4
        at += 1 + int(rows[at][0])  # skip the label table
        lines = []
        for r in rows[at : at + count]:
            lines.append((r[2], int(r[1]) == -1, r[-1].strip().upper() == "#TRUE#"))
        if len(lines) != count:
            raise ValueError("file is cut short")
    except (ValueError, IndexError) as exc:
        raise ProgramError(f"This is not a CPU simulator program file ({exc}).") from None
    return {"name": name, "base": base, "pages": max(1, pages), "lines": lines}


class FileCommands:
    """SAVE... / LOAD... (mixed into Machine)."""

    def save_program(self, program: str) -> dict[str, str]:
        p = self.programs.get(program)
        return {"filename": f"{p.name}.sas", "text": dump_program(p)}

    def load_program(self, text: str, base: object = -1) -> str:
        """Base Address -1 keeps the base saved in the file."""
        info = parse_program(text)
        want = int(str(base).strip() or "-1") if str(base).strip().lstrip("-").isdigit() else -1
        p = self.programs.create(
            info["name"], want if want >= 0 else info["base"], info["pages"], self.config.page_size
        )
        try:
            for line, is_label, bp in info["lines"]:
                if is_label:
                    p.add_label(line)
                else:
                    p.add(line)
                if bp:
                    p.set_breakpoint(len(p.instructions) - 1, True)
        except ProgramError as exc:
            self.programs.remove(p.name)
            raise ProgramError(f"Could not load {info['name']}: {exc}") from None
        self._program_created(p)
        return p.name
