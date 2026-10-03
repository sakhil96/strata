"""Compiled outputs are committed; these tests rebuild them in memory and require an exact match."""

import copy
import json

import pytest
import yaml

import compile as compiler
import semantic

VERSION = 1


@pytest.fixture(scope="module")
def registry():
    return semantic.load_registry()


@pytest.fixture(scope="module")
def ontology():
    return yaml.safe_load(compiler.ONTOLOGY_PATH.read_text())


@pytest.mark.parametrize("view", list(compiler.VIEWS))
def test_semantic_view_matches_committed_yaml(registry, view):
    vqrs = compiler.verified_queries(registry, view, VERSION)
    body = compiler.semantic_view(registry, view, compiler.VIEWS[view], "dev", VERSION, vqrs)
    committed = compiler.SEMANTIC_DIR / f"{view.lower()}_v{VERSION}.yaml"
    assert compiler.dump(body) == committed.read_text(), f"{committed.name} is stale; run make compile"


def test_glossary_matches_committed_json(registry):
    built = json.dumps(compiler.glossary(registry), indent=2, sort_keys=True) + "\n"
    assert built == (compiler.GENERATED / "glossary.json").read_text()


def test_dbt_schema_and_policies_match(registry, ontology):
    assert compiler.dbt_schema(ontology, registry) == compiler.DBT_SCHEMA.read_text()
    ent = compiler.load_entitlements()
    assert compiler.tags_sql(ent, "dev") == (compiler.POLICY_DIR / "tags.sql").read_text()
    assert compiler.secure_views_sql(ent, registry, "dev") == (compiler.POLICY_DIR / "standard" / "secure_views.sql").read_text()
    assert compiler.entitlements_sql(ent, "dev") == (compiler.POLICY_DIR / "standard" / "entitlements.sql").read_text()
    assert compiler.enterprise_policies_sql(ent, "dev") == (compiler.POLICY_DIR / "enterprise" / "policies.sql").read_text()


def test_cube_and_ossie_match(registry):
    for name, text in compiler.cube_models(registry).items():
        assert text == (compiler.CUBE_DIR / name).read_text(), name
    assert compiler.dump(compiler.ossie(registry, "dev")) == (compiler.GENERATED / "ossie_model.yaml").read_text()


def test_every_view_carries_identical_metric_expressions(registry):
    expressions = {}
    for view, persona in compiler.VIEWS.items():
        body = compiler.semantic_view(registry, view, persona, "dev", VERSION, [])
        expressions[view] = {m["name"]: m["expr"] for t in body["tables"] for m in t.get("metrics", [])}
    first = next(iter(expressions.values()))
    assert all(e == first for e in expressions.values())


def test_registry_refuses_a_metric_without_a_steward():
    raw = yaml.safe_load(semantic.REGISTRY_PATH.read_text())
    metrics = copy.deepcopy(raw["metrics"])
    del metrics["on_time_delivery"]["steward"]
    with pytest.raises(semantic.SemanticError) as err:
        semantic.flatten_metrics(metrics)
    assert err.value.code == "registry_incomplete"


def test_prod_refuses_draft_metrics(registry):
    drafted = copy.deepcopy(registry)
    drafted.metrics["unit_fill_rate"]["status"] = "draft"
    assert any("cannot ship to SCM_PROD" in p for p in compiler.check_registry(drafted, "prod"))
    assert compiler.check_registry(drafted, "test") == []



def test_cli_rewrites_committed_outputs_unchanged():
    from click.testing import CliRunner

    targets = ["snowflake-semantic", "vqr", "governance", "dbt", "glossary", "ossie", "cube", "databricks"]
    watched = sorted(p for d in (compiler.SEMANTIC_DIR, compiler.CUBE_DIR, compiler.DATABRICKS_DIR) for p in d.rglob("*")
                     if p.is_file())
    before = {p: p.read_bytes() for p in watched}
    args = [a for t in targets for a in ("--target", t)]
    result = CliRunner().invoke(compiler.main, args)
    assert result.exit_code == 0, result.output
    assert {p: p.read_bytes() for p in watched} == before


def test_cli_refuses_prod_when_a_metric_is_not_approved(monkeypatch):
    from click.testing import CliRunner

    real = semantic.load_registry

    def drafted():
        registry = real()
        registry.metrics["unit_fill_rate"]["status"] = "draft"
        return registry

    monkeypatch.setattr(compiler.semantic, "load_registry", drafted)
    result = CliRunner().invoke(compiler.main, ["--env", "prod", "--target", "glossary"])
    assert result.exit_code != 0
    assert "cannot ship to SCM_PROD" in result.output
