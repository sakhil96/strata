# Status

Last updated 2026-10-02. "Done" means proven by a command run on the local build; "needs account"
means written and checked locally (compiles, renders, lints) but only provable on Snowflake.

## Finish checks (all run on this commit's tree)

| Check | Result |
|---|---|
| `scripts/reproducible.sh` (`make data` and `make compile` twice) | 184 files byte-identical |
| `dbt build --target local` | 78 of 78 pass |
| `pytest ontology/tests api/tests eval` | 121 passed, 3 skipped (need account); coverage 83% |
| `eval/report.py` | 85 of 85 runnable checks pass across 7 suites; 2 need the account |
| `ruff check .` | clean |
| `npm run build`, `npm run build:demo`, `npm run lint` | pass |
| Playwright at 390, 1024, 1440 with axe and CSP checks | 78 of 78 pass |
| `pip-audit` on requirements.lock, `npm audit --omit=dev` | no known vulnerabilities |
| `cortex plugin validate .` | valid |

## Spec sections

| Section | Status | Evidence |
|---|---|---|
| Ontology (LinkML) and metric registry | done | `ontology/`, `ontology/tests` |
| Compiler targets: semantic views, VQRs, policies, dbt, glossary, Ossie, Cube, Databricks, LinkML, ER | done | `make compile`, golden tests |
| Synthetic sources, truth by month × plant × region × segment × family | done | `eval/test_metric_identity.py` |
| dbt on DuckDB and Snowflake | done locally; Snowflake target needs account | `dbt/` |
| Semantic views deployed, round-trip YAML | needs account | `snowflake/semantic/deploy.sql` |
| Masking, row access, grants | written; needs account | `snowflake/setup/04_policies.sql` |
| Procedures GOVERNED_QUERY, DESCRIBE_METRIC, EXPLAIN_LINEAGE | logic tested locally; deployment needs account | `snowflake/procs/` |
| Agent with Analyst and Search, Steward agent, MCP server | written; needs account | `snowflake/agent/` |
| Unstructured notes, AI_CLASSIFY, AI_FILTER, Cortex Search | generated and modelled; AI functions need account | `dbt/macros/portable.sql`, `snowflake/search/` |
| Dynamic table, task loop, ops views, alerts | written; needs account | `snowflake/dynamic_tables/`, `snowflake/tasks/` |
| API: query, ask, compare, before-after, meta, glossary, lineage, audit, status, operations | done | `api/tests` |
| Front end: ten pages, design system, states, footer status | done | Playwright, `docs/design.md` QA checklist |
| Public mirror (demo mode) | done; hosting not done | `make demo-mirror` |
| Seven evaluation suites | done locally; account variants pending | `eval/report.md` |
| CI: locks, pip-audit, npm audit, SBOM, image scan | written; runs on first push | `.github/workflows/ci.yml` |
| SPCS service, smoke, release gate, rollback | written; needs account | `scripts/spcs.py`, `scripts/release_gate.py` |
| Cortex Code plugin: skills, commands, subagents, hooks, MCP, tasks | done | `docs/built-with-coco.md` |
| Documents and runbooks | done | `docs/`, root markdown |
| Databricks metric views | compiled; not run on Databricks | `ontology/generated/databricks/` |
| Marketplace join, CoWork publication | notes only | `docs/marketplace.md`, `docs/cowork.md` |
| History of 40 to 80 commits | done: 80 | `git rev-list --count HEAD` |

## Needs the account

1. `make setup ENV=dev`: roles (including JUDGE_ROLE and the service user), schemas, policies, monitors, event table, alerts, ops views.
2. `make load`, then `dbt build --target dev` on Snowflake, including the AI_CLASSIFY and AI_FILTER models and the delivery-event dynamic table.
3. `make release ENV=dev`: semantic views, procedures, agents, Cortex Search; YAML round-trip check.
4. `make smoke` and `make eval-account`: the agent:run accuracy floor and the Time Travel restore check (the two pending checks), GET_LINEAGE parity (Enterprise edition).
5. SPCS image push, `scripts/spcs.py deploy`, rollback drill.
6. snowflake-connector-python 4.x paths (moved from 3.x for the security fix) against a live connection.
7. First CI run on GitHub: SBOM upload and the trivy image scan.
8. Re-author the history with the team identity before pushing; no team identity is configured on this machine.
9. Hosting the public mirror, Marketplace listing choice, CoWork publication.
