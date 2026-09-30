/*
 * File: web/js/windows/instructionDialog.js
 *
 * Behaviour of the "Instructions: CPU 0" dialog (layout: instructionLayout.js),
 * opened by ADD NEW..., INSERT ABOVE..., INSERT BELOW... and EDIT...
 *
 * Everything is driven by the ISA table the engine sends at boot (ctx.isa):
 * - a group tab lists its op codes; picking one shows its description;
 * - only the addressing modes that instruction allows are enabled, and the
 *   destination modes follow the chosen source mode (e.g. MVS);
 * - NEW INSTRUCTION builds the text ("MOV #20, R00") and sends it to the
 *   engine, which validates it again. The dialog stays open, like YASMIN.
 * - A jump to a label: pick it from the dropdown on the Value box (or type
 *   $Name with Direct Mem): "JNE $L0", as in the Programming Model 2 tutorial.
 *   TODO(research): the exact look of YASMIN 7.5.50's label dropdown.
 * Exec. Clocks and Memory read/write cycles are shown but not used yet.
 * TODO(research): what they change; how 1-operand instructions are placed
 * (here always in Source Operand); the button text when editing.
 */

import { messageBox } from "../ui/messageBox.js";
import { openWindow } from "../ui/window.js";
import { GROUP_ROWS, HEIGHT, WIDTH, layoutHtml } from "./instructionLayout.js";
import { openLabelDialog } from "./labelDialog.js";

const VALUE_MODES = [0, 2, 4, 5];
const REG_MODES = [1, 3, 6, 7];
// Descriptions exactly as YASMIN 7.5.50 shows them; others use the ISA document.
const YASMIN_TEXT = { MOV: "Moves data to register", ADD: "Adds values in registers", OUT: "Puts output from register or memory" };

export function openInstructionDialog(ctx, { mode, program, index = 0 }) {
  if (!ctx.isa?.length) {
    messageBox("YASMAX", "The instruction set has not loaded. Reload the page (Shift + Reload).", { icon: "error" });
    return null;
  }
  const win = openWindow({ id: "instructions", title: "Instructions: CPU 0", width: WIDTH, height: HEIGHT, html: layoutHtml() });
  const $ = (id) => win.body.querySelector(`#${id}`);
  const snap = ctx.store.get();
  const byName = Object.fromEntries(ctx.isa.map((s) => [s.mnemonic, s]));
  let spec = null;
  let target = { mode, program, index };

  const regNames = snap.gpr.map((r) => r.name);
  for (const op of ["s", "d"]) $(`ind-${op}-reg`).innerHTML = regNames.map((n) => `<option>${n}</option>`).join("");
  const base = snap.programs.find((p) => p.name === program)?.base ?? 0;
  $("ind-base").value = String(base).padStart(4, "0");
  $("ind-ok").textContent = mode === "edit" ? "EDIT INSTRUCTION" : "NEW INSTRUCTION";

  // ---- which modes are allowed right now ----
  const radios = (op, g = "") => [...win.body.querySelectorAll(`input[name^="ind-${op}-${g}"][name$="mode"]`)];
  function checkedMode(op) {
    const g = $(`ind-${op}-kind-val`).checked ? "v" : $(`ind-${op}-kind-reg`).checked ? "r" : null;
    return g ? Number(radios(op, g).find((r) => r.checked)?.dataset.mode ?? -1) : -1;
  }
  function allowed(op) {
    if (!spec) return [];
    if (op === "s") return [...new Set(spec.forms.filter((f) => f.length).map((f) => f[0]))];
    return spec.forms.filter((f) => f.length === 2 && f[0] === checkedMode("s")).map((f) => f[1]);
  }

  function refreshOperand(op) {
    const ok = allowed(op);
    const valKind = $(`ind-${op}-kind-val`);
    const regKind = $(`ind-${op}-kind-reg`);
    valKind.disabled = !ok.some((m) => VALUE_MODES.includes(m));
    regKind.disabled = !ok.some((m) => REG_MODES.includes(m));
    if ((valKind.checked && valKind.disabled) || (regKind.checked && regKind.disabled) || (!valKind.checked && !regKind.checked)) {
      valKind.checked = !valKind.disabled;
      regKind.checked = valKind.disabled && !regKind.disabled;
    }
    // Each frame keeps its own selection: the first allowed mode by default.
    for (const [g, order] of [["v", VALUE_MODES], ["r", REG_MODES]]) {
      const group = radios(op, g);
      for (const r of group) r.disabled = !ok.includes(Number(r.dataset.mode));
      if (!group.some((r) => r.checked && !r.disabled)) {
        const first = order.find((m) => ok.includes(m));
        for (const r of group) r.checked = Number(r.dataset.mode) === first;
      }
    }
    for (const lbl of win.body.querySelectorAll(`#ind-${op}-panel .mode-label`)) {
      lbl.classList.toggle("dim", !ok.includes(Number(lbl.dataset.m)) && !ok.includes(Number(lbl.dataset.l)));
    }
    $(`ind-${op}-val`).disabled = !valKind.checked;
    $(`ind-${op}-reg`).disabled = !regKind.checked;
    const rel = [6, 7].includes(checkedMode(op));
    for (const d of ["up", "down"]) $(`ind-${op}-${d}`).disabled = !rel;
  }
  // ---- label dropdown (Control Transfer: JMP $L0, CAL $L2, LOOP $L0, R01) ----
  function labelNames() {
    return ctx.store.get().memory.filter((m) => m.program === target.program && m.label).map((m) => m.text.slice(0, -1));
  }
  function refreshLabels() {
    const pick = $("ind-s-lbl");
    const show = spec?.group === "Control Transfer" && allowed("s").includes(2);
    pick.hidden = !show;
    $("ind-s-val").style.width = show ? "50px" : "72px";
    if (!show) return;
    pick.innerHTML = '<option value=""></option>' + labelNames().map((n) => `<option value="$${n}">${n}</option>`).join("");
    pick.disabled = !labelNames().length;
  }
  $("ind-s-lbl").addEventListener("mousedown", refreshLabels);
  $("ind-s-lbl").addEventListener("change", (e) => {
    const picked = e.target.value;
    if (!picked) return;
    $("ind-s-kind-val").checked = true;
    refresh();
    for (const r of radios("s", "v")) r.checked = Number(r.dataset.mode) === 2;
    $("ind-s-val").value = picked;
    refresh();
  });

  const refresh = () => { refreshOperand("s"); refreshOperand("d"); refreshLabels(); };

  // ---- groups and op codes ----
  function showGroup(group, select) {
    for (const t of win.body.querySelectorAll(".w-tab")) t.classList.toggle("active", t.dataset.group === group);
    const ops = ctx.isa.filter((s) => s.group === group);
    $("ind-ops").innerHTML = ops.map((s) => `<li data-op="${s.mnemonic}">${s.mnemonic}</li>`).join("");
    selectOp(select ?? ops[0]?.mnemonic);
  }
  function selectOp(name) {
    spec = byName[name] ?? null;
    // Like YASMIN: each op code starts from its default modes (Literal Value
    // if allowed, else the first allowed mode). Typed values are kept.
    for (const r of win.body.querySelectorAll('input[name$="-kind"], input[name$="mode"]')) r.checked = false;
    for (const li of $("ind-ops").children) li.classList.toggle("selected", li.dataset.op === name);
    $("ind-desc").textContent = spec ? `${spec.mnemonic}: ${YASMIN_TEXT[spec.mnemonic] ?? spec.summary}` : "";
    refresh();
  }

  // ---- instruction text ----
  function operandText(op) {
    const m = checkedMode(op);
    const val = $(`ind-${op}-val`).value.trim();
    const reg = $(`ind-${op}-reg`).value;
    const sign = win.body.querySelector(`input[name="ind-${op}-dir"]:checked`)?.value ?? "-";
    return { 0: `#${val}`, 1: reg, 2: val, 3: `@${reg}`, 4: `@${val}`, 5: /^[+-]/.test(val) ? val : `+${val}`, 6: sign + reg, 7: `${sign}@${reg}` }[m];
  }
  function instructionText() {
    const count = spec.forms[0].length;
    return [spec.mnemonic, [operandText("s"), operandText("d")].slice(0, count).join(", ")].join(" ").trim();
  }

  // ---- EDIT...: fill in from the existing instruction ----
  function load(row) {
    showGroup(byName[row.op].group, row.op);
    row.operands.forEach((o, i) => {
      const op = i === 0 ? "s" : "d";
      $(`ind-${op}-kind-${VALUE_MODES.includes(o.mode) ? "val" : "reg"}`).checked = true;
      refresh();
      for (const r of radios(op)) if (Number(r.dataset.mode) === o.mode) r.checked = true;
      if (VALUE_MODES.includes(o.mode)) $(`ind-${op}-val`).value = o.label ? `$${o.label}` : o.value;
      else $(`ind-${op}-reg`).value = `R${String(o.value).padStart(2, "0")}`;
      if ([6, 7].includes(o.mode)) $(`ind-${op}-${o.negative ? "down" : "up"}`).checked = true;
      refresh();
    });
  }

  // ---- events ----
  for (const t of win.body.querySelectorAll(".w-tab")) t.addEventListener("click", () => showGroup(t.dataset.group));
  $("ind-ops").addEventListener("click", (e) => e.target.dataset.op && selectOp(e.target.dataset.op));
  win.body.addEventListener("change", (e) => e.target.type === "radio" && refresh());
  $("ind-close").addEventListener("click", () => win.close());
  $("ind-label").addEventListener("click", () =>
    openLabelDialog(async (name) => {
      // Labels go where the next instruction would: appended, or inserted.
      const { mode: m, program: p, index: i } = target;
      const at = m === "add" ? null : m === "below" ? i + 1 : i;
      const reply = await ctx.send("add_label", { program: p, name, index: at });
      if (reply.ok && m !== "add") target = { ...target, index: i + 1 };
    }),
  );
  $("ind-ok").addEventListener("click", async () => {
    if (!spec) return;
    const text = instructionText();
    const { mode: m, program: p, index: i } = target;
    const cmd = m === "add" ? "add_instruction" : m === "edit" ? "edit_instruction" : "insert_instruction";
    const args = m === "add" ? { program: p, text } : { program: p, index: m === "below" ? i + 1 : i, text };
    const reply = await ctx.send(cmd, args);
    // Consecutive inserts go one after another, like typing a block of code.
    if (reply.ok && m !== "add" && m !== "edit") target = { ...target, index: i + 1 };
  });

  const row = mode === "edit" ? snap.memory.find((r) => r.program === program && r.index === index) : null;
  if (row) load(row);
  else showGroup(GROUP_ROWS[1][0]);
  return win;
}
