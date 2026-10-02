# Metric change process

## When a metric definition changes

1. **Propose**: open a pull request to `ontology/metrics.yaml` with:
   - The changed fields (numerator, denominator, formula_text, etc.).
   - A rationale in the PR body explaining why the change is needed.
   - A bumped `version` field.

2. **Review**: the metric steward (named in the `steward` field) reviews the change.
   - They verify the business logic is correct.
   - They verify the change does not break downstream consumers.
   - They add their name to `approved_by` and today's date to `approved_on`.

3. **Compile**: `make compile` succeeds with no errors.
   - The compiler refuses metrics missing required fields.
   - The compiler validates that the formula text is consistent with the type.

4. **Test**: CI runs the full evaluation suite.
   - Metric identity tests must pass (truth metrics updated if the definition changed).
   - Persona consistency tests must pass (all roles get the same answer).
   - NL accuracy tests must pass (the agent resolves the metric correctly).

5. **Deploy**: the new semantic view version is deployed as `_V{n+1}`.
   - The previous version `_V{n}` is kept for rollback.
   - Grants are swapped from old to new version.
   - The old definition is marked `status: deprecated` in the glossary for one release cycle.

6. **Communicate**: the deprecation notice appears in the glossary with the replacement metric.
   - The glossary shows both versions during the transition period.
   - After one release cycle, the deprecated version is removed.

## Invariants

- `status: draft` metrics compile for DEV and TEST but are blocked from PROD.
- `status: deprecated` metrics are emitted with a deprecation notice.
- Only `status: approved` metrics deploy to PROD.
- The version field is monotonically increasing per metric.
