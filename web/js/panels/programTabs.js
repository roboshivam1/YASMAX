/*
 * File: web/js/panels/programTabs.js
 *
 * Region H: the Program / Instructions / Optimize - Assemble tab control.
 *
 * Program tab:   "New Program" (Program Name, Pages, Base Address, ADD) and
 *                "Files" (SAVE..., LOAD..., Program List, Base Address -1),
 *                plus COPY TO CLIPBOARD from YASMIN 7.5.50.
 *                ADD creates the program; the Program List dropdown lists
 *                ALL and every program; COPY TO CLIPBOARD copies the chosen
 *                program's instructions (one per line) to the clipboard.
 *                TODO(R-10): SAVE/LOAD need the original file format.
 * Instructions:  see instructionsTab.js.
 * Optimize - Assemble (7.5.50): ASSEMBLE, OPTIMIZE, Instruction Index, GO TO.
 *                GO TO selects that instruction of the selected program;
 *                ASSEMBLE and OPTIMIZE report "not built yet".
 */

import { button, checkbox, dropdown, group, tabs, textBox } from "../ui/widgets.js";
import { messageBox } from "../ui/messageBox.js";
import { instructionsHtml, wireInstructions } from "./instructionsTab.js";

const label = (id, text) => `<span class="w-label" id="${id}">${text}</span>`;

function programTab() {
  const newProgram = group(
    "New Program",
    label("lbl-prog-name", "Program Name") + textBox("", { id: "prog-name" }) +
      label("lbl-pages", "Pages") +
      dropdown(Array.from({ length: 16 }, (_, i) => i + 1), 1, { id: "prog-pages" }) +
      label("lbl-prog-base", "Base Address") + textBox("", { id: "prog-base" }) +
      button("ADD", { id: "btn-add" }),
    { cls: "grp-newprog" },
  );
  const files = group(
    "Files",
    button("SAVE...", { id: "btn-save", disabled: true }) + button("LOAD...", { id: "btn-load" }) +
      label("lbl-prog-filter", "Program List") + dropdown(["ALL"], "ALL", { id: "prog-filter" }) +
      label("lbl-load-base", "Base Address") + textBox("-1", { id: "load-base" }) +
      checkbox({ id: "load-base-chk", checked: true }),
    { cls: "grp-files" },
  );
  return newProgram + files + button("COPY TO CLIPBOARD", { id: "btn-copy-clip" });
}

function optimizeTab() {
  return (
    button("ASSEMBLE", { id: "btn-assemble" }) + button("OPTIMIZE", { id: "btn-optimize" }) +
    label("lbl-goto", "Instruction Index") + textBox("0", { id: "goto-index" }) + button("GO TO", { id: "btn-goto" })
  );
}

export function mount(el, ctx) {
  const { send, notYet, store } = ctx;
  el.classList.add("bottom");
  el.innerHTML = tabs(
    [
      { label: "Program", html: programTab() },
      { label: "Instructions", html: instructionsHtml() },
      { label: "Optimize - Assemble", html: optimizeTab() },
    ],
    0,
  );
  const $ = (id) => el.querySelector(`#${id}`);
  let selectedProgram = null;
  document.addEventListener("yasmax:program-selected", (e) => (selectedProgram = e.detail));
  wireInstructions(el, ctx);

  // ---- Program tab ----
  $("btn-add").addEventListener("click", () =>
    send("create_program", { name: $("prog-name").value, base: $("prog-base").value, pages: $("prog-pages").value }),
  );
  $("btn-load").addEventListener("click", () => notYet("Loading programs"));
  store.subscribe((snap) => {
    const names = ["ALL", ...snap.programs.map((p) => p.name)];
    const box = $("prog-filter");
    const keep = names.includes(box.value) ? box.value : "ALL";
    if ([...box.options].map((o) => o.value).join("\n") !== names.join("\n")) {
      box.innerHTML = names.map((n) => `<option>${n.replace(/</g, "&lt;")}</option>`).join("");
    }
    box.value = keep;
  });
  $("btn-copy-clip").addEventListener("click", async () => {
    const which = $("prog-filter").value;
    const lines = store.get().memory.filter((m) => which === "ALL" || m.program === which).map((m) => m.text);
    try {
      await navigator.clipboard.writeText(lines.join("\n"));
    } catch {
      await messageBox("CPU Simulator", "Could not copy to the clipboard.", { icon: "error" });
    }
  });

  // ---- Optimize - Assemble tab ----
  $("btn-assemble").addEventListener("click", () => notYet("ASSEMBLE"));
  $("btn-optimize").addEventListener("click", () => notYet("OPTIMIZE"));
  $("btn-goto").addEventListener("click", () => {
    const index = Number.parseInt($("goto-index").value, 10);
    const exists = store.get().memory.some((m) => m.program === selectedProgram && m.index === index);
    if (!exists) return messageBox("CPU Simulator", "There is no instruction at that index.", { icon: "error" });
    document.dispatchEvent(new CustomEvent("yasmax:select-instruction", { detail: { program: selectedProgram, index } }));
  });
}
