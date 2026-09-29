# YASMAX — Tech Stack

Status: Draft v0.1 · Last updated: 2026-09-29

The guiding rule is to use the fewest tools that meet the goals: zero install, offline, faithful replica, and a Python engine. Every item below has a reason. If a reason stops being true, drop the tool.

## Runtime (what the student's browser runs)

| Piece | Choice | Why |
|---|---|---|
| Python runtime | **Pyodide** (CPython compiled to WebAssembly), loaded from the jsDelivr CDN and pinned to one version | Runs the real Python engine locally in the browser. See ARCHITECTURE D-1 for why not PyScript. |
| Threading | **Web Worker** | Keeps Python off the UI thread so RUN never freezes the window |
| UI | **Plain HTML + CSS + vanilla JavaScript (ES modules)** | The UI is a fixed replica. A framework would add a build step and learning overhead with no payoff. |
| Layout | **CSS Grid** for window regions, plus `transform: scale()` to fit the screen | Mirrors the original's fixed layout exactly, with no reflow |
| Look | Hand-written **Win7-style CSS** (buttons, tabs, group boxes, list headers, title bar) | The original is a Windows 7 WinForms app. Its look is part of "exactly like the lab". |
| Fonts | System UI stack (Segoe UI → Tahoma → sans-serif) for controls, plus a bold monospace for register and list headers | Matches the original. Exact faces are to be confirmed from screenshots. |
| Offline | **Service worker** (hand-written, cache-first) | Works in labs and hostels with bad Wi-Fi |
| Storage | **Files** (download and upload) for programs. `localStorage` only for small conveniences such as last speed and last tab. | Matches YASMIN's SAVE/LOAD workflow, and nothing is lost when the browser clears storage |

## Development

| Piece | Choice | Why |
|---|---|---|
| Engine language | **Python 3.12** (match the Pyodide version's CPython) | Same interpreter locally and in the browser |
| Engine tests | **pytest** | Test the engine with no browser at all |
| Lint and format | **ruff** (lint + format) | One fast tool |
| Types | Type hints, optional **mypy** later | Helps with a table-driven ISA |
| Local server | `python3 -m http.server` | Nothing to install |
| Build | `tools/build_engine.py`, which zips the engine for the worker | No bundler, npm or node needed |
| E2E (later) | **Playwright for Python** | A smoke test that the worker boots and a STEP updates the UI |
| Version control | Git + GitHub | |
| Hosting | **GitHub Pages** | Free and static. Custom domain optional. |
| CI (later) | GitHub Actions: run pytest and ruff, build `engine.zip`, deploy Pages | |

## Learning path (both are new to you)

1. **Pyodide basics:** load Pyodide in a page, run `pyodide.runPython("1+1")`, and use `pyodide.loadPackage`. Then load a zip of your own package into its filesystem and import it.
2. **Web Workers:** post a message, receive a reply, then wrap it in a Promise. That wrapper is `bridge.js`.
3. **Pyodide in a worker:** combine 1 and 2. This is the M3 milestone and the only tricky integration.
4. Everything else is Python you already know and HTML/CSS/JS.

## Explicitly not used (and why)

| Not using | Reason |
|---|---|
| PyScript | An extra abstraction on top of Pyodide that we don't need (D-1) |
| React, Vue, Svelte | A build step and learning overhead for a static replica |
| Flask, FastAPI, any backend | Everything runs locally, and a server adds hosting and latency |
| Electron or Tauri | "Open a URL" beats "install an app". A desktop wrapper could come later if needed. |
| npm or a bundler | Nothing to bundle. ES modules load natively. |
| SharedArrayBuffer | Needs COOP/COEP headers that GitHub Pages can't set (ARCHITECTURE D-4) |
