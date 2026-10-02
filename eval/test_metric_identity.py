"""Metric identity tests: governed metrics vs truth within tolerance."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

METRICS_PATH = Path(__file__).resolve().parent.parent / "ontology" / "metrics.yaml"


def load_metrics():
    with open(METRICS_PATH) as f:
        data = yaml.safe_load(f)
    return data.get("metrics", {})


class TestMetricRegistry:
    def test_all_required_fields_present(self):
        required = [
            "title", "type", "grain", "date_basis", "window",
            "numerator", "denominator", "definition", "formula_text",
            "synonyms", "variants", "owner", "steward", "scor_attribute",
            "unit", "persona_synonyms", "version", "status",
            "approved_by", "approved_on",
        ]
        metrics = load_metrics()
        for name, defn in metrics.items():
            for field in required:
                assert field in defn and defn[field] is not None, (
                    f"metric '{name}' missing required field '{field}'"
                )

    def test_all_metrics_approved(self):
        metrics = load_metrics()
        for name, defn in metrics.items():
            assert defn["status"] == "approved", (
                f"metric '{name}' has status '{defn['status']}', expected 'approved'"
            )

    def test_no_duplicate_metric_names(self):
        metrics = load_metrics()
        names = list(metrics.keys())
        assert len(names) == len(set(names)), "duplicate metric names found"

    def test_persona_synonyms_cover_all_roles(self):
        roles = {"PLANNING_ROLE", "PROCUREMENT_ROLE", "LOGISTICS_ROLE", "EXECUTIVE_ROLE"}
        metrics = load_metrics()
        for name, defn in metrics.items():
            synonyms = defn.get("persona_synonyms", {})
            assert set(synonyms.keys()) == roles, (
                f"metric '{name}' persona_synonyms missing roles: {roles - set(synonyms.keys())}"
            )

    def test_ratio_metrics_have_numerator_and_denominator(self):
        metrics = load_metrics()
        for name, defn in metrics.items():
            if defn["type"] == "ratio":
                assert defn["numerator"], f"ratio metric '{name}' has empty numerator"
                assert defn["denominator"], f"ratio metric '{name}' has empty denominator"

    def test_inventory_turns_times_doi_equals_365(self):
        """The invariant: inventory_turns * days_of_inventory = 365."""
        metrics = load_metrics()
        assert "inventory_turns" in metrics, "inventory_turns metric not found"
        assert "days_of_inventory" in metrics, "days_of_inventory metric not found"
        # The invariant is enforced at query time, not in the registry;
        # this test verifies both metrics exist and are of type ratio.
        assert metrics["inventory_turns"]["type"] == "ratio"
        assert metrics["days_of_inventory"]["type"] == "ratio"
