"use client";

interface ConvergenceItem {
  persona: string;
  value: string;
  phrasing: string;
}

interface ConvergenceProps {
  metrics: ConvergenceItem[];
  hash: string;
}

export function Convergence({ metrics, hash }: ConvergenceProps) {
  const allMatch = new Set(metrics.map((m) => m.value)).size === 1;

  return (
    <div className="py-6">
      <div className="grid grid-cols-12 gap-3">
        {metrics.map((m, i) => (
          <div
            key={m.persona}
            className={`${i === 0 ? "col-span-4" : i === 1 ? "col-span-4" : "col-span-4"}`}
          >
            <p className="text-micro uppercase text-ash tracking-widest mb-1">
              {m.persona}
            </p>
            <p className="text-ash text-sm italic mb-2">
              &ldquo;{m.phrasing}&rdquo;
            </p>
            <p
              className={`font-display text-5xl font-semibold tabular-nums ${allMatch ? "text-ore" : "text-bone"}`}
            >
              {m.value}
            </p>
          </div>
        ))}
      </div>

      {allMatch && (
        <div className="mt-3 border-t border-ore pt-2 flex items-center gap-2">
          <span className="font-mono text-sm text-ore">{hash}</span>
          <span className="text-micro uppercase text-ash tracking-widest">
            identical hash across all personas
          </span>
        </div>
      )}
    </div>
  );
}
