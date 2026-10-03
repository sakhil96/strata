"use client";

import { useEffect, useRef, useState } from "react";

import { Builder } from "@/components/builder";
import { Chart } from "@/components/chart";
import { Ledger } from "@/components/ledger";
import { Numeral } from "@/components/numeral";
import { PageHead } from "@/components/section";
import { Fallback, Loading, Problem, Refused } from "@/components/states";
import { ApiProblem, api } from "@/lib/api";
import { PERSONA_LABEL, formatValue, monthLabel, period } from "@/lib/format";
import { usePersona } from "@/lib/persona";
import type { Answer, Refusal, SemanticQuery } from "@/lib/types";

const PROMPTS = [
  "What is on-time delivery for FY2026?",
  "Which suppliers have the worst on-time receipt?",
  "How did landed cost move by month across the July tariff step?",
  "What is DOI by plant?",
];

type Ask = { kind: "question"; text: string } | { kind: "query"; query: SemanticQuery };

export default function AskPage() {
  const { persona } = usePersona();
  const [mode, setMode] = useState<"ask" | "build">("ask");
  const [text, setText] = useState("");
  const [last, setLast] = useState<Ask | null>(null);
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [refusal, setRefusal] = useState<Refusal | null>(null);
  const [problem, setProblem] = useState<ApiProblem | null>(null);
  const [busy, setBusy] = useState(false);
  const [sheet, setSheet] = useState(false);
  const askedAs = useRef(persona);

  async function run(next: Ask) {
    setBusy(true);
    setProblem(null);
    setRefusal(null);
    setLast(next);
    askedAs.current = persona;
    try {
      const reply = next.kind === "question" ? await api.ask(next.text, persona) : await api.query(next.query, persona);
      if ("refusal" in reply) {
        setRefusal(reply);
        setAnswer(null);
      } else {
        setAnswer(reply);
      }
    } catch (err) {
      setProblem(err instanceof ApiProblem ? err : new ApiProblem({ error: "failed", message: String(err) }, 0));
      setAnswer(null);
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    if (last && askedAs.current !== persona) void run(last);
    // Re-running on a role change is the point: the same question, a different role, the same governed answer.
  }, [persona]);

  const metric = answer?.canonical_query.metrics[0];
  const unit = answer?.metrics[0].unit ?? "ratio";
  const dimension = answer?.canonical_query.dimensions[0];
  const single = answer && !dimension && answer.rows.length === 1 && metric ? Number(answer.rows[0][metric]) : null;

  return (
    <div className="grid grid-cols-12 gap-x-3">
      <div className="col-span-12 lg:col-span-8 lg:pr-4">
        <PageHead
          numeral="05"
          kicker={`Asking as ${PERSONA_LABEL[persona]}`}
          title="Ask a supply chain question"
          lede="Name a metric in your own words. We resolve it to the governed definition, run it through the semantic view for your role, and show the working in the ledger."
        />
        <div role="tablist" aria-label="How to ask" className="mb-3 flex gap-3">
          {(["ask", "build"] as const).map((m) => (
            <button
              key={m}
              role="tab"
              type="button"
              aria-selected={mode === m}
              onClick={() => setMode(m)}
              className={`micro pb-0.5 ${mode === m ? "border-b border-ore text-ore" : "text-ash hover:text-bone"}`}
            >
              {m === "ask" ? "In words" : "Builder, without the model"}
            </button>
          ))}
        </div>

        {mode === "ask" ? (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (text.trim().length >= 3) void run({ kind: "question", text: text.trim() });
            }}
          >
            <label htmlFor="question" className="micro">
              Your question
            </label>
            <textarea
              id="question"
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={3}
              maxLength={500}
              className="control mt-0.5 w-full resize-none font-display text-xl font-light"
            />
            <div className="mt-1 flex flex-wrap items-center gap-3">
              <button type="submit" className="action" disabled={busy || text.trim().length < 3}>
                {busy ? "Answering" : "Answer it"}
              </button>
              <span className="text-sm text-ash">Try:</span>
              {PROMPTS.map((p) => (
                <button key={p} type="button" className="quiet-action" onClick={() => setText(p)}>
                  {p}
                </button>
              ))}
            </div>
          </form>
        ) : (
          <Builder busy={busy} onRun={(query) => void run({ kind: "query", query })} />
        )}

        <div className="mt-6" aria-live="polite">
          {busy ? <Loading what={`Running the governed query as ${PERSONA_LABEL[persona]}`} /> : null}
          {problem ? <Problem problem={problem} onRetry={last ? () => void run(last) : undefined} /> : null}
          {refusal ? <Refused reason={refusal.refusal} /> : null}
          {answer?.fallback ? <Fallback reason={answer.fallback_reason} onBuild={() => setMode("build")} /> : null}
          {answer && !busy ? (
            <article aria-label="Answer" className="mt-3">
              <p className="micro">
                {answer.metrics[0].title} · {period(answer.canonical_query.time)} · {PERSONA_LABEL[answer.role]}
              </p>
              {single !== null ? (
                <p className="mt-1">
                  <Numeral value={single} unit={unit} className="text-4xl font-light text-ore lg:text-5xl" />
                </p>
              ) : null}
              {answer.narrative ? <p className="mt-2 max-w-measure text-base text-bone">{answer.narrative}</p> : null}
              {dimension && metric ? (
                <>
                  <div className="mt-3">
                    <Chart
                      rows={answer.rows}
                      dimension={dimension}
                      metric={metric}
                      unit={unit}
                      title={`${answer.metrics[0].title} by ${dimension.replaceAll("_", " ")}`}
                      marker={
                        dimension === "period_month" && metric.startsWith("landed_cost")
                          ? { at: "2026-08-01", label: "tariff step 24 Jul" }
                          : undefined
                      }
                    />
                  </div>
                  <table className="mt-3 w-full font-mono text-sm">
                    <caption className="sr-only">Rows returned</caption>
                    <thead>
                      <tr className="border-b border-hairline text-left">
                        <th scope="col" className="micro pb-1 font-normal">
                          {dimension.replaceAll("_", " ")}
                        </th>
                        {answer.canonical_query.metrics.map((m) => (
                          <th key={m} scope="col" className="micro pb-1 text-right font-normal">
                            {m}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {answer.rows.map((r, i) => (
                        <tr key={i} className="border-b border-hairline">
                          <td className="py-0.5">
                            {dimension === "period_month" ? monthLabel(String(r[dimension])) : String(r[dimension])}
                          </td>
                          {answer.canonical_query.metrics.map((m) => (
                            <td key={m} className="py-0.5 text-right tabular">
                              {formatValue(
                                r[m] === null ? null : Number(r[m]),
                                answer.metrics.find((x) => x.name === m)?.unit ?? unit,
                              )}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </>
              ) : null}
            </article>
          ) : null}
        </div>
      </div>

      <div className="col-span-12 hidden lg:col-span-4 lg:block">
        <div className="sticky top-2 w-full max-w-rail border-l border-hairline pl-3">
          <Ledger answer={answer} />
        </div>
      </div>
      {answer ? (
        <div className="fixed inset-x-0 bottom-0 z-10 border-t border-hairline bg-stratum lg:hidden">
          <button
            type="button"
            className="micro w-full px-3 py-2 text-left"
            aria-expanded={sheet}
            onClick={() => setSheet((v) => !v)}
          >
            {sheet ? "Close the ledger" : "Open the resolution ledger"}
          </button>
          {sheet ? (
            <div className="max-h-[70vh] overflow-y-auto px-3 pb-3">
              <Ledger answer={answer} />
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
