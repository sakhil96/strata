"use client";

import { SectionNumber } from "@/components/section-number";
import { StatusBar } from "@/components/status-bar";

export default function AboutPage() {
  return (
    <main className="pt-6">
      <SectionNumber number="10" />
      <h1 className="font-display text-2xl font-light mt-1 mb-4">About</h1>

      <div className="grid grid-cols-12 gap-3">
        <div className="col-span-8">
          <h2 className="text-micro uppercase text-ash tracking-widest mb-2">
            Architecture
          </h2>
          <div className="font-mono text-sm text-ash space-y-1">
            <p>ontology.yaml → compile.py → semantic views, dbt, glossary, Ossie, Cube</p>
            <p>4 source systems → RAW → STAGING → CONFORMED → SEMANTIC</p>
            <p>Cortex Agent → GOVERNED_QUERY → SEMANTIC_VIEW() → AUDIT.ANSWERS</p>
            <p>FastAPI + Next.js → SPCS container → Snowflake login</p>
          </div>

          <h2 className="text-micro uppercase text-ash tracking-widest mt-4 mb-2">
            Data card
          </h2>
          <div className="font-mono text-sm text-ash space-y-0">
            <p>Fiscal year: 1 Oct 2025 – 30 Sep 2026</p>
            <p>3 plants (US, DE, SG) + 2 DCs</p>
            <p>40 suppliers in 8 countries</p>
            <p>300 parts in 6 categories, 18 families</p>
            <p>120 customers in 4 segments</p>
            <p>~60k sales order lines, ~15k shipments, ~8k PO lines</p>
            <p>Daily inventory snapshots, FX rates, delivery events</p>
            <p>Deterministic seed: 20261002</p>
          </div>

          <h2 className="text-micro uppercase text-ash tracking-widest mt-4 mb-2">
            Design principles
          </h2>
          <ol className="text-sm text-bone space-y-1 list-decimal ml-4">
            <li>One ontology, many targets. Edit the registry, not the output.</li>
            <li>Governed by default. No raw SQL in the agent. Every answer audited.</li>
            <li>Identical answers. Same hash, same number, every persona.</li>
            <li>Ratios of sums. Never average pre-computed ratios.</li>
            <li>The AI is a component, not the application.</li>
          </ol>
        </div>

        <div className="col-span-4">
          <h2 className="text-micro uppercase text-ash tracking-widest mb-2">
            Licences
          </h2>
          <div className="text-sm text-ash space-y-1">
            <p>Project: Apache 2.0</p>
            <p>Fonts: SIL Open Font License</p>
            <p>Reference data: public domain / public data</p>
          </div>

          <h2 className="text-micro uppercase text-ash tracking-widest mt-4 mb-2">
            Sources
          </h2>
          <div className="text-sm text-ash space-y-1">
            <p>HTS 2026: USITC (public domain)</p>
            <p>GSCPI: NY Fed (public data)</p>
            <p>SCOR attributes: ASCM (fair use)</p>
          </div>
        </div>
      </div>

      <StatusBar />
    </main>
  );
}
