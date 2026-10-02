"use client";

import { useState } from "react";
import { Convergence } from "@/components/convergence";
import { SectionNumber } from "@/components/section-number";
import { StatusBar } from "@/components/status-bar";

export default function ComparePage() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<{
    metrics: Array<{ persona: string; value: string; phrasing: string }>;
    hash: string;
  } | null>(null);

  async function handleCompare() {
    if (!question.trim()) return;
    try {
      const resp = await fetch("/api/compare", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          personas: ["PLANNING_ROLE", "PROCUREMENT_ROLE", "LOGISTICS_ROLE"],
        }),
      });
      const data = await resp.json();
      setResult(data);
    } catch {
      setResult(null);
    }
  }

  return (
    <main className="pt-6">
      <SectionNumber number="05" />
      <h1 className="font-display text-2xl font-light mt-1 mb-4">
        Cross-persona comparison
      </h1>

      <div className="max-w-[600px] space-y-2 mb-6">
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="What is on-time delivery for Q2 FY2026?"
          rows={2}
          className="w-full bg-stratum border border-hairline text-bone font-sans text-base p-2 rounded-sm resize-none focus:border-ore focus:outline-none"
        />
        <button
          onClick={handleCompare}
          disabled={!question.trim()}
          className="bg-ore text-ground font-sans text-sm px-3 py-1 rounded-sm hover:brightness-110 transition-all disabled:opacity-40"
        >
          Compare across personas
        </button>
      </div>

      {result && <Convergence metrics={result.metrics} hash={result.hash} />}
      <StatusBar />
    </main>
  );
}
