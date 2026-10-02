"use client";

import { useState } from "react";
import { PersonaDial } from "@/components/persona-dial";
import { Builder } from "@/components/builder";
import { Ledger } from "@/components/ledger";
import { StatusBar } from "@/components/status-bar";

export default function AskPage() {
  const [persona, setPersona] = useState("EXECUTIVE_ROLE");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<"ask" | "build">("ask");

  async function handleAsk() {
    if (!question.trim()) return;
    setLoading(true);
    try {
      const resp = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, persona }),
      });
      const data = await resp.json();
      setAnswer(data);
    } catch {
      setAnswer({ error: "Request failed. The service may be unavailable." });
    }
    setLoading(false);
  }

  async function handleBuild(query: {
    metrics: string[];
    dimensions: string[];
    time: { start: string; end: string };
    filters: Array<{ column: string; operator: string; value: string }>;
  }) {
    setLoading(true);
    try {
      const resp = await fetch("/api/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Persona": persona,
        },
        body: JSON.stringify({
          view: "SCM_GOVERNED_V1",
          metrics: query.metrics,
          dimensions: query.dimensions,
          time: query.time,
          filters: query.filters,
        }),
      });
      const data = await resp.json();
      setAnswer(data);
    } catch {
      setAnswer({ error: "Query failed." });
    }
    setLoading(false);
  }

  return (
    <main>
      <div className="pt-6 pb-4">
        <PersonaDial active={persona} onChange={setPersona} />
      </div>

      <div className="grid grid-cols-12 gap-3">
        <div className="col-span-7 lg:col-span-8">
          <div className="flex gap-3 mb-3">
            <button
              onClick={() => setMode("ask")}
              className={`text-micro uppercase tracking-widest pb-1 border-b-2 ${mode === "ask" ? "text-ore border-ore" : "text-ash border-transparent"}`}
            >
              Ask
            </button>
            <button
              onClick={() => setMode("build")}
              className={`text-micro uppercase tracking-widest pb-1 border-b-2 ${mode === "build" ? "text-ore border-ore" : "text-ash border-transparent"}`}
            >
              Build
            </button>
          </div>

          {mode === "ask" ? (
            <div className="space-y-2">
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="What is on-time delivery this quarter?"
                rows={3}
                className="w-full bg-stratum border border-hairline text-bone font-sans text-base p-2 rounded-sm resize-none focus:border-ore focus:outline-none"
              />
              <button
                onClick={handleAsk}
                disabled={loading || !question.trim()}
                className="bg-ore text-ground font-sans text-sm px-3 py-1 rounded-sm
                           hover:brightness-110 transition-all disabled:opacity-40"
              >
                {loading ? "Querying..." : "Ask"}
              </button>
            </div>
          ) : (
            <Builder onSubmit={handleBuild} />
          )}

          {answer && !answer.error && (
            <div className="mt-4">
              <p className="text-micro uppercase text-ash tracking-widest mb-1">
                Result
              </p>
              {answer.rows && Array.isArray(answer.rows) && (
                <div className="overflow-x-auto">
                  <table className="w-full font-mono text-sm">
                    <thead>
                      <tr className="border-b border-hairline">
                        {answer.rows.length > 0 &&
                          Object.keys(
                            answer.rows[0] as Record<string, unknown>,
                          ).map((k) => (
                            <th
                              key={k}
                              className="text-left text-micro uppercase text-ash tracking-widest pr-3 pb-1"
                            >
                              {k}
                            </th>
                          ))}
                      </tr>
                    </thead>
                    <tbody>
                      {(answer.rows as Record<string, unknown>[]).map(
                        (row, i) => (
                          <tr key={i} className="border-b border-hairline">
                            {Object.values(row).map((v, j) => (
                              <td key={j} className="pr-3 py-0 tabular-nums">
                                {String(v)}
                              </td>
                            ))}
                          </tr>
                        ),
                      )}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {answer?.error && (
            <div className="mt-4 border border-critical p-2">
              <p className="text-critical text-sm">{String(answer.error)}</p>
            </div>
          )}
        </div>

        <div className="col-span-5 lg:col-span-4">
          <Ledger
            metric={answer?.metric_name as string}
            definition={answer?.definition as string}
            canonicalQuery={
              answer?.canonical_query as Record<string, unknown> | undefined
            }
            hash={answer?.semantic_query_hash as string}
            sql={answer?.sql as string}
            role={answer?.role as string}
            latencyMs={answer?.latency_ms as number}
          />
        </div>
      </div>

      <StatusBar serviceHealth="ready" />
    </main>
  );
}
