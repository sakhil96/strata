---
name: ontology-compile
description: Compile the LinkML ontology and metric registry into every downstream target (semantic views, VQRs, policies, dbt, glossary, Ossie, Cube, Databricks, LinkML artefacts, ER diagram). Use with /compile or after any edit to ontology/.
---

# Ontology compile

1. `make compile` (or `python ontology/compile.py --env dev --version 1`; `--target` limits to one).
   `check_registry` refuses the compile if a metric lacks a required field or names an unknown table.
2. `pytest ontology/tests -q`: golden files and registry invariants.
3. `git diff --stat snowflake/semantic dbt/models ontology/generated` and report what moved.
4. Name any metric still `status: draft`; drafts compile for DEV and TEST only.
5. Never hand-edit compiled output. Change `ontology/metrics.yaml` or `ontology/ontology.yaml` and recompile.
