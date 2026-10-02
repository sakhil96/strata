.PHONY: compile data load deploy eval local-demo setup spcs-deploy spcs-rollback spcs-logs clean

ENV ?= dev
VERSION ?= 1

compile:
	python ontology/compile.py --env $(ENV) --version $(VERSION)

data:
	python data/generate.py

load:
	python data/load.py --env $(ENV)

setup:
	@echo "Run snowflake/setup/00_account.sql through 09_secrets.sql against the account"
	@echo "Substitute {{DB}} with SCM_$(shell echo $(ENV) | tr a-z A-Z) and {{ENV}} with $(shell echo $(ENV) | tr a-z A-Z)"

deploy: compile
	@echo "Deploying semantic views to SCM_$(shell echo $(ENV) | tr a-z A-Z)"
	snow sql -f snowflake/semantic/deploy.sql
	snow sql -f snowflake/semantic/versioning.sql

eval:
	pytest eval/ -v --tb=short -q 2>&1 | tee eval/report.md
	python eval/report.py

local-demo:
	@echo "Starting local demo with DuckDB + dbt-core + Cube"
	python data/generate.py
	cd dbt && dbt run --target duckdb
	cd cube && python cube.py
	@echo "Local demo ready"

spcs-deploy:
	snow spcs compute-pool create SCM_POOL_$(shell echo $(ENV) | tr a-z A-Z) \
		--family CPU_X64_XS --min-nodes 1 --max-nodes 1 --auto-suspend-secs 300 || true
	snow spcs service create STRATA_SERVICE \
		--compute-pool SCM_POOL_$(shell echo $(ENV) | tr a-z A-Z) \
		--spec-path snowflake/spcs/service_spec.yaml

spcs-rollback:
	@echo "Rolling back to previous image tag"
	snow spcs service set STRATA_SERVICE --spec-path snowflake/spcs/service_spec.yaml.prev

spcs-logs:
	snow spcs service logs STRATA_SERVICE --container strata

clean:
	rm -rf ontology/generated/* snowflake/semantic/*.yaml snowflake/semantic/*.sql
	rm -rf cube/model/* data/out/*
