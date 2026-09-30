/*
 * File: web/js/panels/advanced.js
 *
 * Region J: the Advanced / New CPU tab control.
 *
 * INPUT OUTPUT... opens the Console window (windows/console.js), which the
 * OUT and IN instructions use. The other buttons open separate YASMIN tools
 * (compiler, OS simulator, virtual OS, interrupts) that YASMAX does not
 * recreate (PRD §4, F-50): they are drawn as in the original and show the
 * standard "not available" notice. The New CPU tab does the same instead
 * of switching, since YASMAX simulates one CPU.
 */

import { button, tabs } from "../ui/widgets.js";
import { openConsole } from "../windows/console.js";

// [button id, caption, feature name for the notice]
const BUTTONS = [
  ["btn-compiler", "COMPILER...", "The compiler"],
  ["btn-os", "OS 0...", "The OS simulator"],
  ["btn-io", "INPUT OUTPUT...", "The input/output window"],
  ["btn-vos", "VIRTUAL OS...", "The virtual OS"],
  ["btn-interrupts", "INTERRUPTS...", "The interrupts window"],
];

export function mount(el, ctx) {
  const { notAvailable } = ctx;
  el.classList.add("bottom");
  el.innerHTML = tabs(
    [
      { label: "Advanced", html: BUTTONS.map(([id, caption]) => button(caption, { id })).join("") },
      { label: "New CPU", html: "" },
    ],
    0,
  );

  for (const [id, , feature] of BUTTONS) {
    const open = id === "btn-io" ? () => openConsole(ctx) : () => notAvailable(feature);
    el.querySelector(`#${id}`).addEventListener("click", open);
  }

  // Stop the click before the tab control switches panes (see wireTabs).
  el.querySelector('.w-tab[data-tab="1"]').addEventListener("click", (event) => {
    event.stopPropagation();
    notAvailable("Adding another CPU");
  });
}
