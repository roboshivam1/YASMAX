# YASMAX — Research: behaviour to verify on the original

Status: v0.4 · Last updated: 2026-09-30

**Nothing here is implemented from guesswork.** Each item is answered from the
original YASMIN, the course material, or YASMIN's own documentation, with the
source recorded. Sources so far:
- **ISA** = *CPU Simulator Instruction Set Architecture* (10-page PDF)
- **TUT** = *Programming Model 1* lab tutorial (12-page PDF)
- **SHOT** = screenshots of YASMIN 7.2.27 (main window, Program/Instructions tabs),
  7.5.50 (instruction dialog) and a data memory window
- **LAB** = screenshots of YASMIN **7.5.50, the version used in the lab** (main window
  before/after running, all bottom tabs, Execution Unit, instruction dialog on two
  tabs, Apply label, data memory, console). Decision: keep the 7.2.27 look, add the
  7.5.50 functions and instructions.
- **TUT2** = *Programming Model 2* tutorial (teach-sim.com): labels, subroutines, OUT
- **LAB2** = second set of 7.5.50 screenshots, a saved `TRAIN.sas` file and the
  student's own tests (CMP, HLT, DIV, RESET PROGRAM).

Items marked *provisional* below are implemented with the best guess and a
`TODO(research)` in the code, so they are easy to find and fix.

## Answered

| ID | Question | Answer | Source |
|---|---|---|---|
| R-2 | PAdd, LAdd, Base | LAdd = byte offset in the program; PAdd = Base + LAdd; one Base per program | TUT D.1, SHOT |
| R-2 | Instruction sizes | 1-byte opcode; each operand = 1-byte mode + 1-byte register or 2-byte value; 1 to 7 bytes | ISA p.1-2 |
| R-4 | What BR holds | "Base Register contains current base address" | TUT D.2 |
| R-8 | Instruction list | 47 opcodes in 7 groups, with opcode numbers | ISA p.4-6 |
| R-8a | Addressing modes | 8 modes and their syntax (`#n`, `Rnn`, `n`, `@Rnn`, `@n`, `+/-n`, `+/-Rnn`, `+/-@Rnn`) | ISA p.3 |
| R-8a | Allowed operand forms | per instruction, e.g. MOV (R,R) and (#,R) | ISA p.4-6 |
| R-8b | Which instructions set SR | marked with * in the table; all arithmetic and compare | ISA p.4-6 |
| R-8b | Flag meanings | OV = too big for a register (OV alone); Z = zero result; N = negative result | ISA p.6 |
| R-8c | CMP semantics | `CMP a, b`: Z if b = a; no flags if b > a; N if b < a | ISA p.9, TUT appendix |
| R-8c | JLT | jumps if the last compare found operand 2 < operand 1 | ISA p.8 |
| R-12 | Register set sizes | 8, 16, 32 or 64 registers; names R00..R63 | ISA p.3 |
| R-1 | Word size | "A word is 16 bits long"; immediates are 2 bytes | ISA p.4 |
| R-9 | POP on empty stack | error message "Stack overflow" | TUT appendix |
| — | Executing one instruction | double-click it in the instruction memory view | TUT E.2 |
| — | Stack per program | "Each program has its own individual stack" | TUT D.4 |
| — | Page size | 256 bytes (window shows 4 pages = 1024 bytes) | SHOT data memory |
| — | Address display | 4-digit decimal, e.g. `0200` | SHOT 7.5.50 |
| — | Files Base Address | defaults to `-1` | SHOT 7.2.27 |
| — | PC holds a logical address | after reaching MSF at LAdd 35 (base 100): PC 35, MAR 135 | LAB |
| R-3 | Stack direction and entry size | grows UP, 2 bytes per entry: SP 8096 -> 8100 after MSF pushed 2 entries | LAB |
| R-3 | Stack view first column | `TOS->` / `BOS->` markers with a checkbox | LAB |
| R-3 | MSF | pushes two entries: BOS value -1, TOS value 0; Addr column shows the LAdd of MSF (0035) | LAB |
| R-17 | Start / Type columns | a program made with ADD shows Start `0000`, Type `R` | LAB |
| — | Idle registers | with nothing run: PC 0, SP 8096, MAR 2, MDR 0, IR empty | LAB |
| — | Instruction dialog | two-row group tabs, Op Code list, Exec. Clocks, Value/Register + 2 mode frames per operand, read/write cycles, Base address, NEW LABEL / NEW INSTRUCTION / CLOSE | LAB |
| — | Dialog defaults | each op code starts at Literal Value if allowed, and each mode frame keeps its own selection | LAB |
| — | OUT syntax | `OUT #10, 0` (literal value, direct mem 0), 7 bytes | LAB |
| — | 7.5.50 extras | memory view T column + PC arrow + checkbox; COPY / PASTE ABOVE / PASTE BELOW; COPY TO CLIPBOARD; Optimize-Assemble tab; Execution Unit tab; CPU Mode (User/Kernel); "by single tick" | LAB |
| — | T column | "Type of instruction" (help balloon): Arithmetic 1, Control Transfer 2, Comparison 3, I/O 4, label -1 | LAB2 |
| — | Labels | row `Name:` with T -1, same address as the next instruction, 0 bytes | LAB2 |
| R-4 | SR value | SR = 1 after `CMP #0, R00` with R00 = 0 (only Z set), so Z = bit 0 | LAB2 |
| — | CMP forms | `CMP #1, #1` is not allowed; one operand must be a register | LAB2 |
| R-5 | HLT | STEP on HLT: nothing runs, the PC highlight stays on HLT, a "CPU runtime" message box appears | LAB2 |
| R-9 | Divide by zero | no error; the register keeps its value | LAB2 |
| R-11 | RESET PROGRAM | empties the stack, PC highlight back to the top instruction | LAB2 |
| R-10 | SAVE file | `.sas` text file, CRLF; header, label table, one line per row (LAdd, T, text, breakpoint) | LAB2 |
| — | Initialise Data | String = `03` + ASCII + `00`; Integer 25 = `02 00 19 00` | LAB2 |
| — | Stack view | top row first, `TOS->` highlighted; rows show Pos, Val (D), Addr | LAB2 |
| — | Console | full layout: SHOW KEYBD..., Stay on top, No output display, Display CPU id, Colours, Fonts, PRINT..., CLEAR, CLOSE | LAB2 |
| — | New CPU tab | CPU List, Coupling TIGHT/LOOSE, Endianness LITTLE/BIG, START NEW CPU... | LAB2 |
| — | Execution Unit tab | 1. FETCH, 2. DECODE, 3. EXECUTE (one enabled at a time); Instruction, Op Code, Opnd1/Opnd2 `x = y` with IMM/RDIR/MDIR/RIND/MIND/JREL; after DECODE: Instruction and Op Code filled | LAB2 |
| — | Last instruction | after the last instruction runs, PC stays on it | LAB2 |
| — | Jumps to labels | `$Name`: `JNE $L0`, `CAL $L2` | TUT2 |
| — | OUT to the console | `OUT 16, 0` prints the data at address 16; "the second parameter must always be a 0" | TUT2 |
| — | MSF / CAL | MSF reserves a space for the return address; CAL saves the return address there and jumps | TUT2 |
| — | Clicking an instruction | highlights it and moves the PC arrow there; RUN / STEP continue from it | LAB2 |

## Provisional (built, please confirm in the lab)

| ID | What YASMAX does now |
|---|---|
| — | T for Data Transfer 0, Logical 5, Miscellaneous 6 |
| R-4 | SR: N = bit 1 (2), OV = bit 2 (4) |
| — | OUT: second operand 0 prints the number (or the tagged value / string at a memory address), 1 prints the character (`OUT #42, 1` prints `*`) |
| — | IN: register gets the next typed character code (0 if none); memory gets the typed line |
| — | Boolean in Initialise Data: `01` then `00`/`01` |
| — | MSF pushes the previous frame position (-1) and 0; CAL writes the return address into the 0; RET returns there and removes both |
| — | LOOP: decrement the register, jump while it is > 0 |
| — | SUBU: absolute difference |
| — | STEP after the last instruction: "End of program" message |
| — | "By single tick": FETCH, DECODE, EXECUTE (3 ticks per instruction) |
| — | Execution Unit Opnd boxes fill on EXECUTE |
| — | Memory view checkbox = breakpoint (RUN stops before it) |
| — | Byte 0 of a new program's data memory = 02; MAR 2 / MDR 0 at start (copied, reason unknown) |
| — | Help balloon over an instruction: its description, size and T |
| — | .sas header fields other than count, name, base, code size, pages are written as seen; LOAD ignores them |

## Still open

| ID | Question |
|---|---|
| — | 7.5.50 new instructions (CVS, CVI, LNS seen in Data Transfer; maybe more): full op list of every dialog tab, their forms and meaning |
| — | Is `$Name` typed in the Value box, or does 7.5.50 offer a label list? |
| — | Exec. Clocks / Memory read and write cycles: stored per instruction? effect on T and on "by single tick"? |
| — | Exact text of the HLT "CPU runtime" message box, and of other error messages (bad address) |
| R-1 | Are registers 16 bits wide too? What happens at 32767 + 1? |
| R-3 | Stack size limit |
| R-6 | "By single tick": how many ticks per instruction, what IR, MAR, MDR show in each |
| R-13 | Colours for Show Reg Access Status |
| R-15 | When each button is enabled |
| R-16 | Pages limit |
| — | Does IN wait for input? Does the console open by itself? |
| — | Does YASMIN load a `.sas` file saved by YASMAX? |

## Lab checklist (about 15 minutes on a lab PC)

Create program `T2`, base address `0`. First open the console (INPUT OUTPUT...).
Add the instructions below, RESET PROGRAM, then STEP one at a time. After each
step note PC, SP, SR, the OV/Z/N boxes, the stack rows and anything the console shows.

~~~
OUT #65, 0        <- console: "65" or "A"?
OUT #65, 1        <- console: "65" or "A"? new line after it?
MOV #-5, R00
CMP #0, R00       <- SR value with N set?
MOV #32767, R01
INC R01           <- value, OV box, SR value
MOV #3, R02
Label:            <- add with NEW LABEL..., name it Label
DEC R02
JNZ Label         <- if the dialog lets you pick the label: how does it show?
MSF
CAL <address of the NOP below>
HLT               <- copy the exact text and title of the message box
NOP
RET               <- stack rows after MSF, after CAL and after RET
~~~

Also:
1. Change to "by single tick" and press STEP three times on one instruction. What do IR, MAR, MDR show after each tick? How many ticks does it take?
2. In the data memory window, write Boolean True at 0 and integer -2 at 8, then screenshot.
3. Screenshot the instruction dialog on every group tab, with the Op Code list scrolled so every op code shows. For CVS, CVI and LNS (and any other new ones), select each one and screenshot its description.
4. SAVE a program in YASMAX, and try to LOAD it in YASMIN. Does it load?
5. Screenshot the window once with "Show Reg Access Status" ticked, right after an ADD.
