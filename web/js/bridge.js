/*
 * File: web/js/bridge.js
 *
 * The main thread's handle on the engine. It hides postMessage behind
 * promises, so panels can write:
 *
 *     const reply = await engine.call("set_register", { name: "R01", value: 5 });
 *
 * instead of juggling message ids.
 *
 * How it works
 * ------------
 * - Starts web/js/worker.js as a MODULE worker (required by Pyodide 314+).
 * - Every call() gets a unique id. The promise is kept in `pending` until
 *   the worker replies with that id.
 * - Messages without an id (boot progress, ready, later run ticks) go to
 *   listeners registered with on(type, fn).
 *
 * Contract
 * --------
 * call() ALWAYS resolves with {ok, snapshot, events}. It never rejects.
 * ok=false is a normal outcome (e.g. the student typed "abc" as a register
 * value), and the caller decides what dialog to show from `events`.
 * That keeps try/catch out of every button handler.
 */

export function createEngine() {
  const worker = new Worker(new URL("./worker.js", import.meta.url), { type: "module" });

  let nextId = 1;
  const pending = new Map(); // id -> resolve function
  const listeners = new Map(); // message type -> Set of callbacks

  let resolveReady;
  let rejectReady;
  const ready = new Promise((resolve, reject) => {
    resolveReady = resolve;
    rejectReady = reject;
  });

  function emit(type, message) {
    for (const fn of listeners.get(type) ?? []) fn(message);
  }

  worker.onmessage = (event) => {
    const message = event.data;

    if (message.id != null) {
      const resolve = pending.get(message.id);
      pending.delete(message.id);
      if (resolve) resolve(message);
      return;
    }

    if (message.type === "ready") resolveReady(message);
    if (message.type === "boot_error") rejectReady(new Error(message.message));
    emit(message.type, message);
  };

  // Errors thrown while loading the worker script itself (e.g. a syntax
  // error in worker.js), which the worker can't report on its own.
  worker.onerror = (event) => {
    const error = new Error(event.message || "The engine worker failed to start.");
    rejectReady(error);
    emit("boot_error", { type: "boot_error", message: error.message });
  };

  return {
    /** Resolves with the "ready" message once Python and the engine have loaded. */
    ready,

    /** Send one command. Resolves with {id, ok, snapshot, events}. */
    call(cmd, args = {}) {
      const id = nextId++;
      return new Promise((resolve) => {
        pending.set(id, resolve);
        worker.postMessage({ id, cmd, args });
      });
    },

    /** Listen for messages without an id. Returns an unsubscribe function. */
    on(type, fn) {
      if (!listeners.has(type)) listeners.set(type, new Set());
      listeners.get(type).add(fn);
      return () => listeners.get(type).delete(fn);
    },
  };
}
