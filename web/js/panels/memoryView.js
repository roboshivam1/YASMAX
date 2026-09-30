/*
 * File: web/js/panels/memoryView.js
 *
 * Region A: "CPU INSTRUCTIONS IN MEMORY (RAM)".
 * A cyan list view with columns PAdd | LAdd | Instruction | Base, showing
 * the instructions of every program in memory order. Addresses are shown
 * as 4-digit decimals ("0200"), as in the original.
 * In the original the Base column is cut off by the panel edge, so the
 * table is deliberately wider than the list and scrolls sideways.
 *
 * Clicking a row selects that instruction and announces it with a
 * "yasmax:instruction-selected" event ({program, index}), which the
 * Instructions tab uses for EDIT, DELETE, MOVE UP/DOWN and INSERT.
 * The selection survives redraws as long as that instruction exists, and
 * other panels can move it with a "yasmax:select-instruction" event.
 * TODO: double-click executes the instruction (tutorial), with STEP.
 *
 * Data: snapshot.memory = [{padd, ladd, text, base, program, index, current}].
 */

import { esc, group, unchanged } from "../ui/widgets.js";
import { fillRows, listView } from "../ui/lists.js";

const COLUMNS = [
  { label: "PAdd", width: 105 },
  { label: "LAdd", width: 66 },
  { label: "Instruction", width: 196 },
  { label: "Base", width: 80 },
];

export const addr = (n) => String(n).padStart(4, "0");

export function mount(el, { store }) {
  el.innerHTML =
    group("CPU INSTRUCTIONS IN MEMORY (RAM)", "", { cls: "section" }) +
    listView({ id: "mem-list", cls: "cyan", columns: COLUMNS });

  const body = el.querySelector("#mem-list tbody");
  let selected = null; // {program, index}

  function select(row) {
    for (const r of body.querySelectorAll("tr.selected")) r.classList.remove("selected");
    selected = row ? { program: row.dataset.program, index: Number(row.dataset.index) } : null;
    row?.classList.add("selected");
    document.dispatchEvent(new CustomEvent("yasmax:instruction-selected", { detail: selected }));
  }

  body.addEventListener("click", (event) => {
    const row = event.target.closest("tr[data-program]");
    if (row) select(row);
  });

  // Other panels move the selection, e.g. after MOVE UP or DELETE.
  document.addEventListener("yasmax:select-instruction", (event) => {
    const d = event.detail;
    select(d ? body.querySelector(`tr[data-program="${CSS.escape(d.program)}"][data-index="${d.index}"]`) : null);
  });

  store.subscribe((snap, prev) => {
    if (unchanged(prev, snap, "memory")) return;
    body.innerHTML = snap.memory
      .map((m) => {
        const cls = [m.current ? "current" : "", selected && selected.program === m.program && selected.index === m.index ? "selected" : ""];
        return (
          `<tr class="${cls.join(" ").trim()}" data-program="${esc(m.program)}" data-index="${m.index}">` +
          `<td>${addr(m.padd)}</td><td>${addr(m.ladd)}</td><td>${esc(m.text)}</td><td>${addr(m.base)}</td></tr>`
        );
      })
      .join("");
    if (selected && !body.querySelector("tr.selected")) select(null);
    fillRows(body.closest(".w-list"));
    body.querySelector("tr.current")?.scrollIntoView({ block: "nearest" });
  });
}
