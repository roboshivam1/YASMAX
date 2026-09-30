/*
 * File: web/js/ui/messageBox.js
 *
 * A Windows 7 style message box (title, text, OK button) drawn inside the
 * page, used for errors, "not available" and "not built yet" notices.
 *
 *     await messageBox("CPU Simulator", "Please enter a whole number.");
 *
 * It returns a promise that resolves when the user clicks OK or presses
 * Enter/Escape, so callers can wait for it just like the modal dialogs
 * in the original. Styles are in css/dialogs.css.
 */

import { esc } from "./widgets.js";

export function messageBox(title, text, { icon = "info" } = {}) {
  return new Promise((resolve) => {
    const backdrop = document.createElement("div");
    backdrop.className = "w-modal-backdrop";
    backdrop.innerHTML =
      `<div class="w-dialog" role="alertdialog" aria-label="${esc(title)}">` +
      `<div class="w-dialog-title">${esc(title)}<span class="w-dialog-x">x</span></div>` +
      `<div class="w-dialog-body"><span class="w-dialog-icon ${icon}"></span><p>${esc(text).replaceAll("\n", "<br>")}</p></div>` +
      `<div class="w-dialog-foot"><button type="button" class="w-btn w-dialog-ok">OK</button></div>` +
      `</div>`;

    function close() {
      document.removeEventListener("keydown", onKey, true);
      backdrop.remove();
      resolve();
    }
    function onKey(event) {
      if (event.key === "Enter" || event.key === "Escape") {
        event.preventDefault();
        close();
      }
    }

    backdrop.querySelector(".w-dialog-ok").addEventListener("click", close);
    backdrop.querySelector(".w-dialog-x").addEventListener("click", close);
    document.addEventListener("keydown", onKey, true);
    document.body.append(backdrop);
    backdrop.querySelector(".w-dialog-ok").focus();
  });
}

/** The standard notice for parts of YASMIN that YASMAX does not recreate. */
export function notAvailable(feature) {
  return messageBox(
    "YASMAX",
    `${feature} is part of the full YASMIN CPU-OS Simulator and is not available in YASMAX yet.\n` +
      "YASMAX recreates the CPU Simulator window only.",
  );
}

/** Notice for YASMAX features that are planned but not built yet. */
export function notYet(feature) {
  return messageBox("YASMAX", `${feature} is not built yet. It will arrive in a later version of YASMAX.`);
}
