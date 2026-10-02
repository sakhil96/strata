"use client";

import { motion, useReducedMotion } from "framer-motion";
import Link from "next/link";
import { useEffect, useState } from "react";

import { ContourField } from "@/components/contour-field";
import { ArrowRight } from "@/components/icons";
import { Section } from "@/components/section";
import { Loading, Problem } from "@/components/states";
import { api } from "@/lib/api";
import { formatValue } from "@/lib/format";
import { useResource } from "@/lib/use-resource";

export default function Landing() {
  const story = useResource(() => api.beforeAfter("fy2026"), []);
  const report = useResource(() => api.evalReport(), []);
  const glossary = useResource(() => api.glossary(), []);
  const still = useReducedMotion();
  const [merged, setMerged] = useState(false);

  useEffect(() => {
    if (story.state !== "ready") return;
    const t = window.setTimeout(() => setMerged(true), still ? 0 : 1400);
    return () => window.clearTimeout(t);
  }, [story.state, still]);

  return (
    <>
      <ContourField />
      <section aria-labelledby="hero" className="grid grid-cols-12 gap-x-3 pb-12 pt-12">
        <div className="col-span-12 lg:col-span-7">
          <p className="micro">Supply chain ontology on Snowflake</p>
          <h1 id="hero" className="mt-2 font-display text-3xl font-light leading-none text-bone md:text-4xl">
            Three teams.
            <br />
            Three numbers.
            <br />
            <em className="font-normal text-ore">One question.</em>
          </h1>
          <p className="mt-4 max-w-measure text-lg text-ash">
            Planning, procurement and logistics each reported on-time delivery for FY2026, and each was right by its own rules. We
            wrote the rules down once, compiled them into governed semantic views, and every role now gets the same number with
            its working shown.
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            <Link href="/compare" className="action">
              Ask it as three roles <ArrowRight />
            </Link>
            <Link href="/before-after" className="quiet-action">
              See where the old numbers came from
            </Link>
          </div>
        </div>
        <div className="col-span-12 mt-8 lg:col-span-5 lg:mt-0" aria-live="polite">
          {story.state === "loading" ? <Loading what="Reading the three reports" /> : null}
          {story.state === "failed" ? <Problem problem={story.problem} /> : null}
          {story.state === "ready" ? (
            <div className="relative h-[360px]">
              {story.value.legacy.map((l, i) => (
                <motion.div
                  key={l.key}
                  initial={false}
                  animate={{ y: merged ? 120 : i * 112, opacity: merged ? 0 : 1 }}
                  transition={{ duration: 0.24, delay: merged ? i * 0.04 : 0, ease: [0.16, 1, 0.3, 1] }}
                  className="absolute left-0 right-0 flex items-baseline justify-between border-b border-hairline pb-1"
                >
                  <span className="micro">
                    {l.team} · {l.label}
                  </span>
                  <span className="font-display text-3xl font-light tabular text-bone">{formatValue(l.value, "ratio")}</span>
                </motion.div>
              ))}
              <motion.div
                initial={false}
                animate={{ opacity: merged ? 1 : 0, y: merged ? 96 : 140 }}
                transition={{ duration: 0.24, ease: [0.16, 1, 0.3, 1] }}
                className="absolute left-0 right-0"
                aria-hidden={!merged}
              >
                <p className="micro text-ore">Governed · on_time_delivery v1 · every role</p>
                <p className="font-display text-5xl font-light tabular text-ore">
                  {formatValue(story.value.governed.value, "ratio")}
                </p>
                <p className="mt-1 max-w-[44ch] text-sm text-ash">{story.value.governed.basis}</p>
              </motion.div>
            </div>
          ) : null}
        </div>
      </section>

      <div className="space-y-12">
        <Section
          numeral="01"
          title="The ontology"
          lede="Sixteen entities, from supplier to tariff code, written once in LinkML. Every metric names its grain, date basis, numerator, denominator, owner and steward, and the compiler refuses one that does not."
        >
          <dl className="grid grid-cols-12 gap-x-3 gap-y-4">
            {[
              ["Governed metrics and variants", glossary.state === "ready" ? glossary.value.length : null],
              ["Source systems reconciled", 4],
              ["Semantic views per environment", 5],
              ["Compiler targets", 8],
            ].map(([label, n]) => (
              <div key={String(label)} className="col-span-6 md:col-span-3">
                <dt className="micro">{label}</dt>
                <dd className="font-display text-3xl font-light tabular text-bone">{n ?? "—"}</dd>
              </div>
            ))}
          </dl>
        </Section>

        <Section
          numeral="02"
          title="Governed views"
          lede="One governed view and four persona views carry identical metric expressions. They differ only in the words each team uses and the breakdowns it reaches for first. Masking follows each column's sensitivity tag; row access follows a plant scope table."
        >
          <Link href="/glossary" className="link text-sm">
            Read the glossary
          </Link>
        </Section>

        <Section
          numeral="03"
          title="One answer"
          lede="The agent has three tools and no SQL. Every number it gives you came out of GOVERNED_QUERY, and arrives with the definition, the canonical query, its hash, the SQL that ran, the lineage and the role. When the model is down, the Builder asks the same procedure directly."
        >
          <Link href="/ask" className="link text-sm">
            Ask a question
          </Link>
        </Section>

        <Section
          numeral="04"
          title="Proof"
          lede="Seven evaluation suites gate every release to production. The latest run is below."
        >
          {report.state === "ready" ? (
            <p className="font-mono text-sm text-bone">
              {String((report.value as { summary?: string }).summary ?? "")}{" "}
              <Link href="/governance" className="link">
                Full report
              </Link>
            </p>
          ) : (
            <p className="text-sm text-ash">
              No evaluation report yet. Run <code className="font-mono">make eval</code> and it appears here.
            </p>
          )}
        </Section>
      </div>
    </>
  );
}
