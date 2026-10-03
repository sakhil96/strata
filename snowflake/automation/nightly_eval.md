You are running unattended in a Snowflake AGENT TASK; complete the task autonomously and do NOT ask clarifying questions. Use SQL only; you have read-only access.

Database SCM_DEV. For each metric in (on_time_delivery, unit_fill_rate, otif, days_of_inventory, landed_cost_per_unit) do two things.

1. Governed value. Run, substituting the metric and its logical table (delivered_lines for on_time_delivery and otif, requested_lines for unit_fill_rate, inventory for days_of_inventory, po_lines for landed_cost_per_unit):
   SELECT * FROM SEMANTIC_VIEW(SCM_DEV.SEMANTIC.SCM_GOVERNED_V1 METRICS <table>.<metric> WHERE <table>.period_month BETWEEN '2025-10-01' AND '2026-09-01')
   For days_of_inventory use WHERE inventory.period_month = '2026-09-01' instead, because it is a month-end position.
2. Truth. From SCM_DEV.EVAL.TRUTH_METRICS where grouping = 'month' and month between '2025-10-01' and '2026-09-01': for days_of_inventory take value at month '2026-09-01'; for the others SUM(numerator) / SUM(denominator).
   A metric passes when the absolute difference is below 0.000001.

Then read the last run of the operational loop:
   SELECT name, state, error_message FROM TABLE(SCM_DEV.INFORMATION_SCHEMA.TASK_HISTORY(SCHEDULED_TIME_RANGE_START => DATEADD(hour, -24, CURRENT_TIMESTAMP()))) WHERE name LIKE 'LOOP_%'
   SELECT suite, passed, total, run_at FROM SCM_DEV.EVAL.EVAL_RUNS ORDER BY run_at DESC LIMIT 1

Report a table of metric, governed value, truth and pass, then the loop tasks that did not succeed, if any.
End with exactly one line: NIGHTLY_EVAL_OK metrics=<passed>/5 loop_failures=<n> last_identity=<passed>/<total>
or, if anything failed: NIGHTLY_EVAL_FAILED:<one-line reason>
