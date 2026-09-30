/*
 * File: web/js/main.js
 *
 * Boots the YASMAX page:
 *   1. Make the window fill the browser (js/ui/scale.js).
 *   2. Mount every panel into its region, so the window is visible at
 *      once, before Python has loaded.
 *   3. Start the engine worker, show boot progress in the overlay, and
 *      publish the first snapshot, which makes the panels fill in.
 *
 * Every panel gets the same `ctx` object:
 *   store        latest snapshot + subscribe()        (js/store.js)
 *   engine       call(cmd, args) to the worker        (js/bridge.js)
 *   send         call + publish snapshot + show any error dialog; also puts
 *                console output in the Console and shows HLT / end /
 *                breakpoint messages (events from the engine)
 *   runner       STEP / RUN / STOP                    (js/runner.js)
 *   ui           UI-only settings (step mode, run speed) shared by panels
 *   notAvailable notice for YASMIN parts YASMAX won't recreate
 *   notYet       notice for YASMAX features not built yet
 *   isa          the instruction set table sent by the engine at boot
 *
 * window.yasmax exposes send/store/engine for testing in the browser console.
 */

import { BUILD } from "./build.js";
import { createEngine } from "./bridge.js";
import { createRunner } from "./runner.js";
import { consoleWrite } from "./windows/console.js";
import { createStore } from "./store.js";
import { refillAll } from "./ui/lists.js";
import { messageBox, notAvailable, notYet } from "./ui/messageBox.js";
import { fitToScreen } from "./ui/scale.js";
import { wireTabs } from "./ui/widgets.js";
import * as advanced from "./panels/advanced.js";
import * as cachePipeline from "./panels/cachePipeline.js";
import * as gpRegs from "./panels/gpRegs.js";
import * as memoryView from "./panels/memoryView.js";
import * as programControl from "./panels/programControl.js";
import * as programList from "./panels/programList.js";
import * as programTabs from "./panels/programTabs.js";
import * as regTabs from "./panels/regTabs.js";
import * as specialRegs from "./panels/specialRegs.js";
import * as stackView from "./panels/stackView.js";

// region id -> panel module (region letters: docs/UI_SPEC.md §2)
const PANELS = {
  "p-memory": memoryView,
  "p-cache": cachePipeline,
  "p-proglist": programList,
  "p-special": specialRegs,
  "p-stack": stackView,
  "p-gpr": gpRegs,
  "p-progtabs": programTabs,
  "p-control": programControl,
  "p-advanced": advanced,
  "p-regtabs": regTabs,
};

const store = createStore();
const engine = createEngine();

// Engine events that come with a message box: [title, icon].
// TODO(R-9): the original's exact titles and wording.
const NOTICES = {
  halt: ["CPU runtime", "info"],
  end: ["CPU runtime", "info"],
  breakpoint: ["CPU Simulator", "info"],
  watch: ["CPU Simulator", "info"],
};

/** Send a command, publish the new state, show output and any dialog. */
async function send(cmd, args) {
  const reply = store.applyReply(await engine.call(cmd, args));
  for (const e of reply.events) if (e.type === "output") consoleWrite(e.text);
  if (!reply.ok) {
    const event = reply.events[0] ?? { message: "Unknown error" };
    await messageBox("CPU Simulator", event.message, { icon: "error" });
  }
  for (const e of reply.events) {
    if (NOTICES[e.type]) await messageBox(NOTICES[e.type][0], e.message, { icon: NOTICES[e.type][1] });
  }
  return reply;
}

const ui = { stepMode: "instruction", speed: 1 };
const ctx = { store, engine, send, ui, notAvailable, notYet, isa: [] };
ctx.runner = createRunner(ctx);

// Developer handle for the browser console, e.g.
//   await yasmax.send("add_instruction", { program: "P1", text: "MOV #5, R00" })
window.yasmax = { send, store, engine, runner: ctx.runner };

// Never fail silently: show any script error, so a student can report it.
window.addEventListener("error", (e) => messageBox("YASMAX error", String(e.message), { icon: "error" }));
window.addEventListener("unhandledrejection", (e) =>
  messageBox("YASMAX error", String(e.reason?.message ?? e.reason), { icon: "error" }),
);

fitToScreen(document.getElementById("stage"), { onResize: refillAll });
for (const [id, panel] of Object.entries(PANELS)) {
  panel.mount(document.getElementById(id), ctx);
}
wireTabs(document.getElementById("client"));

const overlay = document.getElementById("boot-overlay");
engine.on("boot", (m) => {
  overlay.firstElementChild.textContent = m.message;
});

try {
  const info = await engine.ready;
  // Ask the engine directly if the worker did not send it (an old cached
  // worker.js did not): without it the instruction dialog cannot work.
  ctx.isa = info.isa ?? (await engine.call("isa")).result ?? [];
  store.set(info.snapshot);
  overlay.hidden = true;
  console.info(`YASMAX ready: engine ${info.engineVersion}, Pyodide ${info.pyodideVersion}`);
} catch (err) {
  overlay.classList.add("error");
  overlay.firstElementChild.textContent = `YASMAX could not start: ${err.message}`;
}

// Offline mode and "Install app": only for published builds (tools/build_site.py
// stamps BUILD), so local development never runs stale cached files.
if (BUILD !== "dev" && "serviceWorker" in navigator) {
  const hadWorker = Boolean(navigator.serviceWorker.controller);
  navigator.serviceWorker.register("sw.js").catch((err) => console.warn("Offline mode unavailable:", err));
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    if (!hadWorker) return; // first install: nothing to update
    document.getElementById("update-note").hidden = false;
  });
  document.getElementById("update-reload").addEventListener("click", (e) => {
    e.preventDefault();
    location.reload();
  });
}
