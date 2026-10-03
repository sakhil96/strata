# AGENTS.md — Cortex Code operating rules for scm-ontology

## Purpose

We are building STRATA, an enterprise supply chain ontology application on Snowflake.
The ontology is authored once in LinkML YAML, compiled into Snowflake semantic views,
dbt models, a glossary, Apache Ossie interchange models and a Cube fallback. A Cortex
Agent answers cross-domain questions only through governed procedures over semantic views.
Planning, procurement, logistics and executive personas get identical answers to the same
question. The AI is one governed component of the application, not the application.

## Ontology-first rule

Every metric definition, entity relationship, hierarchy and data-quality rule lives in
`ontology/ontology.yaml` and `ontology/metrics.yaml`. The compiler (`ontology/compile.py`)
generates all downstream artefacts. We never hand-edit generated files. If the compiler
output is wrong, we fix the registry or the compiler, never the output.

## No-SQL-in-agent rule

The Cortex Agent has exactly three tools: `GOVERNED_QUERY`, `DESCRIBE_METRIC` and
`EXPLAIN_LINEAGE`. It has no SQL tool. It never sees table names. Its instructions and
evaluation sets are versioned in Git. Its model is pinned.

## Registry rules

Every metric in `ontology/metrics.yaml` declares: name, title, type, grain, date_basis,
window, numerator, denominator, definition, formula_text, synonyms, variants, owner,
steward, scor_attribute, unit, persona_synonyms, version, status, approved_by, approved_on.
The compiler refuses any metric missing a required field. Only metrics with
`status: approved` deploy to SCM_PROD.

## Environment rule

- **SCM_DEV**: development work, created and torn down freely.
- **SCM_TEST**: CI and integration testing; nightly evaluation runs here.
- **SCM_PROD**: production; changes arrive only through `deploy.yml` after all gates pass.

Always `/guardrails` to the current environment database before executing statements.

## Role hierarchy

```
SCM_ADMIN
  └── SCM_DEPLOY
        ├── PLANNING_ROLE
        ├── PROCUREMENT_ROLE
        ├── LOGISTICS_ROLE
        └── EXECUTIVE_ROLE
              └── SCM_READER
```

Row access policies on conformed facts. Tag-based masking policies on contact and
bank-detail columns. Grants are snapshotted and diffed in CI.

## Design bans (section 12)

Rejected on sight: purple or blue gradients; glassmorphism; glowing or animated borders;
emoji or sparkle/rocket/brain/robot icons; centred hero with three equal feature cards;
equal-box card grids with icons; chat bubbles with avatars; "Powered by AI" badge;
default library styling; stock photos or video; lorem ipsum; rainbow categorical colours;
drop shadows; pill buttons everywhere; dark-mode toggle as a hero feature.

## Authorship rules (section 13)

- Write config files by hand; never keep scaffold output.
- Comments are sparse, explain why, read like notes to a colleague.
- No docstrings restating a function name. No file headers except the compiler's single
  generated line.
- No comments containing: "generated", "AI", "assistant", "here is", "example",
  "placeholder", "sample", "TODO", "lorem", "foo", "bar".
- Names from the domain: ledger, persona, basis, grain, stratum, lane.
- No dead code, unused dependencies, commented-out blocks, console.log, print debugging
  or empty catch blocks.
- Test names describe behaviour; fixtures have domain names.

## Workflow

1. `cortex --plan` for any DDL or grant statement.
2. `/guardrails` before executing in any environment.
3. Commit at every milestone with an imperative message.
4. Record assumptions in docs/DECISIONS.md with dates.
5. Keep CHANGELOG.md current.
