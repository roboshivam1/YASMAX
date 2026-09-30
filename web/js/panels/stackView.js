/*
 * File: web/js/panels/stackView.js
 *
 * Region E: "PROGRAM STACK (RAM)".
 * Pale-yellow list view: (checkbox + marker) | Pos | Val (D) | Addr, top of
 * the stack first, as in YASMIN 7.5.50. The top row is marked "TOS->" and
 * highlighted, the bottom row (Pos 0) "BOS->". Addr is the LAdd of the
 * instruction that pushed the entry.
 * TODO(research): what the row checkboxes do in the original.
 *
 * Data: snapshot.stack = [{pos, val, addr}], bottom first.
 */

import { group, unchanged } from "../ui/widgets.js";
import { fillRows, listView } from "../ui/lists.js";

const COLUMNS = [
  { label: "", width: 84 },
  { label: "Pos", width: 52, align: "right" },
  { label: "Val (D)", width: 88, align: "right" },
  { label: "Addr", width: 70, align: "right" },
];

export function mount(el, { store }) {
  el.innerHTML =
    group("PROGRAM STACK (RAM)", "", { cls: "section" }) +
    listView({ id: "stack-list", cls: "pale-yellow", columns: COLUMNS });

  const body = el.querySelector("#stack-list tbody");

  store.subscribe((snap, prev) => {
    if (unchanged(prev, snap, "stack")) return;
    const top = snap.stack.length - 1;
    body.innerHTML = [...snap.stack]
      .reverse()
      .map((s) => {
        const mark = s.pos === top ? "TOS-&gt;" : s.pos === 0 ? "BOS-&gt;" : "";
        return (
          `<tr class="${s.pos === top ? "selected" : ""}"><td><input type="checkbox"><span class="stack-mark">${mark}</span></td>` +
          `<td class="r">${s.pos}</td><td class="r">${s.val}</td><td class="r">${String(s.addr).padStart(4, "0")}</td></tr>`
        );
      })
      .join("");
    fillRows(body.closest(".w-list"));
  });
}
