-- SCM_STEWARD: drafts metric-change proposals for stewards. It reads the glossary,
-- the audit trail and the evaluation runs; it cannot change the registry, deploy, or
-- answer metric questions for end users. Its output is a pull-request description.

USE ROLE SCM_DEPLOY;
USE SCHEMA {{DB}}.AGENT;

CREATE OR REPLACE PROCEDURE {{DB}}.AGENT.STEWARD_EVIDENCE(METRIC STRING)
RETURNS VARIANT
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
DECLARE
    evidence VARIANT;
BEGIN
    SELECT OBJECT_CONSTRUCT(
        'definition', (SELECT entry FROM SEMANTIC.GLOSSARY WHERE metric_name = :METRIC),
        'asked_last_30_days', (SELECT COUNT(*) FROM AUDIT.ANSWERS
                               WHERE metric_names ILIKE '%' || :METRIC || '%' AND ts > DATEADD(day, -30, CURRENT_TIMESTAMP())),
        'refusals_mentioning', (SELECT COUNT(*) FROM AUDIT.ANSWERS
                                WHERE refusal IS NOT NULL AND question ILIKE '%' || REPLACE(:METRIC, '_', ' ') || '%'),
        'last_eval', (SELECT OBJECT_CONSTRUCT('pass_rate', pass_rate, 'run_at', run_at)
                      FROM EVAL.EVAL_RUNS ORDER BY run_at DESC LIMIT 1)
    ) INTO :evidence;
    RETURN evidence;
END;
$$;

CREATE OR REPLACE AGENT {{DB}}.AGENT.SCM_STEWARD
  COMMENT = 'Drafts registry change proposals; no write access'
  FROM SPECIFICATION
$$
models:
  orchestration: claude-4-sonnet
instructions:
  orchestration: >-
    You help a metric steward prepare a change to ontology/metrics.yaml. Gather evidence with
    STEWARD_EVIDENCE and the current definition with DESCRIBE_METRIC. Produce a pull-request
    description with: the proposed change, the rationale, the evidence, the version bump, which
    evaluation questions will change, and the deprecation notice for the old definition. Never
    claim a change has been made; you cannot make one.
  response: Plain markdown, sentence case, no marketing language.
tools:
  - tool_spec:
      type: generic
      name: STEWARD_EVIDENCE
      description: Usage, refusals and the latest evaluation for one metric.
      input_schema: {type: object, properties: {metric: {type: string}}, required: [metric]}
  - tool_spec:
      type: generic
      name: DESCRIBE_METRIC
      description: The governed definition of one metric.
      input_schema: {type: object, properties: {name: {type: string}}, required: [name]}
tool_resources:
  STEWARD_EVIDENCE:
    type: procedure
    identifier: {{DB}}.AGENT.STEWARD_EVIDENCE
    execution_environment: {type: warehouse, warehouse: {{WH}}}
  DESCRIBE_METRIC:
    type: procedure
    identifier: {{DB}}.AGENT.DESCRIBE_METRIC
    execution_environment: {type: warehouse, warehouse: {{WH}}}
$$;

GRANT USAGE ON AGENT {{DB}}.AGENT.SCM_STEWARD TO ROLE SCM_DEPLOY;
