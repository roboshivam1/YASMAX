/*
 * File: web/js/panels/specialRegs.js
 *
 * Region D: "SPECIAL CPU REGISTERS".
 * PC, SP, SR (cyan boxes), BR (yellow box), the OV / Z / N status flag
 * checkboxes, and IR, MAR, MDR (peach boxes).
 *
 * Everything is read-only and redrawn from snapshot.special and
 * snapshot.flags. Empty engine values (None -> null) show as an empty
 * box, exactly like IR and MDR in the original before a program runs.
 */

import { checkbox, group, valueBox } from "../ui/widgets.js";

// [register, colour class] for every value box in this panel.
const BOXES = [
  ["PC", "cyan"],
  ["SP", "cyan"],
  ["SR", "cyan"],
  ["BR", "yellow"],
  ["IR", "peach"],
  ["MAR", "peach"],
  ["MDR", "peach"],
];
const FLAGS = ["OV", "Z", "N"];

function label(name) {
  return `<span class="w-label bold" id="lbl-${name.toLowerCase()}">${name}</span>`;
}

export function mount(el, { store }) {
  el.innerHTML =
    group("SPECIAL CPU REGISTERS", "", { cls: "section" }) +
    BOXES.map(([name, colour]) => label(name) + valueBox("", { id: `reg-${name.toLowerCase()}`, cls: colour })).join("") +
    '<span class="w-label bold" id="lbl-flags">Status Flags</span>' +
    '<div class="w-group flags-box"></div>' +
    FLAGS.map((f) => label(f) + checkbox({ id: `flag-${f.toLowerCase()}`, disabled: true })).join("");

  // Keep references so updates only touch text, never rebuild the panel.
  const boxes = Object.fromEntries(BOXES.map(([name]) => [name, el.querySelector(`#reg-${name.toLowerCase()}`)]));
  const flags = Object.fromEntries(FLAGS.map((f) => [f, el.querySelector(`#flag-${f.toLowerCase()}`)]));

  store.subscribe((snap) => {
    for (const [name, box] of Object.entries(boxes)) {
      const value = snap.special[name];
      box.textContent = value == null ? "" : String(value);
    }
    for (const [name, box] of Object.entries(flags)) {
      box.checked = Boolean(snap.flags[name]);
    }
  });
}
