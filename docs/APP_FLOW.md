# YASMAX — App Flow

Status: Draft v0.1 · Last updated: 2026-09-29

This describes what the student does and what the system does in response. Steps marked **(R-n)** depend on behaviour of the original that still has to be verified (see `RESEARCH.md`). Until it is verified, implement the flow as written but keep the detail configurable.

## 0. Boot

```
Open URL
  → window skeleton renders immediately (static HTML/CSS), all controls disabled
  → status overlay: "Loading Python engine…" (first visit: Pyodide download, ~10 MB)
  → worker loads Pyodide → unpacks engine.zip → creates Machine
  → worker posts initial snapshot + ISA table
  → panels render: empty memory, empty program list, registers at 0, SP at initial value (R-3)
  → controls enabled; overlay fades
```

- On repeat visits, the service worker serves everything from cache, so boot takes about 1–2 s.
- If boot fails (an old browser, or no network on the first visit), show a plain error box that explains what to do.

## 1. Create a program (Program tab)

```
Student types Program Name, Pages, Base Address → clicks ADD
  → engine.create_program(name, pages, base)
  → validation fails? → modal error, same wording style as YASMIN (R-9)
  → success → Program List gains a row (Name, Base, Start, Type)
            → program becomes the selected program
            → Instructions tab is ready for this program
```

## 2. Add instructions (Instructions tab)

```
Student opens Instructions tab → clicks "New/Add instruction" (exact controls: R-7)
  → Instruction dialog opens
       - instruction list (from ISA table, grouped as YASMIN groups them)
       - operand 1 / operand 2 fields with type selectors (register, immediate, address, …)
       - only operand types valid for the chosen instruction are enabled
  → Student fills in → OK
  → engine.add_instruction(...)
  → CPU Instructions in Memory view gains a row (PAdd, LAdd, Instruction, Base)
```

- Insert, edit and delete work the same way, on the selected row.
- The instruction text is rendered exactly as YASMIN renders it, e.g. `MOV #5, R01` (the exact syntax is R-8).

## 3. Execute

### 3.1 STEP

```
Student chooses "by instruction" (default) or "by clock"
Student clicks STEP
  → engine.step(mode)
  → snapshot
  → current instruction row highlighted in memory view
  → PC, SP, SR, BR, IR, MAR, MDR updated
  → changed GP registers updated (and highlighted if "Show Reg Access Status" is on)
  → flags OV / Z / N checkboxes updated
  → stack view updated if PSH/POP/CAL/RET executed
```

In "by clock" mode, each STEP advances one phase of the cycle (fetch, decode, execute sub-steps), and IR, MAR and MDR fill in as they would on real hardware (R-6).

### 3.2 RUN, STOP and the speed slider

```
Student sets slider (Fast ↔ Slow), clicks RUN
  → STEP/RUN disabled, STOP enabled
  → worker runs batches, posting run_tick snapshots; UI re-renders on each
  → ends when:
       HLT executed   → state "halted" → (end-of-program behaviour: R-5)
       STOP clicked   → state "idle", can continue with STEP or RUN
       fault          → state "fault" → error dialog (R-9)
  → controls restored
```

- Moving the slider during RUN takes effect on the next batch.

### 3.3 RESET PROGRAM

```
Click RESET PROGRAM
  → PC back to program start, stack cleared, flags cleared
  → whether GP registers are cleared: R-11
```

## 4. Inspect and modify state

| Action | Flow |
|---|---|
| Change a register | Select a register row → type a value in Reg Value → CHANGE → `engine.set_register` |
| Reset registers | RESET ALL → all GPRs set to 0 |
| Register set size | Choose from the dropdown (e.g. 8, 16, 32; R-12) → the register table shows that many rows |
| Show Reg Access Status | Checkbox. Registers read or written in the last step are highlighted (R-13 for colours). |
| Program Stack tab | Same data as the stack view, in the bottom-right tab set |
| Program data memory | SHOW PROGRAM DATA MEMORY → a separate window listing the data memory |

## 5. Save and load

```
SAVE… → engine.save_program(name) → text → browser downloads "<name>.yasmax" (format: see RESEARCH R-10)
LOAD… → browser file picker → file text → engine.load_program(text, base override?)
      → Program List + memory view update
```

- Later: import original YASMIN program files if their format can be decoded.

## 6. Out-of-scope features

Clicking COMPILER..., OS 0..., INPUT OUTPUT..., VIRTUAL OS..., INTERRUPTS..., the New CPU tab, or (until they are built) SHOW PIPELINE and SHOW CACHE:

```
  → modal: "This feature is part of the full YASMIN CPU-OS Simulator and is not
            available in YASMAX. YASMAX recreates the CPU Simulator only."
  → OK closes; no state change
```

## 7. About and credit

The CPU Help tab has a link or button that opens the About dialog, and so does clicking the title-bar icon:

- YASMAX name, version and purpose
- **Credit:** "Modelled on the YASMIN CPU-OS Simulator by Besim Mustafa, Edge Hill University."
- **Disclaimer:** not affiliated or endorsed; for educational use only; no commercial use.
- A link to the project repo and the licence

## 8. State machine (run state)

```
          create/load program
  empty ───────────────────► idle ◄──────────────┐
                              │  ▲               │
                        RUN   │  │ STOP          │ RESET PROGRAM
                              ▼  │               │
                            running ──HLT──► halted
                              │                  │
                              └──fault──► fault ─┘
  STEP is allowed from idle (and halted/fault only after RESET, R-5).
```
