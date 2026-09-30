/*
 * File: web/js/panels/programControl.js
 *
 * Region I: the Program Control / CPU View / CPU Help tab control.
 *
 * Program Control tab:
 *   STEP, RUN, STOP        stacked on the left
 *   by instruction / by single tick   step mode (label as in YASMIN 7.5.50)
 *   Fast..Slow slider      RUN speed (a Win7 vertical trackbar)
 *   RESET PROGRAM, SHOW PCB...
 *
 * The execution buttons start disabled, as in the screenshot with no
 * program loaded. They are wired up when the engine can step (later batch).
 * The step mode and speed already work: they are kept in ctx.ui, where the
 * RUN code will read them.
 * TODO(R-18): map slider positions to real run speeds.
 *
 * CPU Help tab: credit to the original and the YASMAX disclaimer (PRD F-51).
 * CPU View tab: empty until captured from the original (UI_SPEC U-5).
 */

import { button, radio, tabs } from "../ui/widgets.js";

const SPEED_STEPS = 6; // tick marks on the original slider
const TRACK_TOP = 6;
const TRACK_STEP = 15.6; // px between ticks

function controlTab() {
  const ticks = Array.from({ length: SPEED_STEPS }, (_, i) => `<span class="tick" style="top:${TRACK_TOP + i * TRACK_STEP}px"></span>`).join("");
  return (
    button("STEP", { id: "btn-step", disabled: true }) +
    button("RUN", { id: "btn-run", disabled: true }) +
    button("STOP", { id: "btn-stop", disabled: true }) +
    radio("step-mode", "by instruction", { id: "mode-instr", value: "instruction", checked: true }) +
    radio("step-mode", "by single tick", { id: "mode-clock", value: "clock" }) +
    '<span class="w-label" id="lbl-fast">Fast</span><span class="w-label" id="lbl-slow">Slow</span>' +
    `<div id="speed" role="slider" tabindex="0" aria-label="Run speed" aria-valuemin="0" aria-valuemax="${SPEED_STEPS - 1}">` +
    `<span class="track"></span>${ticks}<span class="thumb"></span></div>` +
    button("RESET\nPROGRAM", { id: "btn-reset-prog", disabled: true }) +
    button("SHOW PCB...", { id: "btn-show-pcb", disabled: true })
  );
}

const HELP =
  '<div class="about">' +
  "<p><b>YASMAX</b>: Yet Another Simple Machine Architecture eXplorer.</p>" +
  "<p>An independent, non-commercial educational recreation of the CPU Simulator window of the " +
  "<b>YASMIN CPU-OS Simulator</b> by <b>Besim Mustafa, Edge Hill University</b>, for students " +
  "who cannot run the Windows-only original.</p>" +
  "<p>Not affiliated with or endorsed by the original author. No commercial use.</p>" +
  "</div>";

/** Wire the vertical speed slider. Position 0 is Fast (top). */
function wireSpeed(slider, ui) {
  const thumb = slider.querySelector(".thumb");
  function set(step) {
    ui.speed = Math.max(0, Math.min(SPEED_STEPS - 1, step));
    thumb.style.top = `${TRACK_TOP + ui.speed * TRACK_STEP}px`;
    slider.setAttribute("aria-valuenow", String(ui.speed));
  }
  function fromPointer(event) {
    const y = event.clientY - slider.getBoundingClientRect().top;
    const scale = slider.getBoundingClientRect().height / slider.offsetHeight;
    set(Math.round((y / scale - TRACK_TOP) / TRACK_STEP));
  }
  slider.addEventListener("pointerdown", (event) => {
    slider.setPointerCapture(event.pointerId);
    fromPointer(event);
  });
  slider.addEventListener("pointermove", (event) => {
    if (slider.hasPointerCapture(event.pointerId)) fromPointer(event);
  });
  slider.addEventListener("keydown", (event) => {
    if (event.key === "ArrowUp") set(ui.speed - 1);
    if (event.key === "ArrowDown") set(ui.speed + 1);
  });
  set(ui.speed);
}

export function mount(el, { ui }) {
  el.classList.add("bottom");
  el.innerHTML = tabs(
    [
      { label: "Program Control", html: controlTab() },
      { label: "CPU View", html: "" },
      { label: "CPU Help", html: HELP },
    ],
    0,
  );

  for (const r of el.querySelectorAll('input[name="step-mode"]')) {
    r.addEventListener("change", () => {
      ui.stepMode = r.value;
    });
  }
  wireSpeed(el.querySelector("#speed"), ui);
}
