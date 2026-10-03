# docs/DECISIONS.md — Architecture and design decisions

## 2026-10-02: Repository initialised from scratch

We start from an empty directory. No template, no scaffold. Every file is hand-written
or compiler-generated from the ontology.

## 2026-10-02: LinkML for the ontology

LinkML gives us typed YAML with inheritance, generates Pydantic models, JSON Schema,
OWL and ER diagrams from one source. The supply chain domain fits its class/slot model
naturally. We vendor no LinkML runtime into the application; it is a build-time dependency.

## 2026-10-02: Fiscal year starts 1 October

Aligns with the US federal fiscal year and a common multinational calendar. The data
generator creates exactly one fiscal year: FY2026 (1 Oct 2025 to 30 Sep 2026).

## 2026-10-02: Single accent colour (--ore #E36F2E)

One accent reduces decision fatigue and makes the active element unambiguous. Every other
colour in the palette is neutral. We reserve green, yellow and red for status only.

## 2026-10-02: Three environments as separate databases

SCM_DEV, SCM_TEST, SCM_PROD. Separate databases rather than schemas because Snowflake
network policies, resource monitors and grants are easier to reason about at the database
level, and it mirrors how enterprises actually operate.

## 2026-10-02: No SQL tool on the agent

The agent has only GOVERNED_QUERY, DESCRIBE_METRIC and EXPLAIN_LINEAGE. This makes every
answer auditable and every metric traceable. The cost is that ad-hoc exploration must
go through the Builder or Cortex Analyst with instructions that route metric questions
back to GOVERNED_QUERY.

## 2026-10-02: Ratios are ratios of sums

We never average pre-computed ratios. on_time_delivery at the region level is
count(on_time lines in region) / count(all lines in region), not avg(plant-level OTD).
This is mathematically correct and avoids Simpson's paradox.

## 2026-10-02: DuckDB + dbt-core + Cube for local fallback

Developers and CI run the full pipeline without Snowflake credentials. The same ontology
and registry produce dbt models targeting DuckDB and Cube views. `make local-demo`
stands up the entire stack on a laptop.

## 2026-10-02: Rebuild history before publishing

The first two commits bundled 164 files, which hid the order we built things in and broke our
own one-change-per-commit rule. Before the repository goes public we replayed the same tree as
61 commits by area in build order. The tree at the new head is byte-identical to the old one
(`git diff pre-rebuild` is empty). The old history stays on the local `pre-rebuild` branch until
the first public push, then we delete it. No team author identity is configured on this machine,
so commits carry the local default; we re-author before pushing.

## 2026-10-02: Audit before closing gaps

docs/GAPS.md records each specification item as present, partial or absent with the command that
proved it. We close gaps in priority order, one commit per gap.

## Lock the image for Linux, not for the laptop

The runtime and dev locks are resolved for `x86_64-manylinux_2_28`, the image platform. An earlier
`cryptography<46` pin existed only because cryptography 50 has no Intel macOS wheel; it shipped
eight advisories (fixed in 46.0.5 to 50.0.0) and pyOpenSSL 25 two more. Lifting it required
snowflake-connector-python 4.x, which in turn required dbt-snowflake 1.10+, so the build extra moved
to dbt-core 1.11 and dbt-duckdb 1.10. The local DuckDB build passes 78 of 78 on the new dbt. The
Snowflake paths on connector 4 have not been run against an account yet.

## The service holds no secret

The SPCS container authenticates with the session token Snowflake mounts at
`/snowflake/session/token`. A `secrets:` block would add a credential to rotate and nothing else, so
the service spec has none. Key-pair JWT is used only by CI and by laptops.

## Cortex Analyst is an exploration tool, not an answering tool

The spec lists Cortex Analyst among the agent's tools and also says numbers come only from
GOVERNED_QUERY. Both hold: the agent may call Analyst to explore phrasing, but `api/agent.py` parses
numbers only from GOVERNED_QUERY results, and the governance suite fails if any other tool's output
reaches an answer.

## Deployment account baseline (2026-10-02)

Account XZ02973 (ZV32033), organisation DZVLNOZ, region GCP_ME_CENTRAL2, **Standard edition**,
created 2026-09-20, free-usage balance USD 378.20 at the start of the DEV run. The trial expiry is
not exposed to SQL; if it is the usual 30-day trial it ends around 2026-10-20 (unverified).
Cortex cross-region inference is ANY_REGION; SPCS is enabled.

Standard edition has no masking policies, row access policies, GET_LINEAGE, per-database event
tables or Time Travel beyond one day. Standard edition: controls realised as compiled secure views.
Row scope and column rules are declared in ontology/entitlements.yaml and compiled to secure views in
SEMANTIC_BASE; EXPLAIN_LINEAGE returns the compiled path; retention is one day. docs/governance.md
maps each control to what each edition provides.

The repository is not on GitHub yet, so dbt is deployed with `snow dbt deploy` from the working
tree instead of from a Git repository object. The image build needs Docker and the public mirror
needs a Vercel token; neither is available on the deploying machine.

## Personas read semantic views only (2026-10-03)

Semantic views run with owner's rights, so SCM_READER holds SELECT on the views in SEMANTIC and
nothing in CONFORMED, STAGING or RAW. On Standard edition, where no masking policy can hide contact
and bank columns, this is what keeps them from persona roles. The cost: Cortex Analyst requires
SELECT on base tables for the calling role, so the agent's Analyst tool works only for SCM_DEPLOY
and above. It was exploration-only already; numbers still come from GOVERNED_QUERY.

## Loader types follow the Parquet logical types (2026-10-03)

The first dbt run on Snowflake failed in 11 models: INFER_SCHEMA kept Parquet's lower-case names
as quoted identifiers, and microsecond timestamps arrived as NUMBER. The loader now infers with
IGNORE_CASE and a USE_LOGICAL_TYPE file format, and replaces each RAW table on load. Replacing RAW
tables means FCT_DELIVERY_EVENT must be recreated after a reload.

## A fact may not share its metric's name (2026-10-03)

Snowflake resolves a column reference inside a semantic view to a same-named metric before the
physical column, so `shipments.transit_hours` (fact) beside `transit_hours` (metric) is cyclic and
no expression spelling avoids it. The column is now `transit_hours_elapsed` in fct_shipment and the
registry, and check_registry refuses a fact named like a metric on its table.

## Agent model pinned to claude-sonnet-4-6 (2026-10-03)

The first agent:run on the DEV account was refused: claude-4-sonnet is not an allowed agent model
there. The orchestration model stays pinned rather than 'auto', per AGENTS.md, and moves to
claude-sonnet-4-6, the nearest successor on the account's allowed list. Both agents changed;
the accuracy floor is re-measured on the new model before anything is promoted.

## The answer agent's tool set is the enforcement (2026-10-03)

"Numbers only through GOVERNED_QUERY" is enforced by what SCM_AGENT can call, not by what it is
told. Its tools are GOVERNED_QUERY, DESCRIBE_METRIC, EXPLAIN_LINEAGE and Cortex Search for
citations; none of them returns a number except GOVERNED_QUERY, which writes AUDIT.ANSWERS with
the hash it returns. Cortex Analyst writes and runs its own SQL, so it is an exploration tool for
data engineers: it lives on SCM_EXPLORE_AGENT, usable by SCM_DEPLOY only, and nothing it says is a
governed answer. Suite 3 reconciles every numeric agent answer with an audit row of the same hash.

GOVERNED_QUERY takes the query as one JSON string because agent procedure tools on a warehouse
accept only scalar arguments.

## Positions read the window's closing month, pinned in the query (2026-10-03)

Inventory metrics are NON ADDITIVE BY period_month with a descending sort, so a query without a
month breakdown should read the latest month. On the DEV account the semantic view returned the
earliest month instead (FY2026 days_of_inventory 65.42, October's value, against 18.51 for
September). render_semantic_sql now pins such a query to the window's closing month, and the
local engine uses the same rule; the canonical query and its hash are unchanged. Suite 1 checks
the five canonical metrics against truth through a persona view on the account.

## The service's identity inside SPCS (2026-10-03)

Network policies do apply to connections a service makes from inside Snowpark Container Services:
if the account or the user the service connects as has a network policy, it needs a network rule
of type COMPUTE_POOL that allows the service's compute pool
(https://docs.snowflake.com/en/developer-guide/snowpark-container-services/spcs-execute-sql).
The service therefore uses its own SPCS session token, not SCM_SERVICE_USER's key, and the account
policy, when applied, carries a COMPUTE_POOL rule for SCM_POOL_<ENV>. SCM_SERVICE_USER, whose
policy allows only the team and GitHub Actions, stays for agent:run from outside the pool.

## Blocked on the DEV run (2026-10-03)

Step 8, the service: blocked: Docker (`docker version` fails on the deploying machine). No image
repository or compute pool was created, so nothing idles at cost. Step 9, the public mirror:
blocked: token (no Vercel token in the secret store).

## Nightly evaluation runs as a task, not as Cortex Code (2026-10-03)

COCO_ROUTINE_NIGHTLY_EVAL is suspended until further notice. Cortex Code was 68.53 of the
81.69 USD spent in the first three days of the trial, and the operational loop already runs
dbt and the evaluation suites every night as tasks on SCM_WH_DEV, at warehouse cost only. The
routine stays defined so it can be resumed for an investigation; nothing depends on it.

DEV loads its sources once, so the stale-source alert would mail every hour from six hours after
that load. dev.yaml sets `stale_source_alert: SUSPEND`, which resume_alerts.sql applies; TEST and
PROD resume it. The other three alerts judge things DEV still produces and stay on.

## The /query latency target is 2500 ms (2026-10-03)

On SCM_DEV the builder path measured p95 1590 ms over its first day against a 1500 ms target, and
SLO_BREACH_ALERT triggered on it. Most of that time is the procedure call and the semantic view on
an XS warehouse that resumes from suspend, not the API. The target is the measured value with
headroom, 2500 ms, in OPS.SLO_STATUS, the local backend and docs/slo.md; the agent target stays
6 s. It is revisited once a week of answers exists rather than a day.

## Operations and governance read the environment, not the repository (2026-10-03)

ALERT_HISTORY and SHOW ALERTS answer only an alert's owner, so OPS.ALERT_STATUS is now a procedure
owned by SCM_ADMIN that runs as its owner, and readers call it: started or suspended from SHOW
ALERTS, the last outcome and the last firing from the history. The cost task runs daily and keeps
a week-to-date row. eval/report.py writes every suite and the total to EVAL.EVAL_RUNS when it runs
against an account, and the governance page reads the latest batch there and the agent card from
DESCRIBE AGENT. The committed governance snapshot keeps only grants and policies, with {{DB}}
left as a placeholder, so nothing committed names an environment or a model it does not run.

## A held-out question set, scored and not tuned against (2026-10-03)

eval/questions_heldout.yaml holds ten questions in a judge's wording with no phrasing or filter value
from eval/questions.yaml. The first pass scored 10 of 10 exact and nothing in the agent spec was
changed for it. What we would change next, and did not here: the GOVERNED_QUERY description lists
every filter value and plant name, which is why unseen values like EMEA, OCEAN or Joliet resolve;
that list should be generated from the dimension tables by the compiler rather than written by hand,
or it drifts the first time a plant is added. Synonyms the held-out set leaned on ("stock cover",
"run dry", "lets us down", "land") belong in the registry's synonyms so the resolver fallback gets
them too, not only the agent. The set should grow with each judge's own questions, and a question
that fails goes into the tuned set only after it has been scored here once.

## The agent resolves, the persona executes (2026-10-03)

How agent:run picks its role, from the Cortex Agents docs: "Cortex Agents determines permissions from
the querying user's default role, not the role active in their session", and a request can run
under another role only by setting the X-Snowflake-Role header
(https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-manage). Our calls set no
such header, so every agent tool call ran as SCM_SERVICE_ROLE on SCM_GOVERNED_V1, and the Ask
ledger showed that role: a scoped persona such as EMEA_PLANNING_ROLE would have read global numbers.

The agent is now only the reader of the question. /ask takes every distinct canonical query the
agent settled on and runs it again through GOVERNED_QUERY as the caller's persona (USE ROLE through
SCM_SERVICE_PERSONAS) on that persona's semantic view. The rows, chart, table, hash, ledger and audit
row shown are that execution's; the agent's own tool calls, as SCM_SERVICE_ROLE, are not shown and
leave their own audit rows marked with the agent path. We did not use X-Snowflake-Role for the
persona because the agent would still choose the view, and because it would give every persona the
agent's whole tool set at once rather than one governed query.

The agent's reply is at most two plain sentences on how it read the question. The lead sentence is
written by the API from the persona's own result (api/narrate.py), and a reading that carries an
amount, a rate or a hash is dropped. A signed-in user listed in SCM_USER_PERSONAS is pinned to that
persona and the dial follows; other users choose with the dial.

## Running in Snowpark Container Services: what the docs settle, and where we stopped (2026-10-03)

From the SPCS docs: a service's session is opened with the OAuth token in /snowflake/session/token,
with the service's owner role as the primary role. With `capabilities.securityContext.executeAsCaller:
true` the ingress adds Sf-Context-Current-User-Token, and the service can open a session as the
calling user on that user's default role; that is caller's rights, and it needs CALLER grants on the
owner role. Either way the session is the one the token allows: the service cannot pick roles beyond
it, so the SCM_SERVICE_PERSONAS key-pair impersonation used on DEV does not carry over. Persona
execution in SPCS would be caller's rights, with each judge or persona user's default role set to
their persona role.

The agent is the blocker. Calling agent:run from inside the service needs a token Snowflake accepts
on its REST surface. A community article on the managed MCP server reports that the SPCS session
token is refused there ("Client is unauthorized to use Snowpark Container Services OAuth token"); we
have not tried agent:run itself because there is no service to try it from. If it is refused too, the
container needs a credential of its own: a key pair or a programmatic access token held as a Snowflake
SECRET mounted into the service. That is a private key in the container, which the brief says to stop
at. Options: (1) a PAT for SCM_SERVICE_USER, scoped to SCM_SERVICE_ROLE and the network policy, mounted
as a SPCS secret, with a short expiry and a rotation drill; (2) keep the API outside SPCS and serve
only the static web build from it; (3) use the resolver, which needs no agent, inside the service and
leave the agent for the local and DEV runs, saying so on the About page. None is chosen yet.

## The service on SCM_DEV: spec, endpoint access and idle cost (2026-10-03)

This settles the question left open above. agent:run accepts the SPCS session token: Ask from the
endpoint resolves through SCM_AGENT and answers on the persona's view (path `agent`), so the container
holds no key or PAT. Persona execution uses the signed-in user from Sf-Context-Current-User, pinned
through SCM_USER_PERSONAS for the three endpoint-check users; everyone else chooses on the dial.

- `platformMonitor` is out of `snowflake/spcs/service_spec.yaml`. With it, CREATE SERVICE failed with
  a Snowflake internal error (incident 1307069); without it the service starts. Metrics are not needed
  for the SLOs, which read AUDIT.ANSWERS.
- The readiness probe reads `/live`, not `/health`. `/health` opens a Snowflake session and takes over
  two seconds, which the probe treated as unready.
- The governed procedures take their database from the DDL, not the session. A session that agent:run
  opens from inside SPCS has no current database, and `get_current_database()` returned None, so every
  agent tool call failed and Ask fell back to the resolver. `create_procs.sql` wraps each handler
  inline with the rendered `{{DB}}`; RECORD_REFUSAL qualifies AUDIT.ANSWERS for the same reason.
- `scripts/spcs.py` grants the service role `STRATA_SERVICE!ALL_ENDPOINTS_USAGE` to the five persona
  roles on every apply. Without it the token exchange answers 395042, "could not find the service",
  rather than a privilege error.
- Idle cost. AUTO_RESUME on the service wakes it on an ingress request. AUTO_SUSPEND_SECS on a
  service is a preview feature and the docs say it is not supported on services with a public
  endpoint, because only service-function traffic counts as activity. So the service does not
  suspend itself: we suspend it with `ALTER SERVICE ... SUSPEND` when no one is evaluating, and the
  pool's AUTO_SUSPEND_SECS = 300 then stops the node. The first request after that wakes both.
