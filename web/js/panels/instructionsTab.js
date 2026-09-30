/*
 * File: web/js/panels/instructionsTab.js
 *
 * The Instructions tab of region H (the tab control itself is built by
 * programTabs.js). Button grid as in YASMIN 7.5.50:
 *
 *     ADD NEW...       SHOW...      UNDO
 *     INSERT ABOVE...  MOVE DOWN    EDIT...
 *     INSERT BELOW...  MOVE UP      DELETE
 *     COPY             PASTE ABOVE  PASTE BELOW
 *
 * ADD NEW / INSERT / EDIT open the instruction dialog. COPY remembers the
 * selected instructions (Ctrl / Shift + click in the memory view selects
 * several); PASTE ABOVE / BELOW insert copies of them, in order.
 * ADD NEW needs a program selected in the program list; the rest need an
 * instruction selected in the memory view. TODO(R-15): confirm these rules.
 * UNDO stays disabled and SHOW... reports "not built yet" until we know
 * exactly what they do.
 */

import { messageBox } from "../ui/messageBox.js";
import { button } from "../ui/widgets.js";
import { openInstructionDialog } from "../windows/instructionDialog.js";

// [id, caption] in reading order; positions are in css/layout-bottom.css.
const BUTTONS = [
  ["btn-ins-add", "ADD NEW..."], ["btn-ins-show", "SHOW..."], ["btn-ins-undo", "UNDO"],
  ["btn-ins-above", "INSERT ABOVE..."], ["btn-ins-down", "MOVE DOWN"], ["btn-ins-edit", "EDIT..."],
  ["btn-ins-below", "INSERT BELOW..."], ["btn-ins-up", "MOVE UP"], ["btn-ins-delete", "DELETE"],
  ["btn-ins-copy", "COPY"], ["btn-ins-paste-above", "PASTE ABOVE"], ["btn-ins-paste-below", "PASTE BELOW"],
];
const NEEDS_INSTRUCTION = ["btn-ins-above", "btn-ins-below", "btn-ins-edit", "btn-ins-up", "btn-ins-down", "btn-ins-delete", "btn-ins-copy"];

export function instructionsHtml() {
  return BUTTONS.map(([id, c]) => button(c, { id, disabled: id !== "btn-ins-show" })).join("");
}

export function wireInstructions(el, ctx) {
  const $ = (id) => el.querySelector(`#${id}`);
  let program = null; // selected in the program list
  let instruction = null; // {program, index} selected in the memory view
  let clipboard = null; // instruction texts copied with COPY

  function refresh() {
    $("btn-ins-add").disabled = !program;
    for (const id of NEEDS_INSTRUCTION) $(id).disabled = !instruction;
    $("btn-ins-paste-above").disabled = $("btn-ins-paste-below").disabled = !(instruction && clipboard);
  }
  document.addEventListener("yasmax:program-selected", (e) => { program = e.detail; refresh(); });
  document.addEventListener("yasmax:instruction-selected", (e) => { instruction = e.detail; refresh(); });
  const reselect = (detail) => document.dispatchEvent(new CustomEvent("yasmax:select-instruction", { detail }));

  const dialog = (mode) => openInstructionDialog(ctx, mode === "add" ? { mode, program } : { mode, ...instruction });
  $("btn-ins-add").addEventListener("click", () => dialog("add"));
  $("btn-ins-above").addEventListener("click", () => dialog("above"));
  $("btn-ins-below").addEventListener("click", () => dialog("below"));
  const rowOf = (s) => ctx.store.get().memory.find((m) => m.program === s.program && m.index === s.index);
  $("btn-ins-edit").addEventListener("click", () => {
    if (rowOf(instruction)?.label) return messageBox("CPU Simulator", "A label cannot be edited. Delete it and add a new one.");
    dialog("edit");
  });
  $("btn-ins-show").addEventListener("click", () => ctx.notYet("SHOW..."));

  for (const [id, delta] of [["btn-ins-up", -1], ["btn-ins-down", 1]]) {
    $(id).addEventListener("click", async () => {
      const { program: p, index } = instruction;
      const reply = await ctx.send("move_instruction", { program: p, index, delta });
      const count = reply.snapshot.memory.filter((m) => m.program === p).length;
      if (reply.ok) reselect({ program: p, index: Math.max(0, Math.min(count - 1, index + delta)) });
    });
  }
  $("btn-ins-delete").addEventListener("click", async () => {
    const reply = await ctx.send("delete_instruction", instruction);
    if (reply.ok) reselect(null);
  });

  $("btn-ins-copy").addEventListener("click", () => {
    const texts = (instruction.all ?? [instruction]).map(rowOf).filter((r) => r && !r.label).map((r) => r.text);
    clipboard = texts.length ? texts : null;
    refresh();
  });
  for (const [id, offset] of [["btn-ins-paste-above", 0], ["btn-ins-paste-below", 1]]) {
    $(id).addEventListener("click", async () => {
      const { program: p, index } = instruction;
      for (const [i, text] of clipboard.entries()) {
        const reply = await ctx.send("insert_instruction", { program: p, index: index + offset + i, text });
        if (!reply.ok) return;
      }
      reselect({ program: p, index: index + offset });
    });
  }
}
