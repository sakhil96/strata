"use client";

import { useEffect, useState } from "react";
import { SectionNumber } from "@/components/section-number";
import { StatusBar } from "@/components/status-bar";

interface GlossaryEntry {
  metric_name: string;
  title: string;
  definition: string;
  formula_text: string;
  owner: string;
  steward: string;
  version: number;
  status: string;
  scor_attribute: string;
  unit: string;
  synonyms: string[];
  variants: string[];
}

export default function GlossaryPage() {
  const [entries, setEntries] = useState<GlossaryEntry[]>([]);

  useEffect(() => {
    fetch("/api/glossary")
      .then((r) => r.json())
      .then(setEntries)
      .catch(() => setEntries([]));
  }, []);

  return (
    <main className="pt-6">
      <SectionNumber number="07" />
      <h1 className="font-display text-2xl font-light mt-1 mb-4">Glossary</h1>

      <div className="space-y-4">
        {entries.map((e) => (
          <div key={e.metric_name} className="border-b border-hairline pb-3">
            <div className="flex items-baseline gap-3">
              <h3 className="font-display text-xl font-semibold text-bone">
                {e.title}
              </h3>
              <span className="font-mono text-sm text-ash">{e.metric_name}</span>
              <span
                className={`text-micro uppercase tracking-widest ${e.status === "approved" ? "text-good" : e.status === "deprecated" ? "text-critical" : "text-warn"}`}
              >
                {e.status}
              </span>
              <span className="font-mono text-sm text-ash">v{e.version}</span>
            </div>
            <p className="text-base text-bone mt-1">{e.definition}</p>
            <div className="flex gap-6 mt-1 text-sm text-ash">
              <span>Owner: {e.owner}</span>
              <span>Steward: {e.steward}</span>
              <span>SCOR: {e.scor_attribute}</span>
              <span>Unit: {e.unit}</span>
            </div>
            {e.synonyms.length > 0 && (
              <p className="text-sm text-ash mt-1">
                Synonyms: {e.synonyms.join(", ")}
              </p>
            )}
            {e.variants.length > 0 && (
              <p className="text-sm text-ash">
                Variants: {e.variants.join(", ")}
              </p>
            )}
            <details className="mt-1">
              <summary className="text-micro uppercase text-ash tracking-widest cursor-pointer hover:text-bone">
                Formula
              </summary>
              <pre className="font-mono text-sm text-bone bg-stratum p-2 border border-hairline mt-1">
                {e.formula_text}
              </pre>
            </details>
          </div>
        ))}
      </div>
      <StatusBar />
    </main>
  );
}
