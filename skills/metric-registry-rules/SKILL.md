---
name: metric-registry-rules
description: Enforce the metric registry schema, change process and deployment gates.
---

# Metric registry rules

Every metric in `ontology/metrics.yaml` must declare:
name, title, type, grain, date_basis, window, numerator, denominator, definition,
formula_text, synonyms, variants, owner, steward, scor_attribute, unit,
persona_synonyms, version, status, approved_by, approved_on.

## Compilation gates

- Missing a required field: compile refuses.
- `status: draft`: compiles for DEV and TEST, blocked from PROD.
- `status: deprecated`: emitted with a deprecation notice in the glossary.

## Change process

1. Pull request to `metrics.yaml` with rationale in the PR body.
2. Steward approves (their name goes in `approved_by`).
3. Version bumped; `approved_on` set to today.
4. Compile and evaluation green in CI.
5. Deploy as a new semantic view version (`_V{n+1}`).
6. Previous version kept for rollback; deprecated after one release cycle.
