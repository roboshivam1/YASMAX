/*
 * File: web/js/panels/programList.js
 *
 * Region C: "PROGRAM LIST".
 * A yellow list view (Name | Base | Start | Type) and six buttons in a
 * 2 x 3 grid. The Type column is cut off by the panel edge in the original,
 * so the table scrolls sideways.
 *
 * Behaviour (tutorial, section D.5):
 * - Clicking a program selects it ("yasmax:program-selected" event). The
 *   Instructions tab adds new instructions to the selected program.
 *   A newly created program becomes the selected one.
 * - REMOVE PROGRAM removes the selected program, REMOVE ALL PROGRAMS
 *   removes every program; their instructions leave memory too.
 * - SHOW PROGRAM DATA MEMORY... opens the selected program's data memory
 *   window (windows/dataMemory.js).
 * TODO(R-15): confirm the original's enable/disable rules.
 * Start and Type show what YASMIN 7.5.50 shows for a program made with ADD.
 * LOAD COMPILED CODE and the INSTANCE buttons belong to the compiler and
 * OS simulator, which YASMAX does not recreate.
 */

import { button, esc, group, unchanged } from "../ui/widgets.js";
import { fillRows, listView } from "../ui/lists.js";
import { openDataMemory } from "../windows/dataMemory.js";

const COLUMNS = [
  { label: "Name", width: 141 },
  { label: "Base", width: 68 },
  { label: "Start", width: 72 },
  { label: "Type", width: 70 },
];

const BUTTONS = [
  ["btn-load-compiled", "LOAD COMPILED\nCODE IN MEMORY"],
  ["btn-show-data-mem", "SHOW PROGRAM\nDATA MEMORY..."],
  ["btn-remove-program", "REMOVE PROGRAM"],
  ["btn-remove-all", "REMOVE ALL\nPROGRAMS"],
  ["btn-create-instance", "CREATE PROGRAM\nINSTANCE"],
  ["btn-delete-instance", "DELETE PROGRAM\nINSTANCE"],
];

const pad = (n) => (n == null ? "" : String(n).padStart(4, "0"));

export function mount(el, ctx) {
  const { store, send } = ctx;
  el.innerHTML =
    group("PROGRAM LIST", "", { cls: "section" }) +
    listView({ id: "prog-list", cls: "yellow", columns: COLUMNS }) +
    BUTTONS.map(([id, label]) => button(label, { id, disabled: true })).join("");

  const body = el.querySelector("#prog-list tbody");
  const removeOne = el.querySelector("#btn-remove-program");
  const removeAll = el.querySelector("#btn-remove-all");
  const showData = el.querySelector("#btn-show-data-mem");
  let selected = null;
  let knownNames = [];

  function select(name) {
    selected = name;
    for (const r of body.querySelectorAll("tr[data-name]")) r.classList.toggle("selected", r.dataset.name === name);
    removeOne.disabled = showData.disabled = !name;
    document.dispatchEvent(new CustomEvent("yasmax:program-selected", { detail: name }));
  }

  body.addEventListener("click", (event) => {
    const row = event.target.closest("tr[data-name]");
    if (row) select(row.dataset.name);
  });
  removeOne.addEventListener("click", () => selected && send("remove_program", { name: selected }));
  removeAll.addEventListener("click", () => send("remove_all_programs"));
  showData.addEventListener("click", () => selected && openDataMemory(ctx, selected));

  store.subscribe((snap, prev) => {
    if (unchanged(prev, snap, "programs")) return;
    const names = snap.programs.map((p) => p.name);
    body.innerHTML = snap.programs
      .map(
        (p) =>
          `<tr data-name="${esc(p.name)}"><td>${esc(p.name)}</td><td>${pad(p.base)}</td>` +
          `<td>${pad(p.start)}</td><td>${esc(p.type ?? "")}</td></tr>`,
      )
      .join("");
    fillRows(body.closest(".w-list"));
    removeAll.disabled = names.length === 0;

    const added = names.find((n) => !knownNames.includes(n));
    knownNames = names;
    select(added ?? (names.includes(selected) ? selected : null));
  });
}
