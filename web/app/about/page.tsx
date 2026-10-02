"use client";

import { ContourField } from "@/components/contour-field";
import { PageHead, Section } from "@/components/section";
import { api } from "@/lib/api";
import { useResource } from "@/lib/use-resource";

const PRINCIPLES = [
  ["One registry, many targets", "Semantic views, dbt tests, the glossary, Ossie, Cube and Databricks are compiled from the same two files. We edit the registry, never the output."],
  ["Numbers come from one procedure", "The agent cannot write SQL. Every number passes through GOVERNED_QUERY, which writes the audit row before it returns."],
  ["Same question, same hash", "Roles differ in vocabulary, never in arithmetic. Four persona views carry the governed view's expressions byte for byte."],
  ["Ratios of sums", "We sum numerators and denominators at the grouping asked for. Averaging plant rates is how the board dashboard went wrong."],
  ["The model is optional", "The Builder and the resolver answer without it. The product degrades to slower typing, not to wrong numbers."],
];

export default function AboutPage() {
  const status = useResource(() => api.status(), []);
  const card = status.state === "ready" ? ((status.value as unknown as { data_card?: { rows?: Record<string, number>; seed?: number } }).data_card ?? {}) : {};
  return (
    <>
      <ContourField seed={7} />
      <PageHead
        numeral="13"
        kicker="How it is built"
        title="About Strata"
        lede="A supply chain ontology authored once and compiled into governed Snowflake semantic views. The model answers questions; it does not decide what the numbers mean."
      />
      <div className="space-y-12">
        <Section numeral="13.1" title="Architecture">
          <ol className="font-mono text-sm leading-7 text-bone">
            <li><span className="text-ash">01 bedrock</span> ontology.yaml + metrics.yaml → compile.py</li>
            <li><span className="text-ash">02 sources</span> ERP, TMS, supplier portal, warehouse sensors → RAW</li>
            <li><span className="text-ash">03 strata</span> dbt staging resolves keys, units, clocks and currencies → CONFORMED</li>
            <li><span className="text-ash">04 views</span> SCM_GOVERNED and four persona semantic views → SEMANTIC</li>
            <li><span className="text-ash">05 answer</span> Cortex Agent → GOVERNED_QUERY → SEMANTIC_VIEW() → AUDIT.ANSWERS</li>
            <li><span className="text-ash">06 surface</span> this front end and its API in one container on Snowpark Container Services</li>
          </ol>
        </Section>
        <Section numeral="13.2" title="Entities and relationships">
          <img src="/er_diagram.svg" alt="Entity relationship diagram of the supply chain ontology: suppliers, parts, plants, customers, orders, shipments, carriers, inventory and tariffs" className="w-full max-w-[960px]" />
        </Section>
        <Section numeral="13.3" title="Data card" lede="One simulated fiscal year, 1 October 2025 to 30 September 2026, deterministic from one seed.">
          <dl className="grid grid-cols-12 gap-x-3 gap-y-3">
            {Object.entries(card.rows ?? {}).map(([k, v]) => (
              <div key={k} className="col-span-6 md:col-span-3">
                <dt className="micro">{k.replaceAll("_", " ")}</dt>
                <dd className="font-mono text-lg tabular">{v.toLocaleString("en-GB")}</dd>
              </div>
            ))}
          </dl>
          {card.seed ? <p className="mt-2 font-mono text-micro text-ash">seed {card.seed}</p> : null}
        </Section>
        <Section numeral="13.4" title="Principles">
          <ol className="space-y-3">
            {PRINCIPLES.map(([title, body], i) => (
              <li key={title} className="grid grid-cols-12 gap-x-3 border-b border-hairline pb-2">
                <span className="col-span-2 font-display text-xl font-light text-ash md:col-span-1">{String(i + 1).padStart(2, "0")}</span>
                <span className="col-span-10 md:col-span-4 font-display text-lg text-bone">{title}</span>
                <span className="col-span-12 text-sm text-ash md:col-span-7">{body}</span>
              </li>
            ))}
          </ol>
        </Section>
        <Section numeral="13.5" title="Licences and sources">
          <ul className="space-y-1 text-sm text-ash">
            <li>Code: Apache 2.0.</li>
            <li>Fraunces, Instrument Sans and JetBrains Mono: SIL Open Font License 1.1, served from this origin.</li>
            <li>Tariff schedule extract: US International Trade Commission, public domain. Supply chain pressure index: Federal Reserve Bank of New York.</li>
            <li>All operational data is simulated. No proprietary dataset was used to build or calibrate it.</li>
          </ul>
        </Section>
      </div>
    </>
  );
}
