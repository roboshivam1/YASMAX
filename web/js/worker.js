/*
 * File: web/js/worker.js
 *
 * The Pyodide host. Runs inside a Web Worker, so Python never blocks the
 * window (docs/ARCHITECTURE.md §4, decision D-2).
 *
 * Boot sequence
 * -------------
 *   1. Load the Pyodide runtime (Python compiled to WebAssembly) from the CDN.
 *   2. Download web/engine.zip (built by tools/build_engine.py).
 *   3. Unpack it into Pyodide's in-memory filesystem at /engine.
 *   4. Put /engine on sys.path and import yasmax_engine.api.
 *   5. Call api.boot() and post {type: "ready", ...} to the main thread.
 *
 * Progress is posted as {type: "boot", stage: "..."} so the UI can show a
 * loading message. On failure it posts {type: "boot_error", message}.
 *
 * Message protocol
 * ----------------
 *   main -> worker:  {id, cmd, args}
 *   worker -> main:  {id, ok, snapshot, events}      (reply to that id)
 *   worker -> main:  {type: "boot" | "ready" | "boot_error", ...}  (no id)
 *
 * All data crossing into Python is JSON text (see engine api.py for why).
 *
 * Notes on Pyodide 314.x
 * ----------------------
 * Since 314.0.0, Pyodide only works in MODULE workers. That's why this file
 * uses `import` and bridge.js creates it with {type: "module"}.
 * RUN (chunked execution) will be added here once the engine can step.
 */

// One place to change the Pyodide version. Keep it pinned: an unpinned
// "latest" could change Python behaviour under students mid-semester.
const PYODIDE_VERSION = "314.0.7";
const PYODIDE_BASE = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

// Messages that arrive while booting simply wait on `ready` (see onmessage
// below), so the handler is registered immediately and nothing is lost.
let dispatch = null;

function post(message) {
  self.postMessage(message);
}

async function boot() {
  post({ type: "boot", stage: "runtime", message: "Loading Python runtime…" });
  const { loadPyodide } = await import(`${PYODIDE_BASE}pyodide.mjs`);
  const pyodide = await loadPyodide({ indexURL: PYODIDE_BASE });

  post({ type: "boot", stage: "engine", message: "Loading YASMAX engine…" });
  // "no-cache" means the browser revalidates, so a rebuilt engine.zip is
  // picked up on reload during development. The service worker will
  // handle offline caching later.
  const response = await fetch(new URL("../engine.zip", import.meta.url), { cache: "no-cache" });
  if (!response.ok) {
    throw new Error(
      `Could not download engine.zip (HTTP ${response.status}). ` +
        "Did you run `python3 tools/build_engine.py`?",
    );
  }
  pyodide.unpackArchive(await response.arrayBuffer(), "zip", { extractDir: "/engine" });
  pyodide.runPython("import sys\nif '/engine' not in sys.path: sys.path.insert(0, '/engine')");

  const api = pyodide.pyimport("yasmax_engine.api");
  // Keep a reference to the Python function for the life of the worker.
  dispatch = api.dispatch;

  const info = JSON.parse(api.boot());
  post({
    type: "ready",
    pyodideVersion: pyodide.version,
    engineVersion: info.engine_version,
    commands: info.commands,
    snapshot: info.snapshot,
  });
}

const ready = boot().catch((err) => {
  post({ type: "boot_error", message: String(err?.message ?? err) });
  throw err;
});

self.onmessage = async (event) => {
  const { id, cmd, args } = event.data ?? {};
  try {
    await ready;
    const replyText = dispatch(cmd, JSON.stringify(args ?? {}));
    post({ id, ...JSON.parse(replyText) });
  } catch (err) {
    // Reached only if boot failed or Pyodide itself crashed. Engine
    // errors come back as normal replies with ok=false, not here.
    post({
      id,
      ok: false,
      snapshot: null,
      events: [{ type: "worker_error", message: String(err?.message ?? err) }],
    });
  }
};
