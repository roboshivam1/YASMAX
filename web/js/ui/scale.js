/*
 * File: web/js/ui/scale.js
 *
 * Makes the YASMIN window fill the whole browser window, like a maximized
 * Windows form, without distorting it.
 *
 * How:
 *   1. Pick one uniform zoom `s` so the ORIGINAL window (1482 x 992 incl.
 *      the disclaimer line) just fits the browser. Text is never stretched.
 *   2. At that zoom, the browser is usually wider or taller than the
 *      original. That leftover space is handed to the layout as two CSS
 *      variables on #stage:
 *        --ex  extra width PER COLUMN (the window has 4 columns)
 *        --ey  extra height for the upper panels
 *      css/layout.css adds them to widths, heights and positions with
 *      calc(), so the lists grow and everything else keeps its place.
 *   3. Lists re-pad their empty grid rows for the new size (onResize).
 */

const BASE_WIDTH = 1482;
const BASE_HEIGHT = 966;
const DISCLAIMER = 26;
const COLUMNS = 4;

export function fitToScreen(stageEl, { onResize } = {}) {
  function apply() {
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const scale = Math.min(vw / BASE_WIDTH, vh / (BASE_HEIGHT + DISCLAIMER));

    // Size of the browser window measured in "original" pixels.
    const width = vw / scale;
    const height = vh / scale;
    const extraX = Math.max(0, (width - BASE_WIDTH) / COLUMNS);
    const extraY = Math.max(0, height - DISCLAIMER - BASE_HEIGHT);

    stageEl.style.setProperty("--ex", `${extraX.toFixed(2)}px`);
    stageEl.style.setProperty("--ey", `${extraY.toFixed(2)}px`);
    stageEl.style.width = `${width}px`;
    stageEl.style.height = `${height}px`;
    stageEl.style.transformOrigin = "0 0";
    stageEl.style.transform = `scale(${scale})`;

    onResize?.();
  }

  let pending = 0;
  window.addEventListener("resize", () => {
    cancelAnimationFrame(pending);
    pending = requestAnimationFrame(apply);
  });
  apply();
}
