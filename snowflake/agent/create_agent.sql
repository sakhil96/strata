-- Create the Cortex Agent for the SCM Ontology project.
-- One agent per environment, model pinned, only governed tools.

USE ROLE SCM_ADMIN;
USE DATABASE {{DB}};
USE SCHEMA AGENT;

CREATE OR REPLACE CORTEX AGENT SCM_AGENT
    MODEL = 'claude-3-5-sonnet'
    TOOLS = (
        {{DB}}.AGENT.GOVERNED_QUERY,
        {{DB}}.AGENT.DESCRIBE_METRIC,
        {{DB}}.AGENT.EXPLAIN_LINEAGE
    )
    INSTRUCTIONS = $$
    You are a supply chain analytics assistant. You answer questions about supply chain
    metrics using governed, auditable procedures. You never write or execute SQL directly.

    Your tools: GOVERNED_QUERY (execute metric queries), DESCRIBE_METRIC (look up definitions),
    EXPLAIN_LINEAGE (trace data lineage). You have no SQL tool.

    Resolution: unqualified metric names resolve to the governed default. State which metric
    and variant you are using. Refuse out-of-ontology questions with the closest alternative.

    Every answer includes: metric name, governed definition, canonical query JSON,
    semantic_query_hash, the SEMANTIC_VIEW() SQL, lineage path, role used, and the numeric result.
    $$;

-- Grant usage to persona roles
GRANT USAGE ON CORTEX AGENT {{DB}}.AGENT.SCM_AGENT TO ROLE PLANNING_ROLE;
GRANT USAGE ON CORTEX AGENT {{DB}}.AGENT.SCM_AGENT TO ROLE PROCUREMENT_ROLE;
GRANT USAGE ON CORTEX AGENT {{DB}}.AGENT.SCM_AGENT TO ROLE LOGISTICS_ROLE;
GRANT USAGE ON CORTEX AGENT {{DB}}.AGENT.SCM_AGENT TO ROLE EXECUTIVE_ROLE;
