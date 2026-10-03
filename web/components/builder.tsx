"use client";

import { useMemo, useState } from "react";

import { api } from "@/lib/api";
import { useResource } from "@/lib/use-resource";
import type { SemanticQuery } from "@/lib/types";

import { Loading, Problem } from "./states";

const WINDOW_LABEL: Record<string, string> = {
  fy2026: "FY2026, Oct 2025 – Sep 2026",
  q1: "Q1, Oct – Dec 2025",
  q2: "Q2, Jan – Mar 2026",
  q3: "Q3, Apr – Jun 2026",
  q4: "Q4, Jul – Sep 2026",
  last_quarter: "Last quarter, Jul – Sep 2026",
  last_month: "Last month, Sep 2026",
  across_tariff_step: "Across the tariff step, Apr – Sep 2026",
  pre_tariff_step: "Before the tariff step, Apr – Jun 2026",
  post_tariff_step: "After the tariff step, Aug – Sep 2026",
};

export function Builder({ onRun, busy, initial }: { onRun: (q: SemanticQuery) => void; busy: boolean; initial?: SemanticQuery }) {
  const meta = useResource(() => api.meta(), []);
  const [metric, setMetric] = useState(initial?.metrics[0] ?? "on_time_delivery");
  const [dimension, setDimension] = useState(initial?.dimensions[0] ?? "");
  const [window, setWindow] = useState(initial?.time.range ?? "fy2026");
  const [filterDim, setFilterDim] = useState("");
  const [filterValue, setFilterValue] = useState("");

  const selected = useMemo(
    () => (meta.state === "ready" ? meta.value.metrics.find((m) => m.name === metric) : undefined),
    [meta, metric],
  );

  if (meta.state === "loading") return <Loading what="Reading the governed registry" />;
  if (meta.state === "failed") return <Problem problem={meta.problem} />;

  const reachable = selected?.dimensions ?? [];
  const values = meta.value.values[filterDim] ?? [];
  const governed = meta.value.metrics.filter((m) => !m.parent);

  function run() {
    onRun({
      metrics: [metric],
      dimensions: dimension ? [dimension] : [],
      time: { range: window },
      filters: filterDim && filterValue ? [{ dimension: filterDim, operator: "=", value: filterValue }] : [],
    });
  }

  return (
    <form
      aria-label="Build a governed query"
      className="grid grid-cols-12 gap-x-3 gap-y-2"
      onSubmit={(e) => {
        e.preventDefault();
        run();
      }}
    >
      <label className="col-span-12 md:col-span-6">
        <span className="micro">Metric</span>
        <select className="control mt-0.5 w-full" value={metric} onChange={(e) => setMetric(e.target.value)}>
          {governed.map((m) => (
            <optgroup key={m.name} label={m.title}>
              <option value={m.name}>{m.title} (governed)</option>
              {meta.value.metrics
                .filter((v) => v.parent === m.name)
                .map((v) => (
                  <option key={v.name} value={v.name}>
                    {v.title}
                  </option>
                ))}
            </optgroup>
          ))}
        </select>
      </label>
      <label className="col-span-12 md:col-span-6">
        <span className="micro">Window</span>
        <select className="control mt-0.5 w-full" value={window} onChange={(e) => setWindow(e.target.value)}>
          {meta.value.windows.map((w) => (
            <option key={w} value={w}>
              {WINDOW_LABEL[w] ?? w}
            </option>
          ))}
        </select>
      </label>
      <label className="col-span-12 md:col-span-4">
        <span className="micro">Break down by</span>
        <select className="control mt-0.5 w-full" value={dimension} onChange={(e) => setDimension(e.target.value)}>
          <option value="">No breakdown</option>
          {reachable.map((d) => (
            <option key={d} value={d}>
              {d.replaceAll("_", " ")}
            </option>
          ))}
        </select>
      </label>
      <label className="col-span-6 md:col-span-4">
        <span className="micro">Filter on</span>
        <select
          className="control mt-0.5 w-full"
          value={filterDim}
          onChange={(e) => {
            setFilterDim(e.target.value);
            setFilterValue("");
          }}
        >
          <option value="">No filter</option>
          {reachable
            .filter((d) => d !== "period_month" && meta.value.values[d])
            .map((d) => (
              <option key={d} value={d}>
                {d.replaceAll("_", " ")}
              </option>
            ))}
        </select>
      </label>
      <label className="col-span-6 md:col-span-4">
        <span className="micro">Equal to</span>
        <select
          className="control mt-0.5 w-full"
          value={filterValue}
          disabled={!filterDim}
          onChange={(e) => setFilterValue(e.target.value)}
        >
          <option value="">Choose a value</option>
          {values.map((v) => (
            <option key={v} value={v}>
              {v}
            </option>
          ))}
        </select>
      </label>
      <div className="col-span-12 flex items-center gap-3">
        <button type="submit" className="action" disabled={busy || (Boolean(filterDim) && !filterValue)}>
          {busy ? "Running" : "Run governed query"}
        </button>
        <span className="text-sm text-ash">Runs without the model: the same procedure, the same hash.</span>
      </div>
    </form>
  );
}
