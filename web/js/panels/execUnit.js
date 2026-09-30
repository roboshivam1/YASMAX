/*
 * File: web/js/panels/execUnit.js
 *
 * The Execution Unit tab of region B (YASMIN 7.5.50), built by
 * cachePipeline.js. It walks one instruction through the CPU by hand:
 *
 *   1. FETCH    Instruction box = the instruction at PC (IR, MAR, MDR too)
 *   2. DECODE   Op Code box = its mnemonic
 *   3. EXECUTE  runs it; Opnd1 / Opnd2 show "operand = value" and the
 *               addressing mode: IMM #n, RDIR Rnn, MDIR n, RIND @Rnn,
 *               MIND @n, JREL +/-...
 * Only the next phase's button is enabled, as in the lab screenshots.
 * TODO(research): whether the Opnd boxes fill on DECODE or EXECUTE (the lab
 * screenshot after DECODE shows them empty, so here they fill on EXECUTE).
 *
 * Data: snapshot.exec = {instruction, opcode, operands: [{text, value, mode}]}
 * and snapshot.run.cycle_phase (null, "fetched" or "decoded").
 */

import { button, group } from "../ui/widgets.js";

// radio caption -> addressing mode codes it stands for
const MODES = [["IMM", [0]], ["RDIR", [1]], ["MDIR", [2]], ["RIND", [3]], ["MIND", [4]], ["JREL", [5, 6, 7]]];

function operandGroup(n) {
  const radios = MODES.map(
    ([name], i) =>
      `<label class="w-radio eu-mode" style="left:${i % 2 ? 84 : 8}px;top:${50 + Math.floor(i / 2) * 21}px">` +
      `<input type="radio" name="eu-op${n}" value="${name}" tabindex="-1"> ${name}</label>`,
  ).join("");
  return group(
    `Opnd${n}`,
    `<input type="text" class="w-text" id="eu-op${n}-text" readonly style="left:8px;top:18px;width:64px;height:26px">` +
      '<span class="w-label" style="left:78px;top:22px">=</span>' +
      `<input type="text" class="w-text" id="eu-op${n}-val" readonly style="left:94px;top:18px;width:52px;height:26px">` +
      radios,
    { cls: `eu-opnd eu-opnd${n}` },
  );
}

export function execUnitHtml() {
  return (
    button("1. FETCH", { id: "eu-fetch", disabled: true }) +
    '<span class="w-label" id="eu-lbl-ins">Instruction</span>' +
    '<input type="text" class="w-text" id="eu-ins" readonly>' +
    button("2. DECODE", { id: "eu-decode", disabled: true }) +
    '<span class="w-label" id="eu-lbl-op">Op Code</span>' +
    '<input type="text" class="w-text" id="eu-op" readonly>' +
    operandGroup(1) + operandGroup(2) +
    button("3. EXECUTE", { id: "eu-execute", disabled: true })
  );
}

export function wireExecUnit(el, { store, send, runner }) {
  const $ = (id) => el.querySelector(`#${id}`);
  for (const phase of ["fetch", "decode", "execute"]) {
    $(`eu-${phase}`).addEventListener("click", () => send(phase));
  }

  function refresh() {
    const snap = store.get();
    if (!snap) return;
    const phase = snap.run.cycle_phase;
    const loaded = snap.memory.length > 0 && !runner.running;
    $("eu-fetch").disabled = !loaded || phase !== null;
    $("eu-decode").disabled = !loaded || phase !== "fetched";
    $("eu-execute").disabled = !loaded || phase !== "decoded";
    $("eu-ins").value = snap.exec.instruction;
    $("eu-op").value = snap.exec.opcode;
    for (const n of [1, 2]) {
      const o = snap.exec.operands[n - 1];
      $(`eu-op${n}-text`).value = o ? o.text : "";
      $(`eu-op${n}-val`).value = o?.value ?? "";
      const name = o && MODES.find(([, codes]) => codes.includes(o.mode))[0];
      for (const r of el.querySelectorAll(`input[name="eu-op${n}"]`)) r.checked = r.value === name;
    }
  }
  store.subscribe(refresh);
  document.addEventListener("yasmax:running", refresh);
}
