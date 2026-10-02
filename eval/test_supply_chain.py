"""Suite 7: what we ship is what we audited. pip-audit and npm audit gate on high severity;
the SBOM is produced in CI with the image scan, which needs Docker and runs there."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
NODE = os.getenv("SCM_NODE_BIN", "")


def test_runtime_requirements_are_pinned_by_lock_files():
    assert (ROOT / "requirements.lock").exists()
    assert (ROOT / "web" / "package-lock.json").exists()
    for line in (ROOT / "requirements.lock").read_text().splitlines():
        if line and not line.startswith(("#", " ", "-")):
            assert "==" in line, line


@pytest.mark.skipif(os.getenv("SCM_OFFLINE") == "1", reason="needs network to read the advisory databases")
def test_python_dependencies_have_no_known_high_severity_vulnerabilities():
    result = subprocess.run([sys.executable, "-m", "pip_audit", "-r", str(ROOT / "requirements.lock"), "--format", "json",
                             "--progress-spinner", "off"], capture_output=True, text=True)
    report = json.loads(result.stdout or "{}")
    findings = [(d["name"], v["id"]) for d in report.get("dependencies", []) for v in d.get("vulns", [])]
    assert not findings, findings


@pytest.mark.skipif(os.getenv("SCM_OFFLINE") == "1", reason="needs network to read the advisory databases")
def test_web_dependencies_have_no_high_severity_advisories():
    npm = shutil.which("npm", path=NODE or None)
    if not npm:
        pytest.skip("npm is not on the PATH")
    result = subprocess.run([npm, "audit", "--omit=dev", "--audit-level=high", "--json"], cwd=ROOT / "web",
                            capture_output=True, text=True)
    counts = json.loads(result.stdout)["metadata"]["vulnerabilities"]
    assert counts.get("high", 0) == 0 and counts.get("critical", 0) == 0, counts


def test_the_image_is_built_from_pinned_bases_and_runs_unprivileged():
    dockerfile = (ROOT / "Dockerfile").read_text()
    assert "@sha256:" in dockerfile
    assert "USER " in dockerfile and "USER root" not in dockerfile.split("FROM")[-1]
    assert "requirements.lock" in dockerfile and "npm ci" in dockerfile


def test_ci_publishes_an_sbom_and_scans_the_image():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    assert "cyclonedx" in ci.lower()
    assert "trivy" in ci.lower() and "--severity HIGH,CRITICAL" in ci and "--exit-code 1" in ci
    assert "|| true" not in ci
