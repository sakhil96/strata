"use client";

import { AxisBottom, AxisLeft } from "@visx/axis";
import { Group } from "@visx/group";
import { scaleBand, scaleLinear, scalePoint } from "@visx/scale";
import { Bar, LinePath } from "@visx/shape";
import { useEffect, useRef, useState } from "react";

import { formatValue, monthLabel, monthTick } from "@/lib/format";
import type { Row } from "@/lib/types";

const MARGIN = { top: 16, right: 24, bottom: 32, left: 64 };
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
  // Drawn at the width it is shown, so labels stay at their set size on a phone.
  const frame = useRef<HTMLElement>(null);
  const [measured, setMeasured] = useState(width);
  useEffect(() => {
    const el = frame.current;
    if (!el) return;
    const observer = new ResizeObserver(([entry]) => setMeasured(Math.max(300, Math.round(entry.contentRect.width))));
    observer.observe(el);
    return () => observer.disconnect();
  }, []);
  width = measured;
  height = measured < 520 ? 240 : height;
  const points = rows.filter((r) => r[metric] !== null && r[dimension] !== null);
  if (!points.length) return null;
  const values = points.map((r) => Number(r[metric]));
  const lo = Math.min(...values);
  const hi = Math.max(...values);
  const pad = (hi - lo || Math.abs(hi) || 1) * 0.15;
  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = height - MARGIN.top - MARGIN.bottom;
  // Whole-number ticks repeat on a narrow range; give them one decimal there.
  const span = (hi - lo) * (unit === "ratio" ? 100 : 1);
  const tickDigits = span < 5 ? 1 : 0;
  const y = scaleLinear({ domain: [Math.max(0, lo - pad), hi + pad], range: [innerH, 0], nice: true });
  const keys = points.map((r) => String(r[dimension]));
  const temporal = dimension === "period_month";
  const tick = (k: string) => (temporal ? monthLabel(k) : k);
  const shown = hover ?? points.length - 1;

  const series = temporal
    ? (() => {
        const x = scalePoint({ domain: keys, range: [0, innerW], padding: 0.3 });
        const every = Math.max(1, Math.ceil(52 / (innerW / keys.length)));
        const shownTicks = keys.filter((_, i) => i % every === 0);
        const ticks = new Map(shownTicks.map((k, i) => [k, monthTick(k, i ? shownTicks[i - 1] : null)]));
        // A marker is drawn only for a month inside the domain, and inside the plot, never over the ticks.
        const markAt = marker && keys.includes(marker.at) ? (x(marker.at) ?? null) : null;
        const markRight = markAt !== null && markAt > innerW - 140;
        // On a narrow plot the dashed line stays and its label moves to the caption, clear of the axes.
        const markInPlot = innerW >= 480;
        const at = (i: number) => x(keys[i]) ?? 0;
        const labelRight = at(shown) > innerW - 120;
        return (
          <>
            {markAt !== null && marker ? (
              <g>
                <line x1={markAt} x2={markAt} y1={0} y2={innerH} stroke="rgb(var(--ash))" strokeDasharray="2 4" />
                {markInPlot ? (
                  <text
                    x={markRight ? markAt - 6 : markAt + 6}
                    y={12}
                    textAnchor={markRight ? "end" : "start"}
                    fill="rgb(var(--ash))"
                    fontSize={11}
                    fontFamily="JetBrains Mono"
                  >
                    {marker.label}
                  </text>
                ) : null}
              </g>
            ) : null}
            <LinePath
              data={points}
              x={(r) => x(String(r[dimension])) ?? 0}
              y={(r) => y(Number(r[metric]))}
              stroke="rgb(var(--ore))"
              strokeWidth={1.5}
            />
            {points.map((r, i) => (
              <circle
                key={i}
                cx={x(String(r[dimension])) ?? 0}
                cy={y(Number(r[metric]))}
                r={i === shown ? 4 : 2.5}
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
              x={labelRight ? at(shown) - 8 : at(shown) + 8}
              y={Math.max(12, y(values[shown]) - 8)}
              textAnchor={labelRight ? "end" : "start"}
              fill="rgb(var(--bone))"
              fontSize={12}
              fontFamily="JetBrains Mono"
            >
              {`${monthLabel(keys[shown])} ${formatValue(values[shown], unit)}`}
            </text>
            <AxisBottom top={innerH} scale={x} tickValues={shownTicks} tickFormat={(k) => ticks.get(String(k)) ?? ""} {...AXIS} />
          </>
        );
      })()
    : (() => {
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
      })();

  return (
    <figure ref={frame} className="w-full overflow-hidden">
      <svg viewBox={`0 0 ${width} ${height}`} width={width} height={height} role="img" aria-label={title}>
        <title>{title}</title>
        <Group left={MARGIN.left} top={MARGIN.top}>
          <AxisLeft
            scale={y}
            numTicks={4}
            tickFormat={(v) => formatValue(Number(v), unit, tickDigits)}
            {...AXIS}
            tickLabelProps={() => ({ ...AXIS.tickLabelProps(), textAnchor: "end", dx: -6, dy: "0.33em" })}
          />
          {series}
        </Group>
      </svg>
      {marker && temporal && keys.includes(marker.at) && width - MARGIN.left - MARGIN.right < 480 ? (
        <figcaption className="mt-0.5 font-mono text-micro text-ash">Dashed line: {marker.label}</figcaption>
      ) : null}
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
