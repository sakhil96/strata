#!/usr/bin/env bash
# make data and make compile twice; every output must be byte-identical between the runs.
set -euo pipefail
cd "$(dirname "$0")/.."
outputs="data/out ontology/generated snowflake/semantic dbt/models/conformed/schema.yml cube/model docs/er_diagram.svg"
digest() { find $outputs -type f ! -name '*.pyc' -print0 | sort -z | xargs -0 shasum -a 256; }
python data/generate.py >/dev/null && python ontology/compile.py >/dev/null
digest > /tmp/strata-run-1.sha
python data/generate.py >/dev/null && python ontology/compile.py >/dev/null
digest > /tmp/strata-run-2.sha
if diff -q /tmp/strata-run-1.sha /tmp/strata-run-2.sha >/dev/null; then
  echo "reproducible: $(wc -l < /tmp/strata-run-1.sha | tr -d ' ') files byte-identical across two runs"
else
  diff /tmp/strata-run-1.sha /tmp/strata-run-2.sha; exit 1
fi
