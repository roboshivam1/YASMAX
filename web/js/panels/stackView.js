/*
 * File: web/js/panels/stackView.js
 *
 * Region E: "PROGRAM STACK (RAM)".
 * A pale-yellow list view with columns (blank) | Pos | Val (D) | Addr.
 * The meaning of the first, unlabelled column is not known yet, so it
 * stays empty (see docs/RESEARCH.md, R-3).
 *
 * Data: snapshot.stack = [{pos, val, addr}], filled in once the engine
 * has a stack (later batch).
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
    const rows = snap.stack
      .map((s) => `<tr><td></td><td class="r">${s.pos}</td><td class="r">${s.val}</td><td class="r">${s.addr}</td></tr>`)
      .join("");
    body.innerHTML = rows;
    fillRows(body.closest(".w-list"));
  });
}
