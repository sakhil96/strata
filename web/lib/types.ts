export type Persona =
  "PLANNING_ROLE" | "PROCUREMENT_ROLE" | "LOGISTICS_ROLE" | "EXECUTIVE_ROLE" | "EMEA_PLANNING_ROLE" | "JUDGE_ROLE";

export interface TimeWindow {
  range?: string;
  start?: string;
  end?: string;
}

export interface Filter {
  dimension: string;
  operator: "=" | "!=" | "in";
  value: string | string[];
}

export interface SemanticQuery {
  metrics: string[];
  dimensions: string[];
  time: TimeWindow;
  filters: Filter[];
}

export interface MetricCard {
  name: string;
  title: string;
  definition: string;
  formula_text: string;
  version: number;
  status: string;
  grain: string;
  date_basis: string;
  window: string;
  denominator: string;
  unit: string;
  owner: string;
  steward: string;
  parent: string | null;
}

export interface LineageStep {
  layer: "source" | "staging" | "conformed" | "semantic";
  objects: string[];
  columns?: string[];
}

export interface Lineage {
  metric: string;
  source: string;
  path: LineageStep[];
  expression: string;
}

export type Row = Record<string, string | number | null>;

export interface Answer {
  metric_name: string;
  metrics: MetricCard[];
  definition: string;
  canonical_query: { metrics: string[]; dimensions: string[]; time: { start: string; end: string }; filters: Filter[] };
  semantic_query_hash: string;
  sql: string;
  view: string;
  engine: string;
  lineage: Lineage;
  role: Persona;
  user: string;
  rows: Row[];
  row_count: number;
  result_checksum: string;
  latency_ms: number;
  notes: string[];
  path?: "agent" | "resolver" | "builder" | "recorded";
  fallback?: boolean;
  fallback_reason?: string | null;
  narrative?: string;
  lead?: string | null;
  reading?: string | null;
  answers?: Answer[];
  total_ms?: number;
  request_id: string;
}

export interface Refusal {
  refusal: string;
  path: string;
  fallback?: boolean;
  fallback_reason?: string | null;
  narrative?: string;
}

export interface Problem {
  error: string;
  message?: string;
  suggestions?: Record<string, string[]>;
  valid_dimensions?: string[];
  request_id?: string;
}

export interface CompareColumn {
  role: Persona;
  phrasing: string;
  hash?: string;
  metric_name?: string;
  value?: number | null;
  unit?: string;
  refusal?: string;
  ledger?: Answer;
}

export interface CompareResult {
  columns: CompareColumn[];
  converged: boolean;
  hash: string | null;
}

export interface LegacyNumber {
  key: string;
  team: string;
  label: string;
  basis: string;
  value: number;
}

export interface BeforeAfter {
  window: { start: string; end: string };
  legacy: LegacyNumber[];
  governed: { value: number; basis: string; ledger: Answer };
}

export interface GlossaryEntry {
  metric_name: string;
  title: string;
  parent: string | null;
  variants: string[];
  type: string;
  grain: string;
  date_basis: string;
  window: string;
  numerator: string;
  denominator: string;
  definition: string;
  formula_text: string;
  expression: string;
  unit: string;
  owner: string;
  steward: string;
  scor_attribute: string;
  synonyms: string[];
  version: number;
  status: string;
  approved_by: string;
  approved_on: string;
  deprecated_by: string | null;
}

export interface MetaMetric {
  name: string;
  title: string;
  type: string;
  unit: string;
  parent: string | null;
  date_basis: string;
  dimensions: string[];
}

export interface Meta {
  version: number;
  metrics: MetaMetric[];
  dimensions: Record<string, { table: string; title?: string; synonyms: string[] }>;
  windows: string[];
  values: Record<string, string[]>;
}

export interface AuditEntry {
  ts: string;
  user: string;
  role: string;
  metric: string | null;
  hash: string | null;
  refusal?: string;
  latency_ms?: number;
  question?: string | null;
}

export interface Status {
  mode: string;
  as_of?: string;
  freshness: { source: string; loaded_at: string; files?: number; rows?: number }[];
  dbt: { finished_at: string | null; passed: number; failed: number };
  eval: { pass_rate: number | null; generated_at: string | null };
}
