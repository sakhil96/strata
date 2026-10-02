import { Convergence } from "@/components/convergence";
import { SectionNumber } from "@/components/section-number";

export default function LandingPage() {
  return (
    <main>
      <header className="pt-10 pb-8">
        <p className="text-micro uppercase text-ash tracking-widest mb-1">
          STRATA
        </p>
        <h1 className="font-display text-4xl font-light text-bone leading-tight">
          Three teams. Three numbers.
          <br />
          One question.
        </h1>
      </header>

      <Convergence
        metrics={[
          {
            persona: "Planning",
            value: "91.3%",
            phrasing: "What is our delivery rate?",
          },
          {
            persona: "Procurement",
            value: "91.3%",
            phrasing: "How is supplier delivery performance?",
          },
          {
            persona: "Logistics",
            value: "91.3%",
            phrasing: "What is carrier on-time?",
          },
        ]}
        hash="a4f2e91c"
      />

      <section className="grid grid-cols-12 gap-3 mt-10">
        <div className="col-span-7">
          <SectionNumber number="01" />
          <h2 className="font-display text-2xl font-light mt-1 mb-2">
            The ontology
          </h2>
          <p className="text-ash text-base max-w-[480px]">
            Every metric is defined once in a typed registry. The compiler
            generates semantic views, dbt models, a glossary, and interchange
            formats from that single source.
          </p>
        </div>
        <div className="col-span-5" />
      </section>

      <section className="grid grid-cols-12 gap-3 mt-8">
        <div className="col-span-5" />
        <div className="col-span-7">
          <SectionNumber number="02" />
          <h2 className="font-display text-2xl font-light mt-1 mb-2">
            Governed views
          </h2>
          <p className="text-ash text-base max-w-[480px]">
            Five semantic views — one governed master and four persona views —
            expose identical metric expressions. Row access and masking policies
            enforce who sees what.
          </p>
        </div>
      </section>

      <section className="grid grid-cols-12 gap-3 mt-8">
        <div className="col-span-8">
          <SectionNumber number="03" />
          <h2 className="font-display text-2xl font-light mt-1 mb-2">
            One answer
          </h2>
          <p className="text-ash text-base max-w-[480px]">
            The agent has three tools and no SQL access. Every answer returns
            the metric name, governed definition, canonical query, hash,
            lineage, and role. Every answer is audited.
          </p>
        </div>
        <div className="col-span-4" />
      </section>

      <section className="grid grid-cols-12 gap-3 mt-8 mb-10">
        <div className="col-span-4" />
        <div className="col-span-8">
          <SectionNumber number="04" />
          <h2 className="font-display text-2xl font-light mt-1 mb-2">Proof</h2>
          <p className="text-ash text-base max-w-[480px]">
            Seven evaluation suites gate every release. The evaluation report,
            grants snapshot, YAML round-trip, and DESCRIBE AGENT output are
            available on the governance page.
          </p>
        </div>
      </section>
    </main>
  );
}
