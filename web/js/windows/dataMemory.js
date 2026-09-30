/*
 * File: web/js/windows/dataMemory.js
 *
 * The data memory window ("TRAIN: Pid 0"), opened by SHOW PROGRAM DATA
 * MEMORY... Laid out from YASMIN 7.5.50 screenshots.
 *
 *   DATA MEMORY list  PAdd | LAdd | B0..B7 | Data, a "PAGE n" row per page,
 *                     8 bytes per row, Data shows printable ASCII else "."
 *   Initialise Data   Integer / Boolean / String value at an address, UPDATE
 *   Debug control     click a row, edit its 8 bytes in hex, UPDATE;
 *                     B0..B7 "suspend when modified" checkboxes (kept, used
 *                     once execution exists), RESET clears them
 *   Stay on top, Status, SHOW PAGE TABLE..., Pages, Size, RESET ALL, CLOSE
 *
 * PAdd shows "----" as in the screenshot of a program that is not loaded
 * as a process. The window re-reads memory from the engine after every
 * snapshot, so it stays current while programs run.
 */

import { button, dropdown, esc, group } from "../ui/widgets.js";
import { openWindow } from "../ui/window.js";

const at = (l, t, w, h) => `position:absolute;left:${l}px;top:${t}px` + (w ? `;width:${w}px` : "") + (h ? `;height:${h}px` : "");
const btn = (label, id, l, t, w, h) => button(label, { id }).replace("<button", `<button style="${at(l, t, w, h)}"`);
const hex = (b) => b.toString(16).toUpperCase().padStart(2, "0");
const ch = (b) => (b >= 32 && b < 127 ? String.fromCharCode(b) : ".");
const bs = Array.from({ length: 8 }, (_, i) => i);

function html() {
  const head = ["PAdd", "LAdd", ...bs.map((i) => `B${i}`), "Data"];
  const widths = [90, 58, ...bs.map(() => 37), 100];
  return (
    '<span class="w-label bold" style="left:6px;top:4px">DATA MEMORY</span>' +
    `<div class="w-list pale-yellow" id="dm-list" style="${at(4, 22, 620, 366)}"><table><colgroup>` +
    widths.map((w) => `<col style="width:${w}px">`).join("") +
    `</colgroup><thead><tr>${head.map((h) => `<th>${h}</th>`).join("")}</tr></thead><tbody></tbody></table></div>` +
    group("Initialise Data", "", { cls: "dm-init", style: at(4, 400, 292, 158) }) +
    `<label class="w-radio" style="${at(12, 420)}"><input type="radio" name="dm-kind" value="integer"> Integer</label>` +
    `<label class="w-radio" style="${at(12, 445)}"><input type="radio" name="dm-kind" value="boolean" checked> Boolean</label>` +
    `<label class="w-radio" style="${at(12, 470)}"><input type="radio" name="dm-kind" value="string"> String</label>` +
    ["Value:", "Value:", "Value:"].map((v, i) => `<span class="w-label" style="${at(96, 421 + i * 25)}">${v}</span>`).join("") +
    `<input type="text" class="w-text" id="dm-int" style="${at(144, 418, 70, 22)}">` +
    dropdown(["False", "True"], "False", { id: "dm-bool" }).replace("<select", `<select style="${at(144, 443, 70, 22)}"`) +
    `<input type="text" class="w-text" id="dm-str" style="${at(144, 468, 136, 22)}">` +
    `<span class="w-label" style="${at(12, 498)};line-height:14px">Address<br>location</span>` +
    `<select class="w-select" id="dm-addr" style="${at(74, 502, 80, 22)}"></select>` +
    btn("UPDATE", "dm-init-update", 208, 512, 72, 34) +
    group("Debug control", "", { style: at(302, 400, 322, 158) }) +
    `<span class="w-label" style="${at(310, 416)};line-height:15px;font-size:12px">Check boxes to suspend when corresponding<br>data byte addresses are modified by code.</span>` +
    bs.map((i) => `<input type="checkbox" class="dm-watch" style="${at(314 + i * 26.5, 454)}"><span class="w-label" style="${at(312 + i * 26.5, 470)};font-size:12px">B${i}</span>`).join("") +
    bs.map((i) => `<input type="text" class="w-text dm-byte" maxlength="2" style="${at(310 + i * 26.5, 504, 25, 26)};text-align:center">`).join("") +
    btn("RESET", "dm-watch-reset", 528, 468, 84, 32) + btn("UPDATE", "dm-row-update", 528, 506, 84, 32) +
    `<span class="w-label" style="${at(6, 566)}">Stay on top</span><input type="checkbox" id="dm-top" style="${at(88, 568)}">` +
    `<span class="w-label" style="${at(146, 566)}" id="dm-status">Status:</span>` +
    btn("SHOW PAGE\nTABLE...", "dm-pagetable", 4, 592, 104, 40) +
    `<span class="w-label" style="${at(140, 604)}">Pages:</span><input type="text" class="w-text" id="dm-pages" readonly style="${at(190, 600, 48, 24)}">` +
    `<span class="w-label" style="${at(246, 604)}">Size:</span><input type="text" class="w-text" id="dm-size" readonly style="${at(286, 600, 64, 24)}">` +
    btn("RESET ALL", "dm-reset", 398, 592, 106, 40) + btn("CLOSE", "dm-close", 536, 592, 86, 40)
  );
}

export function openDataMemory(ctx, program) {
  const win = openWindow({ id: `data-${program}`, title: `${program}: Pid 0`, width: 630, height: 638, html: html() });
  const $ = (id) => win.body.querySelector(`#${id}`);
  const body = $("dm-list").querySelector("tbody");
  let mem = null;
  let rowAddr = 0;

  function selectRow(addr) {
    rowAddr = addr;
    for (const tr of body.querySelectorAll("tr[data-addr]")) tr.classList.toggle("selected", Number(tr.dataset.addr) === addr);
    win.body.querySelectorAll(".dm-byte").forEach((box, i) => (box.value = hex(mem.bytes[addr + i] ?? 0)));
  }

  function render() {
    const rows = [];
    for (let a = 0; a < mem.size; a += 8) {
      if (a % mem.page_size === 0) rows.push(`<tr class="dm-page"><td colspan="11"><input type="checkbox"> PAGE ${a / mem.page_size}</td></tr>`);
      const b = mem.bytes.slice(a, a + 8);
      rows.push(
        `<tr data-addr="${a}"><td><input type="checkbox"> ----</td><td>${String(a).padStart(4, "0")}</td>` +
          b.map((x) => `<td>${hex(x)}</td>`).join("") + `<td>${esc(b.map(ch).join(""))}</td></tr>`,
      );
    }
    body.innerHTML = rows.join("");
    $("dm-pages").value = mem.pages;
    $("dm-size").value = mem.size;
    if ($("dm-addr").options.length !== mem.size) {
      $("dm-addr").innerHTML = Array.from({ length: mem.size }, (_, i) => `<option>${i}</option>`).join("");
    }
    selectRow(Math.min(rowAddr, mem.size - 8));
  }

  async function reload() {
    const reply = await ctx.engine.call("data_memory", { program });
    if (!reply.ok) return win.close(); // program was removed
    mem = reply.result;
    render();
  }

  body.addEventListener("click", (e) => {
    const tr = e.target.closest("tr[data-addr]");
    if (tr) selectRow(Number(tr.dataset.addr));
  });
  $("dm-init-update").addEventListener("click", () => {
    const kind = win.body.querySelector('input[name="dm-kind"]:checked').value;
    const value = { integer: $("dm-int").value, boolean: $("dm-bool").value, string: $("dm-str").value }[kind];
    ctx.send("write_data", { program, address: $("dm-addr").value, kind, value });
  });
  $("dm-row-update").addEventListener("click", () => {
    const values = [...win.body.querySelectorAll(".dm-byte")].map((b) => b.value);
    ctx.send("write_data_bytes", { program, address: rowAddr, values });
  });
  $("dm-watch-reset").addEventListener("click", () => win.body.querySelectorAll(".dm-watch").forEach((c) => (c.checked = false)));
  $("dm-reset").addEventListener("click", () => ctx.send("reset_data_memory", { program }));
  $("dm-top").addEventListener("change", (e) => win.setStayOnTop(e.target.checked));
  $("dm-pagetable").addEventListener("click", () => ctx.notAvailable("The page table"));
  $("dm-close").addEventListener("click", () => win.close());

  const unsubscribe = ctx.store.subscribe(() => reload());
  const close = win.close;
  win.close = () => { unsubscribe(); close(); };
  return win;
}
