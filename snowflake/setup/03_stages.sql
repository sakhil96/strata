-- Internal stages for data loading and artefact storage.

USE ROLE SCM_DEPLOY;
USE DATABASE {{DB}};

CREATE STAGE IF NOT EXISTS RAW.SOURCE_DATA
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Raw source system files (Parquet)';

CREATE STAGE IF NOT EXISTS RAW.REFERENCE_DATA
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Reference data (HTS tariff schedule, GSCPI, FX rates)';

CREATE STAGE IF NOT EXISTS EVAL.TRUTH_STAGE
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Evaluation truth metrics';

CREATE STAGE IF NOT EXISTS OPS.ARTEFACTS
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Operational artefacts (dbt manifests, eval reports)';

CREATE STAGE IF NOT EXISTS SEMANTIC.VIEW_YAML
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Semantic view YAML files for deployment';

-- The glossary arrives as one JSON document and is flattened by semantic/load_glossary.sql.
CREATE FILE FORMAT IF NOT EXISTS SEMANTIC.JSON_DOC TYPE = JSON;
