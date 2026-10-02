"use client";

import { AxisBottom, AxisLeft } from "@visx/axis";
import { curveMonotoneX } from "@visx/curve";
import { Group } from "@visx/group";
import { scaleBand, scaleLinear, scalePoint } from "@visx/scale";
import { Bar, LinePath } from "@visx/shape";
import { useState } from "react";

import { formatValue, monthLabel } from "@/lib/format";
import type { Row } from "@/lib/types";

const MARGIN = { top: 16, right: 96, bottom: 32, left: 56 };
const AXIS = {
  stroke: "rgb(var(--hairline))",
  tickStroke: "rgb(var(--hairline))",
  tickLabelProps: () => ({ fill: "rgb(var(--ash))", fontSize: 11, fontFamily: "JetBrains Mono" }),
};

export function Chart({
  rows,
  dimension,
  metric,
  unit,
  width = 720,
  height = 280,
  marker,
  title,
}: {
  rows: Row[];
  dimension: string;
  metric: string;
  unit: string;
  width?: number;
  height?: number;
  marker?: { at: string; label: string };
  title: string;
}) {
  const [hover, setHover] = useState<number | null>(null);
  const points = rows.filter((r) => r[metric] !== null && r[dimension] !== null);
  if (!points.length) return null;
  const values = points.map((r) => Number(r[metric]));
  const lo = Math.min(...values);
  const hi = Math.max(...values);
  const pad = (hi - lo || Math.abs(hi) || 1) * 0.15;
  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = height - MARGIN.top - MARGIN.bottom;
  const y = scaleLinear({ domain: [Math.max(0, lo - pad), hi + pad], range: [innerH, 0], nice: true });
  const keys = points.map((r) => String(r[dimension]));
  const temporal = dimension === "period_month";
  const tick = (k: string) => (temporal ? monthLabel(k) : k);
  const shown = hover ?? points.length - 1;

  const series = temporal ? (
    (() => {
      const x = scalePoint({ domain: keys, range: [0, innerW] });
      return (
        <>
          {marker ? (
            <g>
              <line x1={x(marker.at) ?? 0} x2={x(marker.at) ?? 0} y1={0} y2={innerH} stroke="rgb(var(--ash))" strokeDasharray="2 4" />
              <text x={(x(marker.at) ?? 0) + 6} y={12} fill="rgb(var(--ash))" fontSize={11} fontFamily="JetBrains Mono">
                {marker.label}
              </text>
            </g>
          ) : null}
          <LinePath
            data={points}
            x={(r) => x(String(r[dimension])) ?? 0}
            y={(r) => y(Number(r[metric]))}
            stroke="rgb(var(--ore))"
            strokeWidth={1.5}
            curve={curveMonotoneX}
          />
          {points.map((r, i) => (
            <circle
              key={i}
              cx={x(String(r[dimension])) ?? 0}
              cy={y(Number(r[metric]))}
              r={i === shown ? 3.5 : 0}
              fill="rgb(var(--ore))"
            />
          ))}
          {points.map((r, i) => (
            <rect
              key={`hit-${i}`}
              x={(x(String(r[dimension])) ?? 0) - innerW / points.length / 2}
              width={innerW / points.length}
              y={0}
              height={innerH}
              fill="transparent"
              onMouseEnter={() => setHover(i)}
              onMouseLeave={() => setHover(null)}
            />
          ))}
          <text
            x={(x(keys[shown]) ?? 0) + 8}
            y={y(values[shown]) - 8}
            fill="rgb(var(--bone))"
            fontSize={12}
            fontFamily="JetBrains Mono"
          >
            {`${tick(keys[shown])} ${formatValue(values[shown], unit)}`}
          </text>
          <AxisBottom top={innerH} scale={x} tickFormat={(k) => tick(String(k))} numTicks={6} {...AXIS} />
        </>
      );
    })()
  ) : (
    (() => {
      const x = scaleBand({ domain: keys, range: [0, innerW], padding: 0.4 });
      return (
        <>
          {points.map((r, i) => (
            <g key={i} onMouseEnter={() => setHover(i)} onMouseLeave={() => setHover(null)}>
              <Bar
                x={x(String(r[dimension]))}
                width={x.bandwidth()}
                y={y(Number(r[metric]))}
                height={innerH - y(Number(r[metric]))}
                fill={i === shown ? "rgb(var(--ore))" : "rgb(var(--ash) / 0.35)"}
              />
              <text
                x={(x(String(r[dimension])) ?? 0) + x.bandwidth() / 2}
                y={y(Number(r[metric])) - 6}
                textAnchor="middle"
                fill={i === shown ? "rgb(var(--bone))" : "rgb(var(--ash))"}
                fontSize={11}
                fontFamily="JetBrains Mono"
              >
                {formatValue(Number(r[metric]), unit)}
              </text>
            </g>
          ))}
          <AxisBottom top={innerH} scale={x} {...AXIS} />
        </>
      );
    })()
  );

  return (
    <figure>
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" role="img" aria-label={title}>
        <title>{title}</title>
        <Group left={MARGIN.left} top={MARGIN.top}>
          <AxisLeft scale={y} numTicks={4} tickFormat={(v) => formatValue(Number(v), unit, unit === "ratio" ? 0 : 0)} {...AXIS} />
          {series}
        </Group>
      </svg>
      <table className="sr-only">
        <caption>{title}</caption>
        <tbody>
          {points.map((r, i) => (
            <tr key={i}>
              <th scope="row">{tick(String(r[dimension]))}</th>
              <td>{formatValue(Number(r[metric]), unit)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </figure>
  );
}
