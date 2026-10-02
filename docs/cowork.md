# Publishing to Snowflake CoWork

SCM_AGENT can be surfaced in Snowflake CoWork (formerly Snowflake Intelligence) by granting USAGE on
the agent to the roles that should see it and adding it to the CoWork agent list. Its answers are
then the same governed answers the API returns, with the same audit rows. The Steward agent should
stay unpublished: it proposes registry changes and is for stewards only. Not done: needs the account.
