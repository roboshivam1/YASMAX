# YASMAX — Research: behaviour to verify on the original

Status: v0.3 · Last updated: 2026-09-30

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

## Still open (blocks STEP / RUN)

| ID | Question |
|---|---|
| — | 7.5.50 new instructions (CVS, CVI, LNS seen in Data Transfer; maybe more): full op list of every dialog tab, their forms and meaning |
| — | Memory view T column: what it counts (OUT = 4, MSF = 2) |
| — | Labels: how a label shows in the memory view and how jumps use it |
| — | Exec. Clocks / Memory read and write cycles: stored per instruction? effect on T and on "by single tick"? |
| — | Initialise Data byte layout: Integer (2 bytes? endianness), Boolean (1 byte?), String (length prefix? terminator?) |
| — | Console: bottom of the window (second colour option, Fonts, PRINT), what SHOW does, how OUT's second operand (0 or 1) changes output |
| — | Execution Unit tab: what FETCH / DECODE / EXECUTE fill in, and the IMM/RDIR/MDIR/RIND/MIND/JREL radios |
| — | Why MAR shows 2 before anything runs; why data memory byte 0 showed 02 |
| R-1 | Are registers 16 bits wide too? What happens at 32767 + 1? |
| R-3 | Stack size limit, and what PSH / POP / CAL / RET put in the Addr column |
| R-4 | What number SR shows (packed flags? which bits?) |
| R-5 | What happens at HLT; can you STEP after HLT |
| R-6 | "By clock" micro-steps: what IR, MAR, MDR show in each |
| R-9 | Messages for divide by zero, bad address, other errors |
| R-11 | What RESET PROGRAM clears |
| R-13 | Colours for Show Reg Access Status |
| R-15 | When each button is enabled |
| R-16/17 | Pages limit; Start and Type columns in the program list |
| R-10 | SAVE file format |
| — | Double-click: does it run the instruction at the PC, or the clicked one, and does PC move? |
| — | Exact behaviour of LOOP (does it decrement the register?), MSF/CAL/RET frame layout |

## Lab checklist (about 15 minutes on a lab PC)

Create program `T1`, base address `100`. Add the instructions below. Execute
them **one at a time by double-clicking**, and after each one write down:
PC, SP, SR, BR, IR, MAR, MDR, the OV/Z/N boxes, and the rows in the stack view.

~~~
MOV #5, R00
MOV #8, R01
ADD R00, R01
PSH R01
PSH #-2
CMP R00, R01
POP R02
POP R03
POP R04          <- expect "Stack overflow": copy the exact dialog text and title
MOV #32767, R05
INC R05          <- register width: does it become -32768 / 32768? is OV set?
MOV #0, R06
DIV R06, R07     <- divide by zero: exact message
JMP 0            <- PC is logical: does it show 0?
HLT              <- what happens? can you STEP again?
~~~

Also:
1. Press STEP and RESET PROGRAM once each, and note what changes.
2. SAVE the program and send the file (for R-10).
3. Screenshot the instruction dialog (7.5.50) on every group tab, with the Op Code list visible.
4. Screenshot the whole window once mid-run (for R-13 and R-14 colours).
