-- Cortex Search over exception notes, contract clauses and operating procedures.
-- The agent's SEARCH_NOTES tool reads this service; it quotes notes and never derives metrics from them.

USE ROLE SCM_DEPLOY;

CREATE OR REPLACE CORTEX SEARCH SERVICE {{DB}}.SEMANTIC.SCM_NOTES_SEARCH
  ON body
  PRIMARY KEY (doc_id)
  ATTRIBUTES kind, category, is_customer_impacting, related_id, title
  WAREHOUSE = {{WH}}
  TARGET_LAG = '1 hour'
  EMBEDDING_MODEL = 'snowflake-arctic-embed-m-v1.5'
  COMMENT = 'Exception notes, contract clauses and procedures for the governed agent'
AS
  SELECT doc_id, body, kind, category, is_customer_impacting::string AS is_customer_impacting, related_id, title
  FROM {{DB}}.CONFORMED.DIM_DOCUMENT;

GRANT USAGE ON CORTEX SEARCH SERVICE {{DB}}.SEMANTIC.SCM_NOTES_SEARCH TO ROLE SCM_READER;

-- How far Cortex agrees with the simulator's ground truth on exception causes.
CREATE OR REPLACE VIEW {{DB}}.EVAL.NOTE_CLASSIFICATION_AGREEMENT AS
SELECT
    COUNT(*) AS notes,
    COUNT_IF(category = source_category) / NULLIF(COUNT(*), 0) AS cause_agreement
FROM {{DB}}.CONFORMED.DIM_DOCUMENT
WHERE kind = 'exception_note';
