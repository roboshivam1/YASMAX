/*
 * File: web/js/panels/gpRegs.js
 *
 * Region G: "GENERAL PURPOSE CPU REGISTERS".
 * A grey list view with columns Reg | Val (D) | C | Val (D). Each row has
 * a checkbox and a register name (R00, R01, ...).
 *
 * What the C column and the second Val (D) column mean is research R-12,
 * so they stay empty for now.
 *
 * Behaviour already here:
 * - Values update in place from snapshot.gpr, with no full redraw, so the
 *   scroll position stays put while a program runs.
 * - The table is rebuilt only when the register set size changes.
 * - Clicking a row selects that register and announces it with a
 *   "yasmax:register-selected" event. The Registers tab (next batch)
 *   listens for it, so CHANGE knows which register to set.
 * - Each row carries the engine's access mark ("read"/"write"/"both") as a
 *   class. It is shown only when "Show Reg Access Status" is ticked.
 */

import { group } from "../ui/widgets.js";
import { listView } from "../ui/lists.js";

const COLUMNS = [
  { label: "Reg", width: 105 },
  { label: "Val (D)", width: 88, align: "right" },
  { label: "C", width: 38 },
  { label: "Val (D)", width: 99, align: "right" },
];

function rowHtml(r) {
  return (
    `<tr data-reg="${r.name}"><td><input type="checkbox" tabindex="-1"><span class="reg-name">${r.name}</span></td>` +
    `<td class="r val">${r.val}</td><td></td><td class="r"></td></tr>`
  );
}

export function mount(el, { store }) {
  el.innerHTML =
    group("GENERAL PURPOSE CPU REGISTERS", "", { cls: "section" }) +
    listView({ id: "gpr-list", cls: "grey", columns: COLUMNS });

  const list = el.querySelector("#gpr-list");
  const body = list.querySelector("tbody");
  let valueCells = [];

  list.addEventListener("click", (event) => {
    const row = event.target.closest("tr[data-reg]");
    if (!row) return;
    for (const r of body.querySelectorAll("tr.selected")) r.classList.remove("selected");
    row.classList.add("selected");
    document.dispatchEvent(new CustomEvent("yasmax:register-selected", { detail: row.dataset.reg }));
  });

  store.subscribe((snap) => {
    if (valueCells.length !== snap.gpr.length) {
      body.innerHTML = snap.gpr.map(rowHtml).join("");
      valueCells = [...body.querySelectorAll("td.val")];
    }
    snap.gpr.forEach((r, i) => {
      const text = String(r.val);
      if (valueCells[i].textContent !== text) valueCells[i].textContent = text;
      valueCells[i].parentElement.className = [
        valueCells[i].parentElement.classList.contains("selected") ? "selected" : "",
        r.access ? `access-${r.access}` : "",
      ].join(" ").trim();
    });
  });
}
