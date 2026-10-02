"use client";

import { api } from "@/lib/api";
import { useResource } from "@/lib/use-resource";

export function StatusLine() {
  const status = useResource(() => api.status(), []);
  if (status.state === "loading") return <p className="micro">Reading system status</p>;
  if (status.state === "failed") return <p className="micro text-critical">Status unavailable · {status.problem.problem.error}</p>;
  const s = status.value;
  const evalRate = s.eval.pass_rate;
  return (
    <ul aria-label="System status" className="flex flex-wrap gap-x-4 gap-y-1 font-mono text-micro uppercase text-ash">
      <li>
        <span className="text-good" aria-hidden>
          ●{" "}
        </span>
        {s.mode} · data as of {s.as_of ?? "unknown"}
      </li>
      {s.freshness.map((f) => (
        <li key={f.source}>
          {f.source} {f.loaded_at.slice(0, 16).replace("T", " ")}
        </li>
      ))}
      <li className={s.dbt.failed ? "text-critical" : ""}>
        dbt {s.dbt.passed} passed{s.dbt.failed ? ` · ${s.dbt.failed} failed` : ""}
      </li>
      <li className={evalRate === null ? "" : evalRate >= 0.9 ? "text-good" : "text-critical"}>
        eval {evalRate === null ? "not run" : `${Math.round(evalRate * 100)}%`}
      </li>
    </ul>
  );
}
