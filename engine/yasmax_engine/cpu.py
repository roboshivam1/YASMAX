"""
File: engine/yasmax_engine/cpu.py

Running programs: the ExecutionCommands mixin of Machine.

An instruction goes through three phases, the buttons of the Execution
Unit tab: FETCH (IR = MDR = the instruction, MAR = its PAdd), DECODE
(Op Code) and EXECUTE (the handler runs, operands shown, PC moves on).
    step()     all remaining phases ("by instruction")
    tick()     one phase ("by single tick"). TODO(R-6): real tick count
    fetch() / decode() / execute()   the Execution Unit buttons

Lab facts (YASMIN 7.5.50): PC is the LOGICAL address in the current
program (BR = its base). After the last instruction PC stays on it.
HLT: PC stays, a "CPU runtime" message appears, every time you STEP.
RESET PROGRAM empties the stack and puts PC back on the top instruction.
Double-clicking an instruction executes that instruction (tutorial).
"""

from __future__ import annotations

from enum import StrEnum

from .access import Access
from .errors import FaultCode, MachineFault, ProgramError
from .handlers import HALT, HANDLERS
from .program import Program


class RunState(StrEnum):
    """The run state machine from docs/APP_FLOW.md §8 (ENDED: PC is on the
    last instruction and it has been executed)."""

    EMPTY = "empty"
    IDLE = "idle"
    RUNNING = "running"
    HALTED = "halted"
    ENDED = "ended"
    FAULT = "fault"


class ExecutionCommands:
    """Needs: programs, special, gpr, flags, stack, current, phase,
    exec_unit, run_state, input_queue and emit() from Machine."""

    # ---- which program and instruction ----

    def _current_program(self) -> Program:
        if not self.programs.programs:
            raise ProgramError("There are no instructions in memory.")
        names = [p.name for p in self.programs.programs]
        if self.current not in names:
            self.current = names[0]
            self.special.BR = self.programs.get(self.current).base
        return self.programs.get(self.current)

    def _locate(self):
        p = self._current_program()
        found = p.instruction_at(self.special.PC)
        if found is None:
            raise MachineFault(
                FaultCode.NO_INSTRUCTION, f"There is no instruction at address {self.special.PC}."
            )
        return p, found[0], found[1]

    def _clear_exec_unit(self) -> None:
        self.phase = None
        self.exec_unit = {"instruction": "", "opcode": "", "operands": []}

    # ---- the three phases ----

    def fetch(self) -> None:
        if self.run_state == RunState.ENDED:
            self.emit("end", message="End of program. Use RESET PROGRAM to run it again.")
            return
        p, _index, ins = self._locate()
        self.special.IR = self.special.MDR = str(ins)
        self.special.MAR = p.base + self.special.PC
        self.exec_unit = {"instruction": str(ins), "opcode": "", "operands": []}
        self.phase = "fetched"

    def decode(self) -> None:
        if self.phase != "fetched":
            raise ProgramError("FETCH the instruction first.")
        _p, _i, ins = self._locate()
        self.exec_unit["opcode"] = ins.spec.mnemonic
        self.phase = "decoded"

    def execute(self) -> None:
        if self.phase != "decoded":
            raise ProgramError("DECODE the instruction first.")
        p, _index, ins = self._locate()
        here = self.special.PC
        x = Access(self, p, ins, here)
        self.exec_unit["operands"] = [
            {"text": str(o), "value": x.shown_value(o), "mode": int(o.mode)} for o in ins.operands
        ]
        self.gpr.begin_step()
        p.data.hits.clear()
        self.phase = None
        try:
            result = HANDLERS[ins.spec.mnemonic](x)
        except MachineFault:
            self.run_state = RunState.FAULT
            raise
        finally:
            self.special.SR = self.flags.as_sr_bits()
            self.special.SP = self.stack.sp
        if result == HALT:
            self.run_state = RunState.HALTED
            self.emit("halt", message="CPU halted (HLT).")
            return
        target = x.next if result is None else result
        if result is None and p.instruction_at(target) is None:
            self.run_state = RunState.ENDED  # last instruction: PC stays on it
        else:
            self.special.PC = self.config.wrap(target)
            self.run_state = RunState.IDLE
        if p.data.hits:
            self.emit("watch", message=f"Data memory address {p.data.hits[0]} was modified.")

    # ---- the buttons ----

    def step(self, stop_at_breakpoint: bool = False) -> None:
        """STEP by instruction (and each RUN step). With stop_at_breakpoint,
        a ticked instruction is not executed; a "breakpoint" event says why."""
        if self.phase is None and stop_at_breakpoint:
            p, _i, ins = self._locate()
            if p.is_breakpoint(ins):
                self.emit("breakpoint", message=f"Breakpoint at {ins}.")
                return
        if self.phase is None:
            self.fetch()
            if self.phase is None:
                return
        if self.phase == "fetched":
            self.decode()
        self.execute()

    def tick(self) -> None:
        """STEP by single tick: one phase."""
        {None: self.fetch, "fetched": self.decode, "decoded": self.execute}[self.phase]()

    def reset_program(self) -> None:
        """RESET PROGRAM."""
        self.stack.reset()
        self.special.SP = self.stack.sp
        self.special.PC = 0
        self._clear_exec_unit()
        self.run_state = RunState.IDLE if self.programs.programs else RunState.EMPTY

    def execute_at(self, program: str, index: int) -> None:
        """Double-click in the memory view: execute that instruction."""
        p = self.programs.get(program)
        ladd = p.ladd_of(index)
        self.current, self.special.BR, self.special.PC = p.name, p.base, ladd
        self._clear_exec_unit()
        self.run_state = RunState.IDLE
        self.step()

    def set_breakpoint(self, program: str, index: int, on: bool) -> None:
        """The checkbox of a memory view row."""
        self.programs.get(program).set_breakpoint(index, bool(on))

    def console_input(self, text: str) -> None:
        """A line typed into the console's INPUT box (read by IN)."""
        self.input_queue.append(str(text))

    def set_data_watch(self, program: str, addresses: list) -> None:
        """Debug control checkboxes: suspend when code modifies these bytes."""
        self.programs.get(program).data.watch = {int(a) for a in addresses}
