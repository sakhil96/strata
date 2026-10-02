#!/usr/bin/env bash
# Writes a key-pair connection for CI from the runner's secret. The key never touches the repo.
set -euo pipefail
name="$1"; role="$2"
umask 077
mkdir -p ~/.snowflake
printf '%s\n' "$SNOWFLAKE_PRIVATE_KEY_RAW" > ~/.snowflake/"$name".p8
cat >> ~/.snowflake/connections.toml <<TOML
[$name]
account = "$SNOWFLAKE_ACCOUNT"
user = "SCM_SERVICE_USER"
role = "$role"
authenticator = "SNOWFLAKE_JWT"
private_key_file = "$HOME/.snowflake/$name.p8"
TOML
chmod 600 ~/.snowflake/connections.toml
