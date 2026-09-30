/*
 * File: web/js/panels/cachePipeline.js
 *
 * Region B: the "Cache - Pipeline" / "Execution Unit" tab control.
 *
 * Cache - Pipeline tab: a "Pipeline" group (single/dual radio buttons,
 * pipeline dropdown, SHOW PIPELINE...) and a "Cache" group (cache type
 * dropdown, SHOW CACHE...). The pipeline and cache windows are PRD items
 * F-41/F-42 (later). Until then, their buttons report "not available"
 * through ctx.notAvailable.
 *
 * The Execution Unit tab is empty until it is captured from the original
 * (docs/UI_SPEC.md, U-2).
 */

import { button, dropdown, group, radio, tabs } from "../ui/widgets.js";

function cachePipelineTab() {
  const pipeline = group(
    "Pipeline",
    radio("pipeline", "Single pipeline", { id: "pipe-single", checked: true }) +
      radio("pipeline", "Dual pipeline", { id: "pipe-dual", disabled: true }) +
      '<span class="w-label lbl-select-pipeline">Select pipeline</span>' +
      dropdown(["0"], "0", { id: "pipe-select" }) +
      button("SHOW\nPIPELINE...", { id: "btn-show-pipeline" }),
    { cls: "grp-pipeline" },
  );
  const cache = group(
    "Cache",
    '<span class="w-label lbl-cache-type">Select cache type</span>' +
      dropdown(["Data", "Instruction"], "Data", { id: "cache-type" }) +
      button("SHOW\nCACHE...", { id: "btn-show-cache" }),
    { cls: "grp-cache" },
  );
  return pipeline + cache;
}

export function mount(el, { notAvailable }) {
  el.innerHTML = tabs(
    [
      { label: "Cache - Pipeline", html: cachePipelineTab() },
      { label: "Execution Unit", html: "" },
    ],
    0,
  );

  el.querySelector("#btn-show-pipeline").addEventListener("click", () => notAvailable("Pipeline view"));
  el.querySelector("#btn-show-cache").addEventListener("click", () => notAvailable("Cache view"));
}
