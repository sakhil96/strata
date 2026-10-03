# Built with Cortex Code

The repository is a Cortex Code plugin (`.cortex-plugin/plugin.json`; `cortex plugin validate .`
passes). Loading it gives a session the project's rules instead of re-explaining them.

| Part | Path | Use |
|---|---|---|
| Skills | `skills/<name>/SKILL.md` | registry rules, compile, semantic views, security baseline, design system, evals, release, authorship |
| Commands | `commands/*.md` | `/compile`, `/data`, `/eval`, `/deploy`, `/rollback`, `/audit-metric`, `/design-check` |
| Subagents | `agents/*.md` | metric-steward, governance-auditor, eval-analyst, frontend-reviewer; all report, none edit |
| Hooks | `hooks/hooks.json`, `hooks/guard.py` | PreToolUse bans: destructive DDL on SCM_PROD, RAW reads, ACCOUNTADMIN, force push, `--no-verify`, edits to compiled output, credential files |
| MCP | `.mcp.json` | Playwright for page checks, GitHub, and the project's own MCP server over the three procedures |
| Plan | `tasks/day01.md` to `day14.md` | the build order, each with a done-when check |

Bundled skills used during the build: `cortex-ai-function-studio` for the AI_CLASSIFY and AI_FILTER
note models, and `cortex-code-guide` for the plugin layout. Account-side checks those skills
recommend (privilege checks, live validation) were deferred to the account run and are listed in
docs/STATUS.md.

## The deployment session (2026-10-03)

Cortex Code ran the SPCS deployment, endpoint checks, evaluator access, history scrub and squash, CI
repairs, the mirror and these documents in one session against SCM_DEV, with the session's Cortex Code
credits read from METERING_HISTORY before and after each step. Two defects surfaced only on the
account and were fixed in the repository rather than worked around: the procedures' missing database
inside agent:run, and the endpoint service role missing from the persona roles.
