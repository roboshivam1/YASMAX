/*
 * File: web/js/ui/widgets.js
 *
 * Small helpers that return HTML strings for the Windows 7 style controls
 * the YASMIN window is made of: group boxes, buttons, tabs, read-only
 * value fields, checkboxes, radios and dropdowns. List views live in
 * js/ui/lists.js.
 *
 * Why strings instead of a framework? The window is a fixed replica, so
 * panels build their markup once with these helpers (innerHTML) and then
 * only update individual cells. That keeps every panel file short and easy
 * to compare against the screenshot.
 *
 * All styling lives in css/win7.css (the look) and css/layout.css (where
 * each panel sits). These helpers only emit class names.
 */

/** Escape text before putting it inside HTML. */
export function esc(text) {
  return String(text ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

/**
 * True if snapshot section `key` is the same in `prev` and `snap`.
 * Snapshots are fresh JSON every time, so === never matches; compare values.
 * Panels use this to skip redrawing sections that did not change.
 */
export function unchanged(prev, snap, key) {
  return prev != null && JSON.stringify(prev[key]) === JSON.stringify(snap[key]);
}

/** Turn {id: "x", cls: "y"} into ' id="x" class="y"'. */
export function attrs({ id, cls, style } = {}) {
  return (id ? ` id="${id}"` : "") + (cls ? ` class="${cls}"` : "") + (style ? ` style="${style}"` : "");
}

/**
 * Group box: a thin rounded frame with a caption sitting on its top edge
 * ("Pipeline", "PROGRAM LIST", ...). A plain div rather than <fieldset>,
 * because fieldset legends are placed differently by each browser.
 */
export function group(caption, inner = "", opts = {}) {
  const cls = `w-group ${opts.cls ?? ""}`;
  return `<div${attrs({ ...opts, cls })}><span class="w-legend">${esc(caption)}</span>${inner}</div>`;
}

/** Push button. "\n" in the label becomes a line break, as in "SHOW\nPIPELINE...". */
export function button(label, opts = {}) {
  const text = esc(label).replaceAll("\n", "<br>");
  const disabled = opts.disabled ? " disabled" : "";
  return `<button type="button"${attrs({ ...opts, cls: `w-btn ${opts.cls ?? ""}` })}${disabled}>${text}</button>`;
}

/**
 * Tab control. `tabs` is [{label, html}], `active` is the selected index.
 * Call wireTabs(root) once after inserting the HTML to make tabs clickable.
 */
export function tabs(tabList, active = 0, opts = {}) {
  const strip = tabList
    .map((t, i) => `<li class="w-tab${i === active ? " active" : ""}" data-tab="${i}">${esc(t.label)}</li>`)
    .join("");
  const panes = tabList
    .map((t, i) => `<div class="w-tabpane" data-pane="${i}"${i === active ? "" : " hidden"}>${t.html ?? ""}</div>`)
    .join("");
  return `<div${attrs({ ...opts, cls: `w-tabs ${opts.cls ?? ""}` })}><ul class="w-tabstrip">${strip}</ul><div class="w-tabbody">${panes}</div></div>`;
}

/** Make every tab control inside `root` switch panes on click. */
export function wireTabs(root) {
  for (const control of root.querySelectorAll(".w-tabs")) {
    control.querySelector(".w-tabstrip").addEventListener("click", (event) => {
      const tab = event.target.closest(".w-tab");
      if (!tab) return;
      const index = tab.dataset.tab;
      for (const t of control.querySelectorAll(":scope > .w-tabstrip > .w-tab")) {
        t.classList.toggle("active", t.dataset.tab === index);
      }
      for (const p of control.querySelectorAll(":scope > .w-tabbody > .w-tabpane")) {
        p.hidden = p.dataset.pane !== index;
      }
    });
  }
}

/** Read-only value box (PC, SP, IR...). */
export function valueBox(value, opts = {}) {
  return `<div${attrs({ ...opts, cls: `w-value ${opts.cls ?? ""}` })}>${esc(value)}</div>`;
}

/** Text input box. */
export function textBox(value = "", opts = {}) {
  return `<input type="text"${attrs({ ...opts, cls: `w-text ${opts.cls ?? ""}` })} value="${esc(value)}">`;
}

/** Checkbox, optionally with a label on the left (as in "Show Reg Access Status"). */
export function checkbox({ label, checked = false, disabled = false, ...opts } = {}) {
  const box = `<input type="checkbox"${attrs(opts)}${checked ? " checked" : ""}${disabled ? " disabled" : ""}>`;
  return label ? `<label class="w-check">${esc(label)} ${box}</label>` : box;
}

/** Radio button with a label on the right. `id` goes on the label, so layout.css can position it. */
export function radio(name, label, { checked = false, disabled = false, id, value } = {}) {
  const state = (checked ? " checked" : "") + (disabled ? " disabled" : "");
  const val = value != null ? ` value="${esc(value)}"` : "";
  return `<label${attrs({ id, cls: `w-radio${disabled ? " disabled" : ""}` })}><input type="radio" name="${name}"${val}${state}> ${esc(label)}</label>`;
}

/** Dropdown (ComboBox in DropDownList style). */
export function dropdown(options, selected, opts = {}) {
  const items = options
    .map((o) => `<option${String(o) === String(selected) ? " selected" : ""}>${esc(o)}</option>`)
    .join("");
  return `<select${attrs({ ...opts, cls: `w-select ${opts.cls ?? ""}` })}>${items}</select>`;
}
