import type {
  Answer,
  AuditEntry,
  BeforeAfter,
  CompareResult,
  GlossaryEntry,
  Lineage,
  Meta,
  Persona,
  Problem,
  Refusal,
  SemanticQuery,
  Status,
} from "./types";

// The public mirror has no Snowflake behind it: it replays answers recorded from the
// local build, and sends Builder queries to a service-user API when one is configured.
export const DEMO = process.env.NEXT_PUBLIC_STRATA_MODE === "demo";
const SERVICE_API = process.env.NEXT_PUBLIC_STRATA_API ?? "";

export class ApiProblem extends Error {
  constructor(
    public readonly problem: Problem,
    public readonly status: number,
  ) {
    super(problem.message ?? problem.error);
  }
}

async function call<T>(path: string, persona: Persona | null, init?: RequestInit, base = ""): Promise<T> {
  const headers: Record<string, string> = { Accept: "application/json" };
  if (init?.body) headers["Content-Type"] = "application/json";
  if (persona) headers["X-Persona"] = persona;
  let response: Response;
  try {
    response = await fetch(`${base}/api${path}`, { ...init, headers, cache: "no-store" });
  } catch {
    throw new ApiProblem({ error: "unreachable", message: "The service did not answer. Check your connection and retry." }, 0);
  }
  const body = await response
    .json()
    .catch(() => ({ error: "unreadable", message: "The service sent a reply we could not read." }));
  if (!response.ok) throw new ApiProblem(body as Problem, response.status);
  return body as T;
}

async function recorded<T>(name: string): Promise<T> {
  const response = await fetch(`/recorded/${name}.json`);
  if (!response.ok)
    throw new ApiProblem({ error: "not_recorded", message: "This answer was not recorded for the public mirror." }, 404);
  return (await response.json()) as T;
}

export function slug(text: string): string {
  let hash = 0;
  for (const ch of text.trim().toLowerCase()) hash = (hash * 31 + ch.charCodeAt(0)) >>> 0;
  return hash.toString(16).padStart(8, "0");
}

export const api = {
  ask(question: string, persona: Persona): Promise<Answer | Refusal> {
    if (DEMO) return recorded(`ask-${persona}-${slug(question)}`);
    return call("/ask", persona, { method: "POST", body: JSON.stringify({ question, persona }) });
  },
  query(query: SemanticQuery, persona: Persona): Promise<Answer> {
    if (DEMO && !SERVICE_API) return recorded(`query-${persona}-${slug(JSON.stringify(query))}`);
    return call("/query", persona, { method: "POST", body: JSON.stringify({ query, persona }) }, DEMO ? SERVICE_API : "");
  },
  compare(phrasings: Partial<Record<Persona, string>>): Promise<CompareResult> {
    if (DEMO) return recorded(`compare-${slug(JSON.stringify(phrasings))}`);
    return call("/compare", null, { method: "POST", body: JSON.stringify({ phrasings }) });
  },
  beforeAfter(window: string): Promise<BeforeAfter> {
    if (DEMO) return recorded(`before-after-${window}`);
    return call("/before-after", "EXECUTIVE_ROLE", { method: "POST", body: JSON.stringify({ window }) });
  },
  meta: (): Promise<Meta> => (DEMO ? recorded("meta") : call("/meta", null)),
  glossary: (): Promise<GlossaryEntry[]> => (DEMO ? recorded("glossary") : call("/glossary", null)),
  lineage: (metric: string): Promise<Lineage> => (DEMO ? recorded(`lineage-${metric}`) : call(`/lineage/${metric}`, null)),
  audit: (limit = 20): Promise<AuditEntry[]> => (DEMO ? recorded("audit") : call(`/audit?limit=${limit}`, null)),
  status: (): Promise<Status> => (DEMO ? recorded("status") : call("/status", null)),
  evalReport: (): Promise<Record<string, unknown>> => (DEMO ? recorded("eval-report") : call("/eval/report", null)),
  operations: (): Promise<Record<string, unknown>> => (DEMO ? recorded("operations") : call("/operations", null)),
  governance: (): Promise<Record<string, unknown>> => (DEMO ? recorded("governance") : call("/governance", null)),
  personas: (): Promise<{ default: Persona; personas: Persona[] }> =>
    DEMO ? Promise.resolve({ default: "EXECUTIVE_ROLE", personas: [] }) : call("/personas", null),
};
