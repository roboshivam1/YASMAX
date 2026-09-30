/*
 * File: web/js/panels/regTabs.js
 *
 * Region K: the Registers / Program Stack / Watch tab control (bottom right).
 *
 * Registers tab: the first panel that really talks to the engine.
 *   Reg Value + CHANGE        set the register selected in the GP register
 *                             list (engine: set_register)
 *   RESET ALL                 all GP registers to 0 (engine: reset_all_registers)
 *   Show Reg Access Status    highlight registers the last instruction
 *                             read or wrote (colours in css/layout.css)
 *   Select Register Set Size  8 / 16 / 32 ... (engine: set_register_set_size)
 *
 * Which register is selected comes from gpRegs.js through the
 * "yasmax:register-selected" event. Errors (e.g. typing "abc") come back
 * from the engine and are shown by ctx.send as a message box.
 * TODO(R-9): match the original's wording when no register is selected.
 *
 * Program Stack and Watch tabs: empty until captured (UI_SPEC U-6).
 */

import { button, dropdown, tabs, textBox } from "../ui/widgets.js";
import { messageBox } from "../ui/messageBox.js";

function registersTab() {
  return (
    '<span class="w-label" id="lbl-reg-value">Reg Value</span>' +
    textBox("", { id: "reg-value" }) +
    button("CHANGE", { id: "btn-change" }) +
    button("RESET ALL", { id: "btn-reset-all" }) +
    '<span class="w-label" id="lbl-access">Show Reg Access Status</span>' +
    '<input type="checkbox" id="chk-access">' +
    '<span class="w-label" id="lbl-set-size">Select Register Set Size</span>' +
    dropdown([32], 32, { id: "reg-set-size" })
  );
}

export function mount(el, { store, send }) {
  el.classList.add("bottom");
  el.innerHTML = tabs(
    [
      { label: "Registers", html: registersTab() },
      { label: "Program Stack", html: "" },
      { label: "Watch", html: "" },
    ],
    0,
  );

  const valueBox = el.querySelector("#reg-value");
  const sizeBox = el.querySelector("#reg-set-size");
  let selected = null;

  document.addEventListener("yasmax:register-selected", (event) => {
    selected = event.detail;
  });

  async function change() {
    if (!selected) {
      await messageBox("CPU Simulator", "Please select a register first.");
      return;
    }
    await send("set_register", { name: selected, value: valueBox.value });
  }

  el.querySelector("#btn-change").addEventListener("click", change);
  valueBox.addEventListener("keydown", (event) => {
    if (event.key === "Enter") change();
  });
  el.querySelector("#btn-reset-all").addEventListener("click", () => send("reset_all_registers"));
  el.querySelector("#chk-access").addEventListener("change", (event) => {
    document.getElementById("gpr-list").classList.toggle("show-access", event.target.checked);
  });
  sizeBox.addEventListener("change", () => send("set_register_set_size", { size: sizeBox.value }));

  // Keep the size dropdown in step with the engine, and forget a selected
  // register that no longer exists after shrinking the register set.
  store.subscribe((snap) => {
    const { gpr_set_sizes: sizes, gpr_count: count } = snap.config;
    if (sizeBox.options.length !== sizes.length) {
      sizeBox.innerHTML = sizes.map((s) => `<option>${s}</option>`).join("");
    }
    sizeBox.value = String(count);
    if (selected && !snap.gpr.some((r) => r.name === selected)) selected = null;
  });
}
