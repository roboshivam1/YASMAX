/*
 * File: web/js/windows/console.js
 *
 * The Console window (opened by INPUT OUTPUT...), laid out from a YASMIN
 * 7.5.50 screenshot: a grey OUTPUT screen, INPUT box, SHOW, Stay on top,
 * No output display, Colours (screen / text colour), Fonts, PRINT, CLEAR,
 * CLOSE.
 *
 * The OUT instruction will call consoleWrite(); IN will read what the user
 * typed via takeInput(). Output is kept while the window is closed, so
 * nothing is lost if a program prints with the console hidden.
 * TODO(research): the bottom of the window was cut off in the screenshot,
 * so the second colour option ("Text colour"), the Fonts button and what
 * SHOW and PRINT do are not confirmed. SHOW, Fonts and PRINT report "not
 * built yet" rather than guessing.
 */

import { button, group } from "../ui/widgets.js";
import { openWindow } from "../ui/window.js";

let output = "";
const inputQueue = [];
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

/** Next line the user typed into INPUT, or undefined (used by IN). */
export function takeInput() {
  return inputQueue.shift();
}

const at = (l, t, w, h) => `position:absolute;left:${l}px;top:${t}px` + (w ? `;width:${w}px` : "") + (h ? `;height:${h}px` : "");
const btn = (label, id, l, t, w, h) => button(label, { id }).replace("<button", `<button style="${at(l, t, w, h)}"`);

function html() {
  return (
    '<span class="w-label bold" style="left:6px;top:4px">OUTPUT</span>' +
    `<pre id="con-out" style="${at(4, 24, 896, 410)};margin:0;padding:4px 6px;box-sizing:border-box;overflow-y:scroll;` +
    `white-space:pre-wrap;font:15px var(--font-mono);border:1px solid #828790"></pre>` +
    '<span class="w-label bold" style="left:6px;top:446px">INPUT</span>' +
    `<input type="text" class="w-text" id="con-in" style="${at(6, 468, 48, 26)}">` +
    btn("SHOW", "con-show", 62, 452, 76, 34) +
    `<span class="w-label" style="${at(146, 452)}">Stay on top</span><input type="checkbox" id="con-top" style="${at(256, 454)}">` +
    `<span class="w-label" style="${at(146, 474)}">No output display</span><input type="checkbox" id="con-quiet" style="${at(256, 476)}">` +
    group("Colours", "", { style: at(290, 448, 206, 62) }) +
    `<span class="w-label" style="${at(300, 460)}">Screen colour</span><input type="radio" name="con-col" value="screen" checked style="${at(404, 462)}">` +
    `<span class="w-label" style="${at(300, 482)}">Text colour</span><input type="radio" name="con-col" value="text" style="${at(404, 484)}">` +
    btn("", "con-colour", 424, 462, 60, 36) + `<input type="color" id="con-picker" style="display:none">` +
    group("Fonts", "", { style: at(502, 448, 96, 62) }) +
    btn("", "con-font", 518, 462, 62, 36) +
    btn("PRINT", "con-print", 614, 458, 82, 40) +
    btn("CLEAR", "con-clear", 726, 458, 82, 40) +
    btn("CLOSE", "con-close", 822, 454, 84, 44)
  );
}

export function openConsole(ctx) {
  const win = openWindow({ id: "console", title: "Console", width: 910, height: 516, html: html() });
  const $ = (id) => win.body.querySelector(`#${id}`);
  const out = $("con-out");

  redraw = () => {
    out.textContent = output;
    out.style.background = screen;
    out.style.color = ink;
    $("con-colour").style.background = win.body.querySelector('input[name="con-col"]:checked').value === "screen" ? screen : ink;
    out.scrollTop = out.scrollHeight;
  };
  redraw();

  $("con-in").addEventListener("keydown", (e) => {
    if (e.key !== "Enter") return;
    inputQueue.push(e.target.value);
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
  $("con-show").addEventListener("click", () => ctx.notYet("Console SHOW"));
  $("con-font").addEventListener("click", () => ctx.notYet("Console fonts"));
  $("con-print").addEventListener("click", () => ctx.notYet("Console PRINT"));
  $("con-clear").addEventListener("click", () => { output = ""; redraw(); });
  $("con-close").addEventListener("click", () => win.close());

  const close = win.close;
  win.close = () => { redraw = null; close(); };
  return win;
}
