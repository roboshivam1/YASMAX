/*
 * File: web/js/ui/balloon.js
 *
 * The Windows balloon tooltip ("i Help" with a tail) that YASMIN 7.5.50
 * shows when the mouse rests over the instruction memory view.
 *
 *     attachBalloon(el, (target) => ({ title, lines }) or null)
 *
 * After the mouse rests on `el` for DELAY ms, the callback is asked what
 * to show for the element under the mouse; null shows nothing. Any mouse
 * press, scroll or leaving the element hides it. Lives inside #stage, so
 * it scales with the window. Styles: css/execution.css (.w-balloon).
 */

import { esc } from "./widgets.js";

const DELAY = 900;

export function attachBalloon(el, content) {
  let timer = null;
  let tip = null;

  function hide() {
    clearTimeout(timer);
    tip?.remove();
    tip = null;
  }

  function show(event) {
    const what = content(document.elementFromPoint(event.clientX, event.clientY));
    if (!what) return;
    const stage = document.getElementById("stage");
    const box = stage.getBoundingClientRect();
    const zoom = box.width / stage.offsetWidth || 1;
    tip = document.createElement("div");
    tip.className = "w-balloon";
    tip.innerHTML =
      `<div class="w-balloon-title"><span class="w-balloon-i">i</span>${esc(what.title)}</div>` +
      what.lines.map((l) => `<div>${l === "" ? "&nbsp;" : esc(l)}</div>`).join("");
    stage.append(tip);
    // Like Windows: the balloon sits above the pointer, its tail pointing down.
    const y = (event.clientY - box.top) / zoom - tip.offsetHeight - 18;
    tip.style.left = `${(event.clientX - box.left) / zoom - 22}px`;
    tip.style.top = `${Math.max(4, y)}px`;
  }

  el.addEventListener("mousemove", (event) => {
    if (tip) return;
    clearTimeout(timer);
    timer = setTimeout(() => show(event), DELAY);
  });
  el.addEventListener("mouseleave", hide);
  el.addEventListener("mousedown", hide);
  el.addEventListener("wheel", hide, { passive: true });
}
