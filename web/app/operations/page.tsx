"use client";

import { PageHead, Section } from "@/components/section";
import { Loading, Problem } from "@/components/states";
import { api } from "@/lib/api";
import { useResource } from "@/lib/use-resource";

interface Slo {
  name: string;
  target: string;
  measured: string | null;
  status: "met" | "breached" | "needs_account" | "no_data";
  source: string;
}

interface Ops {
  slo: Slo[];
  alerts: { name: string; schedule: string; last_fired: string | null; state: string }[];
  cost: { week: string; credits: number | null; note: string };
}

const SLO_COLOUR: Record<Slo["status"], string> = {
  met: "text-good",
  breached: "text-critical",
  needs_account: "text-warn",
  no_data: "text-ash",
};

export default function OperationsPage() {
  const status = useResource(() => api.status(), []);
  const ops = useResource(() => api.operations() as Promise<unknown> as Promise<Ops>, []);
  return (
    <>
      <PageHead
        numeral="12"
        kicker="Running it"
        title="Operations"
        lede="Freshness, the last dbt build, the alerts that watch them, what we promised and whether we kept it, and what the week cost."
      />
      <div className="space-y-12">
        <Section numeral="12.1" title="Source freshness and the last build">
          {status.state === "loading" ? <Loading what="Reading freshness" /> : null}
          {status.state === "failed" ? <Problem problem={status.problem} /> : null}
          {status.state === "ready" ? (
            <div className="grid grid-cols-12 gap-x-3">
              <table className="col-span-12 text-sm lg:col-span-7">
                <caption className="sr-only">Source freshness</caption>
                <thead>
                  <tr className="border-b border-hairline text-left">
                    <th scope="col" className="micro pb-1 font-normal">
                      Source
                    </th>
                    <th scope="col" className="micro pb-1 font-normal">
                      Last loaded, UTC
                    </th>
                    <th scope="col" className="micro pb-1 text-right font-normal">
                      Files
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {status.value.freshness.map((f) => (
                    <tr key={f.source} className="border-b border-hairline">
                      <td className="py-1 font-mono">{f.source}</td>
                      <td className="py-1 font-mono tabular">{f.loaded_at.replace("T", " ")}</td>
                      <td className="py-1 text-right font-mono tabular">{f.files ?? f.rows ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <dl className="col-span-12 mt-4 lg:col-span-5 lg:mt-0">
                <dt className="micro">dbt build</dt>
                <dd className="font-display text-3xl font-light tabular">
                  {status.value.dbt.passed}
                  <span className="text-lg text-ash"> passed</span>
                  {status.value.dbt.failed ? (
                    <span className="text-lg text-critical"> · {status.value.dbt.failed} failed</span>
                  ) : null}
                </dd>
                <dd className="font-mono text-micro text-ash">{status.value.dbt.finished_at ?? "no run recorded"}</dd>
              </dl>
            </div>
          ) : null}
        </Section>
        <Section
          numeral="12.2"
          title="Service levels"
          lede="Targets from docs/slo.md, measured from the audit trail and the event table."
        >
          {ops.state === "loading" ? <Loading what="Measuring service levels" /> : null}
          {ops.state === "failed" ? <Problem problem={ops.problem} /> : null}
          {ops.state === "ready" ? (
            <table className="w-full text-sm">
              <caption className="sr-only">Service levels</caption>
              <thead>
                <tr className="border-b border-hairline text-left">
                  {["Objective", "Target", "Measured", "Status", "Measured from"].map((h) => (
                    <th key={h} scope="col" className="micro pb-1 font-normal">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {ops.value.slo.map((s) => (
                  <tr key={s.name} className="border-b border-hairline">
                    <td className="py-1 text-bone">{s.name}</td>
                    <td className="py-1 font-mono">{s.target}</td>
                    <td className="py-1 font-mono tabular">{s.measured ?? "—"}</td>
                    <td className={`py-1 font-mono text-micro uppercase ${SLO_COLOUR[s.status]}`}>
                      {s.status.replace("_", " ")}
                    </td>
                    <td className="py-1 text-ash">{s.source}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : null}
        </Section>
        <Section numeral="12.3" title="Alerts and cost">
          {ops.state === "ready" ? (
            <div className="grid grid-cols-12 gap-x-3 gap-y-6">
              <ul className="col-span-12 text-sm lg:col-span-7">
                {ops.value.alerts.map((a) => (
                  <li key={a.name} className="grid grid-cols-[1fr_auto] border-b border-hairline py-1">
                    <span>
                      <span className="font-mono text-bone">{a.name}</span> <span className="text-ash">· {a.schedule}</span>
                    </span>
                    <span className="font-mono text-micro uppercase text-ash">
                      {a.last_fired ? `fired ${a.last_fired}` : a.state}
                    </span>
                  </li>
                ))}
              </ul>
              <div className="col-span-12 lg:col-span-5">
                <p className="micro">Credits this week</p>
                <p className="font-display text-3xl font-light tabular">{ops.value.cost.credits ?? "—"}</p>
                <p className="text-sm text-ash">{ops.value.cost.note}</p>
              </div>
            </div>
          ) : null}
        </Section>
      </div>
    </>
  );
}
