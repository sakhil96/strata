-- The repository as a Snowflake object, so deploys run committed files and nothing else.
USE ROLE SCM_ADMIN;

CREATE SECRET IF NOT EXISTS {{DB}}.OPS.GIT_READ_TOKEN
    TYPE = PASSWORD USERNAME = 'scm-ontology-ci' PASSWORD = 'set-via-cli'
    COMMENT = 'Read-only fine-grained token; rotated with runbooks/rotate-keys.md';

CREATE API INTEGRATION IF NOT EXISTS SCM_GIT_INTEGRATION
    API_PROVIDER = git_https_api
    API_ALLOWED_PREFIXES = ('https://github.com/scm-ontology/')
    ALLOWED_AUTHENTICATION_SECRETS = ({{DB}}.OPS.GIT_READ_TOKEN)
    ENABLED = TRUE;

CREATE GIT REPOSITORY IF NOT EXISTS {{DB}}.OPS.SCM_REPO
    API_INTEGRATION = SCM_GIT_INTEGRATION
    GIT_CREDENTIALS = {{DB}}.OPS.GIT_READ_TOKEN
    ORIGIN = 'https://github.com/scm-ontology/scm-ontology.git';

GRANT READ ON GIT REPOSITORY {{DB}}.OPS.SCM_REPO TO ROLE SCM_DEPLOY;

-- A deploy is: fetch, then run the files from the commit we just tested.
-- ALTER GIT REPOSITORY {{DB}}.OPS.SCM_REPO FETCH;
-- EXECUTE IMMEDIATE FROM @{{DB}}.OPS.SCM_REPO/branches/main/snowflake/semantic/deploy.sql;
