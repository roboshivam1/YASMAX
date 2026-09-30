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
 * Execution Unit tab (YASMIN 7.5.50): FETCH / DECODE / EXECUTE by hand,
 * see execUnit.js.
 */

import { button, dropdown, group, radio, tabs } from "../ui/widgets.js";
import { execUnitHtml, wireExecUnit } from "./execUnit.js";

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

export function mount(el, ctx) {
  const { notAvailable } = ctx;
  el.innerHTML = tabs(
    [
      { label: "Cache - Pipeline", html: cachePipelineTab() },
      { label: "Execution Unit", html: execUnitHtml() },
    ],
    0,
  );

  el.querySelector("#btn-show-pipeline").addEventListener("click", () => notAvailable("Pipeline view"));
  el.querySelector("#btn-show-cache").addEventListener("click", () => notAvailable("Cache view"));
  wireExecUnit(el, ctx);
}
