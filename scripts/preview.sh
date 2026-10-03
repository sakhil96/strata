#!/usr/bin/env bash
# The whole product on a laptop against SCM_DEV: API on :8000, Next dev on :3000. Nothing deploys.
#   scripts/preview.sh        start both, logs in .strata/
#   scripts/preview.sh stop   stop both
# SCM_DEFAULT_ROLE picks the persona the dial starts on (PLANNING_ROLE unless set).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .strata

stop() {
  for name in api web; do
    if [[ -f .strata/$name.pid ]]; then
      pkill -P "$(cat .strata/$name.pid)" 2>/dev/null || true
      kill "$(cat .strata/$name.pid)" 2>/dev/null || true
      rm -f .strata/$name.pid
    fi
  done
}

if [[ "${1:-start}" == "stop" ]]; then
  stop
  exit 0
fi
stop

NODE_BIN=$(dirname "$(command -v node 2>/dev/null || echo /tmp/node-v22.11.0-darwin-x64/bin/node)")
PY=$([[ -x .venv/bin/python ]] && echo .venv/bin/python || echo python3)

# Queries switch into each persona's role, which the scm_dev key-pair user can do and the service
# role, by design, cannot; agent:run is signed with the service user's key.
SCM_BACKEND=snowflake SCM_ENV=dev SNOWFLAKE_CONNECTION_NAME=scm_dev \
SCM_DEFAULT_ROLE="${SCM_DEFAULT_ROLE:-PLANNING_ROLE}" SCM_PREVIEW_USER="${SCM_PREVIEW_USER:-PREVIEW_PLANNER}" \
SCM_AGENT=on SCM_AGENT_TIMEOUT_S=120 SNOWFLAKE_USER=SCM_SERVICE_USER \
SNOWFLAKE_HOST="${SNOWFLAKE_HOST:-xz02973.me-central2.gcp.snowflakecomputing.com}" \
SNOWFLAKE_ACCOUNT="${SNOWFLAKE_ACCOUNT:-XZ02973}" \
SNOWFLAKE_PRIVATE_KEY_PATH="${SERVICE_KEY:-$HOME/.snowflake/keys/scm_service_dev.p8}" \
nohup "$PY" -m uvicorn preview_api:app --app-dir scripts --port 8000 < /dev/null > .strata/api.log 2>&1 &
echo $! > .strata/api.pid

cd web
PATH="$NODE_BIN:$PATH" STRATA_PREVIEW_API=http://127.0.0.1:8000 \
  nohup ./node_modules/.bin/next dev --port 3000 < /dev/null > ../.strata/web.log 2>&1 &
echo $! > ../.strata/web.pid
cd ..

echo "api http://localhost:8000 (log .strata/api.log), web http://localhost:3000 (log .strata/web.log)"
