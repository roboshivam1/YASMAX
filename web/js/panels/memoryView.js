/*
 * File: web/js/panels/memoryView.js
 *
 * Region A: "CPU INSTRUCTIONS IN MEMORY (RAM)".
 * Cyan list view with the YASMIN 7.5.50 columns PAdd | LAdd | Instruction |
 * Base | T. Addresses are 4-digit decimals ("0100").
 *   - Each row starts with a checkbox (a breakpoint: RUN stops before that
 *     instruction; saved in .sas files) and the red PC arrow on the
 *     instruction the PC points to.
 *   - Labels show as "Name:" with T = -1 and the next instruction's address.
 *   - Click selects AND moves the PC (red arrow) there, so STEP / RUN go on
 *     from that instruction, as in YASMIN. The highlight follows the PC as
 *     the program runs. Ctrl+click adds or removes a row; Shift+click
 *     selects a range (for COPY); these do not move the PC. "yasmax:instruction-selected" carries the clicked
 *     row plus `all` (every selected row in order). Other panels move the
 *     selection with a "yasmax:select-instruction" event.
 *   - Double-click executes that instruction (tutorial).
 *   - Resting the mouse shows the 7.5.50 help balloon.
 *
 * Data: snapshot.memory = [{padd, ladd, text, base, t, label, breakpoint,
 * current, program, index}].
 */

import { attachBalloon } from "../ui/balloon.js";
import { esc, group, unchanged } from "../ui/widgets.js";
import { fillRows, listView } from "../ui/lists.js";

const COLUMNS = [
  { label: "PAdd", width: 100 },
  { label: "LAdd", width: 62 },
  { label: "Instruction", width: 170 },
  { label: "Base", width: 60 },
  { label: "T", width: 34 },
];

const HELP = [
  "This view displays all program code loaded in CPU memory",
  "Place mouse over an instruction for help", "",
  "* PAddr: Physical address, i.e. address in real memory",
  "* LAddr: Logical address, i.e. address the CPU uses",
  "* Instruction: CPU instruction in assembler format",
  "* Base: Base address of instruction",
  "* T: Type of instruction", "",
  "Hold Ctrl and click then hold Shift and click to select instructions to copy",
];

export const addr = (n) => String(n).padStart(4, "0");
const key = (s) => `${s.program}\n${s.index}`;

export function mount(el, ctx) {
  const { store, send, runner } = ctx;
  el.innerHTML =
    group("CPU INSTRUCTIONS IN MEMORY (RAM)", "", { cls: "section" }) +
    listView({ id: "mem-list", cls: "cyan", columns: COLUMNS });

  const list = el.querySelector("#mem-list");
  const body = list.querySelector("tbody");
  let selected = []; // [{program, index}], the last one is the "clicked" row
  let anchor = null;
  let pcRow = null; // key of the row with the PC arrow, to see when it moves

  const rowOf = (s) => body.querySelector(`tr[data-program="${CSS.escape(s.program)}"][data-index="${s.index}"]`);
  const info = (tr) => ({ program: tr.dataset.program, index: Number(tr.dataset.index) });

  function select(rows, clicked = rows.at(-1) ?? null) {
    const keys = new Set(rows.map(key));
    selected = [...body.querySelectorAll("tr[data-program]")].map(info).filter((s) => keys.has(key(s)));
    for (const tr of body.querySelectorAll("tr[data-program]")) tr.classList.toggle("selected", keys.has(key(info(tr))));
    const main = clicked && keys.has(key(clicked)) ? clicked : selected.at(-1) ?? null;
    document.dispatchEvent(new CustomEvent("yasmax:instruction-selected", { detail: main && { ...main, all: selected } }));
  }

  body.addEventListener("click", (event) => {
    const tr = event.target.closest("tr[data-program]");
    if (!tr) return;
    if (event.target.matches("input.bp")) {
      send("set_breakpoint", { ...info(tr), on: event.target.checked });
      return;
    }
    const row = info(tr);
    if (event.shiftKey && anchor && anchor.program === row.program) {
      const [a, b] = [anchor.index, row.index].sort((x, y) => x - y);
      const range = [...body.querySelectorAll(`tr[data-program="${CSS.escape(row.program)}"]`)].map(info).filter((s) => s.index >= a && s.index <= b);
      select(range, row);
    } else if (event.ctrlKey || event.metaKey) {
      anchor = row;
      select(selected.some((s) => key(s) === key(row)) ? selected.filter((s) => key(s) !== key(row)) : [...selected, row], row);
    } else {
      anchor = row;
      select([row]);
      if (!runner.running) send("set_pc", row);
    }
  });

  body.addEventListener("dblclick", (event) => {
    const tr = event.target.closest("tr[data-program]");
    if (tr && !event.target.matches("input") && !runner.running) send("execute_at", info(tr));
  });

  document.addEventListener("yasmax:select-instruction", (event) => {
    const d = event.detail;
    anchor = d;
    select(d ? [d] : []);
    if (d) rowOf(d)?.scrollIntoView({ block: "nearest" });
  });

  attachBalloon(list, (target) => {
    const tr = target?.closest?.("tr[data-program]");
    const row = tr && store.get().memory.find((m) => key(m) === key(info(tr)));
    if (row && !row.label) {
      const spec = ctx.isa.find((s) => s.mnemonic === row.op);
      return { title: row.text, lines: [`${row.op}: ${spec?.summary ?? ""}`, `Size: ${row.size} bytes   T: ${row.t}`] };
    }
    const loaded = store.get().memory.length ? "Currently there is program code loaded" : "Currently there is no program code loaded";
    return { title: "Help", lines: [HELP[0], loaded, ...HELP.slice(1)] };
  });

  store.subscribe((snap, prev) => {
    if (unchanged(prev, snap, "memory")) return;
    const keys = new Set(selected.map(key));
    body.innerHTML = snap.memory
      .map((m) => {
        const cls = [m.current ? "current" : "", keys.has(key(m)) ? "selected" : "", m.label ? "label" : ""];
        return (
          `<tr class="${cls.join(" ").trim()}" data-program="${esc(m.program)}" data-index="${m.index}">` +
          `<td><input type="checkbox" class="bp"${m.breakpoint ? " checked" : ""}><span class="pc-arrow">&#x27A1;</span>${addr(m.padd)}</td>` +
          `<td>${addr(m.ladd)}</td><td>${esc(m.text)}</td><td>${addr(m.base)}</td><td>${m.t}</td></tr>`
        );
      })
      .join("");
    const still = selected.filter((s) => rowOf(s));
    const current = snap.memory.find((m) => m.current);
    const moved = current && key(current) !== pcRow;
    pcRow = current ? key(current) : null;
    if (moved) select([{ program: current.program, index: current.index }]);
    else if (still.length !== selected.length) select(still);
    fillRows(list);
    body.querySelector("tr.current")?.scrollIntoView({ block: "nearest" });
  });
}
