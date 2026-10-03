-- SCM_EXPLORE_AGENT: Cortex Analyst over the governed semantic view, for data engineers.
-- It writes and runs its own SQL, so it is not a path to governed numbers: nothing it says is
-- audited as an answer, and only SCM_DEPLOY may use it. Personas ask SCM_AGENT.

USE ROLE SCM_DEPLOY;
USE SCHEMA {{DB}}.AGENT;

CREATE OR REPLACE AGENT {{DB}}.AGENT.SCM_EXPLORE_AGENT
  COMMENT = 'Engineer exploration over SCM_GOVERNED; not a source of governed numbers'
  PROFILE = '{"display_name": "Strata explore"}'
  FROM SPECIFICATION
$$
models:
  orchestration: claude-sonnet-4-6

orchestration:
  budget:
    seconds: 60
    tokens: 24000

instructions:
  orchestration: >-
    You help data engineers explore the governed supply chain semantic view: which dimensions,
    values and breakdowns exist, and how a metric behaves under a grouping. Say in every reply that
    exploration results are not governed answers and that governed numbers come from SCM_AGENT.
  response: >-
    Show the SQL you ran. Sentence case, no exclamation marks.

tools:
  - tool_spec:
      type: cortex_analyst_text_to_sql
      name: EXPLORE_GOVERNED_VIEW
      description: Text to SQL over SCM_GOVERNED for exploration by engineers.

tool_resources:
  EXPLORE_GOVERNED_VIEW:
    semantic_view: {{DB}}.SEMANTIC.SCM_GOVERNED_V1
    execution_environment: {type: warehouse, warehouse: {{WH}}, query_timeout: 30}
$$;

GRANT USAGE ON AGENT {{DB}}.AGENT.SCM_EXPLORE_AGENT TO ROLE SCM_DEPLOY;
