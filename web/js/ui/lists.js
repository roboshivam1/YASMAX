/*
 * File: web/js/ui/lists.js
 *
 * The WinForms ListView in "details" mode, as used by four YASMIN panels:
 * instructions in memory, program list, program stack and GP registers.
 *
 *   listView({...})  returns the HTML: a scrolling box with a table whose
 *                    header row stays put while the body scrolls.
 *   fillRows(el)     pads the body with empty rows so the grid lines reach
 *                    the bottom edge, exactly filling the visible space.
 *   refillAll()      re-pads every list after the window is resized
 *                    (called by js/ui/scale.js through main.js).
 *
 * Column widths are fixed in px (measured from the original). If the
 * columns are wider than the box, it scrolls sideways, which is how the
 * original cuts off "Base" and "Type".
 */

import { attrs, esc } from "./widgets.js";

/**
 * List view (the WinForms ListView in "details" mode).
 * columns: [{label, width, align}]   rows: array of arrays of cell HTML.
 * Call fillRows() after inserting it, so the grid lines reach the bottom.
 */
export function listView({ columns, rows = [], ...opts }) {
  const cols = columns.map((c) => `<col style="width:${c.width}px">`).join("");
  const head = columns
    .map((c) => `<th class="${c.align === "right" ? "r" : ""}">${esc(c.label)}</th>`)
    .join("");
  const bodyRows = rows.map((r) => `<tr>${r.map((cell, i) => `<td class="${columns[i]?.align === "right" ? "r" : ""}">${cell}</td>`).join("")}</tr>`);
  const all = bodyRows.join("");
  return `<div${attrs({ ...opts, cls: `w-list ${opts.cls ?? ""}` })}><table><colgroup>${cols}</colgroup><thead><tr>${head}</tr></thead><tbody>${all}</tbody></table></div>`;
}

// Every list that has been padded, so refillAll() can redo them on resize.
const padded = new Set();

/**
 * Pad a list view with empty rows so its grid lines reach the bottom
 * edge, like the original, without ever causing a vertical scrollbar.
 * Measures the real space, so it works for any list size. Call it after
 * every redraw of the list's data rows.
 */
export function fillRows(listEl) {
  padded.add(listEl);
  const body = listEl.querySelector("tbody");
  for (const r of body.querySelectorAll("tr.filler")) r.remove();
  const columns = listEl.querySelectorAll("col").length;
  const rowHeight = 24;
  let free = listEl.clientHeight - listEl.querySelector("thead").offsetHeight - body.offsetHeight;
  const cells = "<td></td>".repeat(columns);
  let html = "";
  for (; free >= rowHeight; free -= rowHeight) html += `<tr class="filler">${cells}</tr>`;
  if (free > 2) html += `<tr class="filler last" style="height:${free - 1}px">${cells}</tr>`;
  body.insertAdjacentHTML("beforeend", html);
}

/** Re-pad every list, e.g. after the window size changed. */
export function refillAll() {
  for (const listEl of padded) fillRows(listEl);
}
