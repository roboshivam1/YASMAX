# YASMAX — Yet Another Simple Machine Architecture eXplorer

A browser-based, cross-platform recreation of the **CPU Simulator** window of the YASMIN CPU-OS Simulator, built so students on macOS and Linux can do their Computer Organization & Architecture lab work with a tool that looks and behaves like the one used in their labs.

The simulation engine is written in Python and runs locally in your browser through Pyodide (Python compiled to WebAssembly). There is no server, and after the first load it works offline.

## Credit and intended use

YASMAX is an independent, non-commercial educational project. It is **inspired by and modelled on** the **YASMIN CPU-OS Simulator** by **Besim Mustafa, Edge Hill University**. All credit for the original design, instruction set and teaching approach goes to him.

- YASMAX is **not affiliated with or endorsed by** the original author or Edge Hill University.
- It is for **educational use only**, mainly for students who cannot run the Windows-only original.
- **No commercial use.** See `LICENSE` (to be decided; see `docs/PRD.md` §9).
- If you can run the original YASMIN, use it. YASMAX exists for everyone who can't.

## Scope

v1 recreates the **CPU Simulator window only**. The OS simulator, compiler, virtual OS, interrupts and I/O windows are out of scope. Their buttons are still drawn so the layout matches, and they show a "not available in YASMAX" notice when clicked.

## Docs

| Doc | What it covers |
|---|---|
| [`docs/PRD.md`](docs/PRD.md) | Problem, users, requirements, non-goals, milestones |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Modules, how the engine, worker and UI connect, state model |
| [`docs/TECH_STACK.md`](docs/TECH_STACK.md) | Chosen tools and why |
| [`docs/APP_FLOW.md`](docs/APP_FLOW.md) | What the user does, screen by screen, and what the system does in response |
| [`docs/UI_SPEC.md`](docs/UI_SPEC.md) | Panel-by-panel inventory of the original window |
| [`docs/RESEARCH.md`](docs/RESEARCH.md) | Behaviour of the original we must verify before implementing |

## Running locally

From the repo root:

```bash
python3 tools/build_engine.py
python3 tools/serve.py
```

Then open http://localhost:8000. Use `tools/serve.py`, not `python3 -m http.server`:
it switches browser caching off, so after you paste new code a normal reload
always runs the new files. (A cached old `worker.js` once left the instruction
dialog empty.) If something still looks stale, reload with Shift + Reload.

## Guesses to check in the lab

YASMAX follows the original wherever it is known: the ISA document, the lab
tutorials, lab screenshots of YASMIN 7.5.50 and a saved `.sas` file. Where
nothing was known, it makes a best guess. Every guess is listed here and marked
`TODO(research)` in the code. Details and sources: `docs/RESEARCH.md`.

| Area | What YASMAX does now | Evidence so far |
|---|---|---|
| OUT with a literal or register (`OUT #42, 0`) | 2nd operand 0 prints the number, 1 prints the character (`*`) | Tutorial: "OUT 16, 0 outputs the data in location 16 to the console; the second parameter must always be 0" |
| OUT with a memory address (`OUT 24, 0`) | prints the value stored there: a string (`03` tag) up to `00`, an integer (`02` tag) or a boolean | Tutorial + data memory screenshots |
| IN | a register gets the next typed character code (0 if none); a memory address gets the typed line; nothing waits | only "get input data (if available)" is documented |
| SR number | Z = 1 (lab), N = 2, OV = 4 (guess) | lab: SR 1 with only Z |
| T column | Arithmetic 1, Control 2, Comparison 3, I/O 4, label -1 (lab); Data Transfer 0, Logical 5, Misc 6 (guess) | lab |
| MSF / CAL / RET | MSF pushes the previous frame (-1 if none) and an empty slot; CAL writes the return address there and jumps; RET jumps back and removes the frame | tutorial: "MSF reserves a space for the return address, CAL saves the return address in the reserved space"; lab: MSF pushed -1 and 0 |
| LOOP | subtract 1 from the register, jump while it is still > 0 | ISA: "loops until the value in the register is 0" |
| SUBU | absolute difference | only "unsigned result" is documented |
| Registers | 16-bit signed, wrap around, OV set on overflow | ISA: "a word is 16 bits" |
| Stack | at most 256 entries; POP on empty: "Stack overflow" (tutorial 1; tutorial 2 says "Stack underflow") | tutorials |
| After the last instruction | PC stays on it; STEP again shows an "End of program" message | lab: PC stays |
| HLT message | title "CPU runtime", text "CPU halted (HLT)." | lab: a "CPU runtime" box appears; exact text unknown |
| By single tick | 3 ticks per instruction: FETCH, DECODE, EXECUTE | Execution Unit tab |
| Execution Unit operand boxes | fill in on EXECUTE | lab: empty after DECODE |
| Memory view checkbox | a breakpoint: RUN stops before that instruction | saved as `#TRUE#`/`#FALSE#` in `.sas` |
| Boolean in Initialise Data | `01` then `00`/`01` | string and integer layouts are from the lab |
| New program | data byte 0 = `02`, MAR 2, MDR 0 | copied from lab screenshots, reason unknown |
| `.sas` header | unknown fields written as seen in a lab file; LOAD ignores them | one lab file |
| Endianness (New CPU tab) | shown only; words are always little-endian | lab: integer 25 stored as `19 00` |
| Exec. Clocks, read/write cycles | shown in the dialog, not used | unknown |
| Labels | `Name:` rows; jumps use `$Name` (`JNE $L0`), typed in the Value box with Direct Mem | lab + tutorial 2 |
