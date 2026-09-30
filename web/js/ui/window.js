/*
 * File: web/js/ui/window.js
 *
 * Floating tool windows: the instruction dialog, data memory window,
 * console and small prompts. YASMIN opens these as separate Windows
 * windows; YASMAX draws them inside the page in the same Win7 style as the
 * main window.
 *
 *     const win = openWindow({ id: "console", title: "Console", width, height, html });
 *     win.body       // the client area, lay controls out inside it
 *     win.close()    // also called by the X button
 *
 * - Windows live inside #stage, so they scale with the main window.
 * - Drag by the title bar. Positions are in "original" pixels, so dragging
 *   divides the mouse movement by the current zoom.
 * - Clicking a window brings it to the front. setStayOnTop(true) keeps it
 *   above the others (the "Stay on top" checkboxes).
 * - Opening an id that is already open just brings it to the front.
 * Styles are in css/windows.css.
 */

import { esc } from "./widgets.js";

const open = new Map(); // id -> window handle
let zTop = 20;

function stage() {
  return document.getElementById("stage");
}

function zoom() {
  const s = stage();
  return s.getBoundingClientRect().width / s.offsetWidth || 1;
}

export function isOpen(id) {
  return open.has(id);
}

export function openWindow({ id, title, width, height, html = "", x, y, onClose }) {
  if (open.has(id)) {
    open.get(id).focus();
    return open.get(id);
  }

  const el = document.createElement("div");
  el.className = "w-float";
  el.style.width = `${width}px`;
  el.innerHTML =
    `<div class="w-float-title"><span class="w-float-icon"></span><span class="w-float-text">${esc(title)}</span>` +
    `<span class="w-float-x" title="Close">x</span></div>` +
    `<div class="w-float-client w-client" style="height:${height}px">${html}</div>`;

  // Default position: centred in the visible stage, cascading a little.
  const s = stage();
  const left = x ?? Math.max(10, (s.offsetWidth - width) / 2 + open.size * 24);
  const top = y ?? Math.max(10, (s.offsetHeight - height) / 3 + open.size * 24);
  el.style.left = `${left}px`;
  el.style.top = `${top}px`;
  s.append(el);

  const win = {
    el,
    body: el.querySelector(".w-float-client"),
    stayOnTop: false,
    focus() {
      el.style.zIndex = String((win.stayOnTop ? 1000 : 0) + ++zTop);
    },
    setTitle(text) {
      el.querySelector(".w-float-text").textContent = text;
    },
    setStayOnTop(on) {
      win.stayOnTop = on;
      win.focus();
    },
    close() {
      el.remove();
      open.delete(id);
      onClose?.();
    },
  };

  el.addEventListener("pointerdown", () => win.focus(), true);
  el.querySelector(".w-float-x").addEventListener("click", () => win.close());

  // Dragging by the title bar.
  const bar = el.querySelector(".w-float-title");
  bar.addEventListener("pointerdown", (event) => {
    if (event.target.classList.contains("w-float-x")) return;
    const startX = event.clientX;
    const startY = event.clientY;
    const baseX = el.offsetLeft;
    const baseY = el.offsetTop;
    const z = zoom();
    bar.setPointerCapture(event.pointerId);
    const move = (e) => {
      el.style.left = `${baseX + (e.clientX - startX) / z}px`;
      el.style.top = `${Math.max(0, baseY + (e.clientY - startY) / z)}px`;
    };
    const up = () => {
      bar.removeEventListener("pointermove", move);
      bar.removeEventListener("pointerup", up);
    };
    bar.addEventListener("pointermove", move);
    bar.addEventListener("pointerup", up);
  });

  open.set(id, win);
  win.focus();
  return win;
}
