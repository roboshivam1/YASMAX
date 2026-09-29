# YASMAX — UI Spec (CPU Simulator window)

Status: Draft v0.1 · Source: annotated screenshot of YASMIN v7.2.27 ("Image 1 – CPU Simulator window") · Last updated: 2026-09-29

Goal: a student who knows the original can find every control in the same place. Colours below are **approximate**. Sample exact values with a colour picker from a full-resolution screenshot of the original (task U-1).

## 1. Window

- Title bar: Win7-style, icon + text `CPU Simulator: CPU 0`, plus minimize, maximize and close buttons (decorative).
- YASMAX title text: `YASMAX — CPU Simulator: CPU 0`. **Don't reuse YASMIN's copyright line** in the title bar. Credit goes in the About dialog.
- Background: Win7 light grey (~`#F0F0F0`), with group boxes drawn as etched borders.
- Reference size: about 1480 × 960 px. The layout is fixed and scaled to fit.

## 2. Layout grid

Four columns, from left to right:

```
┌──────────────────┬───────────────────┬───────────────────┬───────────────────┐
│ A CPU INSTRUC-   │ B Cache-Pipeline /│ D SPECIAL CPU     │ G GENERAL PURPOSE │
│   TIONS IN       │   Execution Unit  │   REGISTERS       │   CPU REGISTERS   │
│   MEMORY (RAM)   ├───────────────────┼───────────────────┤                   │
│                  │ C PROGRAM LIST    │ E PROGRAM STACK   │                   │
│                  │   + 6 buttons     │   (RAM)           │                   │
├──────────────────┼───────────────────┼───────────────────┼───────────────────┤
│ H Program /      │ I Program Control │ J Advanced /      │ K Registers /     │
│   Instructions / │   / CPU View /    │   New CPU         │   Program Stack / │
│   Optimize tabs  │   CPU Help tabs   │   tabs            │   Watch tabs      │
└──────────────────┴───────────────────┴───────────────────┴───────────────────┘
```

## 3. Panels

### A. CPU INSTRUCTIONS IN MEMORY (RAM)
- A list view with columns **PAdd | LAdd | Instruction | Base** (the Base column is partly cut off by the panel edge in the original).
- Body colour: cyan (~`#A0FFFF`). The header is a Win7 list header with bold serif-looking text.
- A horizontal scrollbar at the bottom and a vertical scrollbar when needed.
- The current instruction row is highlighted (colour: R-14).

### B. Cache - Pipeline / Execution Unit (tabs)
- **Cache - Pipeline** tab (active tab shown as a blue highlight):
  - Group "Pipeline": radio buttons `Single pipeline` (selected) and `Dual pipeline` (disabled look), a "Select pipeline" dropdown (`0`), and a button **SHOW PIPELINE…**
  - Group "Cache": a "Select cache type" dropdown (`Data`) and a button **SHOW CACHE…**
- **Execution Unit** tab: contents to be captured (U-2).

### C. PROGRAM LIST
- A list view with columns **Name | Base | Start | Type**. Body colour: light yellow (~`#FFFF99`). Horizontal scrollbar.
- A 2 × 3 button grid (grey, with uppercase two-line captions):
  - LOAD COMPILED CODE IN MEMORY · SHOW PROGRAM DATA MEMORY…
  - REMOVE PROGRAM · REMOVE ALL PROGRAMS
  - CREATE PROGRAM INSTANCE · DELETE PROGRAM INSTANCE
- In the screenshot they look disabled when no program is loaded. Enable and disable rules: R-15.

### D. SPECIAL CPU REGISTERS
- **PC** and **SR**: cyan fields, value right-aligned in bold.
- **SP**: cyan field, initial value `8096` in the screenshot.
- **BR**: yellow field.
- "Status Flags": **OV**, **Z** and **N** checkboxes (read-only).
- **IR**, **MAR** and **MDR**: peach fields (~`#FBDDC0`). IR and MDR are wide, and MAR shows `0`.

### E. PROGRAM STACK (RAM)
- A list view with columns **(blank) | Pos | Val (D) | Addr**. Body colour: light yellow.

### G. GENERAL PURPOSE CPU REGISTERS
- A list view with columns **Reg | Val (D) | C | Val (D)**. The second Val (D) column is for the right-hand half of a two-column layout, or for another format; confirm this in R-12.
- Each row has a checkbox, a register name `R00` … `R31`, and a value that defaults to `0`.
- A vertical scrollbar. About 26 rows are visible.

### H. Program / Instructions / Optimize - Assemble (tabs)
- **Program** tab:
  - Group "New Program": `Program Name` text field, `Pages` spinner (default `1`), `Base Address` text field, **ADD** button.
  - Group "Files": **SAVE…**, **LOAD…**, `Program List` dropdown (`ALL`), `Base Address` field with a checkbox (checked).
- **Instructions** tab: the instruction editing controls. Capture them from the original (U-3).
- **Optimize - Assemble** tab: capture it (U-4). Low priority.

### I. Program Control / CPU View / CPU Help (tabs)
- **Program Control** tab:
  - Buttons: **STEP**, **RUN**, **STOP** (stacked on the left), plus **RESET PROGRAM** and **SHOW PCB…** on the right.
  - Radio buttons: `by instruction` (selected) and `by clock`.
  - A vertical speed slider labelled `Fast` at the top and `Slow` at the bottom, with tick marks.
- **CPU View** and **CPU Help**: capture them (U-5).

### J. Advanced / New CPU (tabs)
- **Advanced** tab, a 2-column button grid: **COMPILER…** · **OS 0…**, **INPUT OUTPUT…** · **VIRTUAL OS…**, **INTERRUPTS…**
- All of these show the "not available" dialog in v1.

### K. Registers / Program Stack / Watch (tabs)
- **Registers** tab: `Reg Value` field, **CHANGE** button, **RESET ALL** button, `Show Reg Access Status` checkbox, and a `Select Register Set Size` dropdown (`32`).

## 4. Control styling (Win7)

| Control | Notes |
|---|---|
| Buttons | Light-grey gradient, a 1 px grey border with rounded corners, uppercase captions in a light condensed font |
| Tabs | The active tab has a blue fill with white text, as seen in the screenshot ("Program", "Program Control", "Advanced", "Registers", "Cache - Pipeline") |
| Group boxes | Etched border with the caption inset at top-left |
| List headers | Raised header cells with bold text |
| Text fields | White, sunken 1 px border |

## 5. Capture checklist

To get "exactly the same", we need more reference material than one annotated screenshot:

- [ ] U-1 A full-resolution, un-annotated screenshot of the main window (for colours, fonts and spacing)
- [ ] U-2 The Execution Unit tab
- [ ] U-3 The Instructions tab and the instruction add/edit dialog (**most important**)
- [ ] U-4 The Optimize - Assemble tab
- [ ] U-5 The CPU View and CPU Help tabs
- [ ] U-6 The Program Stack and Watch tabs (bottom right)
- [ ] U-7 The Show Program Data Memory window
- [ ] U-8 The window mid-run: highlighted row, filled IR/MAR/MDR, reg access highlighting
- [ ] U-9 Every error and message dialog you can trigger
- [ ] U-10 The About screen of the original (for credit wording)
