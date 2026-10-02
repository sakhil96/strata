"use client";

import { MetricIndex } from "@/components/index-list";
import { PageHead } from "@/components/section";
import { Loading, Problem } from "@/components/states";
import { api } from "@/lib/api";
import { useResource } from "@/lib/use-resource";

export default function GlossaryPage() {
  const glossary = useResource(() => api.glossary(), []);
  return (
    <>
      <PageHead
        numeral="09"
        kicker="Metric registry"
        title="Glossary"
        lede="Every governed metric and variant, with its owner, steward, version and SCOR attribute. Change one through a pull request to the registry; the process is in docs/metric-change-process.md."
      />
      {glossary.state === "loading" ? <Loading what="Reading the registry" /> : null}
      {glossary.state === "failed" ? <Problem problem={glossary.problem} /> : null}
      {glossary.state === "ready" ? <MetricIndex entries={glossary.value} /> : null}
    </>
  );
}
