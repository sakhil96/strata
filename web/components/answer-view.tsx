"use client";

import { Chart } from "@/components/chart";
import { Numeral } from "@/components/numeral";
import { PERSONA_LABEL, formatValue, joined, monthLabel, period, plain, unitSuffix } from "@/lib/format";
import type { Answer, Meta } from "@/lib/types";

// Numbers in the lead are set in the mono face: amounts, rates, days, months with their year.
// Digits inside a code such as DC-NL01 are part of the name, not a figure.
const FIGURE =
  /((?<![\w-])\$?-?\d[\d,]*(?:\.\d+)?%?(?: points| days| hours| turns a year)?(?![\w-])|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4})/g;

function Lead({ text }: { text: string }) {
  const parts = text.split(FIGURE);
  return (
    <p className="mt-1 max-w-measure font-display text-2xl font-light leading-snug text-bone">
      {parts.map((part, i) =>
        i % 2 ? (
          <span key={i} className="font-mono text-xl tabular text-ore">
            {part}
          </span>
        ) : (
          <span key={i}>{part}</span>
        ),
      )}
    </p>
  );
}

function header(name: string, meta: Meta | null, answer: Answer): string {
  if (name === "period_month") return "Month";
  const card = answer.metrics.find((m) => m.name === name);
  if (card) return `${card.title[0].toUpperCase()}${card.title.slice(1)} (${unitSuffix(card.unit)})`;
  return meta?.dimensions[name]?.title ?? name.replaceAll("_", " ");
}

export function AnswerView({ answer, meta, reading }: { answer: Answer; meta: Meta | null; reading?: string | null }) {
  const metric = answer.canonical_query.metrics[0];
  const unit = answer.metrics.find((m) => m.name === metric)?.unit ?? answer.metrics[0].unit;
  const dims = answer.canonical_query.dimensions;
  const dimension = dims.find((d) => d !== "period_month") ?? dims[0];
  const single = !dims.length && answer.rows.length === 1 ? Number(answer.rows[0][metric]) : null;
  const cleanReading = plain(reading);
  const titled = (d: string) => header(d, meta, answer).toLowerCase();

  return (
    <article aria-label={`Answer: ${answer.metrics.map((m) => m.title).join(", ")}`} className="mt-3">
      <p className="micro">
        {joined(
          answer.metrics.map((m) => m.title).join(", "),
          period(answer.canonical_query.time),
          PERSONA_LABEL[answer.role] ?? answer.role,
        )}
      </p>
      {single !== null ? (
        <p className="mt-1">
          <Numeral value={single} unit={unit} className="text-4xl font-light text-ore lg:text-5xl" />
        </p>
      ) : null}
      {answer.lead ? <Lead text={plain(answer.lead)} /> : null}
      {cleanReading ? (
        <p className="mt-1 max-w-measure text-sm text-ash">
          <span className="micro mr-1">Read as</span>
          {cleanReading}
        </p>
      ) : null}
      {dimension ? (
        <>
          {/* More than a dozen bars cannot be read; the table below carries those. */}
          {dims.length === 1 && (dimension === "period_month" || answer.rows.length <= 12) ? (
            <div className="mt-3">
              <Chart
                rows={answer.rows}
                dimension={dimension}
                metric={metric}
                unit={unit}
                title={`${header(metric, meta, answer)} by ${titled(dimension)}`}
                marker={
                  dimension === "period_month" && metric.startsWith("landed_cost")
                    ? { at: "2026-07-01", label: "tariff step, 24 Jul 2026" }
                    : undefined
                }
              />
            </div>
          ) : null}
          <table className="mt-3 w-full font-mono text-sm">
            <caption className="sr-only">Rows returned</caption>
            <thead>
              <tr className="border-b border-hairline text-left">
                {dims.map((d) => (
                  <th key={d} scope="col" className="micro pb-1 font-normal">
                    {header(d, meta, answer)}
                  </th>
                ))}
                {answer.canonical_query.metrics.map((m) => (
                  <th key={m} scope="col" className="micro pb-1 text-right font-normal">
                    {header(m, meta, answer)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {answer.rows.map((r, i) => (
                <tr key={i} className="border-b border-hairline">
                  {dims.map((d) => (
                    <td key={d} className="py-0.5">
                      {d === "period_month" ? monthLabel(String(r[d])) : String(r[d])}
                    </td>
                  ))}
                  {answer.canonical_query.metrics.map((m) => (
                    <td key={m} className="py-0.5 text-right tabular">
                      {formatValue(r[m] === null ? null : Number(r[m]), answer.metrics.find((x) => x.name === m)?.unit ?? unit)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </>
      ) : null}
    </article>
  );
}
