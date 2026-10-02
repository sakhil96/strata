"use client";

import { AuditStream } from "@/components/audit-stream";
import { PageHead, Section } from "@/components/section";
import { Empty, Loading, Problem } from "@/components/states";
import { api } from "@/lib/api";
import { useResource } from "@/lib/use-resource";

interface Suite {
  name: string;
  title: string;
  status: "passed" | "failed" | "needs_account" | "skipped";
  passed: number;
  total: number;
  detail?: string;
}

interface Report {
  generated_at: string;
  pass_rate: number;
  summary: string;
  suites: Suite[];
}

interface Snapshot {
  agent: { name: string; model: string; tools: { name: string; type: string; description: string }[] };
  grants: { role: string; privilege: string; object: string }[];
  policies: { name: string; kind: string; applies_to: string }[];
  source: string;
}

const STATUS_COPY: Record<Suite["status"], string> = {
  passed: "passed",
  failed: "failed",
  needs_account: "needs the Snowflake account",
  skipped: "not run",
};

export default function GovernancePage() {
  const report = useResource(() => api.evalReport() as Promise<unknown> as Promise<Report>, []);
  const snapshot = useResource(() => api.governance() as Promise<unknown> as Promise<Snapshot>, []);
  const audit = useResource(() => api.audit(20), []);

  return (
    <>
      <PageHead
        numeral="11"
        kicker="Proof"
        title="Governance"
        lede="What the agent may touch, who may read what, and whether the last evaluation held. Everything on this page is read from the build or the account, not typed in."
      />
      <div className="space-y-12">
        <Section numeral="11.1" title="Evaluation" lede="Seven suites. A production release is refused unless every one is green.">
          {report.state === "loading" ? <Loading what="Reading the evaluation report" /> : null}
          {report.state === "failed" ? (
            <Empty title="No evaluation report yet">Run make eval; the report lands in eval/report.json and appears here.</Empty>
          ) : null}
          {report.state === "ready" ? (
            <>
              <p className="font-mono text-sm text-bone">{report.value.summary}</p>
              <table className="mt-3 w-full text-sm">
                <caption className="sr-only">Evaluation suites</caption>
                <thead>
                  <tr className="border-b border-hairline text-left">
                    {["Suite", "Status", "Passed", "Detail"].map((h) => (
                      <th key={h} scope="col" className="micro pb-1 font-normal">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {report.value.suites.map((s) => (
                    <tr key={s.name} className="border-b border-hairline align-top">
                      <td className="py-1 pr-2 text-bone">{s.title}</td>
                      <td
                        className={`py-1 pr-2 font-mono text-micro uppercase ${
                          s.status === "passed" ? "text-good" : s.status === "failed" ? "text-critical" : "text-warn"
                        }`}
                      >
                        {STATUS_COPY[s.status]}
                      </td>
                      <td className="py-1 pr-2 font-mono tabular">
                        {s.total ? `${s.passed}/${s.total}` : "—"}
                      </td>
                      <td className="py-1 text-ash">{s.detail}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          ) : null}
        </Section>

        <Section numeral="11.2" title="Agent tools" lede="Rendered from the agent specification. No tool here can run SQL you write.">
          {snapshot.state === "loading" ? <Loading what="Reading the governance snapshot" /> : null}
          {snapshot.state === "failed" ? <Problem problem={snapshot.problem} /> : null}
          {snapshot.state === "ready" ? (
            <>
              <p className="font-mono text-micro text-ash">
                {snapshot.value.agent.name} · model {snapshot.value.agent.model} · from {snapshot.value.source}
              </p>
              <dl className="mt-2">
                {snapshot.value.agent.tools.map((t) => (
                  <div key={t.name} className="grid grid-cols-12 gap-x-3 border-b border-hairline py-1">
                    <dt className="col-span-12 font-mono text-sm text-ore md:col-span-4">
                      {t.name} <span className="text-ash">· {t.type}</span>
                    </dt>
                    <dd className="col-span-12 text-sm text-ash md:col-span-8">{t.description}</dd>
                  </div>
                ))}
              </dl>
            </>
          ) : null}
        </Section>

        <Section numeral="11.3" title="Grants and policies" lede="The committed snapshot that CI diffs against SHOW GRANTS on every run.">
          {snapshot.state === "ready" ? (
            <div className="grid grid-cols-12 gap-x-3 gap-y-6">
              <div className="col-span-12 lg:col-span-7">
                <p className="micro">Grants</p>
                <ul className="mt-1 font-mono text-micro">
                  {snapshot.value.grants.map((g) => (
                    <li key={`${g.role}-${g.privilege}-${g.object}`} className="grid grid-cols-[150px_110px_1fr] gap-x-2 border-b border-hairline py-0.5">
                      <span className="text-bone">{g.role}</span>
                      <span className="text-ash">{g.privilege}</span>
                      <span className="text-ash">{g.object}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="col-span-12 lg:col-span-5">
                <p className="micro">Policies</p>
                <ul className="mt-1 text-sm">
                  {snapshot.value.policies.map((p) => (
                    <li key={p.name} className="border-b border-hairline py-1">
                      <span className="font-mono text-bone">{p.name}</span> <span className="text-ash">· {p.kind}</span>
                      <p className="text-ash">{p.applies_to}</p>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : null}
        </Section>

        <Section numeral="11.4" title="Audit stream" lede="Every answer and every refusal, newest first.">
          {audit.state === "loading" ? <Loading what="Reading the audit trail" /> : null}
          {audit.state === "failed" ? <Problem problem={audit.problem} /> : null}
          {audit.state === "ready" ? <AuditStream entries={audit.value} /> : null}
        </Section>
      </div>
    </>
  );
}
