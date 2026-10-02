# Contributing to scm-ontology

We welcome contributions that follow these conventions.

## Ontology first

Every metric, entity and relationship is defined in `ontology/ontology.yaml` and
`ontology/metrics.yaml`. The compiler generates downstream artefacts. Never hand-edit
a generated file — fix the registry or the compiler instead.

## Code style

- Python: ruff format, ruff check. Type hints on public functions.
- TypeScript: prettier, tsc strict mode.
- SQL: uppercase keywords, lowercase identifiers, 2-space indent.
- Comments explain why, not what. No docstrings restating a function name.
- Names from the domain (ledger, persona, basis, grain, stratum, lane).

## Commits

- Imperative mood, present tense ("add metric registry", not "added metric registry").
- Each commit is one coherent change.
- No tool names, scaffold references or marketing language in messages.

## Testing

- Test names describe behaviour: `test_otd_excludes_cancelled_lines`.
- Fixtures use domain names: `receipt_on_time`, not `test_data_1`.
- Every metric change requires an evaluation run before merge.

## Metric changes

Follow `docs/metric-change-process.md`: pull request to `metrics.yaml` with rationale,
steward approval, bumped version, compile and evaluation green in CI.

## Security

Report vulnerabilities per SECURITY.md. Never commit secrets, passwords or API keys.
