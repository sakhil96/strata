# STATUS.md — Current state of the STRATA project

Last updated: 2026-10-02

## What passes

### Compilation
- `python ontology/compile.py` compiles all 10 metrics to all targets without errors.
- All metrics have required fields and `status: approved`.
- Generated files carry the single-line header comment.

### Evaluation (local, without Snowflake)
- **Metric identity**: all 10 metrics present, all required fields validated, persona synonyms cover all 4 roles, ratio metrics have numerator/denominator.
- **Governance**: agent SQL has exactly 3 tools, no SQL tool, instructions forbid raw SQL, refusal and resolution policies present, answer contract fields present, no table names in instructions.

### CI
- Lint (ruff check), format (ruff format), and compile jobs defined in `.github/workflows/ci.yml`.
- Data generation and eval jobs defined and chained.
- Deploy workflow with evaluation gate for PROD.

### Front end
- Tokens, typography and layout defined in `tokens.css` and `tailwind.config.ts`.
- Components: PersonaDial, Ledger, Builder, Convergence, Strata, AuditStream, StatusBar.
- Pages: / (landing), /ask, /compare, /before-after, /glossary, /governance, /operations, /about.
- All pages follow the STRATA design system: dark ground, --ore accent, asymmetric layout, Fraunces display, JetBrains Mono for data.

## What does not pass yet

### Snowflake deployment
- Semantic views not yet deployed (requires Snowflake connection and `SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML`).
- Procedures not yet created as Snowflake objects.
- Agent not yet created (requires procedures as tools).
- SPCS service not yet deployed.

### End-to-end integration
- /ask and /query routes require a live Snowflake connection.
- NL accuracy and persona consistency suites require the agent to be deployed.
- Resilience suite requires SPCS probes.

### Data
- Reference data CSVs (hts_2026.csv, gscpi.csv) are placeholders; generate.py creates synthetic data.
- Truth metrics are computed but not yet loaded into EVAL.TRUTH_METRICS.

### Design QA
- Playwright screenshots not yet committed.
- Lighthouse scores not yet measured.
- Font files not yet self-hosted (font-face declarations point to expected locations).

## How to run

```bash
# Local development (no Snowflake)
make data                    # Generate test data
make compile ENV=dev         # Compile ontology to all targets
pytest eval/ -v              # Run local evaluation suite
cd web && npm install && npm run dev   # Start front end

# With Snowflake
make setup ENV=dev           # Run setup SQL
make load ENV=dev            # Load data into Snowflake
make deploy ENV=dev          # Deploy semantic views
cd api && uvicorn main:app   # Start API
```

## Open gaps

See `docs/hardening-backlog.md` for the full list with owners.

Key gaps:
1. Network policy CIDRs are placeholder (0.0.0.0/0).
2. Container image scanning and SBOM not yet automated.
3. Row access policy uses role-based check, not user-to-region mapping table.
4. Failover group for DR not yet configured (requires Business Critical Edition).
5. Font files need to be downloaded and committed (SIL OFL).
6. Ossie and Databricks targets generate structure but are not validated against real runtimes.
7. Cube fallback starts DuckDB but Cube server is not packaged.
8. Demo video placeholder — not yet recorded.

## Commit history

See `git log --oneline` for the full history. Target: 40-80 coherent commits.
