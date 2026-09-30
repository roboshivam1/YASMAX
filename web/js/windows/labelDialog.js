/*
 * File: web/js/windows/labelDialog.js
 *
 * The "Apply label" prompt opened by NEW LABEL... in the instruction dialog:
 * "Enter the name of the label", a text box, OK and Cancel.
 *
 * TODO(research): how YASMIN 7.5.50 shows labels in the instruction list
 * and how jumps refer to them. Until that is known, OK reports that labels
 * are not built yet instead of guessing.
 */

import { button } from "../ui/widgets.js";
import { openWindow } from "../ui/window.js";

export function openLabelDialog(ctx) {
  const html =
    '<span class="w-label" style="left:10px;top:12px">Enter the name of the label</span>' +
    button("OK", { id: "lbl-ok" }).replace("<button", '<button style="left:320px;top:8px;width:78px;height:26px"') +
    button("Cancel", { id: "lbl-cancel" }).replace("<button", '<button style="left:320px;top:40px;width:78px;height:26px"') +
    '<input type="text" class="w-text" id="lbl-name" style="left:10px;top:76px;width:388px;height:24px">';
  const win = openWindow({ id: "apply-label", title: "Apply label", width: 408, height: 110, html });
  const input = win.body.querySelector("#lbl-name");
  input.focus();

  async function ok() {
    const name = input.value.trim();
    win.close();
    if (name) await ctx.notYet(`Labels ("${name}")`);
  }
  win.body.querySelector("#lbl-ok").addEventListener("click", ok);
  win.body.querySelector("#lbl-cancel").addEventListener("click", () => win.close());
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") ok();
    if (e.key === "Escape") win.close();
  });
  return win;
}
