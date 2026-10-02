# Every target runs from the repository root. ENV is dev, test or prod; VERSION is the semantic-view suffix.
ENV ?= dev
VERSION ?= 1
PY ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
CONN ?= scm_$(ENV)
export SCM_ENV := $(ENV)
export SCM_VERSION := $(VERSION)

.PHONY: help setup data compile reproducible dbt-local web lint test eval governance-snapshot e2e screenshots \
	lighthouse load deploy release promote rollback smoke eval-account loop local-demo demo-mirror \
	spcs-build spcs-deploy spcs-rollback spcs-logs clean

help:
	@grep -E '^[a-z-]+:' Makefile | cut -d: -f1 | sort | tr '\n' ' '; echo

setup:            ## account objects for one environment: roles, schemas, policies, monitors, alerts, ops
	$(PY) scripts/render_sql.py setup --env $(ENV) --connection $(CONN)

data:
	$(PY) data/generate.py
	-$(PY) data/reference/fetch_gscpi.py

compile:
	$(PY) ontology/compile.py --env $(ENV) --version $(VERSION)

reproducible:
	scripts/reproducible.sh

dbt-local:
	cd dbt && dbt build --profiles-dir . --target local --quiet

web:
	cd web && npm run build

lint:
	ruff check .
	$(PY) scripts/authorship_lint.py
	cd web && npx prettier --check . && npx tsc --noEmit

test:
	$(PY) -m pytest ontology/tests api/tests --cov --cov-report=term-missing:skip-covered -q

governance-snapshot:
	$(PY) eval/snapshot_governance.py

eval:
	$(PY) eval/report.py

e2e:
	cd web && npx playwright test pages.spec.ts answers.spec.ts

screenshots:
	cd web && npx playwright test screenshots.spec.ts

lighthouse:
	cd web && npm run lighthouse

load:
	$(PY) data/load.py --env $(ENV) --connection $(CONN)

deploy: compile  ## objects and views beside the current version; does not move grants
	snow git fetch SCM_$(shell echo $(ENV) | tr a-z A-Z).OPS.SCM_REPO -c $(CONN)
	$(PY) scripts/render_sql.py objects --env $(ENV) --connection $(CONN)
	$(PY) scripts/render_sql.py views --env $(ENV) --connection $(CONN)
	$(PY) scripts/render_sql.py agent --env $(ENV) --connection $(CONN)

promote:
	$(PY) scripts/render_sql.py promote --env $(ENV) --connection $(CONN)

release: deploy promote

rollback:         ## grants back to VERSION; the newer views stay for diagnosis
	$(PY) ontology/compile.py --env $(ENV) --version $(VERSION) --target snowflake-semantic
	$(PY) scripts/render_sql.py promote --env $(ENV) --connection $(CONN)

smoke:
	$(PY) scripts/smoke.py --env $(ENV) --connection $(CONN)

eval-account:
	SCM_BACKEND=snowflake SCM_AGENT=on SNOWFLAKE_CONNECTION_NAME=$(CONN) $(PY) eval/report.py

loop:
	$(PY) scripts/render_sql.py loop --env $(ENV) --connection $(CONN)

local-demo: data dbt-local compile web  ## the whole product on a laptop, no Snowflake
	SCM_BACKEND=local $(PY) -m uvicorn api.main:app --port 8000

demo-mirror: dbt-local compile  ## the public mirror: recorded answers, no backend
	$(PY) scripts/record_mirror.py
	cd web && npm run build:demo

spcs-build:
	docker build --platform linux/amd64 -t strata:$(shell git rev-parse --short HEAD) .

spcs-deploy:
	$(PY) scripts/spcs.py deploy --env $(ENV) --connection $(CONN) --tag $(shell git rev-parse --short HEAD)

spcs-rollback:
	$(PY) scripts/spcs.py rollback --env $(ENV) --connection $(CONN)

spcs-logs:
	snow spcs service logs SCM_$(shell echo $(ENV) | tr a-z A-Z).AGENT.STRATA_SERVICE --container-name strata --instance-id 0 -c $(CONN)

clean:
	rm -rf data/out dbt/target web/out web/.next .strata eval/.results
