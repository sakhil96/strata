"use client";

import { useState } from "react";

interface BuilderProps {
  onSubmit: (query: {
    metrics: string[];
    dimensions: string[];
    time: { start: string; end: string };
    filters: Array<{ column: string; operator: string; value: string }>;
  }) => void;
}

const METRIC_OPTIONS = [
  "on_time_delivery",
  "otif",
  "unit_fill_rate",
  "days_of_inventory",
  "landed_cost_per_unit",
  "supplier_lead_time_days",
  "inventory_turns",
  "stockout_rate",
  "freight_cost_per_unit",
  "order_fulfilment_cycle_days",
  "transit_hours",
];

const DIMENSION_OPTIONS = [
  "plant",
  "region",
  "country",
  "segment",
  "category",
  "part_family",
  "supplier",
  "carrier",
  "month",
  "quarter",
];

export function Builder({ onSubmit }: BuilderProps) {
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([]);
  const [selectedDims, setSelectedDims] = useState<string[]>([]);
  const [startDate, setStartDate] = useState("2025-10-01");
  const [endDate, setEndDate] = useState("2026-09-30");

  function toggleMetric(m: string) {
    setSelectedMetrics((prev) =>
      prev.includes(m) ? prev.filter((x) => x !== m) : [...prev, m],
    );
  }

  function toggleDim(d: string) {
    setSelectedDims((prev) =>
      prev.includes(d) ? prev.filter((x) => x !== d) : [...prev, d],
    );
  }

  function handleSubmit() {
    if (selectedMetrics.length === 0) return;
    onSubmit({
      metrics: selectedMetrics,
      dimensions: selectedDims,
      time: { start: startDate, end: endDate },
      filters: [],
    });
  }

  return (
    <div className="space-y-3">
      <div>
        <p className="text-micro uppercase text-ash tracking-widest mb-1">
          Metrics
        </p>
        <div className="flex flex-wrap gap-1">
          {METRIC_OPTIONS.map((m) => (
            <button
              key={m}
              onClick={() => toggleMetric(m)}
              className={`
                font-mono text-sm px-2 py-0 border transition-colors
                ${
                  selectedMetrics.includes(m)
                    ? "border-ore text-ore"
                    : "border-hairline text-ash hover:text-bone"
                }
              `}
            >
              {m}
            </button>
          ))}
        </div>
      </div>

      <div>
        <p className="text-micro uppercase text-ash tracking-widest mb-1">
          Dimensions
        </p>
        <div className="flex flex-wrap gap-1">
          {DIMENSION_OPTIONS.map((d) => (
            <button
              key={d}
              onClick={() => toggleDim(d)}
              className={`
                font-mono text-sm px-2 py-0 border transition-colors
                ${
                  selectedDims.includes(d)
                    ? "border-ore text-ore"
                    : "border-hairline text-ash hover:text-bone"
                }
              `}
            >
              {d}
            </button>
          ))}
        </div>
      </div>

      <div className="flex gap-3">
        <div>
          <label className="text-micro uppercase text-ash tracking-widest block">
            From
          </label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="bg-stratum border border-hairline text-bone font-mono text-sm px-2 py-1 rounded-sm"
          />
        </div>
        <div>
          <label className="text-micro uppercase text-ash tracking-widest block">
            To
          </label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="bg-stratum border border-hairline text-bone font-mono text-sm px-2 py-1 rounded-sm"
          />
        </div>
      </div>

      <button
        onClick={handleSubmit}
        disabled={selectedMetrics.length === 0}
        className="bg-ore text-ground font-sans text-sm px-3 py-1 rounded-sm
                   hover:brightness-110 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
      >
        Query
      </button>
    </div>
  );
}
