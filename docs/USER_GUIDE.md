# YASMAX User Guide

YASMAX is the CPU Simulator window of the YASMIN CPU-OS Simulator, running in your
browser. If you have used YASMIN in the lab, you already know how to use it. This
guide shows how to open it, walks you through a first program, and explains every
panel.

> **For practice, not a replacement.** Some behaviour is still a best guess (see
> [Known differences](../README.md#known-differences-and-guesses)). If YASMIN and
> YASMAX disagree, YASMIN is right, and please [tell us](#reporting-a-problem).

---

## 1. Opening YASMAX

### In the browser
Open **<https://roboshivam1.github.io/YASMAX/>**. The first visit downloads about
14 MB (the simulator and a small Python runtime), so give it a few seconds. After
that it loads almost at once, and it keeps working without internet.

### As an app (recommended)
Installing gives YASMAX its own window and a Dock / Start menu / launcher icon, and it
works offline.

| Browser | How to install |
|---|---|
| Chrome, Edge, Brave (macOS, Linux, Windows, ChromeOS) | Click the install icon at the right end of the address bar, or menu **⋮ > Cast, save and share > Install page as app** (the wording differs a little between versions) |
| Safari (macOS 14 Sonoma or later) | **File > Add to Dock** |
| Firefox | No app install. Use it as a normal tab; it still works offline after the first visit. |

When a new version comes out, the footer says **"A new version is ready: reload"**.
Click **reload** when you are not in the middle of something.

### Offline download (no internet at all)
1. Download `yasmax-offline-<version>.zip` from the
   [Releases page](https://github.com/roboshivam1/YASMAX/releases) and unzip it.
2. Start it:
   - **macOS:** double-click `start-mac.command`. The first time, macOS may block
     it: right-click it, choose **Open**, then **Open** again.
   - **Linux:** run `./start-linux.sh` in a terminal.
   - **Windows:** double-click `start-windows.bat`.
3. Your browser opens YASMAX at `http://localhost:8000`. Keep the small terminal
   window open while you work; close it to stop.

This needs **Python 3**. macOS asks to install it (with the "command line developer
tools") the first time you run `python3`; accept. Most Linux systems already have it.

> **Your work is not saved automatically.** Like YASMIN, programs live in the
> simulator's memory. Reloading or closing the page clears them. Use **SAVE...**
> often (see [Saving and loading](#7-saving-and-loading-programs)).

---

## 2. Your first program (5 minutes)

This is the start of the *Programming Model 1* lab.

1. **Create a program.** In the **Program** tab (bottom left), type `TRAIN` as the
   Program Name and `100` as the Base Address, then click **ADD**. TRAIN appears in
   the PROGRAM LIST, and BR shows 100.
2. **Add instructions.** Open the **Instructions** tab and click **ADD NEW...**.
   The *Instructions: CPU 0* window opens.
   - On **Data Transfer**, pick **MOV**. Under Source Operand choose **Value** and
     type `5`. Under Destination Operand choose **Register**, `R00`. Click
     **NEW INSTRUCTION**. `MOV #5, R00` appears in memory.
   - The window stays open, so add `MOV #8, R01` the same way.
   - On **Arithmetic**, pick **ADD**: Source **Register** `R00`, Destination `R01`.
   - On **Data Transfer**, pick **PSH**: Source **Register** `R01`.
   - On **Control Transfer**, pick **HLT**. Then click **CLOSE**.
3. **Run it step by step.** Click **STEP** (Program Control tab). Each click runs one
   instruction. Watch R00, R01, the PC, the stack and SP change. PAdd = Base + LAdd,
   and each instruction's LAdd grows by its size in bytes.
4. At **HLT** a "CPU runtime" message appears and the program stops there.
5. Click **RESET PROGRAM** to empty the stack and go back to the first instruction,
   then try **RUN**.

---

## 3. The window

| Panel | What it shows / does |
|---|---|
| **CPU INSTRUCTIONS IN MEMORY** (top left) | Every instruction: PAdd, LAdd, Instruction, Base, T (type). The red arrow is the PC. |
| **Cache - Pipeline / Execution Unit** | Execution Unit: run one instruction through FETCH, DECODE, EXECUTE by hand. (Pipeline and cache windows are not in YASMAX.) |
| **PROGRAM LIST** | Your programs. SHOW PROGRAM DATA MEMORY... opens a program's data memory. |
| **SPECIAL CPU REGISTERS** | PC, SP, SR, BR, IR, MAR, MDR, the OV / Z / N flags and the CPU mode. |
| **PROGRAM STACK** | Top of stack first (TOS->), bottom last (BOS->). Addr = the instruction that pushed the entry. |
| **GENERAL PURPOSE CPU REGISTERS** | R00 upwards. Click a register, type a value in **Reg Value**, click **CHANGE**. |
| **Program / Instructions / Optimize - Assemble** | Create, save and load programs; add and edit instructions; GO TO an instruction index. |
| **Program Control / CPU View / CPU Help** | STEP, RUN, STOP, speed, RESET PROGRAM; CPU Help has the credits and the build number. |
| **Advanced / New CPU** | INPUT OUTPUT... opens the console. The other tools belong to the full YASMIN and are not in YASMAX. |
| **Registers tab** (bottom right) | RESET ALL registers, Show Reg Access Status, register set size (8/16/32/64). |

Rest the mouse on the instruction list for a help balloon.

---

## 4. Writing programs

### The instruction window
Pick a group tab, then an op code. Only the operand types that instruction allows
are enabled. The yellow strip describes the instruction.

| You want | Choose | Written as |
|---|---|---|
| A number | Value + Literal Value | `#5` |
| A register | Register + Reg Direct | `R01` |
| A memory address | Value + Direct Mem | `100` |
| The address held in a register | Register + Reg Indirect | `@R01` |
| The address held in memory | Value + Indirect Mem | `@100` |
| A jump relative to this instruction | Value + Rel Direct Mem | `+20` / `-20` |
| A jump by a register's value | Register + Rel Reg Direct, Up/Down | `+R04` / `-R04` |

### Labels
A label marks a place to jump to. It takes no memory.
1. In the instruction window, click **NEW LABEL...**, type a name (e.g. `L0`) and click OK.
   The label is added where the next instruction will go.
2. For a jump (**Control Transfer** tab: JMP, JEQ, JNE ..., CAL, LOOP), click the
   dropdown arrow on the Source **Value** box and pick the label. It is written `$L0`.

```
MOV #0, R01
L0:
ADD #1, R01
CMP #5, R01
JNE $L0
HLT
```

### Editing
Click an instruction first. **INSERT ABOVE / BELOW** open the instruction window at
that position. **EDIT...** changes it. **DELETE**, **MOVE UP / DOWN** do what they
say. **COPY** then **PASTE ABOVE / BELOW** duplicates instructions; hold **Ctrl**
(Cmd on a Mac) or **Shift** while clicking to select several.

---

## 5. Running programs

- **Click** an instruction: it is highlighted and the PC arrow moves to it, so STEP
  and RUN continue from there.
- **Double-click** an instruction: runs that one instruction.
- **STEP**: one instruction ("by instruction") or one stage at a time ("by single
  tick": fetch, decode, execute).
- **RUN**: runs until HLT, the end of the program, a breakpoint or **STOP**. The
  **Fast..Slow** slider sets the speed.
- **Breakpoints**: tick the checkbox at the start of a row. RUN stops just before
  that instruction.
- **RESET PROGRAM**: empties the stack and goes back to the first instruction.
  Registers keep their values (use **RESET ALL** in the Registers tab for those).

A program that jumps back to itself (for example a label right before its own jump)
runs forever. That is a real endless loop: press **STOP**.

**Flags after CMP a, b**: Z if they are equal; N if b < a; neither if b > a.
JEQ / JNE / JGT / JGE / JLT / JLE jump based on these.

---

## 6. Data memory and the console

**Data memory:** select a program and click **SHOW PROGRAM DATA MEMORY...**.
- *Initialise Data*: choose Integer, Boolean or String, type a value, pick an
  address, click **UPDATE**.
- *Debug control*: click a row to edit its 8 bytes in hex and click **UPDATE**.
  Tick a byte's box to make RUN stop when the program changes it.

**Console:** **INPUT OUTPUT...** (Advanced tab). `OUT` prints here, for example
`OUT 48, 0` prints the string stored at address 48. Type into **INPUT** and press
Enter to give `IN` something to read. Open the console before running a program that
prints.

---

## 7. Saving and loading programs

- **SAVE...** (Program tab) downloads the program chosen in the Program List dropdown
  as a YASMIN `.sas` file.
- **LOAD...** opens a `.sas` file. Files saved by YASMIN in the lab load in YASMAX.
  Base Address `-1` keeps the base address stored in the file.
- **COPY TO CLIPBOARD** copies the instructions as text.

---

## 8. Troubleshooting

| Problem | Fix |
|---|---|
| Stuck on "Loading Python runtime..." | The first visit needs internet and downloads about 14 MB. Wait, or check your connection. |
| A "YASMAX error" box | Please screenshot it and [report it](#reporting-a-problem). Reloading usually recovers. |
| Something looks old or broken after an update | Reload with **Shift + Reload** (Cmd+Shift+R on a Mac). |
| RUN seems stuck | Your program is probably in an endless loop. Press **STOP**. |
| Nothing prints | Open the console (INPUT OUTPUT...) and check the OUT instruction's address. |
| My programs disappeared | Reloading clears memory, as in YASMIN. Save with SAVE... and load the file back. |
| The offline download does not start | Install Python 3, then run `python3 serve.py --dir app --open` inside the unzipped folder. |

---

## Reporting a problem

- **YASMAX does something different from YASMIN in the lab?** These reports are the
  most valuable ones: [report a difference](https://github.com/roboshivam1/YASMAX/issues/new/choose).
  Include both screenshots.
- **Something is broken?** [Report a bug](https://github.com/roboshivam1/YASMAX/issues/new/choose).

Please include the build number (last line of the **CPU Help** tab).

## Privacy

YASMAX runs entirely in your browser. It has no server, no accounts, no analytics and
no cookies. Your programs never leave your computer unless you save a file yourself.

---

*Modelled on the YASMIN CPU-OS Simulator by Besim Mustafa, Edge Hill University. Not
affiliated with or endorsed by the original author. Assembled with ♥ by Shivam Kapoor ·
[shvmkpr.in](https://shvmkpr.in)*
