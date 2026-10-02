"""Run the seven suites and write eval/report.json and eval/report.md.

A suite whose checks all need the account is reported as needs_account, not as passed. The
pass rate counts only checks that ran. Exit status is non-zero if any check that ran failed."""

from __future__ import annotations

import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SUITES = [
    ("metric_identity", "1 · Metric identity against truth", ["eval/test_metric_identity.py"]),
    ("nl_accuracy", "2 · Words to governed query", ["eval/test_nl_accuracy.py"]),
    ("persona_consistency", "3 · One question, three roles, one hash", ["eval/test_persona_consistency.py"]),
    ("governance", "4 · Governance rules", ["eval/test_governance.py"]),
    ("resilience", "5 · Resilience and operations", ["eval/test_resilience.py"]),
    ("frontend", "6 · Front end", ["eval/test_frontend.py"]),
    ("supply_chain", "7 · Software supply chain", ["eval/test_supply_chain.py"]),
]


def run_suite(name: str, paths: list[str]) -> dict:
    junit = HERE / ".results" / f"{name}.xml"
    junit.parent.mkdir(exist_ok=True)
    subprocess.run([sys.executable, "-m", "pytest", *paths, "-q", "-p", "no:cacheprovider", f"--junitxml={junit}"],
                   cwd=ROOT, capture_output=True, text=True)
    cases = ET.parse(junit).getroot().iter("testcase")
    passed = failed = skipped = 0
    needs_account, failures = [], []
    for case in cases:
        skip = case.find("skipped")
        if skip is not None:
            skipped += 1
            if "needs account" in (skip.get("message") or ""):
                needs_account.append(case.get("name"))
        elif case.find("failure") is not None or case.find("error") is not None:
            failed += 1
            failures.append(case.get("name"))
        else:
            passed += 1
    return {"passed": passed, "failed": failed, "skipped": skipped, "needs_account": needs_account, "failures": failures}


def main() -> int:
    suites = []
    for name, title, paths in SUITES:
        r = run_suite(name, paths)
        total = r["passed"] + r["failed"]
        status = "failed" if r["failed"] else ("needs_account" if not total else "passed")
        detail = "; ".join(filter(None, [
            f"failing: {', '.join(r['failures'][:3])}" if r["failures"] else "",
            f"{len(r['needs_account'])} check(s) need the account" if r["needs_account"] else "",
            f"{r['skipped'] - len(r['needs_account'])} skipped locally" if r["skipped"] - len(r["needs_account"]) else "",
        ]))
        suites.append({"name": name, "title": title, "status": status, "passed": r["passed"], "total": total,
                       "needs_account": r["needs_account"], "detail": detail or "all checks ran"})
    ran = sum(s["total"] for s in suites)
    passed = sum(s["passed"] for s in suites)
    pending = sum(len(s["needs_account"]) for s in suites)
    report = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "environment": "local DuckDB build",
        "pass_rate": round(passed / ran, 4) if ran else None,
        "summary": f"{passed} of {ran} checks passed across {len(suites)} suites; {pending} checks need the account.",
        "suites": suites,
    }
    (HERE / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    lines = [f"# Evaluation report, {report['generated_at']}", "", report["summary"], "",
             "| Suite | Status | Passed | Detail |", "|---|---|---|---|"]
    lines += [f"| {s['title']} | {s['status'].replace('_', ' ')} | {s['passed']}/{s['total']} | {s['detail']} |"
              for s in suites]
    (HERE / "report.md").write_text("\n".join(lines) + "\n")
    print(report["summary"])
    return 1 if any(s["status"] == "failed" for s in suites) else 0


if __name__ == "__main__":
    sys.exit(main())
