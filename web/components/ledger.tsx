"use client";

import { useState } from "react";

interface LedgerProps {
  metric?: string;
  definition?: string;
  version?: number;
  grain?: string;
  dateBasis?: string;
  window?: string;
  canonicalQuery?: Record<string, unknown>;
  hash?: string;
  sql?: string;
  lineage?: string[];
  role?: string;
  latencyMs?: number;
}

export function Ledger({
  metric,
  definition,
  version,
  grain,
  dateBasis,
  window,
  canonicalQuery,
  hash,
  sql,
  lineage,
  role,
  latencyMs,
}: LedgerProps) {
  const [sqlExpanded, setSqlExpanded] = useState(false);

  if (!metric) {
    return (
      <div className="border-l border-hairline pl-3 py-2 text-ash text-sm">
        Ask a question or build a query to see the resolution ledger.
      </div>
    );
  }

  return (
    <aside className="border-l border-hairline pl-3 py-2 space-y-2">
      <div>
        <p className="text-micro uppercase text-ash tracking-widest">Metric</p>
        <p className="font-display text-xl font-semibold text-ore">{metric}</p>
      </div>

      {definition && (
        <div>
          <p className="text-micro uppercase text-ash tracking-widest">
            Definition
          </p>
          <p className="text-sm text-bone">{definition}</p>
        </div>
      )}

      <div className="flex gap-4">
        {version != null && (
          <div>
            <p className="text-micro uppercase text-ash tracking-widest">
              Version
            </p>
            <p className="font-mono text-sm">{version}</p>
          </div>
        )}
        {grain && (
          <div>
            <p className="text-micro uppercase text-ash tracking-widest">
              Grain
            </p>
            <p className="font-mono text-sm">{grain}</p>
          </div>
        )}
        {dateBasis && (
          <div>
            <p className="text-micro uppercase text-ash tracking-widest">
              Date basis
            </p>
            <p className="font-mono text-sm">{dateBasis}</p>
          </div>
        )}
      </div>

      {canonicalQuery && (
        <div>
          <p className="text-micro uppercase text-ash tracking-widest">
            Canonical query
          </p>
          <pre className="font-mono text-sm text-bone bg-stratum p-2 border border-hairline overflow-x-auto">
            {JSON.stringify(canonicalQuery, null, 2)}
          </pre>
        </div>
      )}

      {hash && (
        <div>
          <p className="text-micro uppercase text-ash tracking-widest">Hash</p>
          <p className="font-mono text-sm text-ore">{hash}</p>
        </div>
      )}

      {sql && (
        <div>
          <button
            onClick={() => setSqlExpanded(!sqlExpanded)}
            className="text-micro uppercase text-ash tracking-widest hover:text-bone transition-colors"
          >
            {sqlExpanded ? "Hide SQL" : "Show SQL"}
          </button>
          {sqlExpanded && (
            <pre className="font-mono text-sm text-bone bg-stratum p-2 border border-hairline overflow-x-auto mt-1">
              {sql}
            </pre>
          )}
        </div>
      )}

      {lineage && lineage.length > 0 && (
        <div>
          <p className="text-micro uppercase text-ash tracking-widest">
            Lineage
          </p>
          <ul className="font-mono text-sm space-y-0">
            {lineage.map((step, i) => (
              <li key={i} className="text-ash">
                {i > 0 && <span className="text-hairline mr-1">→</span>}
                {step}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="flex gap-4 pt-1 border-t border-hairline">
        {role && (
          <div>
            <p className="text-micro uppercase text-ash tracking-widest">
              Role
            </p>
            <p className="font-mono text-sm">{role}</p>
          </div>
        )}
        {latencyMs != null && (
          <div>
            <p className="text-micro uppercase text-ash tracking-widest">
              Latency
            </p>
            <p className="font-mono text-sm">{latencyMs} ms</p>
          </div>
        )}
      </div>
    </aside>
  );
}
