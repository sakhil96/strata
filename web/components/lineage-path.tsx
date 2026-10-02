import type { Lineage } from "@/lib/types";

const LAYER_LABEL = { source: "Source files", staging: "Staging", conformed: "Conformed", semantic: "Semantic view" } as const;

export function LineagePath({ lineage }: { lineage: Lineage }) {
  const columns = lineage.path;
  const rowsPer = columns.map((c) => Math.max(c.objects.length, 1));
  const tallest = Math.max(...rowsPer);
  const rowH = 28;
  const colW = 260;
  const height = 48 + tallest * rowH;
  const width = colW * columns.length;
  const y = (i: number, n: number) => 48 + ((tallest - n) * rowH) / 2 + i * rowH + 10;
  const focus = new Set(columns[columns.length - 2]?.objects.slice(0, 1) ?? []);

  return (
    <figure className="overflow-x-auto" aria-label={`Lineage of ${lineage.metric}`}>
      <svg viewBox={`0 0 ${width} ${height}`} width={width} height={height} role="img" className="max-w-none">
        <title>{`Lineage of ${lineage.metric} from source files to the semantic view`}</title>
        {columns.slice(0, -1).map((col, c) =>
          col.objects.map((obj, i) => {
            const next = columns[c + 1];
            const targets = next.objects.length ? next.objects : [""];
            return targets.map((_, j) => {
              const x1 = c * colW + colW - 24;
              const x2 = (c + 1) * colW;
              const y1 = y(i, col.objects.length);
              const y2 = y(j, targets.length);
              const lit = c === columns.length - 2 && focus.has(obj);
              return (
                <path
                  key={`${c}-${i}-${j}`}
                  d={`M${x1} ${y1} C${x1 + 40} ${y1}, ${x2 - 40} ${y2}, ${x2} ${y2}`}
                  fill="none"
                  stroke={lit ? "rgb(var(--ore))" : "rgb(var(--hairline))"}
                  strokeWidth={1}
                />
              );
            });
          }),
        )}
        {columns.map((col, c) => (
          <g key={col.layer} transform={`translate(${c * colW}, 0)`}>
            <text x={0} y={18} className="fill-ash font-mono" fontSize={11} letterSpacing="0.14em">
              {`${String(c + 1).padStart(2, "0")} ${LAYER_LABEL[col.layer].toUpperCase()}`}
            </text>
            {col.objects.map((obj, i) => (
              <text
                key={obj}
                x={0}
                y={y(i, col.objects.length) + 4}
                className={`font-mono ${col.layer === "semantic" ? "fill-ore" : "fill-bone"}`}
                fontSize={12}
              >
                {obj.length > 32 ? `${obj.slice(0, 31)}…` : obj}
              </text>
            ))}
          </g>
        ))}
      </svg>
      <figcaption className="mt-2 font-mono text-micro text-ash">
        {lineage.expression} · traced from the {lineage.source}
        {columns.at(-1)?.columns?.length ? ` · facts ${columns.at(-1)?.columns?.join(", ")}` : ""}
      </figcaption>
    </figure>
  );
}
