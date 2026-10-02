---
name: ontology-compile
description: Compile the LinkML ontology and metric registry into all downstream targets (semantic views, dbt, glossary, Ossie, Cube, Databricks). Run with /compile.
---

# Ontology compile skill

When the user runs `/compile`, execute the following:

1. Validate `ontology/ontology.yaml` with LinkML (`linkml-validate`).
2. Validate `ontology/metrics.yaml` — every metric must have all required fields.
3. Run `python ontology/compile.py` with the requested `--target` and `--env` flags.
   Default: all targets, env from the active guardrails scope.
4. Check that every generated file has the single-line header comment.
5. Run golden-file tests in `ontology/tests/`.
6. Report which files changed and whether any metric has `status: draft`.
