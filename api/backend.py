"""Where answers come from. Local mode reads the DuckDB build; Snowflake mode calls the
governed procedures under the signed-in user's identity. Routes never see the difference."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
import threading
import time
from collections import deque
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "ontology"))
import resolver  # noqa: E402
import semantic  # noqa: E402

from . import legacy  # noqa: E402

log = logging.getLogger("strata.backend")
PERSONA_VIEW = {
    "PLANNING_ROLE": "PLANNING_SV", "PROCUREMENT_ROLE": "PROCUREMENT_SV",
    "LOGISTICS_ROLE": "LOGISTICS_SV", "EXECUTIVE_ROLE": "EXECUTIVE_SV", "JUDGE_ROLE": "SCM_GOVERNED",
}
PERSONAS = tuple(PERSONA_VIEW)
VERSION = int(os.getenv("SCM_VERSION", "1"))
ROW_CAP = 10_000
STALE_AFTER_S = 6 * 3600


@dataclass
class Caller:
    user: str
    role: str
    request_id: str


class Backend(Protocol):
    mode: str

    def query(self, caller: Caller, query: dict[str, Any], question: str | None = None) -> dict[str, Any]: ...
    def resolve(self, caller: Caller, question: str) -> dict[str, Any]: ...
    def legacy_otd(self, window: str) -> list[dict[str, Any]]: ...
    def lineage(self, metric: str) -> dict[str, Any]: ...
    def audit(self, limit: int) -> list[dict[str, Any]]: ...
    def status(self) -> dict[str, Any]: ...
    def health(self) -> dict[str, Any]: ...


def view_for(role: str) -> str:
    return f"{PERSONA_VIEW.get(role, 'SCM_GOVERNED')}_V{VERSION}"


def checksum(rows: list[dict[str, Any]]) -> str:
    return hashlib.sha256(json.dumps(rows, sort_keys=True, default=str).encode()).hexdigest()[:16]


def contract(registry: semantic.Registry, result: dict[str, Any], caller: Caller, view: str,
             lineage: dict[str, Any], started: float, engine: str, notes: list[str] | None = None) -> dict[str, Any]:
    canonical = result["canonical_query"]
    metrics = [registry.metrics[m] for m in canonical["metrics"]]
    return {
        "metric_name": ", ".join(canonical["metrics"]),
        "metrics": [{
            "name": m["name"], "title": m["title"], "definition": m["definition"], "formula_text": m["formula_text"],
            "version": m["version"], "status": m["status"], "grain": m["grain"], "date_basis": m["date_basis"],
            "window": m["window"], "denominator": m["denominator"], "unit": m["unit"], "owner": m["owner"],
            "steward": m["steward"], "parent": m["parent"],
        } for m in metrics],
        "definition": " ".join(m["definition"] for m in metrics),
        "canonical_query": canonical,
        "semantic_query_hash": result["semantic_query_hash"],
        "sql": result.get("sql") or semantic.render_semantic_sql(registry, canonical, view),
        "view": view,
        "engine": engine,
        "lineage": lineage,
        "role": caller.role,
        "user": caller.user,
        "rows": result["rows"],
        "row_count": len(result["rows"]),
        "result_checksum": checksum(result["rows"]),
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "notes": notes or [],
        "request_id": caller.request_id,
    }


class LocalBackend:
    """DuckDB build of the same dbt project; the laptop, CI and the public mirror run this."""

    mode = "local"

    def __init__(self, warehouse: Path | None = None, state_dir: Path | None = None):
        import duckdb

        self.registry = semantic.load_registry()
        self.warehouse_path = warehouse or Path(os.getenv("SCM_DUCKDB", ROOT / "dbt" / "target" / "scm.duckdb"))
        self.state = state_dir or Path(os.getenv("SCM_STATE_DIR", ROOT / ".strata"))
        self.state.mkdir(parents=True, exist_ok=True)
        self.audit_path = self.state / "answers.jsonl"
        self._lock = threading.Lock()
        self._db = duckdb.connect(str(self.warehouse_path), read_only=True)
        self._recent: deque[dict[str, Any]] = deque(maxlen=500)
        if self.audit_path.exists():
            for line in self.audit_path.read_text().splitlines()[-500:]:
                self._recent.append(json.loads(line))
        self._values = None
        self._manifest = None

    def _cursor(self):
        return self._db.cursor()

    def dimension_values(self) -> dict[str, list[str]]:
        if self._values is None:
            cur = self._cursor()

            def distinct(sql: str) -> list[str]:
                return sorted(r[0] for r in cur.execute(sql).fetchall())

            self._values = {
                "segment": distinct("select distinct segment from conformed.dim_customer"),
                "part_family": distinct("select distinct part_family from conformed.dim_part"),
                "category": distinct("select distinct category from conformed.dim_part"),
                "region": distinct("select distinct region from conformed.dim_plant"),
                "plant_id": distinct("select plant_id from conformed.dim_plant"),
                "carrier_type": distinct("select distinct carrier_type from conformed.dim_carrier"),
                "supplier_country": distinct("select distinct supplier_country from conformed.dim_supplier"),
            }
        return self._values

    def resolve(self, caller: Caller, question: str) -> dict[str, Any]:
        return resolver.resolve(self.registry, question, caller.role, self.dimension_values()).as_dict()

    def query(self, caller: Caller, query: dict[str, Any], question: str | None = None) -> dict[str, Any]:
        started = time.perf_counter()
        view = view_for(caller.role)
        result = semantic.execute_local(self._cursor(), self.registry, query)
        result["rows"] = result["rows"][:ROW_CAP]
        answer = contract(self.registry, result, caller, view, self.lineage(result["canonical_query"]["metrics"][0]),
                          started, "duckdb")
        self._write_audit(caller, question, answer)
        return answer

    def _write_audit(self, caller: Caller, question: str | None, answer: dict[str, Any]) -> None:
        record = {
            "ts": datetime.now(UTC).isoformat(timespec="seconds"), "user": caller.user,
            "role": caller.role, "question": question, "metric": answer["metric_name"],
            "canonical_query": answer["canonical_query"], "hash": answer["semantic_query_hash"],
            "sql": answer["sql"], "result_checksum": answer["result_checksum"],
            "latency_ms": answer["latency_ms"], "request_id": caller.request_id,
        }
        with self._lock:
            with self.audit_path.open("a") as fh:
                fh.write(json.dumps(record, sort_keys=True) + "\n")
            self._recent.append(record)

    def record_refusal(self, caller: Caller, question: str, reason: str) -> None:
        record = {"ts": datetime.now(UTC).isoformat(timespec="seconds"), "user": caller.user,
                  "role": caller.role, "question": question, "metric": None, "refusal": reason,
                  "hash": None, "request_id": caller.request_id}
        with self._lock:
            with self.audit_path.open("a") as fh:
                fh.write(json.dumps(record, sort_keys=True) + "\n")
            self._recent.append(record)

    def legacy_otd(self, window: str) -> list[dict[str, Any]]:
        start, end = semantic.fiscal_range(window)
        return legacy.run(self._cursor(), legacy.local_sources(ROOT / "data" / "out"), start, end)

    def _load_manifest(self) -> dict[str, Any]:
        if self._manifest is None:
            path = ROOT / "dbt" / "target" / "manifest.json"
            self._manifest = json.loads(path.read_text()) if path.exists() else {"nodes": {}, "parent_map": {}}
        return self._manifest

    def lineage(self, metric: str) -> dict[str, Any]:
        if metric not in self.registry.metrics:
            raise semantic.SemanticError("unknown_metrics", f"{metric} is not a governed metric",
                                         suggestions={metric: semantic.closest(metric, list(self.registry.metrics))})
        m = self.registry.metrics[metric]
        table = m["semantic"]["table"]
        base = self.registry.tables[table]["base_table"].lower()
        facts = sorted(f for f in self.registry.tables[table].get("facts", []) if f"{table}.{f}" in m["semantic"]["expr"])
        manifest = self._load_manifest()
        parents = manifest.get("parent_map", {})
        start = next((k for k in parents if k.endswith(f".{base}") and k.startswith("model.")), None)
        layers: dict[str, list[str]] = {"source": [], "staging": [], "conformed": []}
        seen, frontier = set(), [start] if start else []
        while frontier:
            node = frontier.pop()
            if node in seen or node is None:
                continue
            seen.add(node)
            label = node.split(".", 2)[-1]
            if node.startswith("source."):
                layers["source"].append(label.replace(".", "/"))
            elif ".stg_" in node:
                layers["staging"].append(label)
            else:
                layers["conformed"].append(label)
            frontier.extend(parents.get(node, []))
        path = [
            {"layer": "source", "objects": sorted(layers["source"])},
            {"layer": "staging", "objects": sorted(layers["staging"])},
            {"layer": "conformed", "objects": sorted(set(layers["conformed"]))},
            {"layer": "semantic", "objects": [f"{table}.{metric}"], "columns": facts},
        ]
        return {"metric": metric, "source": "dbt manifest" if start else "registry", "path": path,
                "expression": m["semantic"]["expr"]}

    def audit(self, limit: int) -> list[dict[str, Any]]:
        return list(reversed(list(self._recent)))[:limit]

    def status(self) -> dict[str, Any]:
        card_path = ROOT / "data" / "out" / "DATA_CARD.json"
        card = json.loads(card_path.read_text()) if card_path.exists() else {}
        run_path = ROOT / "dbt" / "target" / "run_results.json"
        run = json.loads(run_path.read_text()) if run_path.exists() else {}
        report_path = ROOT / "eval" / "report.json"
        report = json.loads(report_path.read_text()) if report_path.exists() else {}
        freshness = []
        for system in ("erp", "tms", "portal", "iot"):
            files = sorted((ROOT / "data" / "out" / system).glob("*.parquet"))
            if files:
                newest = max(f.stat().st_mtime for f in files)
                freshness.append({"source": system, "loaded_at": datetime.fromtimestamp(newest, UTC)
                                  .isoformat(timespec="minutes"), "files": len(files),
                                  "stale": time.time() - newest > STALE_AFTER_S})
        results = run.get("results", [])
        return {
            "mode": self.mode, "as_of": card.get("as_of"), "freshness": freshness,
            "dbt": {"finished_at": run.get("metadata", {}).get("generated_at"),
                    "passed": sum(r["status"] in ("success", "pass") for r in results),
                    "failed": sum(r["status"] in ("error", "fail") for r in results)},
            "eval": {"pass_rate": report.get("pass_rate"), "generated_at": report.get("generated_at")},
            "data_card": card,
        }

    def operations(self) -> dict[str, Any]:
        latencies = sorted(r["latency_ms"] for r in self._recent if r.get("latency_ms") is not None)
        p95 = latencies[min(len(latencies) - 1, int(0.95 * len(latencies)))] if latencies else None
        report_path = ROOT / "eval" / "report.json"
        rate = json.loads(report_path.read_text()).get("pass_rate") if report_path.exists() else None
        slo = [
            slo_row("p95 answer latency through /query", "≤ 1500 ms", p95, 1500, "ms",
                    f"local audit trail, {len(latencies)} answers"),
            {"name": "p95 answer latency through the agent", "target": "≤ 6 s", "measured": None,
             "status": "needs_account", "source": "AUDIT.ANSWERS where path = agent"},
            {"name": "Service availability", "target": "99.5% a month", "measured": None,
             "status": "needs_account", "source": "SPCS readiness probe history in the event table"},
            slo_row("Evaluation pass rate", "≥ 90%", None if rate is None else round(rate * 100, 1), 90, "%",
                    "eval/report.json", higher_is_better=True),
        ]
        return {"slo": slo, "alerts": ALERTS,
                "cost": {"week": "this week", "credits": None,
                         "note": "Locally nothing is spent. On the account this reads the weekly cost task's output."}}

    def health(self) -> dict[str, Any]:
        self._cursor().execute("select 1").fetchone()
        return {"status": "ready", "mode": self.mode, "metrics": len(self.registry.metrics)}


class SnowflakeBackend:
    """Calls the governed procedures. Inside SPCS the service token plus the caller's
    identity header gives caller's-rights execution; outside, key-pair auth from connections.toml."""

    mode = "snowflake"

    def __init__(self):
        import snowflake.connector

        self.registry = semantic.load_registry()
        self.db = f"SCM_{os.getenv('SCM_ENV', 'dev').upper()}"
        token_file = Path("/snowflake/session/token")
        if token_file.exists():
            self._connect = lambda: snowflake.connector.connect(
                host=os.environ["SNOWFLAKE_HOST"], account=os.environ["SNOWFLAKE_ACCOUNT"],
                authenticator="oauth", token=token_file.read_text(), database=self.db, schema="AGENT",
                warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", f"SCM_WH_{os.getenv('SCM_ENV', 'dev').upper()}"))
        else:
            self._connect = lambda: snowflake.connector.connect(
                connection_name=os.getenv("SNOWFLAKE_CONNECTION_NAME", f"scm_{os.getenv('SCM_ENV', 'dev')}"),
                database=self.db, schema="AGENT")

    def _call(self, caller: Caller, procedure: str, *args: Any, path: str = "api") -> dict[str, Any]:
        tag = json.dumps({"app": "strata", "request_id": caller.request_id, "user": caller.user, "path": path})
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 30, QUERY_TAG = %s", (tag,))
            cur.execute("USE SECONDARY ROLES NONE")
            cur.execute("USE ROLE IDENTIFIER(%s)", (caller.role,))
            placeholders = ", ".join(["PARSE_JSON(%s)" if isinstance(a, (dict, list)) else "%s" for a in args])
            cur.execute(f"CALL {self.db}.AGENT.{procedure}({placeholders})",
                        [json.dumps(a) if isinstance(a, (dict, list)) else a for a in args])
            value = cur.fetchone()[0]
        return json.loads(value) if isinstance(value, str) else value

    def resolve(self, caller: Caller, question: str) -> dict[str, Any]:
        return resolver.resolve(self.registry, question, caller.role).as_dict()

    def query(self, caller: Caller, query: dict[str, Any], question: str | None = None) -> dict[str, Any]:
        canonical = semantic.canonicalise(self.registry, query)
        answer = self._call(caller, "GOVERNED_QUERY", view_for(caller.role), canonical["metrics"],
                            canonical["dimensions"], canonical["time"], canonical["filters"], question or "",
                            path="builder" if question is None else "resolver")
        if "error" in answer:
            raise semantic.SemanticError(answer["error"], answer.get("message", answer["error"]),
                                         **{k: v for k, v in answer.items() if k not in ("error", "message")})
        return answer

    def legacy_otd(self, window: str) -> list[dict[str, Any]]:
        start, end = semantic.fiscal_range(window)
        with self._connect() as conn:
            return legacy.run(conn.cursor(), legacy.snowflake_sources(self.db), start, end)

    def lineage(self, metric: str) -> dict[str, Any]:
        return self._call(Caller("service", "SCM_READER", "lineage"), "EXPLAIN_LINEAGE", metric)

    def audit(self, limit: int) -> list[dict[str, Any]]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(f"SELECT ts, username, role_used, metric_names, semantic_query_hash, latency_ms "
                        f"FROM {self.db}.AUDIT.ANSWERS ORDER BY ts DESC LIMIT %s", (min(limit, 200),))
            return [{"ts": str(r[0]), "user": r[1], "role": r[2], "metric": r[3], "hash": r[4], "latency_ms": r[5]}
                    for r in cur.fetchall()]

    def status(self) -> dict[str, Any]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(f"SELECT source_system, MAX(last_loaded_at), SUM(row_count), "
                        f"MAX(TIMESTAMPDIFF(HOUR, last_loaded_at, CURRENT_TIMESTAMP())) > 6 "
                        f"FROM {self.db}.OPS.FRESHNESS GROUP BY 1")
            freshness = [{"source": r[0], "loaded_at": str(r[1]), "rows": r[2], "stale": r[3]} for r in cur.fetchall()]
            cur.execute(f"SELECT MAX(run_started_at), COUNT_IF(status = 'success'), COUNT_IF(status <> 'success') "
                        f"FROM {self.db}.OPS.DBT_RUNS WHERE run_started_at > DATEADD(day, -1, CURRENT_TIMESTAMP())")
            dbt = cur.fetchone()
            cur.execute(f"SELECT pass_rate, run_at FROM {self.db}.EVAL.EVAL_RUNS ORDER BY run_at DESC LIMIT 1")
            ev = cur.fetchone()
        return {"mode": self.mode, "freshness": freshness,
                "dbt": {"finished_at": str(dbt[0]), "passed": dbt[1], "failed": dbt[2]},
                "eval": {"pass_rate": ev[0] if ev else None, "generated_at": str(ev[1]) if ev else None}}

    def operations(self) -> dict[str, Any]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {self.db}.OPS.SLO_STATUS")
            cols = [c[0].lower() for c in cur.description]
            slo = [dict(zip(cols, r, strict=False)) for r in cur.fetchall()]
            cur.execute(f"SELECT name, schedule, last_fired, state FROM {self.db}.OPS.ALERT_STATUS")
            alerts = [dict(zip(("name", "schedule", "last_fired", "state"), r, strict=False)) for r in cur.fetchall()]
            cur.execute(f"SELECT week, credits FROM {self.db}.OPS.WEEKLY_COST ORDER BY week DESC LIMIT 1")
            week = cur.fetchone()
        return {"slo": slo, "alerts": alerts,
                "cost": {"week": str(week[0]) if week else None, "credits": float(week[1]) if week else None,
                         "note": "From the weekly cost task over ACCOUNT_USAGE."}}

    def health(self) -> dict[str, Any]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
        return {"status": "ready", "mode": self.mode, "metrics": len(self.registry.metrics)}

    def record_refusal(self, caller: Caller, question: str, reason: str) -> None:
        self._call(caller, "RECORD_REFUSAL", question, reason)


ALERTS = [
    {"name": "STALE_SOURCE_ALERT", "schedule": "hourly, any source older than 6 h", "last_fired": None,
     "state": "defined, runs on the account"},
    {"name": "DBT_TEST_FAILURE_ALERT", "schedule": "hourly, failures in the last 2 h", "last_fired": None,
     "state": "defined, runs on the account"},
    {"name": "EVAL_REGRESSION_ALERT", "schedule": "daily 03:00 UTC, pass rate under 90%", "last_fired": None,
     "state": "defined, runs on the account"},
    {"name": "SLO_BREACH_ALERT", "schedule": "every 15 min, p95 over target", "last_fired": None,
     "state": "defined, runs on the account"},
    {"name": "SCM_PROD_MONITOR", "schedule": "resource monitor, 50/75/90/100%", "last_fired": None,
     "state": "defined, runs on the account"},
]


def slo_row(name: str, target: str, measured: float | None, limit: float, unit: str, source: str,
            higher_is_better: bool = False) -> dict[str, Any]:
    if measured is None:
        return {"name": name, "target": target, "measured": None, "status": "no_data", "source": source}
    met = measured >= limit if higher_is_better else measured <= limit
    return {"name": name, "target": target, "measured": f"{measured} {unit}", "status": "met" if met else "breached",
            "source": source}


_backend: Backend | None = None


def get_backend() -> Backend:
    global _backend
    if _backend is None:
        _backend = SnowflakeBackend() if os.getenv("SCM_BACKEND", "local") == "snowflake" else LocalBackend()
        log.info("backend_ready", extra={"mode": _backend.mode})
    return _backend


def set_backend(backend: Backend | None) -> None:
    global _backend
    _backend = backend
