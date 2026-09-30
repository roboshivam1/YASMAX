/*
 * File: web/js/windows/console.js
 *
 * The Console window (opened by INPUT OUTPUT...), laid out from a YASMIN
 * 7.5.50 screenshot: grey OUTPUT screen, INPUT box, SHOW KEYBD..., Stay on
 * top, No output display, Display CPU id, Colours (Screen colour / Text
 * colour + SET...), Fonts SET..., PRINT..., CLEAR, CLOSE.
 *
 * OUT's text arrives as "output" events; main.js calls consoleWrite().
 * Output is kept while the window is closed. A line typed into INPUT and
 * ended with Enter goes to the engine (console_input), where IN reads it.
 * TODO(research): SHOW KEYBD..., Display CPU id, Fonts and PRINT (they
 * report "not built yet"); whether IN waits for input.
 */

import { button, group } from "../ui/widgets.js";
import { openWindow } from "../ui/window.js";

let output = "";
let screen = "#646464";
let ink = "#ffffff";
let suppressed = false;
let redraw = null; // set while the window is open

/** Append text to the console (used by OUT). */
export function consoleWrite(text) {
  if (suppressed) return;
  output += text;
  redraw?.();
}


const at = (l, t, w, h) => `position:absolute;left:${l}px;top:${t}px` + (w ? `;width:${w}px` : "") + (h ? `;height:${h}px` : "");
const btn = (label, id, l, t, w, h) => button(label, { id }).replace("<button", `<button style="${at(l, t, w, h)}"`);

function html() {
  const check = (text, id, t) =>
    `<span class="w-label" style="${at(150, t)}">${text}</span><input type="checkbox" id="${id}" style="${at(262, t + 2)}">`;
  return (
    '<span class="w-label bold" style="left:8px;top:2px">OUTPUT</span>' +
    `<pre id="con-out" style="${at(6, 22, 896, 408)};margin:0;padding:4px 6px;box-sizing:border-box;overflow-y:scroll;` +
    `white-space:pre-wrap;font:15px var(--font-mono);border:1px solid #828790"></pre>` +
    '<span class="w-label bold" style="left:10px;top:444px">INPUT</span>' +
    `<input type="text" class="w-text" id="con-in" style="${at(8, 466, 44, 30)}">` +
    btn("SHOW\nKEYBD...", "con-show", 64, 452, 76, 46) +
    check("Stay on top", "con-top", 450) + check("No output display", "con-quiet", 471) +
    check("Display CPU id", "con-cpuid", 492) +
    group("Colours", "", { style: at(290, 446, 214, 66) }) +
    `<span class="w-label" style="${at(300, 468)}">Screen colour</span><input type="radio" name="con-col" value="screen" checked style="${at(404, 470)}">` +
    `<span class="w-label" style="${at(300, 489)}">Text colour</span><input type="radio" name="con-col" value="text" style="${at(404, 491)}">` +
    btn("SET...", "con-colour", 428, 466, 60, 32) + '<input type="color" id="con-picker" style="display:none">' +
    group("Fonts", "", { style: at(508, 446, 98, 66) }) +
    btn("SET...", "con-font", 522, 466, 64, 32) +
    btn("PRINT...", "con-print", 616, 456, 84, 44) +
    btn("CLEAR", "con-clear", 728, 456, 84, 44) +
    btn("CLOSE", "con-close", 824, 450, 86, 48)
  );
}

export function openConsole(ctx) {
  const win = openWindow({ id: "console", title: "Console", width: 912, height: 516, html: html() });
  const $ = (id) => win.body.querySelector(`#${id}`);
  const out = $("con-out");

  redraw = () => {
    out.textContent = output;
    out.style.background = screen;
    out.style.color = ink;
    out.scrollTop = out.scrollHeight;
  };
  redraw();

  $("con-in").addEventListener("keydown", (e) => {
    if (e.key !== "Enter") return;
    ctx.send("console_input", { text: e.target.value });
    e.target.value = "";
  });
  $("con-top").addEventListener("change", (e) => win.setStayOnTop(e.target.checked));
  $("con-quiet").checked = suppressed;
  $("con-quiet").addEventListener("change", (e) => (suppressed = e.target.checked));
  win.body.addEventListener("change", (e) => e.target.name === "con-col" && redraw());
  $("con-colour").addEventListener("click", () => {
    const which = win.body.querySelector('input[name="con-col"]:checked').value;
    $("con-picker").value = which === "screen" ? screen : ink;
    $("con-picker").click();
  });
  $("con-picker").addEventListener("input", (e) => {
    if (win.body.querySelector('input[name="con-col"]:checked').value === "screen") screen = e.target.value;
    else ink = e.target.value;
    redraw();
  });
  $("con-show").addEventListener("click", () => ctx.notYet("The on-screen keyboard"));
  $("con-cpuid").addEventListener("change", () => ctx.notYet("Display CPU id"));
  $("con-font").addEventListener("click", () => ctx.notYet("Console fonts"));
  $("con-print").addEventListener("click", () => ctx.notYet("Console PRINT"));
  $("con-clear").addEventListener("click", () => { output = ""; redraw(); });
  $("con-close").addEventListener("click", () => win.close());

  const close = win.close;
  win.close = () => { redraw = null; close(); };
  return win;
}
