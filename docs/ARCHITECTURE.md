# YASMAX — Architecture

Status: Draft v0.1 · Last updated: 2026-09-29

## 1. Big picture

YASMAX has three layers. They talk only through a message protocol, so any one of them can change without touching the others.

```
┌──────────────────────────── Browser tab ────────────────────────────┐
│                                                                     │
│  MAIN THREAD                              WEB WORKER                │
│  ┌──────────────────────────┐            ┌───────────────────────┐  │
│  │ UI (HTML/CSS/vanilla JS) │            │ Pyodide (Python/WASM) │  │
│  │                          │  commands  │                       │  │
│  │  panels/*.js  ──────────►│ bridge.js ─┼──► worker.js          │  │
│  │  (render only)           │            │       │               │  │
│  │                          │◄───────────┼── state snapshots     │  │
│  │  store.js (last state)   │  + events  │       ▼               │  │
│  └──────────────────────────┘            │  yasmax_engine (pure  │  │
│                                          │  Python package)      │  │
│                                          └───────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

1. **Engine (`engine/yasmax_engine/`).** A pure Python package that holds the CPU. It knows nothing about browsers, Pyodide or the UI. It runs and is tested with plain CPython and pytest on your laptop.
2. **Worker (`web/worker.js`).** It loads Pyodide and the engine inside a Web Worker, receives commands, calls the engine, and posts state back. Keeping Python off the main thread means RUN never freezes the window.
3. **UI (`web/`).** Static HTML, CSS and vanilla JS that replicate the YASMIN window. Panels **only render state and send commands**. They never compute CPU behaviour.

**Rule:** all CPU logic lives in the engine. If a panel needs something computed, such as "which instruction is current?", the engine puts it in the snapshot.

## 2. Repository layout

```
yasmax/
├── README.md
├── LICENSE
├── docs/                     PRD, ARCHITECTURE, TECH_STACK, APP_FLOW, UI_SPEC, RESEARCH
├── engine/
│   ├── pyproject.toml
│   ├── yasmax_engine/
│   │   ├── __init__.py       public API: Machine
│   │   ├── machine.py        Machine: owns everything below, exposes commands
│   │   ├── registers.py      GP register file + special registers
│   │   ├── flags.py          status flags (OV, Z, N) and how ops set them
│   │   ├── memory.py         RAM model, pages, base/logical/physical addressing
│   │   ├── stack.py          program stack (push/pop/overflow rules)
│   │   ├── isa/
│   │   │   ├── spec.py       instruction table: mnemonic → operand kinds, handler
│   │   │   ├── operands.py   operand types (register, immediate, address, indirect…)
│   │   │   └── handlers.py   one function per instruction
│   │   ├── program.py        Program model (name, base, pages, instruction list)
│   │   ├── cycle.py          fetch → decode → execute, instruction and clock stepping
│   │   ├── snapshot.py       Machine → plain dict for the UI
│   │   ├── fileformat.py     save/load YASMAX files (+ YASMIN import later)
│   │   └── errors.py         runtime faults, mirroring YASMIN's behaviour
│   └── tests/
│       ├── unit/             per-instruction and per-module tests
│       └── golden/           traces recorded from the original YASMIN (see §7)
├── web/
│   ├── index.html            the window
│   ├── css/                  win7.css (chrome and controls), yasmin.css (layout and colours)
│   ├── js/
│   │   ├── main.js           boot: start worker, show loading, mount panels
│   │   ├── bridge.js         promise-based wrapper over postMessage
│   │   ├── worker.js         Pyodide host
│   │   ├── store.js          latest snapshot + subscribe()
│   │   ├── panels/           one file per panel (see UI_SPEC)
│   │   └── dialogs/          instruction editor, not-available, about, file dialogs
│   ├── engine.zip            built from engine/ by tools/build_engine.py
│   └── sw.js                 service worker for offline use
└── tools/
    ├── build_engine.py       zip engine/yasmax_engine into web/engine.zip
    └── trace_tool.py         helpers for recording and diffing golden traces
```

## 3. The engine

### 3.1 Machine: the only public object

`Machine` owns the registers, flags, memory, stack and program list. The UI's whole vocabulary is its command methods:

| Group | Commands |
|---|---|
| Programs | `create_program(name, pages, base)`, `remove_program(name)`, `remove_all()`, `select_program(name)` |
| Instructions | `add_instruction(prog, instr)`, `insert_instruction(prog, index, instr)`, `edit_instruction(...)`, `delete_instruction(...)` |
| Execution | `step(mode="instruction" or "clock")`, `run_batch(n)`, `stop()`, `reset_program()` |
| Registers | `set_register(name, value)`, `reset_all_registers()`, `set_register_set_size(n)` |
| Files | `save_program(name) → str`, `load_program(text, base=None)` |
| State | `snapshot(full=False) → dict` |

Every command returns `{ ok, snapshot, events }`. Events are things like `halted`, `fault`, or `reg_read: R03`. The UI never asks follow-up questions, because each reply carries everything it needs.

### 3.2 The instruction set is table-driven

`isa/spec.py` is a single table. Each row has a mnemonic, allowed operand patterns, a handler, which flags it touches, and a clock-cycle cost. The instruction editor dialog reads the same table (via the snapshot's `isa` section), so the dialog and the executor can never disagree.

Adding an instruction = one table row + one handler + tests.

### 3.3 Execution cycle

`cycle.py` models the fetch → decode → execute cycle explicitly, because the UI shows its internals (IR, MAR, MDR) and lab exercises ask about them.

- **By instruction:** run the whole cycle, then snapshot.
- **By clock:** advance one micro-step (fetch: PC→MAR, MEM→MDR, MDR→IR, PC++; then decode; then execute micro-steps) and snapshot after each. The exact micro-step sequence YASMIN shows is research item R-6.

### 3.4 Numbers and addressing

- Word size, signedness, overflow wrap and the meaning of **PAdd vs LAdd** and **BR** must match YASMIN (research R-1 to R-4). They live in one place, `memory.py` and `registers.py`, as named constants.
- Values in the engine are plain Python `int`s, masked to the word size at every write.

## 4. Worker ↔ UI protocol

Messages are plain JSON objects.

**UI → worker**
```json
{ "id": 42, "cmd": "step", "args": { "mode": "instruction" } }
```

**Worker → UI**
```json
{ "id": 42, "ok": true, "snapshot": { ... }, "events": [ ... ] }
{ "id": null, "type": "run_tick", "snapshot": { ... }, "events": [ ... ] }
```

- `bridge.js` turns this into `await engine.step({mode: "instruction"})`.
- Unsolicited messages (`id: null`) are sent during RUN.

### 4.1 How RUN and STOP work

A Python loop inside the worker would block the worker, and STOP messages would never be read. So RUN is **chunked**:

1. The UI sends `run {speed}`.
2. The worker executes `run_batch(n)`, where `n` depends on the slider (Slow: 1 instruction with a long delay; Fast: many instructions with no delay).
3. It posts a `run_tick` snapshot, then schedules the next batch with `setTimeout(delay)`.
4. A `stop` command, or a `halted` or `fault` event, clears the schedule.

This avoids `SharedArrayBuffer`, which needs COOP/COEP headers that GitHub Pages can't set.

## 5. State snapshot (the contract)

A snapshot is the single source of truth the UI renders. Shape (v0, it will grow):

```json
{
  "special": { "PC": 0, "SP": 8096, "SR": 0, "BR": 0, "IR": "", "MAR": 0, "MDR": "" },
  "flags":   { "OV": false, "Z": false, "N": false },
  "gpr":     [ { "name": "R00", "val": 0, "c": "", "access": null }, ... ],
  "memory":  [ { "padd": 0, "ladd": 0, "text": "MOV #5, R01", "base": 0, "current": true }, ... ],
  "stack":   [ { "pos": 0, "val": 0, "addr": 0 }, ... ],
  "programs":[ { "name": "P1", "base": 0, "start": 0, "type": "..." } ],
  "run":     { "state": "idle|running|halted|fault", "cycle_phase": "fetch|decode|execute|null" },
  "isa":     { ... }
}
```

- `isa` is sent once, at boot, for the instruction editor dialog.
- `full=false` snapshots can omit unchanged sections later, as a performance tweak. Start with full snapshots every time, since it's simpler and fast enough at this scale.

## 6. UI structure

- **`index.html`** holds the static skeleton of the whole window. The layout is fixed-size, laid out with CSS grid to mirror the original's regions (see `UI_SPEC.md`).
- **One JS module per panel** (`memoryView.js`, `specialRegs.js`, `gpRegs.js`, `stackView.js`, `programList.js`, `programTab.js`, `instructionsTab.js`, `programControl.js`, `cachePipeline.js`, `advanced.js`, `regTabs.js`). Each exports `mount(el, store, engine)`.
- **`store.js`** holds the latest snapshot. Panels subscribe and re-render their own region. There is no framework and no virtual DOM. Tables update cells in place so scroll position and focus survive.
- **Scaling:** the window is a fixed-size element scaled with `transform: scale()` to fit the viewport. The layout never reflows, which keeps it identical to the original.

## 7. Testing strategy

| Layer | Tests |
|---|---|
| Engine units | pytest per instruction: operands, result, flags, edge cases (overflow, zero, negative) |
| **Golden traces** | Record programs on the original YASMIN, and after each STEP record PC, SP, SR, flags, GPRs and stack into a JSON file. `tests/golden/test_traces.py` replays each program in YASMAX and diffs step by step. **This is how "exactly like YASMIN" gets proven.** |
| Bridge/worker | A small Playwright smoke test later: boot, add an instruction, step, check a register cell |
| Visual | Side-by-side screenshot comparison against a reference screenshot of the original (manual at first) |

Golden trace format:
```json
{
  "program": { "name": "T1", "base": 0, "instructions": ["MOV #5, R01", "ADD #3, R01", "HLT"] },
  "steps": [
    { "PC": 1, "flags": {"OV":0,"Z":0,"N":0}, "gpr": {"R01": 5}, "stack": [] },
    ...
  ],
  "recorded_with": "YASMIN 7.2.27"
}
```

## 8. Build and deploy

- `tools/build_engine.py` zips `engine/yasmax_engine` into `web/engine.zip`. The worker fetches it and unpacks it into Pyodide's virtual filesystem.
- `web/` is a static site. Deploy it to GitHub Pages.
- `sw.js` caches `index.html`, CSS, JS, `engine.zip` and the Pyodide runtime files for offline use.

## 9. Key decisions log

| # | Decision | Why |
|---|---|---|
| D-1 | Pyodide directly rather than PyScript | Our UI is hand-written JS and our Python runs in a worker behind a message protocol. PyScript's main benefit is putting Python *in* the HTML, which we don't need, and it adds a layer to learn and debug. |
| D-2 | Engine in a Web Worker | RUN must never freeze the UI, and STOP must always work |
| D-3 | Vanilla JS, no framework | The UI is a fixed replica, not a dynamic app. Less to learn, nothing to build, easy to match the original pixel by pixel. |
| D-4 | Chunked RUN instead of SharedArrayBuffer | Works on GitHub Pages without special headers |
| D-5 | Table-driven ISA | One source for the executor, the editor dialog and the docs |
| D-6 | Golden traces as the fidelity bar | "Looks similar" isn't testable; step-by-step state equality is |
