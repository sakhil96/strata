"use client";

import Link from "next/link";

import { LineagePath } from "@/components/lineage-path";
import { PageHead } from "@/components/section";
import { Loading, Problem } from "@/components/states";
import { api } from "@/lib/api";
import { useResource } from "@/lib/use-resource";

export function LineageView({ metric }: { metric: string }) {
  const lineage = useResource(() => api.lineage(metric), [metric]);
  return (
    <>
      <PageHead
        numeral="10"
        kicker="Core sample"
        title={<span className="font-mono text-2xl">{metric}</span>}
        lede="From the source files each system sends us, through staging and the conformed model, to the metric in the semantic view. The highlighted strand is the model the metric reads."
      />
      {lineage.state === "loading" ? <Loading what="Tracing lineage" /> : null}
      {lineage.state === "failed" ? <Problem problem={lineage.problem} /> : null}
      {lineage.state === "ready" ? <LineagePath lineage={lineage.value} /> : null}
      <p className="mt-6">
        <Link href={`/glossary#${metric}`} className="link text-sm">
          Read the definition
        </Link>
      </p>
    </>
  );
}
