/*
 * File: web/js/panels/advanced.js
 *
 * Region J: the Advanced / New CPU tab control.
 *
 * INPUT OUTPUT... opens the Console window (windows/console.js), which the
 * OUT and IN instructions use. The other buttons open separate YASMIN tools
 * (compiler, OS simulator, virtual OS, interrupts) that YASMAX does not
 * recreate (PRD §4, F-50): they are drawn as in the original and show the
 * standard "not available" notice. The New CPU tab (YASMIN 7.5.50) shows
 * the CPU List, Coupling (TIGHT / LOOSE) and Endianness (LITTLE / BIG);
 * START NEW CPU... shows the notice, since YASMAX simulates one CPU.
 * TODO(research): whether Endianness changes how words are stored.
 */

import { button, dropdown, group, radio, tabs } from "../ui/widgets.js";
import { openConsole } from "../windows/console.js";

// [button id, caption, feature name for the notice]
const BUTTONS = [
  ["btn-compiler", "COMPILER...", "The compiler"],
  ["btn-os", "OS 0...", "The OS simulator"],
  ["btn-io", "INPUT OUTPUT...", "The input/output window"],
  ["btn-vos", "VIRTUAL OS...", "The virtual OS"],
  ["btn-interrupts", "INTERRUPTS...", "The interrupts window"],
];

function newCpuTab() {
  return (
    '<span class="w-label" id="lbl-cpu-list">CPU List</span>' +
    dropdown(["0: Tightly coupled"], "0: Tightly coupled", { id: "cpu-list" }) +
    group("Coupling", radio("coupling", "TIGHT", { checked: true }) + radio("coupling", "LOOSE"), { cls: "grp-coupling" }) +
    group("Endianness", radio("endian", "LITTLE", { checked: true }) + radio("endian", "BIG"), { cls: "grp-endian" }) +
    button("START NEW CPU...", { id: "btn-new-cpu" })
  );
}

export function mount(el, ctx) {
  const { notAvailable } = ctx;
  el.classList.add("bottom");
  el.innerHTML = tabs(
    [
      { label: "Advanced", html: BUTTONS.map(([id, caption]) => button(caption, { id })).join("") },
      { label: "New CPU", html: newCpuTab() },
    ],
    0,
  );

  for (const [id, , feature] of BUTTONS) {
    const open = id === "btn-io" ? () => openConsole(ctx) : () => notAvailable(feature);
    el.querySelector(`#${id}`).addEventListener("click", open);
  }

  el.querySelector("#btn-new-cpu").addEventListener("click", () => notAvailable("Adding another CPU"));
}
