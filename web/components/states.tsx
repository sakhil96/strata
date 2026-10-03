"use client";

import { type ReactNode, useEffect, useState } from "react";

import { type ApiProblem, onPending, type Pending } from "@/lib/api";
import { REFUSAL_COPY } from "@/lib/format";

const PENDING_COPY: Record<Exclude<Pending, null>, string> = {
  waking: "Waking the service, usually under a minute",
  slow: "Still computing; trying once more",
};

export function Loading({ what }: { what: string }) {
  const [pending, setPending] = useState<Pending>(null);
  useEffect(() => onPending(setPending), []);
  return (
    <div role="status" aria-live="polite" className="flex items-center gap-2 py-3">
      <span className="h-px w-8 animate-pulse bg-ore" aria-hidden />
      <span className="text-sm text-ash">{pending ? PENDING_COPY[pending] : what}</span>
    </div>
  );
}

export function Empty({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="rule py-3">
      <p className="text-base text-bone">{title}</p>
      {children ? <div className="mt-1 max-w-measure text-sm text-ash">{children}</div> : null}
    </div>
  );
}

export function Problem({ problem, onRetry }: { problem: ApiProblem; onRetry?: () => void }) {
  const p = problem.problem;
  return (
    <div role="alert" className="border-l border-critical py-1 pl-2">
      <p className="micro text-critical">{p.error.replaceAll("_", " ")}</p>
      <p className="mt-0.5 text-base text-bone">{p.message ?? "The request did not complete."}</p>
      {p.suggestions ? (
        <p className="mt-0.5 text-sm text-ash">
          Closest governed names:{" "}
          <span className="font-mono text-bone">{Object.values(p.suggestions).flat().slice(0, 3).join(", ")}</span>
        </p>
      ) : null}
      {p.request_id ? <p className="mt-0.5 font-mono text-micro text-ash">request {p.request_id}</p> : null}
      {onRetry ? (
        <button type="button" onClick={onRetry} className="quiet-action mt-1">
          Try again
        </button>
      ) : null}
    </div>
  );
}

export function Refused({ reason }: { reason: string }) {
  return (
    <div role="status" className="border-l border-warn py-1 pl-2">
      <p className="micro text-warn">Not answered</p>
      <p className="mt-0.5 max-w-measure text-base text-bone">{REFUSAL_COPY[reason] ?? "We could not place that question."}</p>
    </div>
  );
}

export function Fallback({ reason, onBuild }: { reason?: string | null; onBuild?: () => void }) {
  return (
    <div role="status" className="border-l border-warn py-1 pl-2">
      <p className="micro text-warn">Answered without the model</p>
      <p className="mt-0.5 max-w-measure text-sm text-ash">
        The agent was not used{reason ? ` (${reason})` : ""}. We matched your words to the governed registry instead; the number
        below is the same governed number the agent would have returned.
      </p>
      {onBuild ? (
        <button type="button" onClick={onBuild} className="quiet-action mt-1">
          Check it in the Builder
        </button>
      ) : null}
    </div>
  );
}
