# YASMAX — Yet Another Simple Machine Architecture eXplorer

**Open it: <https://roboshivam1.github.io/YASMAX/> or <https://yasmax.shvmkpr.in>**. Nothing to install, and it
works offline once installed as an app.

YASMAX is a browser recreation of the **CPU Simulator** window of the
**YASMIN CPU-OS Simulator** (7.5.50, the version used in our labs), for students on
**macOS, Linux and Chromebooks** who cannot run the Windows-only original. Same
window, same instructions, same `.sas` program files, so you can practise at home
and carry on in the lab.

The simulator engine is written in Python and runs inside your browser through
Pyodide (Python compiled to WebAssembly). Nothing is sent anywhere: there is no
server, no account and no tracking.

> **For practice, not a replacement.** YASMAX is checked against the lab version,
> but some behaviour is still a best guess (listed below). If YASMIN and YASMAX ever
> disagree, YASMIN is right. Please [report it](https://github.com/roboshivam1/YASMAX/issues/new/choose).

## Get started

| How | Steps | Offline? |
|---|---|---|
| **In the browser** | Open the link above. | after the first visit, yes |
| **As an app** (recommended) | Chrome / Edge: the install icon in the address bar. Safari (macOS 14+): File > Add to Dock. | yes |
| **Offline download** | Download `yasmax-offline-<version>.zip` from [Releases](https://github.com/roboshivam1/YASMAX/releases), unzip, run `start-mac.command` / `start-linux.sh` / `start-windows.bat`. Needs Python 3. | yes |

New to the simulator? Read the **[User Guide](docs/USER_GUIDE.md)**. It has a five-minute first program.

## Credit and intended use

YASMAX is an independent, non-commercial educational project, **modelled on the
YASMIN CPU-OS Simulator by Besim Mustafa, Edge Hill University** ([teach-sim.com](https://teach-sim.com/)).
All credit for the original design, instruction set and teaching approach goes to him.

- **Not affiliated with or endorsed by** the original author or Edge Hill University.
- **Educational use only. No commercial use.** YASMAX's own code is under the
  [PolyForm Noncommercial License 1.0.0](LICENSE).
- If you can run the original YASMIN, use it. YASMAX exists for everyone who can't.

Assembled with ♥ by **Shivam Kapoor** · [shvmkpr.in](https://shvmkpr.in)

## What is included

The complete CPU Simulator window: instruction memory view (PC arrow, breakpoints,
labels), program list, special and general registers, program stack, the instruction
dialog with every documented instruction, STEP / RUN / STOP / RESET PROGRAM, by-tick
stepping and the Execution Unit tab, program data memory, the console, and SAVE /
LOAD of YASMIN `.sas` files.

**Not included:** the OS simulator, compiler, virtual OS, interrupts, pipeline and
cache windows. Their buttons are drawn so the layout matches, and they say so when clicked.

**Tested on:** Chromium-based browsers (Chrome, Edge, Brave). Safari and Firefox
should work, but have not been tested yet.

## Run it from the source (developers)

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install pytest ruff
python3 tools/build_engine.py        # build the engine (and self-test it)
python3 tools/serve.py               # http://localhost:8000, caching off
(cd engine && pytest -q)             # engine tests
python3 tools/build_site.py --zip    # the publishable site (_site/) + offline zip (dist/)
```

Use `tools/serve.py`, not `python3 -m http.server`: it switches browser caching off,
so a normal reload always runs the files on disk. Offline mode (the service worker)
only switches on in published builds, so development never runs stale files.

| Doc | What it covers |
|---|---|
| [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) | For students: install, first program, every panel, troubleshooting |
| [`docs/LAUNCH_GUIDE.md`](docs/LAUNCH_GUIDE.md) | For the maintainer: publishing on GitHub Pages, releases, updates |
| [`CHANGELOG.md`](CHANGELOG.md) | What changed in each version |
| [`docs/PRD.md`](docs/PRD.md) | Problem, users, requirements, non-goals |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | How the engine, worker and UI connect |
| [`docs/TECH_STACK.md`](docs/TECH_STACK.md) | Chosen tools and why |
| [`docs/APP_FLOW.md`](docs/APP_FLOW.md) | What the user does, and what the system does in response |
| [`docs/UI_SPEC.md`](docs/UI_SPEC.md) | Panel-by-panel inventory of the original window |
| [`docs/RESEARCH.md`](docs/RESEARCH.md) | What is verified against YASMIN, what is still a guess, lab checklist |

## Known differences and guesses

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
