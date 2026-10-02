"use client";

import { useState } from "react";

import { AuditStream } from "@/components/audit-stream";
import { Chart } from "@/components/chart";
import { Convergence } from "@/components/convergence";
import { ArrowRight, Bore, Cross, Mark, Strike } from "@/components/icons";
import { MetricIndex } from "@/components/index-list";
import { Ledger } from "@/components/ledger";
import { LineagePath } from "@/components/lineage-path";
import { Numeral } from "@/components/numeral";
import { PersonaDial } from "@/components/persona-dial";
import { PageHead, Section } from "@/components/section";
import { Degraded, Empty, Loading, Problem, Refused } from "@/components/states";
import { Strata } from "@/components/strata";
import { ApiProblem } from "@/lib/api";
import type { Answer, GlossaryEntry, Lineage } from "@/lib/types";

const TOKENS = ["ground", "stratum", "stratum-2", "hairline", "bone", "ash", "ore", "good", "warn", "critical", "paper", "ink"];
const SCALE = [
  ["micro", "11"],
  ["sm", "13"],
  ["base", "15"],
  ["lg", "18"],
  ["xl", "24"],
  ["2xl", "36"],
  ["3xl", "56"],
  ["4xl", "88"],
  ["5xl", "128"],
];

const joliet_lineage: Lineage = {
  metric: "on_time_delivery",
  source: "dbt manifest",
  expression: "SUM(delivered_lines.is_on_time) / NULLIF(SUM(delivered_lines.is_delivered), 0)",
  path: [
    { layer: "source", objects: ["erp/sales_order_lines", "erp/storage_locations", "tms/shipment_lines", "tms/shipments"] },
    { layer: "staging", objects: ["stg_sales_order_lines", "stg_shipment_lines", "stg_shipments"] },
    { layer: "conformed", objects: ["fct_sales_order_line"] },
    { layer: "semantic", objects: ["delivered_lines.on_time_delivery"], columns: ["is_delivered", "is_on_time"] },
  ],
};

const fy_on_time: Answer = {
  metric_name: "on_time_delivery",
  metrics: [
    {
      name: "on_time_delivery",
      title: "On-time delivery",
      version: 1,
      status: "approved",
      grain: "sales_order_line",
      date_basis: "actual_delivery_date",
      window: "period",
      unit: "ratio",
      owner: "VP Supply Chain",
      steward: "Supply Chain Analytics Lead",
      parent: null,
      definition: "Share of delivered sales order lines that arrived on or before the date we committed to the customer.",
      formula_text: "SUM(is_on_time) / SUM(is_delivered)",
      denominator: "Delivered, non-cancelled lines with actual_delivery_date in the period.",
    },
  ],
  definition: "Share of delivered sales order lines that arrived on or before the date we committed to the customer.",
  canonical_query: {
    metrics: ["on_time_delivery"],
    dimensions: [],
    time: { start: "2025-10-01", end: "2026-09-01" },
    filters: [],
  },
  semantic_query_hash: "3f1c9a0d7b2e44a18c6f0e5d9b7a1c2e4f6a8b0c1d2e3f405162738495a6b7c8",
  sql: "SELECT * FROM SEMANTIC_VIEW(\n    PLANNING_SV_V1\n    METRICS delivered_lines.on_time_delivery\n    WHERE delivered_lines.period_month BETWEEN '2025-10-01' AND '2026-09-01'\n)",
  view: "PLANNING_SV_V1",
  engine: "duckdb",
  lineage: joliet_lineage,
  role: "PLANNING_ROLE",
  user: "PLANNER_A",
  rows: [{ on_time_delivery: 0.8376 }],
  row_count: 1,
  result_checksum: "a1b2c3d4e5f60718",
  latency_ms: 38,
  notes: [],
  request_id: "styleguide",
};

const landed_by_month = [
  "2025-10",
  "2025-11",
  "2025-12",
  "2026-01",
  "2026-02",
  "2026-03",
  "2026-04",
  "2026-05",
  "2026-06",
  "2026-07",
  "2026-08",
  "2026-09",
].map((m, i) => ({ period_month: `${m}-01`, landed_cost_per_unit: 142 + Math.sin(i) * 3 + (i >= 10 ? 14 : 0) }));

const otd_entry: GlossaryEntry = {
  metric_name: "on_time_delivery",
  title: "On-time delivery",
  parent: null,
  variants: ["carrier_on_time", "on_time_to_request"],
  type: "ratio",
  grain: "sales_order_line",
  date_basis: "actual_delivery_date",
  window: "period",
  numerator: "Delivered lines on time to commit.",
  denominator: "Delivered lines.",
  definition: fy_on_time.definition,
  formula_text: "SUM(is_on_time) / SUM(is_delivered)",
  expression: joliet_lineage.expression,
  unit: "ratio",
  owner: "VP Supply Chain",
  steward: "Supply Chain Analytics Lead",
  scor_attribute: "RL.2.1",
  synonyms: ["OTD"],
  version: 1,
  status: "approved",
  approved_by: "VP Supply Chain",
  approved_on: "2026-10-01",
  deprecated_by: null,
};

export default function Styleguide() {
  const [revealed, setRevealed] = useState(true);
  return (
    <>
      <PageHead
        numeral="00"
        kicker="Design system"
        title="Styleguide"
        lede="Every component once, with fixtures from the domain. If it is not here, it does not ship."
      />
      <div className="space-y-12">
        <Section numeral="00.1" title="Tokens">
          <ul className="grid grid-cols-12 gap-x-3 gap-y-2">
            {TOKENS.map((t) => (
              <li key={t} className="col-span-6 md:col-span-2">
                <span className="block h-6 border border-hairline" style={{ background: `rgb(var(--${t}))` }} />
                <span className="font-mono text-micro text-ash">--{t}</span>
              </li>
            ))}
          </ul>
        </Section>
        <Section numeral="00.2" title="Type">
          <ul className="space-y-1">
            {SCALE.map(([name, px]) => (
              <li key={name} className="flex items-baseline gap-3 overflow-hidden">
                <span className="w-16 shrink-0 font-mono text-micro text-ash">{px}px</span>
                <span className={`font-display font-light text-${name} whitespace-nowrap`}>Days of inventory</span>
              </li>
            ))}
            <li className="font-sans text-base">Instrument Sans carries the interface.</li>
            <li className="font-mono text-sm">JetBrains Mono 0123456789 · 3f1c9a0d…b7c8</li>
          </ul>
        </Section>
        <Section numeral="00.3" title="Controls and glyphs">
          <div className="flex flex-wrap items-center gap-3">
            <button type="button" className="action">
              Run governed query <ArrowRight />
            </button>
            <button type="button" className="action" disabled>
              Running
            </button>
            <button type="button" className="quiet-action">
              Show the SQL that ran
            </button>
            <a className="link" href="#tokens">
              Read the definition
            </a>
            <input aria-label="Sample input" className="control" defaultValue="What is OTIF this year?" />
            <span className="flex gap-1 text-ash">
              <ArrowRight title="arrow" />
              <Mark title="mark" />
              <Cross title="cross" />
              <Strike title="strike" />
              <Bore title="bore" />
            </span>
          </div>
        </Section>
        <Section numeral="00.4" title="Persona dial">
          <PersonaDial />
        </Section>
        <Section numeral="00.5" title="Numeral">
          <Numeral value={0.8376} unit="ratio" className="text-5xl font-light text-ore" />
        </Section>
        <Section numeral="00.6" title="Ledger">
          <div className="max-w-rail">
            <Ledger answer={fy_on_time} />
          </div>
        </Section>
        <Section numeral="00.7" title="Convergence">
          <Convergence
            converged
            hash={fy_on_time.semantic_query_hash}
            columns={[
              {
                role: "PLANNING_ROLE",
                phrasing: "What is our delivery rate?",
                value: 0.8376,
                unit: "ratio",
                hash: fy_on_time.semantic_query_hash,
                metric_name: "on_time_delivery",
              },
              {
                role: "PROCUREMENT_ROLE",
                phrasing: "What is customer delivery performance?",
                value: 0.8376,
                unit: "ratio",
                hash: fy_on_time.semantic_query_hash,
                metric_name: "on_time_delivery",
              },
              {
                role: "LOGISTICS_ROLE",
                phrasing: "What is delivery reliability?",
                value: 0.8376,
                unit: "ratio",
                hash: fy_on_time.semantic_query_hash,
                metric_name: "on_time_delivery",
              },
            ]}
          />
        </Section>
        <Section numeral="00.8" title="Strata">
          <Strata
            revealed={revealed}
            governed={0.8376}
            basis="Delivered, non-cancelled lines against the committed date."
            legacy={[
              {
                key: "planning_requested_date",
                team: "Planning",
                label: "Planning workbook",
                basis: "Against the requested date.",
                value: 0.5591,
              },
              {
                key: "logistics_carrier_eta",
                team: "Logistics",
                label: "Carrier scorecard",
                basis: "Shipments against carrier ETA.",
                value: 0.9234,
              },
              {
                key: "executive_plant_average",
                team: "Executive",
                label: "Board dashboard",
                basis: "Cancelled lines kept; plant rates averaged.",
                value: 0.8061,
              },
            ]}
          />
          <button type="button" className="quiet-action mt-2" onClick={() => setRevealed((v) => !v)}>
            Toggle reveal
          </button>
        </Section>
        <Section numeral="00.9" title="Chart">
          <Chart
            rows={landed_by_month}
            dimension="period_month"
            metric="landed_cost_per_unit"
            unit="usd_per_unit"
            title="Landed cost by month, fixture"
            marker={{ at: "2026-08-01", label: "duty step 24 Jul" }}
          />
          <Chart
            rows={[
              { region: "APAC", on_time_delivery: 0.82 },
              { region: "EMEA", on_time_delivery: 0.85 },
              { region: "US", on_time_delivery: 0.84 },
            ]}
            dimension="region"
            metric="on_time_delivery"
            unit="ratio"
            title="On-time delivery by region, fixture"
          />
        </Section>
        <Section numeral="00.10" title="Lineage">
          <LineagePath lineage={joliet_lineage} />
        </Section>
        <Section numeral="00.11" title="Index">
          <MetricIndex entries={[otd_entry]} />
        </Section>
        <Section numeral="00.12" title="Audit stream">
          <AuditStream
            entries={[
              {
                ts: "2026-10-02T09:14:03",
                user: "PLANNER_A",
                role: "PLANNING_ROLE",
                metric: "on_time_delivery",
                hash: fy_on_time.semantic_query_hash,
              },
              {
                ts: "2026-10-02T09:14:41",
                user: "BUYER_B",
                role: "PROCUREMENT_ROLE",
                metric: null,
                hash: null,
                refusal: "raw_sql",
              },
            ]}
          />
        </Section>
        <Section numeral="00.13" title="States">
          <div className="space-y-3">
            <Loading what="Running the governed query as Planning" />
            <Empty title="No answers recorded yet">The first governed answer will appear here with its hash.</Empty>
            <Degraded reason="the agent is switched off in this environment" onBuild={() => undefined} />
            <Refused reason="prompt_injection" />
            <Problem
              problem={
                new ApiProblem(
                  {
                    error: "unknown_metrics",
                    message: "not governed metrics: on_time_delivry",
                    suggestions: { on_time_delivry: ["on_time_delivery"] },
                    request_id: "4e1f09c2a7b3",
                  },
                  422,
                )
              }
            />
          </div>
        </Section>
      </div>
    </>
  );
}
