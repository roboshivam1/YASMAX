"""
File: engine/yasmax_engine/handlers.py

What each instruction DOES. HANDLERS maps a mnemonic to a function that
takes an Access (access.py) and returns the jump target (new PC), None to
go on to the next instruction, or HALT.

Behaviour sources: the ISA document, the tutorial and lab tests.
    Two-operand arithmetic/logic: destination = destination OP source.
    CMP a, b: flags from b - a. Z if equal, N if b < a (tutorial), so
      JLT jumps when N, JGT when neither Z nor N.
    DIV by zero: nothing happens (lab test).
    HLT: PC stays on HLT, a "CPU runtime" message appears (lab test).
TODO(research): SUBU (here |b - a|), LOOP (here: decrement, jump while
> 0), OUT's second operand (here 0 = value / string, 1 = character) and
IN (here: next typed character, or the typed line into memory).
"""

from __future__ import annotations

from .datamem import TAG_BOOL, TAG_INT, TAG_STR
from .errors import FaultCode, MachineFault
from .flags import evaluate
from .isa import AM

HALT = "halt"


def _flags(x, raw, ov=True):
    res = evaluate(raw, x.cfg)
    x.m.flags.apply(res, ov=ov)
    if not ov:
        x.m.flags.update(ov=False)
    return res.value


def _alu(fn, ov=True):
    """dst = fn(dst, src) for (R,R) and (#n,R); fn may return None (no-op)."""

    def run(x):
        src, dst = x.ins.operands
        raw = fn(x.get_reg(dst), x.read_value(src), x.cfg)
        if raw is not None:
            x.set_reg(dst, _flags(x, raw, ov))

    return run


def _shift(left):
    """SHL 2, R10: the memory-direct operand is used as a plain count (ISA doc)."""

    def run(x):
        src, dst = x.ins.operands
        b = x.get_reg(dst)
        raw = b << src.value if left else (b & x.cfg.mask) >> src.value
        x.set_reg(dst, _flags(x, raw, ov=False))

    return run


def _div(b, a, cfg):
    return None if a == 0 else (abs(b) // abs(a)) * (1 if (a < 0) == (b < 0) else -1)


def _unary(delta):
    def run(x):
        (r,) = x.ins.operands
        x.set_reg(r, _flags(x, x.get_reg(r) + delta))

    return run


def _mov(x):
    src, dst = x.ins.operands
    x.set_reg(dst, _flags(x, x.read_value(src), ov=False))


def _cmp(x):
    src, dst = x.ins.operands
    _flags(x, x.get_reg(dst) - x.read_value(src))


def _load(width, bump=0):
    def run(x):
        src, dst = x.ins.operands
        addr = x.address_of(src)
        v = x.data.read_byte(addr) if width == 1 else x.data.read_word(addr)
        x.set_reg(dst, _flags(x, v, ov=False))
        x.bump_pointer(src, bump)

    return run


def _store(width, bump=0):
    def run(x):
        src, dst = x.ins.operands
        v = x.read_value(src)
        addr = x.address_of(dst)
        (x.data.write_byte if width == 1 else x.data.write_word)(addr, v)
        x.bump_pointer(dst, bump)

    return run


def _tas(x):
    src, dst = x.ins.operands
    addr = x.address_of(src)
    x.set_reg(dst, _flags(x, x.data.read_byte(addr), ov=False))
    x.data.write_byte(addr, 1)


def _swp(x):
    a, b = x.ins.operands
    va, vb = x.get_reg(a), x.get_reg(b)
    x.set_reg(a, vb)
    x.set_reg(b, va)


def _pop(x):
    (r,) = x.ins.operands
    x.set_reg(r, _flags(x, x.m.stack.pop(), ov=False))


def _mvs(x):
    src, dst = x.ins.operands
    x.data.write_cstring(x.address_of(dst), x.data.read_cstring(x.address_of(src)))


def _cps(x):
    src, dst = x.ins.operands
    a, b = x.data.read_cstring(x.address_of(src)), x.data.read_cstring(x.address_of(dst))
    x.m.flags.update(z=a == b, n=b < a, ov=False)


def _jump(cond):
    def run(x):
        if cond(x.m.flags):
            return x.jump_target(x.ins.operands[0])
        return None

    return run


def _cal(x):
    target = x.jump_target(x.ins.operands[0])
    x.m.stack.call(x.next, x.here)
    return target


def _loop(x):
    target_op, r = x.ins.operands
    left = x.set_reg(r, x.get_reg(r) - 1)
    return x.jump_target(target_op) if left > 0 else None


def _typed_text(data, addr):
    """Text OUT shows for a data memory address (tagged values)."""
    tag = data.read_byte(addr)
    if tag == TAG_STR:
        return data.read_cstring(addr + 1)
    if tag == TAG_INT:
        return str(data.read_word(addr + 2))
    if tag == TAG_BOOL:
        return "True" if data.read_byte(addr + 1) else "False"
    return data.read_cstring(addr)


def _out(x):
    src, port = x.ins.operands
    as_char = port.value == 1
    if src.mode in (AM.IMM, AM.REG):
        v = x.read_value(src)
        text = chr(v & 0xFF) if as_char else str(v)
    else:
        addr = x.address_of(src)
        text = chr(x.data.read_byte(addr)) if as_char else _typed_text(x.data, addr)
    x.m.emit("output", text=text)


def _in(x):
    _port, dst = x.ins.operands
    line = x.m.input_queue.pop(0) if x.m.input_queue else ""
    if dst.mode == AM.REG:
        x.set_reg(dst, ord(line[0]) if line else 0)
        if len(line) > 1:
            x.m.input_queue.insert(0, line[1:])
    else:
        x.data.write_cstring(x.address_of(dst), line)


def _not_here(x):
    raise MachineFault(
        FaultCode.NOT_AVAILABLE,
        f"{x.ins.spec.mnemonic} needs the OS simulator, which is not part of YASMAX.",
    )


def _push(x):
    x.m.stack.push(x.read_value(x.ins.operands[0]), x.here)


HANDLERS = {
    "MOV": _mov,
    "MVS": _mvs,
    "LDB": _load(1),
    "LDW": _load(2),
    "LDBI": _load(1, 1),
    "LDWI": _load(2, 2),
    "TAS": _tas,
    "STB": _store(1),
    "STW": _store(2),
    "STBI": _store(1, 1),
    "STWI": _store(2, 2),
    "PSH": _push,
    "POP": _pop,
    "SWP": _swp,
    "ADD": _alu(lambda b, a, c: b + a),
    "SUB": _alu(lambda b, a, c: b - a),
    "SUBU": _alu(lambda b, a, c: abs(b - a)),
    "MUL": _alu(lambda b, a, c: b * a),
    "DIV": _alu(_div),
    "INC": _unary(1),
    "DEC": _unary(-1),
    "AND": _alu(lambda b, a, c: b & a, ov=False),
    "OR": _alu(lambda b, a, c: b | a, ov=False),
    "NOT": _alu(lambda b, a, c: ~a, ov=False),
    "SHL": _shift(True),
    "SHR": _shift(False),
    "JMP": _jump(lambda f: True),
    "JEQ": _jump(lambda f: f.z),
    "JNE": _jump(lambda f: not f.z),
    "JGT": _jump(lambda f: not f.z and not f.n),
    "JGE": _jump(lambda f: not f.n),
    "JLT": _jump(lambda f: f.n),
    "JLE": _jump(lambda f: f.z or f.n),
    "JNZ": _jump(lambda f: not f.z),
    "JZR": _jump(lambda f: f.z),
    "CAL": _cal,
    "LOOP": _loop,
    "MSF": lambda x: x.m.stack.mark_frame(x.here),
    "RET": lambda x: x.m.stack.ret(),
    "IRET": _not_here,
    "SWI": _not_here,
    "HLT": lambda x: HALT,
    "CMP": _cmp,
    "CPS": _cps,
    "IN": _in,
    "OUT": _out,
    "NOP": lambda x: None,
}
