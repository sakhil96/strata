# Judging checklist

Each line names the evidence. "needs account" marks items verified only by the account run.

- [ ] Ontology compiles to semantic views, dbt, glossary, Ossie, Cube, Databricks: `make compile`, `ontology/tests`
- [ ] Every metric and variant matches truth on every grouping: `eval/test_metric_identity.py`
- [ ] Persona phrasings converge on one hash: `eval/test_persona_consistency.py`
- [ ] 50 governed questions resolve exactly, 10 refusals refuse: `eval/test_nl_accuracy.py`
- [ ] Agent tools limited to the three procedures for numbers: `eval/test_governance.py`
- [ ] Masking and row access by role: `snowflake/setup/04_policies.sql` (needs account)
- [ ] Lineage from GET_LINEAGE matches the compiled path (needs account, Enterprise edition)
- [ ] Ten pages, axe clean at 390/1024/1440, strict CSP: `web/tests/e2e`
- [ ] Reproducible data and compile: `make reproducible`
- [ ] Hash-locked dependencies, SBOM, image scan: `.github/workflows/ci.yml`
- [ ] Release gate and rollback: `scripts/release_gate.py`, `docs/runbooks/rollback.md` (needs account)
