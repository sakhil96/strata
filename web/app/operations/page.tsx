"use client";

import { SectionNumber } from "@/components/section-number";
import { StatusBar } from "@/components/status-bar";

export default function OperationsPage() {
  return (
    <main className="pt-6">
      <SectionNumber number="09" />
      <h1 className="font-display text-2xl font-light mt-1 mb-4">
        Operations
      </h1>

      <div className="grid grid-cols-12 gap-3">
        <div className="col-span-6">
          <h2 className="text-micro uppercase text-ash tracking-widest mb-2">
            Source freshness
          </h2>
          <table className="w-full font-mono text-sm">
            <thead>
              <tr className="border-b border-hairline">
                <th className="text-left text-micro uppercase text-ash tracking-widest pr-3 pb-1">
                  Source
                </th>
                <th className="text-left text-micro uppercase text-ash tracking-widest pr-3 pb-1">
                  Last loaded
                </th>
                <th className="text-left text-micro uppercase text-ash tracking-widest pb-1">
                  Rows
                </th>
              </tr>
            </thead>
            <tbody className="text-ash">
              <tr className="border-b border-hairline">
                <td className="pr-3 py-0">erp</td>
                <td className="pr-3 py-0 tabular-nums">—</td>
                <td className="py-0 tabular-nums">—</td>
              </tr>
              <tr className="border-b border-hairline">
                <td className="pr-3 py-0">tms</td>
                <td className="pr-3 py-0 tabular-nums">—</td>
                <td className="py-0 tabular-nums">—</td>
              </tr>
              <tr className="border-b border-hairline">
                <td className="pr-3 py-0">portal</td>
                <td className="pr-3 py-0 tabular-nums">—</td>
                <td className="py-0 tabular-nums">—</td>
              </tr>
              <tr className="border-b border-hairline">
                <td className="pr-3 py-0">iot</td>
                <td className="pr-3 py-0 tabular-nums">—</td>
                <td className="py-0 tabular-nums">—</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="col-span-6">
          <h2 className="text-micro uppercase text-ash tracking-widest mb-2">
            SLO status
          </h2>
          <div className="space-y-2 font-mono text-sm">
            <div className="flex justify-between border-b border-hairline pb-1">
              <span className="text-ash">p95 agent answer latency</span>
              <span className="text-ash">target: ≤ 6 s</span>
            </div>
            <div className="flex justify-between border-b border-hairline pb-1">
              <span className="text-ash">p95 /query latency</span>
              <span className="text-ash">target: ≤ 1.5 s</span>
            </div>
            <div className="flex justify-between border-b border-hairline pb-1">
              <span className="text-ash">service availability</span>
              <span className="text-ash">target: 99.5% monthly</span>
            </div>
            <div className="flex justify-between border-b border-hairline pb-1">
              <span className="text-ash">evaluation pass rate</span>
              <span className="text-ash">floor: 90%</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6">
        <h2 className="text-micro uppercase text-ash tracking-widest mb-2">
          Recent alerts
        </h2>
        <p className="text-ash text-sm">
          No alerts fired. Monitoring: source freshness (6 hr), dbt failures (1 hr),
          evaluation regression (daily 03:00 UTC), resource monitors (continuous).
        </p>
      </div>

      <StatusBar />
    </main>
  );
}
