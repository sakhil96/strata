# SLO Targets

## Service availability
- Target: 99.5% monthly uptime for the STRATA SPCS service.
- Measured from: SPCS service status + /health probe success rate.

## Answer latency
- Agent path (/ask): p95 <= 6 seconds end to end.
- Builder path (/query): p95 <= 1.5 seconds.
- Measured from: AUDIT.ANSWERS.latency_ms.

## Evaluation pass rate
- Floor: 90% of all evaluation suites must pass.
- Measured from: eval/report.json after each nightly run.

## Source freshness
- Alert threshold: any source stale > 6 hours.
- Measured from: OPS.FRESHNESS.last_loaded_at.

## dbt build
- Zero test failures in CONFORMED schema.
- Alert on any failure within 2 hours.
