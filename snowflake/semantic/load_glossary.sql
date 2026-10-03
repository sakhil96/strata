-- Generated from ontology/*.yaml by compile.py; edit the registry, not this file.
USE SCHEMA SCM_DEV.SEMANTIC;
CREATE TABLE IF NOT EXISTS SCM_DEV.SEMANTIC.GLOSSARY (metric_name STRING, entry VARIANT, loaded_at TIMESTAMP_NTZ);
CREATE OR REPLACE TEMPORARY TABLE glossary_incoming AS
  SELECT value:metric_name::STRING AS metric_name, value AS entry
  FROM @SCM_DEV.SEMANTIC.VIEW_YAML/glossary.json (FILE_FORMAT => 'SCM_DEV.SEMANTIC.JSON_DOC'),
  LATERAL FLATTEN(input => $1);
MERGE INTO SCM_DEV.SEMANTIC.GLOSSARY g USING glossary_incoming i ON g.metric_name = i.metric_name
  WHEN MATCHED THEN UPDATE SET entry = i.entry, loaded_at = CURRENT_TIMESTAMP()
  WHEN NOT MATCHED THEN INSERT VALUES (i.metric_name, i.entry, CURRENT_TIMESTAMP());
