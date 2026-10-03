# How to evaluate STRATA

Three ways in, from least to most setup.

## 1. The public mirror (no install)

A static build of the front end with answers recorded from the local build (`make demo-mirror`).
Every page works; Ask and Compare replay the questions offered on screen. Typed questions that were
not recorded say so instead of guessing. The Builder answers live only when the mirror is built with
`STRATA_API` pointing at a service-user API.

## 2. A laptop, no Snowflake (about five minutes)

Python 3.11 and Node 22.

```
uv venv .venv --python 3.11 && uv pip install -r requirements-dev.lock
cd web && npm ci && cd ..
make local-demo          # data, dbt on DuckDB, compile, web build, API on :8000
make eval                # seven suites; account-only checks report needs_account
```

Open http://127.0.0.1:8000. The same canonicaliser, query hash and SQL renderer run here as in
the procedures, so hashes match what Snowflake returns for the same question.

## 3. Your Snowflake account (Enterprise edition, for GET_LINEAGE)

```
make setup ENV=dev CONN=scm_dev      # roles incl. JUDGE_ROLE, schemas, policies, monitors, ops
make load ENV=dev CONN=scm_dev
make release ENV=dev CONN=scm_dev        # objects, views, procedures, agent; then grants
make loop ENV=dev CONN=scm_dev           # freshness, dbt and eval tasks
make smoke ENV=dev CONN=scm_dev
make eval-account ENV=dev CONN=scm_dev
```

Grant `JUDGE_ROLE` to your user. It reads the persona views, the glossary and the audit trail and
cannot see RAW or CONFORMED.

## What to check

| Claim | Where to look |
|---|---|
| One definition, three vocabularies, one number | Compare page; `eval/test_persona_consistency.py`; on SCM_DEV, `eval/report/persona_account.md`: 20 cases × 3 roles through GOVERNED_QUERY, identical rows and hashes, hashes equal to the local engine's |
| Numbers match an independent truth | `eval/test_metric_identity.py`, every metric × month × plant × region × segment × family |
| Legacy numbers disagree for stated reasons | Before/after page; `api/legacy.py` |
| The agent cannot answer outside the procedures | Governance page; `eval/test_governance.py` |
| Refusals for raw SQL, table access, injection | Ask page; `eval/questions.yaml` refusals |
| Builds are reproducible | `make reproducible` |
