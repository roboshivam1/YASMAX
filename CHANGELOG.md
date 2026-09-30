# Changelog

All notable changes to YASMAX. Versions follow the engine version
(`engine/yasmax_engine/__init__.py`).

## 0.6.0 (launch)
- Published build: `tools/build_site.py` builds the site with its own copy of the
  Python runtime (no CDN needed), app icons and a build stamp.
- Works offline and can be installed as an app (service worker + web manifest);
  the footer tells you when a new version is ready.
- Offline download (`yasmax-offline-<version>.zip`) with start scripts for macOS,
  Linux and Windows; `tools/serve.py` gained `--dir` and `--open`.
- GitHub Pages deploy and release workflows; issue templates for bugs and for
  differences from YASMIN.
- User guide, launch guide, PolyForm Noncommercial licence, credits.

## 0.5.1
- Instruction dialog: fetches the instruction set itself if an old cached worker
  did not send it; errors now show in a message box.
- Clicking an instruction moves the PC arrow to it (as in YASMIN).
- Jumps to labels: `JNE $L0`, with a label dropdown for Control Transfer instructions.
- `tools/serve.py`: local server with caching off.

## 0.5.0
- Execution engine: every documented instruction; STEP, by single tick, RUN, STOP,
  RESET PROGRAM, double-click to execute, breakpoints, HLT and end-of-program messages.
- Execution Unit tab (FETCH / DECODE / EXECUTE), New CPU tab, CPU Mode.
- Memory view T column, PC arrow, labels, multi-select COPY / PASTE, help balloon;
  stack TOS / BOS markers.
- SAVE / LOAD of YASMIN `.sas` files; full console; tagged data memory values.

## 0.4.0
- YASMIN 7.5.50 windows: instruction dialog, Apply label, data memory, console;
  COPY / PASTE, COPY TO CLIPBOARD, Optimize - Assemble tab.

## 0.1.0 – 0.3.0
- Pyodide engine in a Web Worker, JSON protocol, the full main window replica,
  registers, programs and instruction editing.
