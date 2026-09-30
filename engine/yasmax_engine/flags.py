"""
File: engine/yasmax_engine/flags.py

The status flags shown in the SPECIAL CPU REGISTERS panel:
OV (overflow), Z (zero) and N (negative).

What is decided here, and what is not
-------------------------------------
This file knows HOW each flag is computed from an arithmetic result,
which is standard two's-complement logic:

    Z  = result is zero
    N  = result's sign bit is set
    OV = true result did not fit in a word (and had to wrap)

It does NOT know WHICH instructions set WHICH flags. That is research
item R-8b and belongs to the instruction table (isa/spec.py, later).
So `update()` only touches the flags you pass. An instruction that only
sets Z can say `flags.update(z=True)` and leave N and OV alone.

How it connects
---------------
- Instruction handlers call `evaluate(raw_result, config)` to get the
  wrapped value and the three flag values, then `update()` the ones
  they are allowed to change.
- The snapshot (later) reads `as_dict()` for the UI checkboxes.
"""

from __future__ import annotations

from dataclasses import dataclass

from .config import MachineConfig


@dataclass
class FlagResult:
    """What an arithmetic result means for the flags.

    `value` is the result wrapped to one word, ready to store in a register.
    """

    value: int
    z: bool
    n: bool
    ov: bool


def evaluate(raw: int, config: MachineConfig) -> FlagResult:
    """Wrap a raw result and compute Z, N and OV for it.

    `raw` is the mathematically exact result as a Python int. For
    example, ADD computes `a + b` without any limits and passes it here.
    """
    ov = config.is_overflow(raw)
    value = config.wrap(raw)
    return FlagResult(value=value, z=(value == 0), n=config.is_negative(value), ov=ov)


@dataclass
class StatusFlags:
    """The three flag bits as the CPU holds them."""

    ov: bool = False
    z: bool = False
    n: bool = False

    def clear(self) -> None:
        """Set every flag to false (used on reset)."""
        self.ov = self.z = self.n = False

    def update(
        self,
        *,
        ov: bool | None = None,
        z: bool | None = None,
        n: bool | None = None,
    ) -> None:
        """Change only the flags that are given. `None` means "leave it alone".

        Keyword-only (the `*`) so a call always says which flag it means:
        `update(z=True)` can never be confused with `update(True)`.
        """
        if ov is not None:
            self.ov = ov
        if z is not None:
            self.z = z
        if n is not None:
            self.n = n

    def apply(self, result: FlagResult, *, ov: bool = True, z: bool = True, n: bool = True) -> None:
        """Copy flags from an evaluated result.

        The booleans choose which flags this instruction may change, e.g.
        `apply(res, ov=False)` for an instruction that never touches OV.
        """
        self.update(
            ov=result.ov if ov else None,
            z=result.z if z else None,
            n=result.n if n else None,
        )

    def as_dict(self) -> dict[str, bool]:
        """JSON-safe form for the snapshot, with the UI's upper-case names."""
        return {"OV": self.ov, "Z": self.z, "N": self.n}

    def as_sr_bits(self) -> int:
        """Pack the flags into an integer.

        YASMIN 7.5.50 showed SR = 1 with only Z set, so Z is bit 0.
        TODO(R-4): N = bit 1 and OV = bit 2 are guesses.
        """
        return (int(self.ov) << 2) | (int(self.n) << 1) | int(self.z)
