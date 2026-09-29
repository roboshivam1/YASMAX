# YASMAX — Research: behaviour to verify on the original

Status: Draft v0.1 · Last updated: 2026-09-29

**Nothing here should be implemented from memory or guesswork.** Each item is answered by trying it on real YASMIN (a lab PC, or Wine/CrossOver), by the course lab sheets, or by YASMIN's own help. Record the answer, the source and the date. Where it helps, record a golden trace (ARCHITECTURE §7).

How to record an answer:

```
### R-n  <question>
Answer: ...
Source: lab PC / Wine / lab sheet 3 / YASMIN help → <page>
Verified: 2026-10-xx by Shivam
Trace: tests/golden/r-n_<slug>.json (if any)
```

## Machine basics
| ID | Question | Why it matters |
|---|---|---|
| R-1 | Word size and value range of registers and memory. Signed or unsigned? What happens on overflow (wrap, or saturate plus set OV)? | Every arithmetic result and flag |
| R-2 | What exactly are **PAdd** and **LAdd**, and how does **Base** relate them? Is memory byte- or word-addressed? How many bytes per instruction? | Memory view, jumps, addressing |
| R-3 | Initial SP value (`8096` in the screenshot): why that number? Does the stack grow down or up? What is the stack size? | Stack view, PSH/POP, CAL/RET |
| R-4 | What do **SR** and **BR** hold? (Status register? Base register?) When do they change? | Special registers panel |

## Instruction set
| ID | Question | Why it matters |
|---|---|---|
| R-8 | The **full instruction list** with exact mnemonics, operand forms and text syntax (e.g. `MOV #5, R01`?). Copy the list from the instruction dialog. | The ISA table is the core of the engine |
| R-8a | Addressing modes: immediate, register, direct memory, register-indirect? What is the syntax for each? | Operands |
| R-8b | For every instruction: which flags does it set or clear? | Flags must match exactly |
| R-8c | Conditional jump semantics: based on flags, or on a compare result? | Program logic |
| R-8d | I/O-ish or OS-ish instructions (e.g. software interrupts, output). What do they do when the OS or I/O windows aren't in use? | Scoping v1 |
| R-6 | "By clock" mode: which micro-steps are shown, and in what order do IR, MAR and MDR fill? How many clock steps per instruction type? | Clock stepping |

## Behaviour
| ID | Question | Why it matters |
|---|---|---|
| R-5 | What happens at HLT: a dialog, a status change, or both? Can you STEP again after halting without resetting? | End-of-program flow |
| R-9 | Error cases and their exact messages: invalid address, stack overflow and underflow, divide by zero, invalid program name or base address | Error dialogs |
| R-11 | Does RESET PROGRAM clear GP registers, memory data and the stack, or only the PC? | Reset flow |
| R-12 | Register set sizes available in the dropdown. What are the **C** column and the second **Val (D)** column for? | Registers panel |
| R-13 | Show Reg Access Status: which colours mean read and which mean write, and how long do they persist? | Visual fidelity |
| R-14 | Highlight colour and style for the current instruction row | Visual fidelity |
| R-15 | Enable and disable rules for all buttons in each state (no program, program loaded, running, halted) | UI states |
| R-16 | Pages: what does a "page" mean for program size? What happens when instructions exceed it? | Program creation |
| R-17 | Multiple programs loaded at once: how are bases assigned, and which one runs? | Program list |
| R-18 | What do the speed slider positions map to? (Roughly measure instructions per second at each setting.) | RUN timing |

## Files
| ID | Question | Why it matters |
|---|---|---|
| R-10 | The format of files saved by SAVE…: extension, text or binary. Grab 3–4 sample files covering different instruction kinds. | Importing lab-provided programs (F-5) |

## Course material to collect
- [ ] All CO&A lab sheets that use YASMIN. Each exercise becomes a golden-trace test.
- [ ] Any instructor-provided YASMIN program files
- [ ] YASMIN's built-in help or tutorial text, **for reference only** (do not copy it into YASMAX)

## Suggested order
1. R-8 (instruction list), R-1, R-2, R-3 → enough to start the engine (M1)
2. R-8b, R-5, R-9, R-11 → enough for a correct STEP/RUN
3. The UI capture checklist in `UI_SPEC.md` §5 → enough for the UI shell (M2)
4. Everything else as its milestone comes up
