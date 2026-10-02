"""PreToolUse guard. Reads the tool call as JSON on stdin; exit 2 blocks it with a reason on stderr."""

import json
import re
import sys

SQL_BANS = [
    (r"\b(drop|truncate)\s+(database|schema|table)\b[^;]*\bSCM_PROD\b", "destructive DDL against SCM_PROD"),
    (r"\bgrant\s+\w+.*\bto\s+role\s+(public|\w+_ROLE)\b.*\b(RAW|CONFORMED)\b", "grants on RAW or CONFORMED to a persona role"),
    (r"\buse\s+role\s+accountadmin\b", "ACCOUNTADMIN from an agent session"),
    (r"\bselect\b[^;]*\bfrom\s+\w*\.?RAW\.", "querying RAW directly; answer through GOVERNED_QUERY"),
]
BASH_BANS = [
    (r"git\s+push\b.*--force|git\s+push\s+-f\b", "force push"),
    (r"--no-verify", "skipping hooks"),
    (r"git\s+config\b(?!.*--get)", "changing git config"),
    (r"rm\s+-rf\s+(/|~|\.\s*$)", "recursive delete of a root"),
    (r"make\s+(release|promote|deploy)\s+.*ENV=prod", "production release outside CI"),
]
FILE_BANS = [
    (r"^snowflake/semantic/|^dbt/models/schema\.yml$|^ontology/generated/", "compiled output; edit the ontology and run /compile"),
    (r"(^|/)\.env$|\.p8$|rsa_key", "credential files"),
]


def check(rules, text):
    for pattern, reason in rules:
        if re.search(pattern, text, re.I | re.M):
            print(f"blocked: {reason}", file=sys.stderr)
            sys.exit(2)


call = json.load(sys.stdin)
args = call.get("tool_input", call.get("input", {}))
kind = sys.argv[1]
if kind == "sql":
    check(SQL_BANS, args.get("sql", ""))
elif kind == "bash":
    check(BASH_BANS, args.get("command", ""))
else:
    path = args.get("file_path", "")
    check(FILE_BANS, path.split("supplyC/", 1)[-1])
