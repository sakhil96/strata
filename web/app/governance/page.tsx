"use client";

import { useEffect, useState } from "react";
import { SectionNumber } from "@/components/section-number";
import { AuditStream } from "@/components/audit-stream";
import { StatusBar } from "@/components/status-bar";

export default function GovernancePage() {
  const [evalReport, setEvalReport] = useState<Record<string, unknown> | null>(
    null,
  );
  const [auditEntries, setAuditEntries] = useState<
    Array<{ ts: string; role: string; metric: string; hash: string }>
  >([]);

  useEffect(() => {
    fetch("/api/eval/report")
      .then((r) => r.json())
      .then(setEvalReport)
      .catch(() => null);
    fetch("/api/audit?limit=20")
      .then((r) => r.json())
      .then((data) =>
        setAuditEntries(
          Array.isArray(data) ? data : [],
        ),
      )
      .catch(() => []);
  }, []);

  return (
    <main className="pt-6">
      <SectionNumber number="08" />
      <h1 className="font-display text-2xl font-light mt-1 mb-4">
        Governance
      </h1>

      <div className="grid grid-cols-12 gap-3">
        <div className="col-span-7">
          <h2 className="text-micro uppercase text-ash tracking-widest mb-2">
            Evaluation report
          </h2>
          {evalReport ? (
            <pre className="font-mono text-sm text-bone bg-stratum p-2 border border-hairline overflow-x-auto max-h-[400px] overflow-y-auto">
              {JSON.stringify(evalReport, null, 2)}
            </pre>
          ) : (
            <p className="text-ash text-sm">
              No evaluation report available. Run <code>make eval</code> to generate one.
            </p>
          )}
        </div>

        <div className="col-span-5">
          <h2 className="text-micro uppercase text-ash tracking-widest mb-2">
            Agent tools
          </h2>
          <div className="font-mono text-sm space-y-1">
            <div className="border-b border-hairline pb-1">
              <span className="text-ore">GOVERNED_QUERY</span>
              <span className="text-ash ml-2">
                view, metrics[], dimensions[], time{}, filters[]
              </span>
            </div>
            <div className="border-b border-hairline pb-1">
              <span className="text-ore">DESCRIBE_METRIC</span>
              <span className="text-ash ml-2">name</span>
            </div>
            <div className="border-b border-hairline pb-1">
              <span className="text-ore">EXPLAIN_LINEAGE</span>
              <span className="text-ash ml-2">metric</span>
            </div>
          </div>

          <h2 className="text-micro uppercase text-ash tracking-widest mt-4 mb-2">
            Role hierarchy
          </h2>
          <pre className="font-mono text-sm text-ash">
{`SCM_ADMIN
  └─ SCM_DEPLOY
       ├─ PLANNING_ROLE
       ├─ PROCUREMENT_ROLE
       ├─ LOGISTICS_ROLE
       └─ EXECUTIVE_ROLE
            └─ SCM_READER`}
          </pre>
        </div>
      </div>

      <div className="mt-6">
        <AuditStream entries={auditEntries} />
      </div>

      <StatusBar />
    </main>
  );
}
