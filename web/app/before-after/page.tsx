"use client";

import { useEffect, useState } from "react";

import { Chart } from "@/components/chart";
import { Ledger } from "@/components/ledger";
import { PageHead, Section } from "@/components/section";
import { Strata } from "@/components/strata";
import { Loading, Problem } from "@/components/states";
import { api } from "@/lib/api";
import { formatValue, period } from "@/lib/format";
import { usePersona } from "@/lib/persona";
import { useResource } from "@/lib/use-resource";

export default function BeforeAfterPage() {
  const story = useResource(() => api.beforeAfter("fy2026"), []);
  const { persona } = usePersona();
  const landed = useResource(
    () =>
      api.query(
        { metrics: ["landed_cost_per_unit"], dimensions: ["period_month"], time: { range: "fy2026" }, filters: [{ dimension: "part_family", operator: "=", value: "Control electronics" }] },
        persona,
      ),
    [persona],
  );
  const [revealed, setRevealed] = useState(false);

  useEffect(() => {
    if (story.state === "ready") {
      const t = window.setTimeout(() => setRevealed(true), 900);
      return () => window.clearTimeout(t);
    }
  }, [story.state]);

  return (
    <>
      <PageHead
        numeral="07"
        kicker="Before the ontology"
        title="Three reports, one month-end argument"
        lede="These are the three on-time numbers the business circulated for FY2026, recomputed from the raw source files exactly as each team built them. Each had a reason. None was the definition the business had agreed."
      />
      <div className="grid grid-cols-12 gap-x-3">
        <div className="col-span-12 lg:col-span-8">
          {story.state === "loading" ? <Loading what="Recomputing the three reports from raw files" /> : null}
          {story.state === "failed" ? <Problem problem={story.problem} /> : null}
          {story.state === "ready" ? (
            <>
              <p className="micro mb-3">{period(story.value.window)}</p>
              <Strata legacy={story.value.legacy} governed={story.value.governed.value} basis={story.value.governed.basis} revealed={revealed} />
              <button type="button" className="quiet-action mt-4" onClick={() => setRevealed((v) => !v)}>
                {revealed ? "Hide the governed answer" : "Reveal the governed answer"}
              </button>
            </>
          ) : null}
        </div>
        <div className="col-span-12 mt-6 lg:col-span-4 lg:mt-0 lg:border-l lg:border-hairline lg:pl-3">
          <p className="micro">Why they differ</p>
          <ul className="mt-1 space-y-2 text-sm text-ash">
            <li>
              Planning measured against the date the customer asked for, which is earlier than the date we committed to, so
              its number runs low.
            </li>
            <li>
              Logistics measured shipments against the carrier&rsquo;s own estimate, set after pick-up, and counted shipments
              rather than order lines, so its number runs high.
            </li>
            <li>
              The board dashboard left cancelled lines in the denominator and then averaged five plant rates, which weights a
              small distribution centre the same as a large plant.
            </li>
            <li className="text-bone">
              The governed definition counts delivered, non-cancelled lines against the committed date, as a ratio of sums at
              whatever grouping you ask for.
            </li>
          </ul>
        </div>
      </div>

      <div className="mt-12">
        <Section
          numeral="08"
          title="Landed cost across the tariff step"
          lede="On 24 July 2026 duty on control electronics, power electronics and engineering polymers stepped up. Landed cost carries duty at the rate in force on the day goods left the supplier, so the step shows in the month the first affected receipts land."
        >
          {landed.state === "loading" ? <Loading what="Running landed cost by month" /> : null}
          {landed.state === "failed" ? <Problem problem={landed.problem} /> : null}
          {landed.state === "ready" ? (
            <div className="grid grid-cols-12 gap-x-3">
              <div className="col-span-12 lg:col-span-8">
                <Chart
                  rows={landed.value.rows}
                  dimension="period_month"
                  metric="landed_cost_per_unit"
                  unit="usd_per_unit"
                  title="Landed cost per unit for control electronics by month"
                  marker={{ at: "2026-08-01", label: "duty step 24 Jul" }}
                />
                <p className="mt-1 font-mono text-micro text-ash">
                  control electronics · {formatValue(Number(landed.value.rows[0]?.landed_cost_per_unit), "usd_per_unit")} in October
                </p>
              </div>
              <div className="col-span-12 lg:col-span-4">
                <Ledger answer={landed.value} />
              </div>
            </div>
          ) : null}
        </Section>
      </div>
    </>
  );
}
