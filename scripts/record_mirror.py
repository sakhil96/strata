"""Record the public mirror's answers from the local build.

The demo-mode front end has no backend: it fetches /recorded/<name>.json. This script
calls the local API in-process and writes every answer the mirror's pages ask for,
under the same names web/lib/api.ts derives.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SCM_BACKEND", "local")

from fastapi.testclient import TestClient  # noqa: E402

from api.main import app  # noqa: E402

OUT = ROOT / "web" / "public" / "recorded"
PERSONAS = ["PLANNING_ROLE", "PROCUREMENT_ROLE", "LOGISTICS_ROLE", "EXECUTIVE_ROLE"]

# Kept in step with web/app/ask/page.tsx and web/app/compare/page.tsx.
ASK = [
    "What is on-time delivery for FY2026?",
    "Which suppliers have the worst on-time receipt?",
    "How did landed cost move by month across the July tariff step?",
    "What is DOI by plant?",
]
COMPARE = [
    {
        "PLANNING_ROLE": "What is our delivery rate for FY2026?",
        "PROCUREMENT_ROLE": "What is customer delivery performance for FY2026?",
        "LOGISTICS_ROLE": "What is delivery reliability for FY2026?",
    },
    {
        "PLANNING_ROLE": "What was availability in Q3?",
        "PROCUREMENT_ROLE": "What was unit fill in Q3?",
        "LOGISTICS_ROLE": "What was shipment completeness in Q3?",
    },
    {
        "PLANNING_ROLE": "What are our days of supply?",
        "PROCUREMENT_ROLE": "How many stock days do we hold?",
        "LOGISTICS_ROLE": "What is warehouse days cover?",
    },
]


def slug(text: str) -> str:
    """Same hash as slug() in web/lib/api.ts."""
    h = 0
    for ch in text.strip().lower():
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    return f"{h:08x}"


def js_json(value) -> str:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    client = TestClient(app)
    written = 0

    def save(name: str, response) -> None:
        nonlocal written
        if response.status_code >= 500:
            raise SystemExit(f"{name}: {response.status_code} {response.text[:200]}")
        (OUT / f"{name}.json").write_text(json.dumps(response.json(), indent=2, sort_keys=True) + "\n")
        written += 1

    for name, path in [("meta", "/api/meta"), ("glossary", "/api/glossary"), ("audit", "/api/audit?limit=20"),
                       ("status", "/api/status"), ("eval-report", "/api/eval/report"),
                       ("operations", "/api/operations"), ("governance", "/api/governance")]:
        save(name, client.get(path))
    for entry in client.get("/api/glossary").json():
        save(f"lineage-{entry['metric_name']}", client.get(f"/api/lineage/{entry['metric_name']}"))
    save("before-after-fy2026", client.post("/api/before-after", json={"window": "fy2026"},
                                            headers={"X-Persona": "EXECUTIVE_ROLE"}))
    for phrasings in COMPARE:
        save(f"compare-{slug(js_json(phrasings))}", client.post("/api/compare", json={"phrasings": phrasings}))
    for persona in PERSONAS:
        for question in ASK:
            save(f"ask-{persona}-{slug(question)}",
                 client.post("/api/ask", json={"question": question, "persona": persona},
                             headers={"X-Persona": persona}))
    print(f"recorded {written} answers into {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
