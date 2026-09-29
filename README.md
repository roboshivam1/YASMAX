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

## Running locally (once code exists)

```bash
python3 tools/build_engine.py
python3 -m http.server 8000
```

Then open http://localhost:8000.
