"use client";

import { useState } from "react";

import { PERSONA_LABEL, period, shortHash } from "@/lib/format";
import type { Answer } from "@/lib/types";

function Line({ label, children, mono = true }: { label: string; children: React.ReactNode; mono?: boolean }) {
  return (
    <div className="grid grid-cols-[96px_1fr] gap-x-2 border-b border-dashed border-hairline py-1">
      <dt className="micro pt-0.5">{label}</dt>
      <dd className={mono ? "font-mono text-sm text-bone" : "text-sm text-bone"}>{children}</dd>
    </div>
  );
}

export function Ledger({ answer, placeholderless = false }: { answer: Answer | null; placeholderless?: boolean }) {
  const [showSql, setShowSql] = useState(false);
  if (!answer) {
    if (placeholderless) return null;
    return (
      <aside aria-label="Resolution ledger" className="py-2">
        <p className="micro">Resolution ledger</p>
        <p className="mt-1 text-sm text-ash">
          Every answer is set here like a receipt: which governed metric we used, how it is defined, the exact query, its hash,
          the SQL that ran, where the numbers came from and the role they ran under.
        </p>
      </aside>
    );
  }
  const primary = answer.metrics[0];
  return (
    <aside aria-label="Resolution ledger" className="py-2">
      <p className="micro">Resolution ledger</p>
      <h2 className="mt-1 font-display text-xl font-semibold text-ore">{answer.metrics.map((m) => m.title).join(" · ")}</h2>
      <p className="mt-1 text-sm text-bone">{answer.definition}</p>
      <dl className="mt-2">
        <Line label="Metric">{answer.metric_name}</Line>
        <Line label="Version">
          v{primary.version} · {primary.status}
          {primary.parent ? ` · variant of ${primary.parent}` : ""}
        </Line>
        <Line label="Grain">{primary.grain}</Line>
        <Line label="Date basis">{primary.date_basis}</Line>
        <Line label="Window">{period(answer.canonical_query.time)}</Line>
        <Line label="Denominator" mono={false}>
          {primary.denominator}
        </Line>
        <Line label="Steward" mono={false}>
          {primary.steward} for {primary.owner}
        </Line>
        <Line label="Role">
          {PERSONA_LABEL[answer.role] ?? answer.role} · {answer.view}
        </Line>
        <Line label="Hash">
          <span title={answer.semantic_query_hash} className="text-ore">
            {shortHash(answer.semantic_query_hash)}
          </span>
        </Line>
        <Line label="Latency">
          {answer.latency_ms} ms · {answer.engine}
        </Line>
      </dl>
      <div className="mt-2">
        <p className="micro">Canonical query</p>
        <pre tabIndex={0} aria-label="Canonical query" className="mt-0.5 overflow-x-auto font-mono text-micro leading-5 text-ash">
          {JSON.stringify(answer.canonical_query, null, 2)}
        </pre>
      </div>
      <div className="mt-2">
        <button type="button" aria-expanded={showSql} onClick={() => setShowSql((v) => !v)} className="quiet-action">
          {showSql ? "Hide the SQL that ran" : "Show the SQL that ran"}
        </button>
        {showSql ? (
          <pre tabIndex={0} aria-label="Rendered SQL" className="mt-1 overflow-x-auto font-mono text-micro leading-5 text-bone">
            {answer.sql}
          </pre>
        ) : null}
      </div>
      <div className="mt-2">
        <p className="micro">Lineage</p>
        <ol className="mt-0.5 font-mono text-micro leading-5 text-ash">
          {answer.lineage.path.map((step) => (
            <li key={step.layer}>
              <span className="text-bone">{step.layer}</span> {step.objects.slice(0, 3).join(", ")}
              {step.objects.length > 3 ? ` +${step.objects.length - 3}` : ""}
            </li>
          ))}
        </ol>
        <a className="link mt-1 inline-block text-sm" href={`/lineage/${answer.canonical_query.metrics[0]}`}>
          Open the full lineage
        </a>
      </div>
      {answer.notes.length ? (
        <ul className="mt-2 text-sm text-ash">
          {answer.notes.map((n) => (
            <li key={n}>{n}</li>
          ))}
        </ul>
      ) : null}
    </aside>
  );
}
