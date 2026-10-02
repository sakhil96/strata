import { PERSONA_LABEL, shortHash } from "@/lib/format";
import type { AuditEntry } from "@/lib/types";

export function AuditStream({ entries }: { entries: AuditEntry[] }) {
  if (!entries.length) {
    return <p className="text-sm text-ash">No answers recorded yet. The first governed answer will appear here with its hash.</p>;
  }
  return (
    <ol aria-label="Recent governed answers" className="font-mono text-micro">
      {entries.map((e, i) => (
        <li key={`${e.ts}-${i}`} className="grid grid-cols-[72px_96px_1fr_auto] gap-x-2 border-b border-hairline py-1">
          <time className="tabular text-ash" dateTime={e.ts}>
            {e.ts.slice(11, 19) || e.ts}
          </time>
          <span className="text-bone">{PERSONA_LABEL[e.role] ?? e.role}</span>
          <span className={e.refusal ? "text-warn" : "text-bone"}>
            {e.refusal ? `refused · ${e.refusal.replaceAll("_", " ")}` : e.metric}
          </span>
          <span className="text-ore">{e.hash ? shortHash(e.hash) : ""}</span>
        </li>
      ))}
    </ol>
  );
}
