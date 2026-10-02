---
name: eval-runner
description: Run the evaluation suites against a target environment and report results.
---

# Evaluation runner

Run with `/eval [--env ENV] [--suite SUITE]`.

## Suites

1. **metric-identity**: governed metrics vs truth_metrics within tolerance.
2. **nl-accuracy**: agent resolution and numeric match on questions.yaml.
3. **persona-consistency**: identical hash and number across three roles.
4. **governance**: agent tools, policies, lineage, round-trip, grants, audit, injection refusal.
5. **resilience**: health probes, builder without model, timeouts, rollback, restore.
6. **frontend**: Playwright e2e, axe accessibility, security headers, banned-word lint.
7. **supply-chain**: dependency audit, image scan, SBOM.

## Output

`eval/report.json` and `eval/report.md`. Exit code 0 only if all requested suites pass.
