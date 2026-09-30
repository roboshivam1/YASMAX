/*
 * File: web/js/windows/instructionLayout.js
 *
 * The markup of the "Instructions: CPU 0" dialog, laid out from a
 * screenshot of YASMIN 7.5.50 (1 px = 1 px). Behaviour is in
 * instructionDialog.js; this file only draws.
 *
 *   two-row group tabs          Logical, Miscellaneous /
 *                               Data Transfer, Arithmetic, Control Transfer, Comparison, I/O
 *   Op Code list + Exec. Clocks
 *   Source / Destination Operand, each with:
 *     ( ) Value [....]     frame: Literal Value, Direct Mem, Indirect Mem, Rel Direct Mem
 *     ( ) Register [R00]   frame: Reg Direct, Reg Indirect, Rel Reg Direct, Rel Reg Indirect, Up/Down
 *   (jumps: a dropdown on the Source Value box lists the program's labels)
 *   Memory read cycles, Memory write cycles, Base address
 *   description strip
 *   NEW LABEL...   NEW INSTRUCTION   CLOSE
 *
 * Every mode radio carries data-mode = the ISA addressing mode code (0..7).
 * Each operand has two mode groups: ind-<op>-vmode (value frame) and
 * ind-<op>-rmode (register frame).
 */

import { button, dropdown, esc } from "../ui/widgets.js";

export const WIDTH = 676;
export const HEIGHT = 568;

export const GROUP_ROWS = [
  ["Logical", "Miscellaneous"],
  ["Data Transfer", "Arithmetic", "Control Transfer", "Comparison", "I/O"],
];
const TAB_X = [6, 123, 243, 364, 483, 604];

const at = (l, t, w, h) =>
  `position:absolute;left:${l}px;top:${t}px` + (w ? `;width:${w}px` : "") + (h ? `;height:${h}px` : "");
const text = (s, l, t, extra = "") => `<span class="w-label ${extra}" style="${at(l, t)}">${esc(s)}</span>`;
// Value modes and register modes are separate radio groups, so each frame
// keeps its own selection, as in YASMIN.
const modeRadio = (op, mode, l, t) =>
  `<input type="radio" name="ind-${op}-${[1, 3, 6, 7].includes(mode) ? "r" : "v"}mode" data-mode="${mode}" style="${at(l, t)}">`;
// A mode label greys out when its row is not allowed (data-m = own mode,
// data-l = the mode at the start of the row), matching the screenshots.
const modeText = (s, l, t, m, row) =>
  `<span class="w-label mode-label" data-m="${m}" data-l="${row}" style="${at(l, t)}">${esc(s)}</span>`;

function tabs() {
  return GROUP_ROWS.map((row, r) => {
    const items = row
      .map((g, i) => `<li class="w-tab" data-group="${esc(g)}" style="width:${TAB_X[i + 1] - TAB_X[i] - 1}px">${esc(g)}</li>`)
      .join("");
    return `<ul class="w-tabrow" style="${at(TAB_X[0], 9 + r * 22)};margin:0;padding:0;list-style:none">${items}</ul>`;
  }).join("");
}

/* One operand block. y = block geometry measured from the screenshot. */
function operand(op, title, y) {
  const regs = dropdown(["R00"], "R00", { id: `ind-${op}-reg` });
  return (
    `<div id="ind-${op}-panel">` +
    text(title, 146, y.title, "bold") +
    `<label class="w-radio" style="${at(152, y.valRow)}"><input type="radio" name="ind-${op}-kind" value="value" id="ind-${op}-kind-val"> <span>Value</span></label>` +
    `<input type="text" class="w-text cyan" id="ind-${op}-val" style="${at(234, y.valBox, 72, 24)}">` +
    // Label list for jumps ($L0), shown as a dropdown arrow on the Value box.
    `<select class="w-select lbl-pick" id="ind-${op}-lbl" hidden style="${at(284, y.valBox, 24, 24)}"></select>` +
    `<label class="w-radio" style="${at(152, y.regRow)}"><input type="radio" name="ind-${op}-kind" value="register" id="ind-${op}-kind-reg"> <span>Register</span></label>` +
    regs.replace("<select", `<select style="${at(234, y.regBox, 82, 24)}"`) +
    // Value-mode frame
    `<div class="w-frame" style="${at(320, y.valFrame, 345, y.valFrameH)}">` +
    modeText("Literal Value", 11, 12, 0, 0) + modeRadio(op, 0, 111, 14) +
    modeText("Direct Mem", 11, 32, 2, 2) + modeRadio(op, 2, 111, 34) + modeText("Rel Direct Mem", 136, 32, 5, 2) + modeRadio(op, 5, 242, 34) +
    modeText("Indirect Mem", 11, 52, 4, 4) + modeRadio(op, 4, 111, 54) +
    `</div>` +
    // Register-mode frame
    `<div class="w-frame" style="${at(320, y.regFrame, 345, 80)}">` +
    modeText("Reg Direct", 11, 16, 1, 1) + modeRadio(op, 1, 111, 18) + modeText("Rel Reg Direct", 130, 16, 6, 1) + modeRadio(op, 6, 240, 18) +
    modeText("Reg Indirect", 11, 39, 3, 3) + modeRadio(op, 3, 111, 41) + modeText("Rel Reg Indirect", 130, 39, 7, 3) + modeRadio(op, 7, 240, 41) +
    `<div class="w-frame" style="${at(267, 11, 70, 48)}">` +
    `<label class="w-radio" style="${at(4, 4)}"><input type="radio" name="ind-${op}-dir" value="+" id="ind-${op}-up"> <span>Up</span></label>` +
    `<label class="w-radio" style="${at(4, 24)}"><input type="radio" name="ind-${op}-dir" value="-" id="ind-${op}-down" checked> <span>Down</span></label>` +
    `</div></div></div>`
  );
}

const SOURCE = { title: 71, valRow: 120, valBox: 110, regRow: 194, regBox: 185, valFrame: 70, valFrameH: 83, regFrame: 158 };
const DEST = { title: 260, valRow: 306, valBox: 296, regRow: 369, regBox: 360, valFrame: 257, valFrameH: 73, regFrame: 340 };

const cycles = Array.from({ length: 10 }, (_, i) => i + 1);

export function layoutHtml() {
  return (
    tabs() +
    `<div class="w-frame" style="${at(6, 52, 662, 460)};background:#f5f5f5"></div>` +
    text("Op Code", 50, 92, "bold") +
    `<ul class="w-listbox" id="ind-ops" style="${at(22, 112, 84, 254)}"></ul>` +
    text("Exec. Clocks", 34, 374) +
    dropdown(cycles, 1, { id: "ind-clocks" }).replace("<select", `<select style="${at(48, 392, 56, 24)}"`) +
    operand("s", "Source Operand", SOURCE) +
    operand("d", "Destination Operand", DEST) +
    text("Memory read cycles", 20, 452) +
    dropdown(cycles, 3, { id: "ind-read" }).replace("<select", `<select style="${at(154, 449, 46, 24)}"`) +
    text("Memory write cycles", 238, 452) +
    dropdown(cycles, 3, { id: "ind-write" }).replace("<select", `<select style="${at(366, 449, 46, 24)}"`) +
    text("Base address", 506, 452) +
    `<input type="text" class="w-text" id="ind-base" readonly style="${at(598, 449, 66, 24)};text-align:right">` +
    `<div class="w-strip" id="ind-desc" style="${at(8, 480, 660, 30)}"></div>` +
    button("NEW LABEL...", { id: "ind-label" }).replace("<button", `<button style="${at(6, 522, 106, 38)}"`) +
    button("NEW INSTRUCTION", { id: "ind-ok" }).replace("<button", `<button style="${at(284, 522, 148, 38)}"`) +
    button("CLOSE", { id: "ind-close" }).replace("<button", `<button style="${at(586, 522, 82, 38)}"`)
  );
}
