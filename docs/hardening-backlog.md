# Hardening backlog

Items not yet implemented, with owners and target dates.

## Security
- [ ] Replace 0.0.0.0/0 in network rules with actual team and CI CIDRs. Owner: Platform. 
- [ ] Enable MFA for all human users. Owner: Security.
- [ ] Container image scanning in CI (Trivy or Snyk). Owner: Platform.
- [ ] SBOM generation and publication. Owner: Platform.
- [ ] Row access policy based on user-to-region mapping table (not role-based). Owner: Security.

## Observability
- [ ] Grafana dashboard from event table metrics. Owner: Platform.
- [ ] Alerting via webhook to Slack (currently email only). Owner: Platform.
- [ ] SLO burn-rate alerting. Owner: Platform.

## Resilience
- [ ] Failover group setup on Business Critical Edition. Owner: Platform.
- [ ] Quarterly DR test. Owner: Platform.
- [ ] Chaos testing: inject stale source and verify alert fires. Owner: QA.

## Front end
- [ ] Playwright screenshots at 390/1024/1440 committed. Owner: Design.
- [ ] Lighthouse performance >= 90 on /ask. Owner: Design.
- [ ] Self-hosted icon set (currently no icons). Owner: Design.
- [ ] Print stylesheet with --paper and --ink tokens. Owner: Design.

## Data
- [ ] Reference data: HTS 2026 CSV with real tariff codes. Owner: Data.
- [ ] Reference data: GSCPI CSV with monthly index values. Owner: Data.
- [ ] Insurance and handling cost components in landed cost. Owner: Analytics.
