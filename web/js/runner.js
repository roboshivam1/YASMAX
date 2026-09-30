/*
 * File: web/js/runner.js
 *
 * Running programs from the UI: STEP, RUN and STOP (Program Control tab),
 * shared with the memory view (double-click) and the Execution Unit tab.
 *
 *   step()  one instruction, or one phase when "by single tick" is chosen
 *   run()   keeps stepping until HLT, the end of the program, a breakpoint
 *           (memory view checkbox), a data watch, an error or STOP.
 *           The Fast..Slow slider sets the pause between instructions.
 *   stop()  asks run() to stop after the current instruction.
 *
 * The engine does the work; each step is one ctx.send(), which also shows
 * console output and messages (main.js). Whenever running starts or stops,
 * a "yasmax:running" event (detail true/false) lets buttons update.
 * TODO(R-18): the real speeds of the original slider positions.
 */

const DELAYS_MS = [0, 60, 150, 300, 600, 1000]; // slider position 0 = Fast
const STOPS = new Set(["halt", "end", "breakpoint", "watch"]);
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export function createRunner(ctx) {
  let running = false;
  let stopAsked = false;

  function announce() {
    document.dispatchEvent(new CustomEvent("yasmax:running", { detail: running }));
  }

  return {
    get running() {
      return running;
    },

    step() {
      if (running) return null;
      return ctx.send(ctx.ui.stepMode === "clock" ? "tick" : "step");
    },

    async run() {
      if (running) return;
      running = true;
      stopAsked = false;
      announce();
      let first = true;
      try {
        while (!stopAsked) {
          // The first step always runs, so RUN can leave a breakpoint.
          const reply = await ctx.send("step", { stop_at_breakpoint: !first });
          first = false;
          if (!reply.ok || reply.events.some((e) => STOPS.has(e.type))) break;
          await sleep(DELAYS_MS[ctx.ui.speed] ?? 0);
        }
      } finally {
        running = false;
        announce();
      }
    },

    stop() {
      stopAsked = true;
    },
  };
}
