"""
File: engine/yasmax_engine/datamem.py

A program's DATA memory: the bytes shown in the "<program>: Pid n" window
opened by SHOW PROGRAM DATA MEMORY... Size = pages x 256 bytes.

Initialise Data (the window) writes TAGGED values. Seen in YASMIN 7.5.50:
    String "hello world" at 48 -> 03 68 65 6C 6C 6F 20 77 6F 72 6C 64 00
                                   (tag 03, ASCII, 00 terminator)
    Integer 25 at 96           -> 02 00 19 00   (tag 02, 00, 16-bit LE)
TODO(research): Boolean (guess: tag 01 then 00/01); negative integers.

Instructions (LDB, STW, MVS, OUT ...) use read_byte / read_word /
write_byte / write_word. Words are 16-bit little-endian. A bad address is
a runtime fault. Writes by code to a byte whose Debug control checkbox is
ticked are recorded in `hits`, so the CPU can suspend.
"""

from __future__ import annotations

from .errors import FaultCode, MachineFault, ProgramError

TAG_BOOL, TAG_INT, TAG_STR = 1, 2, 3


def _whole(value: object, field: str) -> int:
    try:
        return int(str(value).strip(), 10)
    except ValueError:
        raise ProgramError("Please enter a whole number.", field=field) from None


def encode_value(kind: str, value: object) -> bytes:
    """Bytes that Initialise Data writes for one value (see module note)."""
    if kind == "integer":
        n = _whole(value, "integer_value")
        if not -32768 <= n <= 65535:
            raise ProgramError(
                "Integer must fit in 16 bits (-32768 to 65535).", field="integer_value"
            )
        return bytes([TAG_INT, 0]) + (n & 0xFFFF).to_bytes(2, "little")
    if kind == "boolean":
        text = str(value).strip().lower()
        if text not in ("true", "false"):
            raise ProgramError("Boolean must be True or False.", field="boolean_value")
        return bytes([TAG_BOOL, 1 if text == "true" else 0])
    if kind == "string":
        text = str(value)
        if not text:
            raise ProgramError("Please enter a string.", field="string_value")
        if not text.isascii():
            raise ProgramError("Only plain ASCII characters are allowed.", field="string_value")
        return bytes([TAG_STR]) + text.encode("ascii") + b"\0"
    raise ProgramError(f"Unknown data type: {kind}", field="kind")


class DataMemory:
    def __init__(self, size: int) -> None:
        self.bytes = bytearray(size)
        self.watch: set[int] = set()
        self.hits: list[int] = []

    @property
    def size(self) -> int:
        return len(self.bytes)

    # ---- the window (user edits, ProgramError on bad input) ----

    def _check_range(self, address: int, length: int) -> None:
        if address < 0 or address + length > self.size:
            raise ProgramError(
                f"Address {address} is outside data memory (0 to {self.size - 1}).", field="address"
            )

    def write(self, address: object, data: bytes) -> None:
        start = _whole(address, "address")
        self._check_range(start, len(data))
        self.bytes[start : start + len(data)] = data

    def write_value(self, address: object, kind: str, value: object) -> None:
        """Initialise Data -> UPDATE."""
        self.write(address, encode_value(kind, value))

    def write_hex_row(self, address: object, values: list[object]) -> None:
        """Debug control -> UPDATE: up to 8 bytes typed as hex ("02", "FF")."""
        data = bytearray()
        for v in values:
            try:
                b = int(str(v).strip() or "0", 16)
            except ValueError:
                raise ProgramError(f"{v!r} is not a hex byte (00 to FF).", field="byte") from None
            if not 0 <= b <= 255:
                raise ProgramError(f"{v!r} is not a hex byte (00 to FF).", field="byte")
            data.append(b)
        self.write(address, bytes(data))

    def reset(self) -> None:
        """RESET ALL: every byte back to 0."""
        self.bytes[:] = bytes(self.size)

    # ---- instructions (MachineFault on a bad address) ----

    def _at(self, address: int, length: int = 1) -> int:
        if not 0 <= address <= self.size - length:
            raise MachineFault(
                FaultCode.INVALID_ADDRESS, f"Invalid data memory address: {address}", addr=address
            )
        return address

    def read_byte(self, address: int) -> int:
        return self.bytes[self._at(address)]

    def read_word(self, address: int) -> int:
        a = self._at(address, 2)
        return int.from_bytes(self.bytes[a : a + 2], "little", signed=True)

    def _store(self, address: int, data: bytes) -> None:
        a = self._at(address, len(data))
        self.bytes[a : a + len(data)] = data
        self.hits += [x for x in range(a, a + len(data)) if x in self.watch]

    def write_byte(self, address: int, value: int) -> None:
        self._store(address, bytes([value & 0xFF]))

    def write_word(self, address: int, value: int) -> None:
        self._store(address, (value & 0xFFFF).to_bytes(2, "little"))

    def read_cstring(self, address: int) -> str:
        """ASCII from `address` up to a 00 byte (or the end of memory)."""
        end = self.bytes.find(0, self._at(address))
        return self.bytes[address : end if end >= 0 else self.size].decode("latin-1")

    def write_cstring(self, address: int, text: str) -> None:
        self._store(address, text.encode("latin-1", "replace") + b"\0")
