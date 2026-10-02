"use client";

interface AuditEntry {
  ts: string;
  role: string;
  metric: string;
  hash: string;
}

interface AuditStreamProps {
  entries: AuditEntry[];
}

export function AuditStream({ entries }: AuditStreamProps) {
  return (
    <div className="border-t border-hairline pt-2">
      <p className="text-micro uppercase text-ash tracking-widest mb-1">
        Recent answers
      </p>
      <div className="space-y-0 font-mono text-sm">
        {entries.map((e, i) => (
          <div
            key={i}
            className="flex gap-3 text-ash border-b border-hairline py-0"
          >
            <span className="w-20 shrink-0 tabular-nums">
              {e.ts.slice(11, 19)}
            </span>
            <span className="w-20 shrink-0 text-bone">{e.role}</span>
            <span className="flex-1">{e.metric}</span>
            <span className="text-ore">{e.hash}</span>
          </div>
        ))}
        {entries.length === 0 && (
          <p className="text-ash py-1">No answers recorded yet.</p>
        )}
      </div>
    </div>
  );
}
