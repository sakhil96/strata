import { formatValue } from "@/lib/format";
import type { GlossaryEntry } from "@/lib/types";

export function MetricIndex({ entries }: { entries: GlossaryEntry[] }) {
  const sorted = [...entries].sort((a, b) => a.title.localeCompare(b.title));
  const letters = [...new Set(sorted.map((e) => e.title[0].toUpperCase()))];
  return (
    <div className="grid grid-cols-12 gap-x-3">
      <nav aria-label="Index letters" className="col-span-12 mb-3 flex flex-wrap gap-2 lg:col-span-1 lg:mb-0 lg:flex-col lg:gap-1">
        {letters.map((l) => (
          <a key={l} href={`#letter-${l}`} className="font-display text-lg font-light text-ash hover:text-ore">
            {l}
          </a>
        ))}
      </nav>
      <div className="col-span-12 lg:col-span-11">
        {letters.map((letter) => (
          <section key={letter} id={`letter-${letter}`} aria-label={`Metrics starting ${letter}`} className="rule pt-2">
            <p className="font-display text-2xl font-light text-hairline" aria-hidden>
              {letter}
            </p>
            {sorted
              .filter((e) => e.title[0].toUpperCase() === letter)
              .map((e) => (
                <article key={e.metric_name} id={e.metric_name} className="grid grid-cols-12 gap-x-3 border-b border-hairline py-3">
                  <header className="col-span-12 md:col-span-4">
                    <h3 className="font-display text-xl font-semibold text-bone">{e.title}</h3>
                    <p className="font-mono text-micro text-ash">{e.metric_name}</p>
                    <p className="mt-1 font-mono text-micro uppercase">
                      <span className={e.status === "approved" ? "text-good" : e.status === "deprecated" ? "text-critical" : "text-warn"}>
                        {e.status}
                      </span>
                      <span className="text-ash"> · v{e.version} · {e.approved_on}</span>
                    </p>
                    {e.parent ? (
                      <p className="mt-1 text-sm text-ash">
                        Variant of{" "}
                        <a className="link" href={`#${e.parent}`}>
                          {e.parent}
                        </a>
                      </p>
                    ) : null}
                    {e.deprecated_by ? (
                      <p className="mt-1 text-sm text-critical">
                        Replaced by <a className="link" href={`#${e.deprecated_by}`}>{e.deprecated_by}</a>
                      </p>
                    ) : null}
                  </header>
                  <div className="col-span-12 md:col-span-8">
                    <p className="text-base text-bone">{e.definition}</p>
                    <dl className="mt-2 grid grid-cols-2 gap-x-3 gap-y-1 text-sm md:grid-cols-4">
                      <div>
                        <dt className="micro">Owner</dt>
                        <dd>{e.owner}</dd>
                      </div>
                      <div>
                        <dt className="micro">Steward</dt>
                        <dd>{e.steward}</dd>
                      </div>
                      <div>
                        <dt className="micro">SCOR</dt>
                        <dd>{e.scor_attribute}</dd>
                      </div>
                      <div>
                        <dt className="micro">Unit</dt>
                        <dd>{formatValue(null, e.unit) === "—" ? e.unit.replaceAll("_", " ") : e.unit}</dd>
                      </div>
                    </dl>
                    <p className="mt-2 font-mono text-micro text-ash">{e.formula_text}</p>
                    {e.variants.length ? (
                      <p className="mt-1 text-sm text-ash">
                        Variants:{" "}
                        {e.variants.map((v, i) => (
                          <span key={v}>
                            {i ? ", " : ""}
                            <a className="link" href={`#${v}`}>
                              {v}
                            </a>
                          </span>
                        ))}
                      </p>
                    ) : null}
                    {e.synonyms.length ? <p className="mt-1 text-sm text-ash">Also asked as {e.synonyms.join(", ")}</p> : null}
                    <a className="link mt-1 inline-block text-sm" href={`/lineage/${e.metric_name}`}>
                      Lineage of {e.title.toLowerCase()}
                    </a>
                  </div>
                </article>
              ))}
          </section>
        ))}
      </div>
    </div>
  );
}
