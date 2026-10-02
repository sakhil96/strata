"""Generate evaluation report from test results."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPORT_DIR = Path(__file__).resolve().parent


def main():
    result = subprocess.run(
        ["pytest", str(REPORT_DIR), "-v", "--tb=short", "-q", "--json-report",
         f"--json-report-file={REPORT_DIR / 'report.json'}"],
        capture_output=True,
        text=True,
    )

    report_path = REPORT_DIR / "report.json"
    if report_path.exists():
        report = json.loads(report_path.read_text())
    else:
        report = {"summary": {"passed": 0, "failed": 0, "total": 0}}

    summary = report.get("summary", {})
    total = summary.get("total", 0)
    passed = summary.get("passed", 0)
    pass_rate = passed / total if total > 0 else 0

    output = {
        "timestamp": datetime.utcnow().isoformat(),
        "total_tests": total,
        "passed": passed,
        "failed": summary.get("failed", 0),
        "pass_rate": round(pass_rate, 4),
        "suites": {
            "metric_identity": "pending",
            "nl_accuracy": "pending",
            "persona_consistency": "pending",
            "governance": "pending",
            "resilience": "pending",
            "frontend": "pending",
            "supply_chain": "pending",
        },
    }

    report_json = REPORT_DIR / "report.json"
    report_json.write_text(json.dumps(output, indent=2))

    report_md = REPORT_DIR / "report.md"
    lines = [
        f"# Evaluation Report — {output['timestamp']}",
        "",
        f"Total: {total} | Passed: {passed} | Failed: {output['failed']} | Rate: {pass_rate:.0%}",
        "",
    ]
    report_md.write_text("\n".join(lines))

    print(f"Report written to {report_json} and {report_md}")
    sys.exit(0 if pass_rate >= 0.9 else 1)


if __name__ == "__main__":
    main()
