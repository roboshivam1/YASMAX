# YASMAX — Product Requirements Document

Status: Draft v0.1 · Owner: Shivam · Last updated: 2026-09-29

## 1. Problem

Colleges, including LNMIIT, teach Computer Organization & Architecture with the **YASMIN CPU-OS Simulator**, which only runs on Windows. Students on macOS or Linux can't practise outside the lab, or they have to rely on a VM or Wine setup that often breaks.

Other CPU simulators exist, but they don't help, for three reasons:

- Lab sheets, exercises and viva questions refer to YASMIN's **exact** panels, buttons, instruction names and behaviour.
- Students learn the tool as well as the concepts. A different simulator means learning twice.
- Programs written for the lab must behave the same at home.

**So the product only works if it is faithful to the original.** A "better" simulator that behaves differently is a failure for this use case.

## 2. Users

| User | Need |
|---|---|
| **Primary: CO&A student on Mac or Linux** | Do lab exercises at home, with the same steps as in the lab |
| Secondary: any student | Practise on any device, including a Chromebook or a tablet with a keyboard |
| Instructor | Can point students to YASMAX without writing a separate guide |

## 3. Goals

1. **Behavioural fidelity:** the same program produces the same register, flag, stack and memory state as YASMIN, step by step.
2. **Visual fidelity:** the layout, labels, colours and control placement match the original CPU Simulator window closely enough that lab instructions apply unchanged.
3. **Zero install:** open a URL and it works. No Python, Wine or VM needed.
4. **Offline after first load:** usable in a lab or hostel with bad internet.
5. **Learning:** building it teaches the developer the course, which is an explicit goal.

## 4. Non-goals (v1)

- OS simulator, process scheduling, virtual memory, the Virtual OS window
- The high-level-language compiler (COMPILER... button)
- The Interrupts and Input/Output windows (these may come later; see §8)
- Multi-CPU (the "New CPU" tab)
- Improving on YASMIN's design, adding new instructions or "modern" UX changes
- Mobile phone layouts. This is a desktop-window replica, and tablets are best-effort.
- Any commercial use, accounts, analytics or backend

## 5. Functional requirements

Priority: **P0** = required for v1 · **P1** = strongly wanted in v1 · **P2** = later

### 5.1 Programs
| ID | Requirement | P |
|---|---|---|
| F-1 | Create a program with a name, a number of pages and a base address (Program tab → ADD) | P0 |
| F-2 | Show loaded programs in the Program List (Name, Base, Start, Type) | P0 |
| F-3 | Remove one program or all programs | P0 |
| F-4 | Save a program to a file and load it back (Files → SAVE / LOAD) | P0 |
| F-5 | Load files saved by the original YASMIN | P1, depends on research (R-10) |
| F-6 | Program List filter (ALL) and load base-address override | P1 |
| F-7 | Create and delete program instance, Show PCB | P2 (OS-flavoured; confirm behaviour first) |

### 5.2 Instructions and memory
| ID | Requirement | P |
|---|---|---|
| F-10 | Add, insert, edit and delete instructions using the same dialog workflow as the original (Instructions tab) | P0 |
| F-11 | Implement the full YASMIN CPU instruction set **as verified** in `RESEARCH.md` | P0 |
| F-12 | Instruction memory view shows PAdd, LAdd, Instruction and Base, and highlights the current instruction | P0 |
| F-13 | Show Program Data Memory window | P1 |
| F-14 | Optimize - Assemble tab | P2, confirm its function first |

### 5.3 Execution
| ID | Requirement | P |
|---|---|---|
| F-20 | STEP, RUN, STOP and RESET PROGRAM | P0 |
| F-21 | Step modes "by instruction" and "by clock" | P0 for instruction mode, P1 for clock mode |
| F-22 | Speed slider (Fast to Slow) controls the RUN rate | P0 |
| F-23 | Halt on HLT, with the same end-of-program behaviour as the original | P0 |
| F-24 | Runtime errors (bad address, stack overflow or underflow, divide by zero) are handled as YASMIN handles them | P0 |

### 5.4 Registers and state
| ID | Requirement | P |
|---|---|---|
| F-30 | Special registers PC, SP, SR, BR, IR, MAR and MDR with live values | P0 |
| F-31 | Status flags OV, Z and N | P0 |
| F-32 | General purpose registers R00–R31, with Val(D) and C columns | P0 |
| F-33 | Select register set size (the "32" dropdown) | P1 |
| F-34 | Edit a register value (Reg Value → CHANGE), and RESET ALL | P0 |
| F-35 | Show Reg Access Status (read/write highlighting) | P1 |
| F-36 | Program Stack view (Pos, Val(D), Addr) plus the Program Stack tab | P0 |
| F-37 | Watch tab | P2 |

### 5.5 Cache and pipeline
| ID | Requirement | P |
|---|---|---|
| F-40 | Cache-Pipeline tab controls, drawn and interactive | P1 |
| F-41 | SHOW PIPELINE window with single and dual pipeline | P2 |
| F-42 | SHOW CACHE window with a selectable cache type | P2 |
| F-43 | Execution Unit tab | P2 |

### 5.6 Out-of-scope buttons
| ID | Requirement | P |
|---|---|---|
| F-50 | COMPILER, OS 0, INPUT OUTPUT, VIRTUAL OS, INTERRUPTS and the New CPU tab are drawn in place, and open a "Not available in YASMAX" dialog | P0 |
| F-51 | CPU Help tab, plus an About dialog with YASMIN credit and the disclaimer | P0 |

## 6. Non-functional requirements

| ID | Requirement |
|---|---|
| N-1 | Works on current Chrome, Firefox and Safari on macOS, Linux and Windows |
| N-2 | First load under ~10 s on typical college Wi-Fi. Repeat loads under 2 s, served from cache. |
| N-3 | Fully offline after the first visit (service worker) |
| N-4 | STEP responds in under 50 ms. RUN at the fastest setting executes at least 1,000 instructions per second while the UI stays responsive. |
| N-5 | The window renders at the original's size (about 1480 × 960 CSS px) and scales down on smaller screens without reflowing panels |
| N-6 | The engine has 100% pass on golden traces (see ARCHITECTURE §7) |
| N-7 | No data leaves the browser. There are no network calls after load except fetching Pyodide from the CDN on first load. |

## 7. Success metrics

- Every lab exercise from the current CO&A course runs in YASMAX with **identical** step-by-step state compared with YASMIN. This is checked with golden traces.
- A student can follow a lab sheet in YASMAX without being told "in YASMAX, do this differently".
- Adoption: used by classmates, and ideally shared by an instructor.

## 8. Milestones

| M | Deliverable |
|---|---|
| M0 | Docs (this set) and research on the original's behaviour (RESEARCH.md filled in) |
| M1 | Python engine: core ISA, registers, flags, memory and stack, with pytest and golden traces. No UI. |
| M2 | Static UI shell: pixel-close replica of the window, no behaviour |
| M3 | Wiring: Pyodide worker, bridge, STEP/RUN/STOP/RESET, and live register, stack and memory views |
| M4 | Program management: create, add instructions, save/load, program list |
| M5 | Clock-mode stepping, reg access status, register-set size, polish |
| M6 | Offline (PWA), About/credit screen, deploy to GitHub Pages, and a v1.0 release |
| Later | Cache and pipeline windows, interrupts and I/O, loading YASMIN's own files |

## 9. Legal and ethics

- YASMIN is copyrighted software by Besim Mustafa. YASMAX **reimplements behaviour** from scratch and copies no code, binaries, icons or help text.
- A near-identical UI is intentional, for educational compatibility. **Recommended:** email the original author before a public release, explain the purpose and ask for his blessing. Credit him prominently whatever the reply.
- Licence to be chosen before release. A non-commercial licence such as **PolyForm Noncommercial 1.0.0** fits the "no commercial use" intent. Note that non-commercial licences are not OSI "open source".
- Disclaimer text appears in the README, the About dialog and the page footer or title.

## 10. Open questions

See `RESEARCH.md` for behavioural unknowns. Product-level questions:

1. Should we support importing lab-provided program files from day one? This depends on whether the original file format can be decoded (R-10).
2. How close does the visual match need to be: pixel-exact, or "same layout and look"? This decides how much effort goes into Win7 chrome.
3. Should the instructor be looped in early? An instructor's endorsement would drive adoption.
