const PERCENT = new Set(["ratio"]);

export function formatValue(value: number | null | undefined, unit: string, digits?: number): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  if (PERCENT.has(unit)) return `${(value * 100).toFixed(digits ?? 1)}%`;
  if (unit === "usd_per_unit") return `$${value.toFixed(digits ?? 2)}`;
  if (unit === "days") return `${value.toFixed(digits ?? 1)} d`;
  if (unit === "hours") return `${value.toFixed(digits ?? 1)} h`;
  if (unit === "turns_per_year") return `${value.toFixed(digits ?? 1)}×`;
  return value.toFixed(digits ?? 2);
}

export function unitLabel(unit: string): string {
  return (
    { ratio: "share of lines", usd_per_unit: "USD per unit", days: "days", hours: "hours", turns_per_year: "turns a year" }[unit] ??
    unit
  );
}

// Fixed abbreviations, not the browser's locale data: the same month must read the same everywhere.
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export function monthLabel(iso: string): string {
  const [year, month] = iso.slice(0, 7).split("-");
  return `${MONTHS[Number(month) - 1]} ${year.slice(2)}`;
}

export function period(window: { start: string; end: string }): string {
  return `${monthLabel(window.start)} – ${monthLabel(window.end)}`;
}

export function shortHash(hash: string | null | undefined): string {
  return hash ? `${hash.slice(0, 8)}…${hash.slice(-4)}` : "—";
}

export const PERSONA_LABEL: Record<string, string> = {
  PLANNING_ROLE: "Planning",
  PROCUREMENT_ROLE: "Procurement",
  LOGISTICS_ROLE: "Logistics",
  EXECUTIVE_ROLE: "Executive",
  JUDGE_ROLE: "Reviewer",
};

export const REFUSAL_COPY: Record<string, string> = {
  out_of_ontology: "That is not something the supply chain ontology measures. Try the glossary for what it does.",
  raw_sql: "We do not run SQL typed into a question. Ask for a metric, or use the Builder.",
  table_access: "Tables, schemas and connections are not exposed here. Every answer goes through a governed view.",
  prompt_injection: "That reads as an attempt to change our instructions, so we stopped. It has been logged.",
  agent_refused: "The agent declined this question. It has been logged.",
};
