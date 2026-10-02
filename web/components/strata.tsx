"use client";

interface StrataItem {
  label: string;
  basis: string;
  value: string;
}

interface StrataProps {
  legacy: StrataItem[];
  governed: { value: string; basis: string };
}

export function Strata({ legacy, governed }: StrataProps) {
  return (
    <div className="space-y-4">
      <div className="space-y-3">
        {legacy.map((item) => (
          <div key={item.label} className="relative">
            <p className="text-micro uppercase text-ash tracking-widest">
              {item.label}
            </p>
            <p className="font-display text-3xl font-light text-ash line-through decoration-hairline">
              {item.value}
            </p>
            <p className="text-sm text-ash">{item.basis}</p>
          </div>
        ))}
      </div>

      <div className="border-t border-ore pt-3">
        <p className="text-micro uppercase text-ore tracking-widest">
          Governed answer
        </p>
        <p className="font-display text-4xl font-semibold text-ore tabular-nums">
          {governed.value}
        </p>
        <p className="text-sm text-bone">{governed.basis}</p>
      </div>
    </div>
  );
}
