"""
File: engine/yasmax_engine/config.py

Machine configuration: every number that defines "what kind of CPU this is".

Why this file exists
--------------------
Many facts about the original YASMIN CPU still have to be verified
(see docs/RESEARCH.md): word size, signedness, initial SP, register set
sizes. Instead of scattering guesses through the code, every such fact
lives here as ONE named field, tagged with its research ID. When a fact
is verified, you change one line here and the whole engine follows.

It also owns the arithmetic helpers that depend on word size (wrapping a
value to the register width, detecting overflow), because those are
properties of the machine, not of any single instruction.

How it connects
---------------
- registers.py uses `wrap()` on every register write.
- flags.py uses `wrap()`, `is_overflow()` and `is_negative()` to derive
  Z / N / OV from raw results.
- machine.py (later) creates one MachineConfig and passes it everywhere.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MachineConfig:
    """Immutable description of the simulated CPU.

    Frozen on purpose: the config never changes while a machine is
    running. To change register set size at runtime, the machine builds
    a new config with `dataclasses.replace()`.
    """

    # TODO(R-1): verify width and signedness of registers and memory words.
    word_bits: int = 32
    signed: bool = True

    # Number of general purpose registers shown by default.
    # The screenshot shows "Select Register Set Size: 32".
    gpr_count: int = 32
    # TODO(R-12): verify which sizes the dropdown actually offers.
    gpr_set_sizes: tuple[int, ...] = (8, 16, 32)

    # TODO(R-3): the screenshot shows SP = 8096 with nothing loaded.
    # Verify why, and whether the stack grows down or up.
    initial_sp: int = 8096
    stack_grows_down: bool = True

    # ------------------------------------------------------------------
    # Derived values and helpers
    # ------------------------------------------------------------------

    @property
    def mask(self) -> int:
        """All-ones bit mask for one word, e.g. 0xFFFFFFFF for 32 bits."""
        return (1 << self.word_bits) - 1

    @property
    def min_value(self) -> int:
        """Smallest value a register can hold."""
        return -(1 << (self.word_bits - 1)) if self.signed else 0

    @property
    def max_value(self) -> int:
        """Largest value a register can hold."""
        if self.signed:
            return (1 << (self.word_bits - 1)) - 1
        return self.mask

    def wrap(self, value: int) -> int:
        """Fit any Python int into one machine word.

        Python ints never overflow, but real registers do. This keeps
        only the low `word_bits` bits and, for a signed machine,
        reinterprets them as two's complement.

        Example (8-bit signed): wrap(130) -> -126, wrap(-1) -> -1.
        """
        raw = value & self.mask
        if self.signed and raw >= (1 << (self.word_bits - 1)):
            raw -= 1 << self.word_bits
        return raw

    def is_overflow(self, value: int) -> bool:
        """True if `value` does not fit in a word without wrapping.

        Instructions compute their result as a plain Python int first,
        then ask this before wrapping, so the OV flag can be set.
        """
        return not (self.min_value <= value <= self.max_value)

    def is_negative(self, value: int) -> bool:
        """True if the (already wrapped) value has its sign bit set."""
        if self.signed:
            return value < 0
        return bool(value & (1 << (self.word_bits - 1)))

    def validate(self) -> None:
        """Raise ValueError if the configuration makes no sense.

        Called once when a machine is built, so a typo in a config
        fails loudly at startup instead of mid-simulation.
        """
        if self.word_bits < 2:
            raise ValueError("word_bits must be at least 2")
        if self.gpr_count not in self.gpr_set_sizes:
            raise ValueError(
                f"gpr_count {self.gpr_count} is not one of gpr_set_sizes {self.gpr_set_sizes}"
            )
        if not self.min_value <= self.initial_sp <= self.max_value:
            raise ValueError("initial_sp does not fit in a word")


# The configuration used unless a caller asks for something else.
DEFAULT_CONFIG = MachineConfig()
