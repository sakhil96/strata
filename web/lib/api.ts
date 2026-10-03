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

// What a pending call is waiting on, for the loading line: the service waking after a suspend, or
// a cold query past its own timeout and retried once.
export type Pending = "waking" | "slow" | null;
const listeners = new Set<(pending: Pending) => void>();
export function onPending(listener: (pending: Pending) => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}
const announce = (pending: Pending) => listeners.forEach((l) => l(pending));

const WAKE_ATTEMPTS = 24;
// The agent path takes about half a minute; everything else answers in a few seconds once warm.
const TIMEOUT_MS: Record<string, number> = { "/ask": 120_000, "/compare": 90_000 };

async function attempt(url: string, init: RequestInit, timeoutMs: number): Promise<Response | "timeout"> {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...init, signal: controller.signal, cache: "no-store" });
  } catch (err) {
    if (controller.signal.aborted) return "timeout";
    throw err;
  } finally {
    window.clearTimeout(timer);
  }
}

async function call<T>(path: string, persona: Persona | null, init?: RequestInit, base = ""): Promise<T> {
  const headers: Record<string, string> = { Accept: "application/json" };
  if (init?.body) headers["Content-Type"] = "application/json";
  if (persona) headers["X-Persona"] = persona;
  const url = `${base}/api${path}`;
  const timeoutMs = TIMEOUT_MS[path] ?? 45_000;
  let retriedSlow = false;
  try {
    for (let wake = 0; ;) {
      let response: Response | "timeout";
      try {
        response = await attempt(url, { ...init, headers }, timeoutMs);
      } catch {
        throw new ApiProblem(
          { error: "unreachable", message: "The service did not answer. Check your connection and retry." },
          0,
        );
      }
      if (response === "timeout") {
        if (retriedSlow)
          throw new ApiProblem({ error: "timed_out", message: "Still computing after two tries. Try again in a minute." }, 0);
        retriedSlow = true;
        announce("slow");
        continue;
      }
      if (response.status === 503 && wake < WAKE_ATTEMPTS) {
        wake += 1;
        announce("waking");
        const seconds = Number(response.headers.get("Retry-After")) || 5;
        await new Promise((resolve) => window.setTimeout(resolve, seconds * 1000));
        continue;
      }
      const body = await response
        .json()
        .catch(() => ({ error: "unreadable", message: "The service sent a reply we could not read." }));
      if (!response.ok) throw new ApiProblem(body as Problem, response.status);
      return body as T;
    }
  } finally {
    announce(null);
  }
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
  personas: (): Promise<{ default: Persona; pinned?: boolean; personas: Persona[] }> =>
    DEMO ? Promise.resolve({ default: "EXECUTIVE_ROLE", pinned: false, personas: [] }) : call("/personas", null),
};
