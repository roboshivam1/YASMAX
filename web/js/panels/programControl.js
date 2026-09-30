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
 * STEP / RUN / STOP go through ctx.runner (js/runner.js). STEP does one
 * instruction, or one phase (FETCH, DECODE, EXECUTE) "by single tick".
 * RESET PROGRAM empties the stack and puts PC on the top instruction.
 * Buttons are enabled only when there is something in memory; while RUN
 * is going, only STOP is. SHOW PCB... belongs to the OS simulator.
 * TODO(R-15): confirm the original's enable rules.
 *
 * CPU Help tab: credit to the original, the YASMAX disclaimer (PRD F-51),
 * who made it, links to the guide and bug reports, and the build id.
 * CPU View tab: empty until captured from the original (UI_SPEC U-5).
 */

import { BUILD } from "../build.js";
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
  "<p><b>YASMAX</b>: Yet Another Simple Machine Architecture eXplorer. A non-commercial educational " +
  "recreation of the <b>YASMIN CPU-OS Simulator</b> by <b>Besim Mustafa</b> (Edge Hill University). " +
  "Not affiliated with or endorsed by him.</p>" +
  '<p>Assembled with <span style="color:#d0243c">&hearts;</span> (and a lot of MOV instructions) by ' +
  '<b>Shivam Kapoor</b> &middot; <a href="https://shvmkpr.in" target="_blank" rel="noopener">shvmkpr.in</a></p>' +
  '<p><a href="https://github.com/roboshivam1/YASMAX/blob/main/docs/USER_GUIDE.md" target="_blank" rel="noopener">User guide</a> &middot; ' +
  '<a href="https://github.com/roboshivam1/YASMAX/issues/new/choose" target="_blank" rel="noopener">Report a bug or a difference</a><br>' +
  'Build <span id="build-id"></span></p>' +
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

export function mount(el, ctx) {
  const { ui, runner, send, store, notAvailable } = ctx;
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
  el.querySelector("#build-id").textContent = BUILD;

  const $ = (id) => el.querySelector(`#${id}`);
  $("btn-step").addEventListener("click", () => runner.step());
  $("btn-run").addEventListener("click", () => runner.run());
  $("btn-stop").addEventListener("click", () => runner.stop());
  $("btn-reset-prog").addEventListener("click", () => send("reset_program"));
  $("btn-show-pcb").addEventListener("click", () => notAvailable("The process control block (PCB)"));

  function refresh() {
    const loaded = (store.get()?.memory.length ?? 0) > 0;
    for (const id of ["btn-step", "btn-run", "btn-reset-prog"]) $(id).disabled = !loaded || runner.running;
    $("btn-stop").disabled = !runner.running;
    $("btn-show-pcb").disabled = !loaded;
  }
  store.subscribe(refresh);
  document.addEventListener("yasmax:running", refresh);
}
