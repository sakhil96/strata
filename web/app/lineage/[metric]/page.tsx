import { readFileSync } from "node:fs";
import { join } from "node:path";

import { LineageView } from "./view";

export function generateStaticParams() {
  const glossary = JSON.parse(readFileSync(join(process.cwd(), "..", "ontology", "generated", "glossary.json"), "utf8")) as {
    metric_name: string;
  }[];
  return glossary.map((g) => ({ metric: g.metric_name }));
}

export default async function LineagePage({ params }: { params: Promise<{ metric: string }> }) {
  const { metric } = await params;
  return <LineageView metric={metric} />;
}
